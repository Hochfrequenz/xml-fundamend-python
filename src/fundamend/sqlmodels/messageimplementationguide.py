"""MessageImplementationGuide SQL models"""

import uuid
from datetime import date
from typing import Optional, Union
from uuid import UUID

from efoli import EdifactFormat, EdifactFormatVersion

# pylint: disable=too-few-public-methods, duplicate-code, missing-function-docstring

# the structures are similar to AHB, still we decided against inheritance,
# so there's naturally a little bit of duplication


try:
    from sqlalchemy import CheckConstraint, UniqueConstraint
    from sqlmodel import Field, Relationship, SQLModel
except ImportError as import_error:
    import_error.msg += "; Did you install fundamend[sqlmodels] or did you try to import from fundamend.models instead?"
    # sqlmodel is only an optional dependency when fundamend is used to fill a database
    raise

from fundamend.models.messageimplementationguide import Code as PydanticCode
from fundamend.models.messageimplementationguide import DataElement as PydanticDataElement
from fundamend.models.messageimplementationguide import DataElementGroup as PydanticDataElementGroup
from fundamend.models.messageimplementationguide import MessageImplementationGuide as PydanticMessageImplementationGuide
from fundamend.models.messageimplementationguide import MigStatus
from fundamend.models.messageimplementationguide import Segment as PydanticSegment
from fundamend.models.messageimplementationguide import SegmentGroup as PydanticSegmentGroup


class MigCode(SQLModel, table=True):
    """
    A single code element inside a MIG DataElement, indicated by the `<Code>` tag.
    """

    __table_args__ = (
        UniqueConstraint("data_element_primary_key", "position", name="IX_mig_code_position_once_per_data_element"),
    )
    primary_key: UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    name: str = Field(index=True)  # e.g. 'Netznutzungszeiten-Nachricht'
    description: str | None = Field(default=None, index=True)  # e.g. ''
    value: str | None = Field(default=None, index=True)  # e.g. 'UTILTS'
    position: Optional[int] = Field(default=None, index=True)

    dataelement: Union["MigDataElement", None] = Relationship(back_populates="codes")
    data_element_primary_key: UUID | None = Field(default=None, foreign_key="migdataelement.primary_key")

    @classmethod
    def from_model(cls, model: PydanticCode, position: Optional[int] = None) -> "MigCode":
        return MigCode(
            name=model.name,
            description=model.description,
            value=model.value,
            position=position,
        )

    def to_model(self) -> PydanticCode:
        return PydanticCode(
            name=self.name,
            description=self.description,
            value=self.value,
        )


class MigDataElement(SQLModel, table=True):
    """
    A single data element inside a MIG Segment, indicated by the `<D_xxxx>` tag.
    This models both the 'Datenelement' and the 'Gruppendatenelement'.
    Can contain a single or multiple Code elements.
    """

    __table_args__ = (
        UniqueConstraint(
            "data_element_group_primary_key", "position", name="IX_mig_de_position_once_per_data_element_group"
        ),
        UniqueConstraint("segment_primary_key", "position", name="IX_mig_de_position_once_per_segment"),
    )
    primary_key: UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    id: str = Field(index=True)  # e.g. 'D_0065'
    name: str = Field(index=True)  # e.g. 'Nachrichtentyp-Kennung'
    description: str | None = Field(default=None, index=True)
    status_std: str  # MigStatus stored as string, e.g. 'M'
    status_specification: str  # MigStatus stored as string, e.g. 'M'
    format_std: str  # e.g. 'an..6'
    format_specification: str  # e.g. 'an..6'
    codes: list[MigCode] = Relationship(back_populates="dataelement")
    position: Optional[int] = Field(default=None, index=True)

    dataelementgroup: Union["MigDataElementGroup", None] = Relationship(back_populates="data_elements")
    data_element_group_primary_key: UUID | None = Field(default=None, foreign_key="migdataelementgroup.primary_key")

    segment: Union["MigSegment", None] = Relationship(back_populates="data_elements")
    segment_primary_key: UUID | None = Field(default=None, foreign_key="migsegment.primary_key")

    @classmethod
    def from_model(cls, model: PydanticDataElement, position: Optional[int] = None) -> "MigDataElement":
        result = MigDataElement(
            id=model.id,
            name=model.name,
            description=model.description,
            status_std=model.status_std.value,
            status_specification=model.status_specification.value,
            format_std=model.format_std,
            format_specification=model.format_specification,
            codes=[
                MigCode.from_model(pydantic_code, position=position_index)
                for position_index, pydantic_code in enumerate(model.codes)
            ],
            position=position,
        )
        return result

    def to_model(self) -> PydanticDataElement:
        return PydanticDataElement(
            id=self.id,
            name=self.name,
            description=self.description,
            status_std=MigStatus(self.status_std),
            status_specification=MigStatus(self.status_specification),
            format_std=self.format_std,
            format_specification=self.format_specification,
            codes=tuple(x.to_model() for x in sorted(self.codes, key=lambda y: y.position or 0)),
        )


class MigDataElementGroup(SQLModel, table=True):
    """
    A group of data elements, German 'Datenelementgruppe', indicated by the `<C_xxxx>` tag.
    Can contain a single or multiple data elements.
    """

    __table_args__ = (UniqueConstraint("segment_primary_key", "position", name="IX_mig_deg_position_once_per_segment"),)
    primary_key: UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    id: str = Field(index=True)  # e.g. 'C_C082'
    name: str = Field(index=True)  # e.g. 'Identifikation des Beteiligten'
    description: str | None = Field(default=None, index=True)
    status_std: str  # MigStatus stored as string
    status_specification: str  # MigStatus stored as string
    data_elements: list[MigDataElement] = Relationship(back_populates="dataelementgroup")
    position: Optional[int] = Field(default=None, index=True)

    segment: Union["MigSegment", None] = Relationship(back_populates="data_element_groups")
    segment_primary_key: Union[UUID, None] = Field(default=None, foreign_key="migsegment.primary_key")

    @classmethod
    def from_model(cls, model: PydanticDataElementGroup, position: Optional[int] = None) -> "MigDataElementGroup":
        result = MigDataElementGroup(
            id=model.id,
            name=model.name,
            description=model.description,
            status_std=model.status_std.value,
            status_specification=model.status_specification.value,
            position=position,
        )
        for position_index, x in enumerate(model.data_elements):
            de = MigDataElement.from_model(x, position=position_index)
            result.data_elements.append(de)
        return result

    def to_model(self) -> PydanticDataElementGroup:
        return PydanticDataElementGroup(
            id=self.id,
            name=self.name,
            description=self.description,
            status_std=MigStatus(self.status_std),
            status_specification=MigStatus(self.status_specification),
            data_elements=tuple(x.to_model() for x in sorted(self.data_elements, key=lambda y: y.position or 0)),
        )


class MigSegment(SQLModel, table=True):
    """
    A segment inside a MIG, indicated by the `<S_xxxx>` tag.
    Contains data elements and data element groups.
    """

    __table_args__ = (
        UniqueConstraint("segmentgroup_primary_key", "position", name="IX_mig_seg_position_once_per_segmentgroup"),
        UniqueConstraint("mig_primary_key", "position", name="IX_mig_seg_position_once_per_mig"),
    )
    primary_key: UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    id: str = Field(index=True)  # e.g. 'NAD'
    name: str = Field(index=True)  # e.g. 'MP-ID Absender'
    description: str | None = Field(default=None, index=True)
    counter: str  # e.g. '0100'
    level: int  # e.g. 1
    number: str = Field(index=True)  # e.g. '00004'
    max_rep_std: int  # e.g. 1
    max_rep_specification: int  # e.g. 1
    status_std: str  # MigStatus stored as string
    status_specification: str  # MigStatus stored as string
    example: str | None  # e.g. "NAD+MS+9900259000002::293'"
    is_on_uebertragungsdatei_level: bool
    data_elements: list[MigDataElement] = Relationship(back_populates="segment")
    data_element_groups: list[MigDataElementGroup] = Relationship(back_populates="segment")
    position: Optional[int] = Field(default=None, index=True)

    segmentgroup: Union["MigSegmentGroup", None] = Relationship(back_populates="segments")
    segmentgroup_primary_key: Union[UUID, None] = Field(default=None, foreign_key="migsegmentgroup.primary_key")

    mig: Union["MessageImplementationGuide", None] = Relationship(back_populates="segments")
    mig_primary_key: Union[UUID, None] = Field(default=None, foreign_key="messageimplementationguide.primary_key")

    @classmethod
    def from_model(cls, model: PydanticSegment, position: Optional[int] = None) -> "MigSegment":
        result = MigSegment(
            id=model.id,
            name=model.name,
            description=model.description,
            counter=model.counter,
            level=model.level,
            number=model.number,
            max_rep_std=model.max_rep_std,
            max_rep_specification=model.max_rep_specification,
            status_std=model.status_std.value,
            status_specification=model.status_specification.value,
            example=model.example,
            is_on_uebertragungsdatei_level=model.is_on_uebertragungsdatei_level,
            position=position,
        )
        for _position, element in enumerate(model.data_elements):
            if isinstance(element, PydanticDataElement):
                result.data_elements.append(MigDataElement.from_model(element, position=_position))
                continue
            if isinstance(element, PydanticDataElementGroup):
                result.data_element_groups.append(MigDataElementGroup.from_model(element, position=_position))
                continue
        return result

    def to_model(self) -> PydanticSegment:
        return PydanticSegment(
            id=self.id,
            name=self.name,
            description=self.description,
            counter=self.counter,
            level=self.level,
            number=self.number,
            max_rep_std=self.max_rep_std,
            max_rep_specification=self.max_rep_specification,
            status_std=MigStatus(self.status_std),
            status_specification=MigStatus(self.status_specification),
            example=self.example,
            is_on_uebertragungsdatei_level=self.is_on_uebertragungsdatei_level,
            data_elements=tuple(
                x.to_model()
                for x in sorted(
                    (self.data_elements or []) + (self.data_element_groups or []),  # type:ignore[operator]
                    key=lambda y: y.position or 0,
                )
            ),
        )


class MigSegmentGroupLink(SQLModel, table=True):
    """Artificial construct in SQL to model MIG Segment Groups being nested in other Segment Groups"""

    parent_id: UUID | None = Field(default=None, foreign_key="migsegmentgroup.primary_key", primary_key=True)
    child_id: UUID | None = Field(default=None, foreign_key="migsegmentgroup.primary_key", primary_key=True)


class MigSegmentGroup(SQLModel, table=True):
    """
    A 'Segmentgruppe' inside a MIG, indicated by the `<G_xxx>` tag.
    Contains segments and segment groups.
    """

    __table_args__ = (UniqueConstraint("mig_primary_key", "position", name="IX_mig_sg_position_once_per_mig"),)
    primary_key: UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    id: str = Field(index=True)  # e.g. 'SG2'
    name: str = Field(index=True)  # e.g. 'MP-ID Empfänger'
    counter: str  # e.g. '0090'
    level: int  # e.g. 1
    max_rep_std: int  # e.g. 99
    max_rep_specification: int  # e.g. 1
    status_std: str  # MigStatus stored as string
    status_specification: str  # MigStatus stored as string
    segments: list[MigSegment] = Relationship(back_populates="segmentgroup")
    position: Optional[int] = Field(default=None, index=True)

    # Self-referential relationship for nested segment groups
    segment_groups: list["MigSegmentGroup"] = Relationship(
        back_populates="parent_segment_group",
        sa_relationship_kwargs={
            "primaryjoin": "MigSegmentGroup.primary_key==MigSegmentGroupLink.parent_id",
            "secondaryjoin": "MigSegmentGroup.primary_key==MigSegmentGroupLink.child_id",
            "foreign_keys": "[MigSegmentGroupLink.parent_id, MigSegmentGroupLink.child_id]",
        },
        link_model=MigSegmentGroupLink,
    )

    parent_segment_group: Optional["MigSegmentGroup"] = Relationship(
        back_populates="segment_groups",
        sa_relationship_kwargs={
            "primaryjoin": "MigSegmentGroup.primary_key==MigSegmentGroupLink.child_id",
            "secondaryjoin": "MigSegmentGroup.primary_key==MigSegmentGroupLink.parent_id",
            "foreign_keys": "[MigSegmentGroupLink.child_id, MigSegmentGroupLink.parent_id]",
        },
        link_model=MigSegmentGroupLink,
    )

    mig: Union["MessageImplementationGuide", None] = Relationship(back_populates="segment_groups")
    mig_primary_key: Union[UUID, None] = Field(default=None, foreign_key="messageimplementationguide.primary_key")

    @classmethod
    def from_model(cls, model: PydanticSegmentGroup, position: Optional[int] = None) -> "MigSegmentGroup":
        result = MigSegmentGroup(
            id=model.id,
            name=model.name,
            counter=model.counter,
            level=model.level,
            max_rep_std=model.max_rep_std,
            max_rep_specification=model.max_rep_specification,
            status_std=model.status_std.value,
            status_specification=model.status_specification.value,
            position=position,
        )
        for _position, element in enumerate(model.elements):
            if isinstance(element, PydanticSegment):
                result.segments.append(MigSegment.from_model(element, position=_position))
                continue
            if isinstance(element, PydanticSegmentGroup):
                sg = MigSegmentGroup.from_model(element, position=_position)
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
            counter=self.counter,
            level=self.level,
            max_rep_std=self.max_rep_std,
            max_rep_specification=self.max_rep_specification,
            status_std=MigStatus(self.status_std),
            status_specification=MigStatus(self.status_specification),
            elements=tuple(
                x.to_model()
                for x in sorted(
                    (self.segments or []) + (self.segment_groups or []),  # type:ignore[operator]
                    key=lambda y: y.position or 0,
                )
            ),
        )


class MessageImplementationGuide(SQLModel, table=True):
    """
    A Message Implementation Guide (MIG) indicated by the `<M_xxxx>` tag.
    """

    __table_args__ = (
        CheckConstraint("gueltig_bis IS NULL OR gueltig_bis > gueltig_von", name="mig_gueltig_von_bis_sanity"),
    )
    primary_key: UUID = Field(primary_key=True, default_factory=uuid.uuid4)

    veroeffentlichungsdatum: date = Field(index=True)
    """publishing date"""

    autor: str
    """author, most likely 'BDEW'"""

    versionsnummer: str
    """e.g. '1.1c'"""

    format: EdifactFormat = Field(index=True)  # e.g. 'UTILTS'

    segments: list[MigSegment] = Relationship(back_populates="mig")
    segment_groups: list[MigSegmentGroup] = Relationship(back_populates="mig")

    # SQL-only fields (not in Pydantic model)
    gueltig_von: Optional[date] = Field(default=None, index=True)
    """
    inklusives Startdatum der Gültigkeit dieser MIG (Deutsche Zeitzone)
    """
    gueltig_bis: Optional[date] = Field(default=None, index=True)
    """
    Ggf. exklusives Enddatum der Gültigkeit dieser MIG (Deutsche Zeitzone).
    Wir verwenden None für ein offenes Ende, nicht 9999-12-31.
    """
    edifact_format_version: Optional[EdifactFormatVersion] = Field(default=None, index=True)
    """
    efoli format version (note that this is not derived from the gueltig von/bis dates but has to be set explicitly).
    It's also not a computed column although technically this might have been possible.
    For details about the type check the documentation of the EdifactFormatVersion enum from the efoli package.
    """

    @classmethod
    def from_model(cls, model: PydanticMessageImplementationGuide) -> "MessageImplementationGuide":
        result = MessageImplementationGuide(
            veroeffentlichungsdatum=model.veroeffentlichungsdatum,
            autor=model.autor,
            versionsnummer=model.versionsnummer,
            format=model.format,
        )
        for _position, element in enumerate(model.elements):
            if isinstance(element, PydanticSegment):
                result.segments.append(MigSegment.from_model(element, position=_position))
                continue
            if isinstance(element, PydanticSegmentGroup):
                result.segment_groups.append(MigSegmentGroup.from_model(element, position=_position))
                continue
        return result

    def to_model(self) -> PydanticMessageImplementationGuide:
        return PydanticMessageImplementationGuide(
            veroeffentlichungsdatum=self.veroeffentlichungsdatum,
            autor=self.autor,
            versionsnummer=self.versionsnummer,
            format=self.format,
            elements=tuple(
                x.to_model()
                for x in sorted(
                    ((self.segments or []) + (self.segment_groups or [])),  # type:ignore[operator]
                    key=lambda y: y.position or 0,
                )
            ),
        )


__all__ = [
    "MigCode",
    "MigDataElement",
    "MigDataElementGroup",
    "MigSegment",
    "MigSegmentGroup",
    "MigSegmentGroupLink",
    "MessageImplementationGuide",
]
