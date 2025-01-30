"""Anwendungshandbuch SQL models"""

from typing import Union

# pylint: disable=too-few-public-methods, duplicate-code
# the structures are similar, still we decided against inheritance, so there's naturally a little bit of duplication


try:
    from sqlalchemy import UniqueConstraint
    from sqlmodel import Field, Relationship, SQLModel
except ImportError as import_error:
    import_error.msg += "; Did you install fundamend[sqlmodels] or did you try to import from fundamend.models instead?"
    # sqlmodel is only an optional dependency when fundamend is used to fill a database
    raise

import uuid
from datetime import date
from uuid import UUID


class Code(SQLModel, table=True):
    """
    A single code element inside an AHB DataElement, indicated by the `<Code>` tag.
    """

    primary_key: UUID = Field(primary_key=True, default=uuid.uuid4)
    name: str  # e.g. 'Netznutzungszeiten-Nachricht'
    description: str | None = None  # e.g. ''
    value: str | None  # e.g. 'UTILTS'
    ahb_status: str  #: e.g. 'X' # new for AHB

    dataelement: Union["DataElement", None] = Relationship(back_populates="codes")
    data_element_primary_key: UUID | None = Field(default=None, foreign_key="dataelement.primary_key")


class DataElement(SQLModel, table=True):
    """
    A single data element, German 'Datenelement' inside an AHB Segment, indicated by the `<D_xxxx>` tag.
    This element can contain a single or multiple Code elements.
    """

    # Example:
    # <D_0065 Name="Nachrichtentyp-Kennung">
    #   <Code Name="Netznutzungszeiten-Nachricht" Description="" AHB_Status="X">UTILTS</Code>
    # </D_0065>
    primary_key: UUID = Field(primary_key=True, default=uuid.uuid4)
    id: str  # e.g. 'D_0065'
    name: str  # e.g. 'Nachrichtentyp-Kennung'
    codes: list[Code] = Relationship(back_populates="dataelement")

    dataelementgroup: Union["DataElementGroup", None] = Relationship(back_populates="data_elements")
    data_element_group_primary_key: UUID | None = Field(default=None, foreign_key="dataelementgroup.primary_key")

    segment: Union["Segment", None] = Relationship(back_populates="data_elements")
    segment_primary_key: UUID | None = Field(default=None, foreign_key="segment.primary_key")


class DataElementGroup(SQLModel, table=True):
    """
    A group of data elements, German 'Datenelementgruppe' inside the AHB, indicated by the `<C_xxxx>` tag.
    This model can contain both the 'Datenelement' and the 'Gruppendatenelement'
    """

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
    primary_key: UUID = Field(primary_key=True, default=uuid.uuid4)
    id: str  # e.g. 'C_C082'
    name: str  # e.g. 'Dokumenten-/Nachrichtenname'
    data_elements: list[DataElement] = Relationship(back_populates="dataelementgroup")

    segment: Union["Segment", None] = Relationship(back_populates="data_element_groups")
    segment_primary_key: Union[UUID, None] = Field(default=None, foreign_key="segment.primary_key")



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
    primary_key: UUID = Field(primary_key=True, default=uuid.uuid4)
    id: str  #: e.g. 'BGM'
    name: str  #: e.g. 'Beginn der Nachricht'
    number: str  #: e.g. '00002'
    ahb_status: str | None  #: e.g. 'Muss'
    data_elements: list[DataElement]=Relationship(back_populates="segment")
    data_element_groups:list[DataElementGroup]=Relationship(back_populates="dataelementgroup")

    segmentgroup: Union["SegmentGroup", None] = Relationship(back_populates="segments")
    segmentgroup_primary_key: Union[UUID, None] = Field(default=None, foreign_key="segmentgroup.primary_key")

    anwendungsfall: Union["Anwendungsfall", None] = Relationship(back_populates="segments")
    anwendungsfall_primary_key: Union[UUID, None] = Field(default=None, foreign_key="anwendungsfall.primary_key")


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
    primary_key: UUID = Field(primary_key=True, default=uuid.uuid4)
    id: str  #: e.g. 'SG6'
    name: str  #: e.g. 'Prüfidentifikator'
    ahb_status: str | None  #: e.g. 'Muss'
    segments:list[Segment]=Relationship(back_populates="segmentgroup")
    segment_groups:list["SegmentGroup"]=Relationship(back_populates="segmentgroup")

    segmentgroup: Union["SegmentGroup", None] = Relationship(back_populates="segment_groups")
    segmentgroup_primary_key: Union[UUID, None] = Field(default=None, foreign_key="segmentgroup.primary_key")

    anwendungsfall: Union["Anwendungsfall", None] = Relationship(back_populates="segment_groups")
    anwendungsfall_primary_key: Union[UUID, None] = Field(default=None, foreign_key="anwendungsfall.primary_key")


class Anwendungsfall(SQLModel, table=True):
    """
    One 'Anwendungsfall', indicated by `<AWF>` tag, corresponds to one Prüfidentifikator or type of Message
    """

    # Example:
    # <AWF Pruefidentifikator="25001" Beschreibung="Berechnungsformel" Kommunikation_von="NB an MSB / LF">
    #   <M_UTILTS>
    #     <S_UNH Name="Nachrichten-Kopfsegment" Number="00001" AHB_Status="Muss">
    #    ...
    #     </S_UNT>
    #   </M_UTILTS>
    # </AWF>
    primary_key: UUID = Field(primary_key=True, default=uuid.uuid4)
    pruefidentifikator: str  #: e.g. '25001'
    beschreibung: str  #: e.g. 'Berechnungsformel'
    kommunikation_von: str  #: e.g. 'NB an MSB / LF'
    format: str  #: e.g. 'UTILTS'
    segments:list[Segment] = Relationship(back_populates="anwendungsfall")
    segment_groups: list[SegmentGroup] = Relationship(back_populates="anwendungsfall")

    anwendungshandbuch: Union["Anwendungshandbuch", None] = Relationship(back_populates="anwendungsfaelle")
    anwendungshandbuch_primary_key: Union[UUID, None] = Field(
        default=None, foreign_key="anwendungshandbuch.primary_key"
    )


class Bedingung(SQLModel, table=True):
    """Ein ConditionKeyConditionText Mapping"""

    primary_key: UUID = Field(primary_key=True, default=uuid.uuid4)
    nummer: str  #: e.g. '1'
    text: str  #: e.g. 'Nur MP-ID aus Sparte Strom'
    anwendungshandbuch: Union["Anwendungshandbuch", None] = Relationship(back_populates="bedingungen")
    anwendungshandbuch_primary_key: Union[UUID, None] = Field(
        default=None, foreign_key="anwendungshandbuch.primary_key"
    )


class UbBedingung(SQLModel, table=True):
    """Eine UB-Bedingung"""

    # Example:
    # <UB_Bedingung Nummer="[UB1]">([931] ∧ [932] [490]) ⊻ ([931] ∧ [933] [491])</UB_Bedingung>
    primary_key: UUID = Field(primary_key=True, default=uuid.uuid4)
    nummer: str  #: e.g. 'UB1'
    text: str  #: e.g. '([931] ∧ [932] [490]) ⊻ ([931] ∧ [933] [491])'
    anwendungshandbuch: Union["Anwendungshandbuch", None] = Relationship(back_populates="ub_bedingungen")
    anwendungshandbuch_primary_key: Union[UUID, None] = Field(
        default=None, foreign_key="anwendungshandbuch.primary_key"
    )


class Paket(SQLModel, table=True):
    """Ein Bedingungspaket/PackageKeyConditionText Mapping"""

    # Example:
    # <Paket Nummer="[1P]">--</Paket>
    primary_key: UUID = Field(primary_key=True, default=uuid.uuid4)
    nummer: str  #: e.g. '1P'
    text: str  #: e.g. '--'

    anwendungshandbuch: Union["Anwendungshandbuch", None] = Relationship(back_populates="pakete")
    anwendungshandbuch_primary_key: Union[UUID, None] = Field(
        default=None, foreign_key="anwendungshandbuch.primary_key"
    )


class Anwendungshandbuch(SQLModel, table=True):
    """
    Ein Anwendungshandbuch, indicated by the `<AHB` tag, bündelt verschiedene Nachrichtentypen/Anwendungsfälle im
    selben Format oder mit der selben regulatorischen Grundlage und stellt gemeinsame Pakete & Bedingungen bereit.
    """

    primary_key: UUID = Field(primary_key=True, default=uuid.uuid4)
    # Example:
    # <AHB Versionsnummer="1.1d" Veroeffentlichungsdatum="02.04.2024" Author="BDEW">
    #  <AWF Pruefidentifikator="25001" Beschreibung="Berechnungsformel" Kommunikation_von="NB an MSB / LF">
    #  </AWF>
    # </AHB>
    veroeffentlichungsdatum: date
    """publishing date"""

    autor: str
    """author, most likely 'BDEW'"""

    versionsnummer: str
    """e.g. '1.1d'"""
    anwendungsfaelle: list[Anwendungsfall] = Relationship(
        back_populates="anwendungshandbuch"
    )  #: die einzelnen Prüfidendifikatoren
    bedingungen: list[Bedingung] = Relationship(back_populates="anwendungshandbuch")
    ub_bedingungen: list[UbBedingung] = Relationship(back_populates="anwendungshandbuch")
    pakete: list[Paket] = Relationship(back_populates="anwendungshandbuch")
