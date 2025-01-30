"""Anwendungshandbuch SQL models"""
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
from typing import Optional
from uuid import UUID
from datetime import date

class Code(SQLModel, table=True):
    """
    A single code element inside an AHB DataElement, indicated by the `<Code>` tag.
    """
    id:UUID = Field(primary_key=True, default=uuid.uuid4)
    name: str  # e.g. 'Netznutzungszeiten-Nachricht'
    description: str | None = None  # e.g. ''
    value: str | None  # e.g. 'UTILTS'
    ahb_status: str  #: e.g. 'X' # new for AHB
    data_element_primary_key: UUID | None = Field(default=None, foreign_key="dataelement.primary_key")
    dataelement: "DataElement" | None = Relationship(back_populates="codes")

class DataElement(SQLModel, table=True):
    """
    A single data element, German 'Datenelement' inside an AHB Segment, indicated by the `<D_xxxx>` tag.
    This element can contain a single or multiple Code elements.
    """

    # Example:
    # <D_0065 Name="Nachrichtentyp-Kennung">
    #   <Code Name="Netznutzungszeiten-Nachricht" Description="" AHB_Status="X">UTILTS</Code>
    # </D_0065>
    primary_key:UUID = Field(primary_key=True, default=uuid.uuid4)
    id: str # e.g. 'D_0065'
    name: str  # e.g. 'Nachrichtentyp-Kennung'
    codes:list[Code] =Relationship(back_populates="dataelement")
    data_element_group_primary_key: UUID | None = Field(default=None, foreign_key="dataelementgroup.primary_key")
    dataelementgroup: "DataElement" | None = Relationship(back_populates="data_elements")

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
    data_elements: list[DataElement]=Relationship(back_populates="dataelementgroup")

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
    id: str  #: e.g. 'BGM'
    name: str  #: e.g. 'Beginn der Nachricht'
    number: str  #: e.g. '00002'
    ahb_status: str | None  #: e.g. 'Muss'
    data_elements: list[DataElement | DataElementGroup]