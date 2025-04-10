"""Anwendungshandbuch SQL models"""

import uuid
from datetime import date
from typing import Optional, Union
from uuid import UUID

from efoli import EdifactFormatVersion

# pylint: disable=too-few-public-methods, duplicate-code, missing-function-docstring

# the structures are similar, still we decided against inheritance, so there's naturally a little bit of duplication


try:
    from sqlalchemy import CheckConstraint, UniqueConstraint
    from sqlmodel import Field, Relationship, SQLModel
except ImportError as import_error:
    import_error.msg += "; Did you install fundamend[sqlmodels] or did you try to import from fundamend.models instead?"
    # sqlmodel is only an optional dependency when fundamend is used to fill a database
    raise


from fundamend.models.anwendungshandbuch import Anwendungsfall as PydanticAnwendungsfall
from fundamend.models.anwendungshandbuch import Anwendungshandbuch as PydanticAnwendungshandbuch
from fundamend.models.anwendungshandbuch import Bedingung as PydanticBedingung
from fundamend.models.anwendungshandbuch import Code as PydanticCode
from fundamend.models.anwendungshandbuch import DataElement as PydanticDataElement
from fundamend.models.anwendungshandbuch import DataElementGroup as PydanticDataElementGroup
from fundamend.models.anwendungshandbuch import Paket as PydanticPaket
from fundamend.models.anwendungshandbuch import Segment as PydanticSegment
from fundamend.models.anwendungshandbuch import SegmentGroup as PydanticSegmentGroup
from fundamend.models.anwendungshandbuch import UbBedingung as PydanticUbBedingung


class Code(SQLModel, table=True):
    """
    A single code element inside an AHB DataElement, indicated by the `<Code>` tag.
    """

    __table_args__ = (
        UniqueConstraint("data_element_primary_key", "position", name="IX_position_once_per_data_element"),
    )
    primary_key: UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    name: str = Field(index=True)  # e.g. 'Netznutzungszeiten-Nachricht'
    description: str | None = Field(default=None, index=True)  # e.g. ''
    value: str | None = Field(default=None, index=True)  # e.g. 'UTILTS'
    ahb_status: str  #: e.g. 'X' # new for AHB
    position: Optional[int] = Field(default=None, index=True)

    dataelement: Union["DataElement", None] = Relationship(back_populates="codes")
    data_element_primary_key: UUID | None = Field(default=None, foreign_key="dataelement.primary_key")

    @classmethod
    def from_model(cls, model: PydanticCode, position: Optional[int] = None) -> "Code":
        return Code(
            name=model.name,
            description=model.description,
            value=model.value,
            ahb_status=model.ahb_status,
            position=position,
        )

    def to_model(self) -> PydanticCode:
        return PydanticCode(
            name=self.name,
            description=self.description,
            value=self.value,
            ahb_status=self.ahb_status,
        )


class DataElement(SQLModel, table=True):
    """
    A single data element, German 'Datenelement' inside an AHB Segment, indicated by the `<D_xxxx>` tag.
    This element can contain a single or multiple Code elements.
    """

    # Example:
    # <D_0065 Name="Nachrichtentyp-Kennung">
    #   <Code Name="Netznutzungszeiten-Nachricht" Description="" AHB_Status="X">UTILTS</Code>
    # </D_0065>
    primary_key: UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    id: str = Field(index=True)  # e.g. 'D_0065'
    name: str = Field(index=True)  # e.g. 'Nachrichtentyp-Kennung'
    codes: list[Code] = Relationship(back_populates="dataelement")
    position: Optional[int] = Field(default=None, index=True)
    ahb_status: Optional[str] = None
    dataelementgroup: Union["DataElementGroup", None] = Relationship(back_populates="data_elements")
    data_element_group_primary_key: UUID | None = Field(default=None, foreign_key="dataelementgroup.primary_key")

    segment: Union["Segment", None] = Relationship(back_populates="data_elements")
    segment_primary_key: UUID | None = Field(default=None, foreign_key="segment.primary_key")

    @classmethod
    def from_model(cls, model: PydanticDataElement, position: Optional[int] = None) -> "DataElement":
        result = DataElement(
            id=model.id,
            name=model.name,
            codes=[
                Code.from_model(pydantic_code, position=position_index)
                for position_index, pydantic_code in enumerate(model.codes)
            ],
            ahb_status=model.ahb_status,
            position=position,
        )
        return result

    def to_model(self) -> PydanticDataElement:
        return PydanticDataElement(
            id=self.id,
            name=self.name,
            ahb_status=self.ahb_status,
            codes=tuple(x.to_model() for x in sorted(self.codes, key=lambda y: y.position or 0)),
        )


class DataElementGroup(SQLModel, table=True):
    """
    A group of data elements, German 'Datenelementgruppe' inside the AHB, indicated by the `<C_xxxx>` tag.
    This model can contain both the 'Datenelement' and the 'Gruppendatenelement'
    """

    __table_args__ = (UniqueConstraint("segment_primary_key", "position", name="IX_position_once_per_segment"),)
    # "Die Datenelementgruppe C0829 enthält mehrere Gruppendatenelemente. Diese Datenelementgruppe enthält das
    # Gruppendatenelement DE3039, hier wird die MP-ID angegeben, sowie das DE3055, welches die code-vergebende Stelle
    # definiert. Diese Datenelementgruppe enthält des Weiteren das Gruppendatenelement DE113110, welches nur in der MIG
    # und nicht im AHB aufgeführt wird, um den Aufbau der EDIFACT Nachricht korrekt umsetzen zu können."
    # Quelle: Allgemeine Festlegungen Kapitel 6.1, Seite 52

    # Example:
    # <C_C002 Name="Dokumenten-/Nachrichtenname">
    #    <D_1001 Name="Dokumentenname, Code">
    #      <Code Name="Berechnungsformel" Description="" AHB_Status="X">Z36</Code>
    #   </D_1001>
    # </C_C002>
    primary_key: UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    id: str = Field(index=True)  # e.g. 'C_C082'
    name: str = Field(index=True)  # e.g. 'Dokumenten-/Nachrichtenname'
    data_elements: list[DataElement] = Relationship(back_populates="dataelementgroup")
    position: Optional[int] = Field(default=None, index=True)
    segment: Union["Segment", None] = Relationship(back_populates="data_element_groups")
    segment_primary_key: Union[UUID, None] = Field(default=None, foreign_key="segment.primary_key")

    @classmethod
    def from_model(cls, model: PydanticDataElementGroup, position: Optional[int] = None) -> "DataElementGroup":
        result = DataElementGroup(
            id=model.id,
            name=model.name,
            position=position,
        )
        for position_index, x in enumerate(model.data_elements):
            de = DataElement.from_model(x, position=position_index)
            result.data_elements.append(de)
        return result

    def to_model(self) -> PydanticDataElementGroup:
        return PydanticDataElementGroup(
            id=self.id,
            name=self.name,
            data_elements=tuple(x.to_model() for x in sorted(self.data_elements, key=lambda y: y.position or 0)),
        )


class Segment(SQLModel, table=True):
    """
    A segment inside an AHB, indicated by the `<S_xxxx>` tag.
    This model can contain both data elements and data element groups.
    """

    # Example:
    # pylint:disable=line-too-long
    #  <S_BGM Name="Beginn der Nachricht" Number="00002" AHB_Status="Muss">
    #    <C_C002 Name="Dokumenten-/Nachrichtenname">
    #       <D_1001 Name="Dokumentenname, Code">
    #         <Code Name="Berechnungsformel" Description="" AHB_Status="X">Z36</Code>
    #       </D_1001>
    #    </C_C002>
    #    <C_C106 Name="Dokumenten-/Nachrichten-Identifikation">
    #       <D_1004 Name="Dokumentennummer" AHB_Status="X"/>
    #    </C_C106>
    # </S_BGM>
    primary_key: UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    id: str = Field(index=True)  #: e.g. 'BGM'
    name: str = Field(index=True)  #: e.g. 'Beginn der Nachricht'
    number: str = Field(index=True)  #: e.g. '00002'
    ahb_status: str | None  #: e.g. 'Muss'
    data_elements: list[DataElement] = Relationship(back_populates="segment")
    data_element_groups: list[DataElementGroup] = Relationship(back_populates="segment")
    position: Optional[int] = Field(default=None, index=True)

    segmentgroup: Union["SegmentGroup", None] = Relationship(back_populates="segments")
    segmentgroup_primary_key: Union[UUID, None] = Field(default=None, foreign_key="segmentgroup.primary_key")

    anwendungsfall: Union["Anwendungsfall", None] = Relationship(back_populates="segments")
    anwendungsfall_primary_key: Union[UUID, None] = Field(default=None, foreign_key="anwendungsfall.primary_key")

    @classmethod
    def from_model(cls, model: PydanticSegment, position: Optional[int] = None) -> "Segment":
        result = Segment(
            id=model.id,
            name=model.name,
            number=model.number,
            ahb_status=model.ahb_status,
            position=position,
        )
        for _position, element in enumerate(model.data_elements):
            if isinstance(element, PydanticDataElement):
                result.data_elements.append(DataElement.from_model(element, position=_position))
                continue
            if isinstance(element, PydanticDataElementGroup):
                result.data_element_groups.append(DataElementGroup.from_model(element, position=_position))
                continue
        return result

    def to_model(self) -> PydanticSegment:
        return PydanticSegment(
            id=self.id,
            name=self.name,
            number=self.number,
            ahb_status=self.ahb_status,
            data_elements=tuple(
                x.to_model()
                for x in sorted(
                    (self.data_elements or []) + (self.data_element_groups or []),  # type:ignore[operator]
                    key=lambda y: y.position or 0,
                )
            ),
        )


class SegmentGroupLink(SQLModel, table=True):
    """artificial construct in SQL to model Segment Groups being nested in other Segment Groups"""

    parent_id: UUID | None = Field(default=None, foreign_key="segmentgroup.primary_key", primary_key=True)
    child_id: UUID | None = Field(default=None, foreign_key="segmentgroup.primary_key", primary_key=True)


class SegmentGroup(SQLModel, table=True):
    """
    A 'Segmentgruppe' inside an AHB, indicated by the `<G_xxxx>` tag.
    This model can contain both Segments and segment groups.
    """

    # Example:
    # <G_SG6 Name="Prüfidentifikator" AHB_Status="Muss">
    #   <S_RFF Name="Prüfidentifikator" Number="00012" AHB_Status="Muss">
    #     <C_C506 Name="Referenz">
    #       <D_1153 Name="Referenz, Qualifier">
    #         <Code Name="Prüfidentifikator" Description="" AHB_Status="X">Z13</Code>
    #       </D_1153>
    #       <D_1154 Name="Referenz, Identifikation">
    #         <Code Name="Berechnungsformel" Description="" AHB_Status="X">25001</Code>
    #       </D_1154>
    #     </C_C506>
    #   </S_RFF>
    #  </G_SG6>
    primary_key: UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    id: str = Field(index=True)  #: e.g. 'SG6'
    name: str = Field(index=True)  #: e.g. 'Prüfidentifikator'
    ahb_status: str | None  #: e.g. 'Muss'
    segments: list[Segment] = Relationship(back_populates="segmentgroup")
    position: Optional[int] = Field(default=None, index=True)
    # Define self-referential relationship
    segment_groups: list["SegmentGroup"] = Relationship(
        back_populates="parent_segment_group",
        sa_relationship_kwargs={
            "primaryjoin": "SegmentGroup.primary_key==SegmentGroupLink.parent_id",
            "secondaryjoin": "SegmentGroup.primary_key==SegmentGroupLink.child_id",
            "foreign_keys": "[SegmentGroupLink.parent_id, SegmentGroupLink.child_id]",
        },
        link_model=SegmentGroupLink,
    )

    parent_segment_group: Optional["SegmentGroup"] = Relationship(
        back_populates="segment_groups",
        sa_relationship_kwargs={
            "primaryjoin": "SegmentGroup.primary_key==SegmentGroupLink.child_id",
            "secondaryjoin": "SegmentGroup.primary_key==SegmentGroupLink.parent_id",
            "foreign_keys": "[SegmentGroupLink.child_id, SegmentGroupLink.parent_id]",
        },
        link_model=SegmentGroupLink,
    )

    anwendungsfall: Union["Anwendungsfall", None] = Relationship(back_populates="segment_groups")
    anwendungsfall_primary_key: Union[UUID, None] = Field(default=None, foreign_key="anwendungsfall.primary_key")

    @classmethod
    def from_model(cls, model: PydanticSegmentGroup, position: Optional[int] = None) -> "SegmentGroup":
        result = SegmentGroup(
            id=model.id,
            name=model.name,
            ahb_status=model.ahb_status,
            position=position,
        )
        for _position, element in enumerate(model.elements):
            if isinstance(element, PydanticSegment):
                result.segments.append(Segment.from_model(element, position=_position))
                continue
            if isinstance(element, PydanticSegmentGroup):
                sg = SegmentGroup.from_model(element, position=_position)
                if result.segment_groups is None:
                    result.segment_groups = [sg]
                else:
                    result.segment_groups.append(sg)
                continue
        return result

    def to_model(self) -> PydanticSegmentGroup:
        return PydanticSegmentGroup(
            id=self.id,
            name=self.name,
            ahb_status=self.ahb_status,
            elements=tuple(
                x.to_model()
                for x in sorted(
                    (self.segments or []) + (self.segment_groups or []),  # type:ignore[operator]
                    key=lambda y: y.position or 0,
                )
            ),
        )


class Anwendungsfall(SQLModel, table=True):
    """
    One 'Anwendungsfall', indicated by `<AWF>` tag, corresponds to one Prüfidentifikator or type of Message
    """

    __table_args__ = (UniqueConstraint("anwendungshandbuch_primary_key", "position", name="IX_position_once_per_ahb"),)
    # Example:
    # <AWF Pruefidentifikator="25001" Beschreibung="Berechnungsformel" Kommunikation_von="NB an MSB / LF">
    #   <M_UTILTS>
    #     <S_UNH Name="Nachrichten-Kopfsegment" Number="00001" AHB_Status="Muss">
    #    ...
    #     </S_UNT>
    #   </M_UTILTS>
    # </AWF>
    primary_key: UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    pruefidentifikator: str = Field(index=True)  #: e.g. '25001'
    beschreibung: str = Field(index=True)  #: e.g. 'Berechnungsformel'
    kommunikation_von: str  #: e.g. 'NB an MSB / LF'
    format: str = Field(index=True)  #: e.g. 'UTILTS'
    segments: list[Segment] = Relationship(back_populates="anwendungsfall")
    segment_groups: list[SegmentGroup] = Relationship(back_populates="anwendungsfall")
    position: Optional[int] = Field(default=None, index=True)
    anwendungshandbuch: Union["Anwendungshandbuch", None] = Relationship(back_populates="anwendungsfaelle")
    anwendungshandbuch_primary_key: Union[UUID, None] = Field(
        default=None, foreign_key="anwendungshandbuch.primary_key"
    )

    @classmethod
    def from_model(cls, model: PydanticAnwendungsfall, position: Optional[int] = None) -> "Anwendungsfall":
        result = Anwendungsfall(
            pruefidentifikator=model.pruefidentifikator,
            beschreibung=model.beschreibung,
            kommunikation_von=model.kommunikation_von,
            format=model.format,
            position=position,
        )
        for _position, element in enumerate(model.elements):
            if isinstance(element, PydanticSegment):
                result.segments.append(Segment.from_model(element, position=_position))
                continue
            if isinstance(element, PydanticSegmentGroup):
                result.segment_groups.append(SegmentGroup.from_model(element, position=_position))
                continue
        return result

    def to_model(self) -> PydanticAnwendungsfall:
        return PydanticAnwendungsfall(
            pruefidentifikator=self.pruefidentifikator,
            beschreibung=self.beschreibung,
            kommunikation_von=self.kommunikation_von,
            format=self.format,
            elements=tuple(
                x.to_model()
                for x in sorted(
                    ((self.segments or []) + (self.segment_groups or [])),  # type:ignore[operator]
                    key=lambda y: y.position or 0,
                )
            ),
        )


class Bedingung(SQLModel, table=True):
    """Ein ConditionKeyConditionText Mapping"""

    __table_args__ = (UniqueConstraint("anwendungshandbuch_primary_key", "position", name="IX_position_once_per_ahb"),)
    primary_key: UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    nummer: str = Field(index=True)  #: e.g. '1'
    text: str  #: e.g. 'Nur MP-ID aus Sparte Strom'
    position: Optional[int] = Field(default=None, index=True)
    anwendungshandbuch: Union["Anwendungshandbuch", None] = Relationship(back_populates="bedingungen")
    anwendungshandbuch_primary_key: Union[UUID, None] = Field(
        default=None, foreign_key="anwendungshandbuch.primary_key"
    )

    @classmethod
    def from_model(cls, model: PydanticBedingung, position: Optional[int] = None) -> "Bedingung":
        return Bedingung(nummer=model.nummer, text=model.text, position=position)

    def to_model(self) -> PydanticBedingung:
        return PydanticBedingung(nummer=self.nummer, text=self.text)


class UbBedingung(SQLModel, table=True):
    """Eine UB-Bedingung"""

    __table_args__ = (UniqueConstraint("anwendungshandbuch_primary_key", "position", name="IX_position_once_per_ahb"),)
    # Example:
    # <UB_Bedingung Nummer="[UB1]">([931] ∧ [932] [490]) ⊻ ([931] ∧ [933] [491])</UB_Bedingung>
    primary_key: UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    nummer: str = Field(index=True)  # e.g. 'UB1'
    text: str  #: e.g. '([931] ∧ [932] [490]) ⊻ ([931] ∧ [933] [491])'
    position: Optional[int] = Field(default=None, index=True)
    anwendungshandbuch: Union["Anwendungshandbuch", None] = Relationship(back_populates="ub_bedingungen")
    anwendungshandbuch_primary_key: Union[UUID, None] = Field(
        default=None, foreign_key="anwendungshandbuch.primary_key"
    )

    @classmethod
    def from_model(cls, model: PydanticUbBedingung, position: Optional[int] = None) -> "UbBedingung":
        return UbBedingung(nummer=model.nummer, text=model.text, position=position)

    def to_model(self) -> PydanticUbBedingung:
        return PydanticUbBedingung(nummer=self.nummer, text=self.text)


class Paket(SQLModel, table=True):
    """Ein Bedingungspaket/PackageKeyConditionText Mapping"""

    __table_args__ = (UniqueConstraint("anwendungshandbuch_primary_key", "position", name="IX_position_once_per_ahb"),)
    # Example:
    # <Paket Nummer="[1P]">--</Paket>
    primary_key: UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    nummer: str = Field(index=True)  #: e.g. '1P'
    text: str  #: e.g. '--'
    position: Optional[int] = Field(default=None, index=True)

    anwendungshandbuch: Union["Anwendungshandbuch", None] = Relationship(back_populates="pakete")
    anwendungshandbuch_primary_key: Union[UUID, None] = Field(
        default=None, foreign_key="anwendungshandbuch.primary_key"
    )

    @classmethod
    def from_model(cls, model: PydanticPaket, position: Optional[int] = None) -> "Paket":
        return Paket(nummer=model.nummer, text=model.text, position=position)

    def to_model(self) -> PydanticPaket:
        return PydanticPaket(nummer=self.nummer, text=self.text)


class Anwendungshandbuch(SQLModel, table=True):
    """
    Ein Anwendungshandbuch, indicated by the `<AHB` tag, bündelt verschiedene Nachrichtentypen/Anwendungsfälle im
    selben Format oder mit der selben regulatorischen Grundlage und stellt gemeinsame Pakete & Bedingungen bereit.
    """

    __table_args__ = (
        CheckConstraint("gueltig_bis IS NULL OR gueltig_bis > gueltig_von", name="gueltig_von_bis_sanity"),
    )
    primary_key: UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    # Example:
    # <AHB Versionsnummer="1.1d" Veroeffentlichungsdatum="02.04.2024" Author="BDEW">
    #  <AWF Pruefidentifikator="25001" Beschreibung="Berechnungsformel" Kommunikation_von="NB an MSB / LF">
    #  </AWF>
    # </AHB>
    veroeffentlichungsdatum: date = Field(index=True)
    """publishing date"""

    autor: str
    """author, most likely 'BDEW'"""

    versionsnummer: str
    """e.g. '1.1d'"""
    anwendungsfaelle: list[Anwendungsfall] = Relationship(
        back_populates="anwendungshandbuch"
    )  #: die einzelnen Prüfidentifikatoren
    bedingungen: list[Bedingung] = Relationship(back_populates="anwendungshandbuch")
    ub_bedingungen: list[UbBedingung] = Relationship(back_populates="anwendungshandbuch")
    pakete: list[Paket] = Relationship(back_populates="anwendungshandbuch")

    # Die Gültig von/bis Datümer sind leider nicht teil des XML-Datenmodells, obwohl sie viel nützlicher wären als bspw.
    # das Veröffentlichungsdatum. Die Informationen darf man sich schön aus der mehr schlecht als recht gepflegten API
    # von bdew-mako.de rauskratzen. Sie sind aber nützlich um mehrere Versionen des AHBs in einer DB zu speichern.
    # Daher hier als SQLModel-Attribute ohne Entsprechung im XML/rohen Original-Datenmodell.
    gueltig_von: Optional[date] = Field(default=None, index=True)
    """
    inklusives Startdatum der Gültigkeit dieses AHBs (Deutsche Zeitzone)
    """
    gueltig_bis: Optional[date] = Field(default=None, index=True)
    """
    Ggf. exklusives Enddatum der Gültigkeit dieses AHBs (Deutsche Zeitzone).
    Wir verwenden None für ein offenes Ende, nicht 9999-12-31.
    """
    edifact_format_version: Optional[EdifactFormatVersion] = Field(default=None, index=True)
    """
    efoli format version (note that this is not derived from the gueltig von/bis dates but has to be set explicitly).
    It's also not a computed column although technically this might have been possible.
    For details about the type check the documentation of the EdifactFormatVersion enum from the efoli package.
    """

    @classmethod
    def from_model(cls, model: PydanticAnwendungshandbuch) -> "Anwendungshandbuch":
        return Anwendungshandbuch(
            veroeffentlichungsdatum=model.veroeffentlichungsdatum,
            autor=model.autor,
            versionsnummer=model.versionsnummer,
            bedingungen=[Bedingung.from_model(x) for x in model.bedingungen],
            ub_bedingungen=[UbBedingung.from_model(x) for x in model.ub_bedingungen],
            pakete=[Paket.from_model(x) for x in model.pakete],
            anwendungsfaelle=[Anwendungsfall.from_model(x) for x in model.anwendungsfaelle if not x.is_outdated],
        )

    def to_model(self) -> PydanticAnwendungshandbuch:
        return PydanticAnwendungshandbuch(
            veroeffentlichungsdatum=self.veroeffentlichungsdatum,
            autor=self.autor,
            versionsnummer=self.versionsnummer,
            bedingungen=tuple(x.to_model() for x in sorted(self.bedingungen, key=lambda y: y.position or 0)),
            ub_bedingungen=tuple(x.to_model() for x in sorted(self.ub_bedingungen, key=lambda y: y.position or 0)),
            pakete=tuple(x.to_model() for x in sorted(self.pakete, key=lambda y: y.position or 0)),
            anwendungsfaelle=tuple(x.to_model() for x in sorted(self.anwendungsfaelle, key=lambda y: y.position or 0)),
        )


class AhbHierarchyMaterialized(SQLModel, table=True):
    """
    A materialized flattened AHB hierarchy containing segment groups, segments, data elements, codes,
    and enriched with metadata like format, versionsnummer, and prüfidentifikator.
    This table is not thought to be written to, but only read from.
    It is created once after all other tables have been filled by the create_ahb_view function in ahbview.py.
    """

    __tablename__ = "ahb_hierarchy_materialized"
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    anwendungsfall_pk: UUID = Field(index=True)
    current_id: UUID
    root_id: UUID
    parent_id: Optional[UUID] = None
    depth: int
    position: Optional[int] = Field(default=None)
    path: str
    parent_path: str
    root_order: int
    type: str = Field(index=True)
    source_id: UUID
    sort_path: str = Field(index=True)

    # Metadata
    pruefidentifikator: str = Field(index=True)
    format: str = Field(index=True)
    versionsnummer: str = Field(index=True)
    gueltig_von: Optional[date] = Field(default=None, index=True)
    gueltig_bis: Optional[date] = Field(default=None, index=True)
    kommunikation_von: Optional[str] = Field(default=None, index=True)
    beschreibung: Optional[str] = Field(default=None, index=True)
    edifact_format_version: Optional[EdifactFormatVersion] = Field(default=None, index=True)

    # Segment Group
    segmentgroup_id: Optional[str] = Field(default=None, index=True)
    segmentgroup_name: Optional[str] = Field(default=None, index=True)
    segmentgroup_ahb_status: Optional[str] = Field(default=None)
    segmentgroup_position: Optional[int] = Field(default=None, index=True)
    segmentgroup_anwendungsfall_primary_key: Optional[UUID] = Field(default=None)

    # Segment
    segment_id: Optional[str] = Field(default=None, index=True)
    segment_name: Optional[str] = Field(default=None, index=True)
    segment_number: Optional[str] = Field(default=None, index=True)
    segment_ahb_status: Optional[str] = Field(default=None)
    segment_position: Optional[int] = Field(default=None, index=True)

    # Data Element Group
    dataelementgroup_id: Optional[str] = Field(default=None, index=True)
    dataelementgroup_name: Optional[str] = Field(default=None, index=True)
    dataelementgroup_position: Optional[int] = Field(default=None, index=True)

    # Data Element
    dataelement_id: Optional[str] = Field(default=None, index=True)
    dataelement_name: Optional[str] = Field(default=None, index=True)
    dataelement_position: Optional[int] = Field(default=None, index=True)
    dataelement_ahb_status: Optional[str] = Field(default=None, index=True)

    # Code
    code_id: Optional[UUID] = Field(default=None, index=True)
    code_name: Optional[str] = Field(default=None, index=True)
    code_description: Optional[str] = Field(default=None, index=True)
    code_value: Optional[str] = Field(default=None, index=True)
    code_ahb_status: Optional[str] = Field(default=None, index=True)
    code_position: Optional[int] = Field(default=None, index=True)
