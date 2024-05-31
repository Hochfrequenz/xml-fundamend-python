"""classes that represent MIGs"""

from datetime import date
from enum import StrEnum

from ._dataclass_wrapper import dataclass

# I didn't invent the data model ;)
# pylint:disable=too-many-instance-attributes


class MigStatus(StrEnum):
    """
    status of a MIG element
    """

    M = "M"
    C = "C"
    R = "R"
    N = "N"
    D = "D"


@dataclass(kw_only=True, eq=True)
class Code:
    """
    a single code element inside a MIG Dataelement
    """

    # Example:
    # <Code Name="Netznutzungszeiten-Nachricht" Description="">UTILTS</Code>
    name: str  # e.g. 'Netznutzungszeiten-Nachricht'
    description: str | None = None  # e.g. ''
    value: str | None  # e.g. 'UTILTS'


@dataclass(kw_only=True, eq=True)
class DataElement:
    """
    A single data element inside a MIG Segment.
    This models both the 'Datenelement' and the 'Gruppendatenelement'
    """

    # pylint:disable=line-too-long
    # Example:
    # <D_0065 Name="Nachrichtentyp-Kennung" Description="" Status_Std="M" Status_Specification="M" Format_Std="an..6" Format_Specification="an..6">
    #   <Code Name="Netznutzungszeiten-Nachricht" Description="">UTILTS</Code>
    # </D_0065>
    id: str  # e.g. 'D_0065'
    name: str  # e.g. 'Nachrichtentyp-Kennung'
    description: str | None = None  # e.g. ''
    status_std: MigStatus
    status_specification: MigStatus
    format_std: str  #: e.g. 'an..6'
    format_specification: str  #: e.g. 'an..6'
    codes: list[Code]


@dataclass(eq=True, kw_only=True)
class DataElementGroup:
    """
    a group of data elements, German 'Datenelementgruppe'.
    """

    # "Die Datenelementgruppe C0829 enthält mehrere Gruppendatenelemente. Diese Datenelementgruppe enthält das
    # Gruppendatenelement DE3039, hier wird die MP-ID angegeben, sowie das DE3055, welches die code-vergebende Stelle
    # definiert. Diese Datenelementgruppe enthält des Weiteren das Gruppendatenelement DE113110, welches nur in der MIG
    # und nicht im AHB aufgeführt wird, um den Aufbau der EDIFACT Nachricht korrekt umsetzen zu können."
    # Quelle: Allgemeine Festlegungen Kapitel 6.1, Seite 52

    # Example:
    # pylint:disable=line-too-long
    # <C_C082 Name="Identifikation des Beteiligten" Description="" Status_Std="C" Status_Specification="R">
    #   <D_3039 Name="MP-ID" Description="" Status_Std="M" Status_Specification="M" Format_Std="an..35" Format_Specification="an..35"/>
    #   <D_1131 Name="Codeliste, Code" Description="" Status_Std="C" Status_Specification="N" Format_Std="an..17" Format_Specification="an..17"/>
    #   <D_3055 Name="Verantwortliche Stelle für die Codepflege, Code" Description="" Status_Std="C" Status_Specification="R" Format_Std="an..3" Format_Specification="an..3">
    #     <Code Name="GS1" Description="">9</Code>
    #     <Code Name="DE, BDEW (Bundesverband der Energie- und Wasserwirtschaft e.V.)" Description="">293</Code>
    #   </D_3055>
    # </C_C082>

    id: str  # e.g. 'C_C082'
    name: str  # e.g. 'Identifikation des Beteiligten'
    description: str | None = None  # e.g. ''
    status_std: MigStatus
    status_specification: MigStatus
    data_elements: list[DataElement]


@dataclass(frozen=True, eq=True, order=True, unsafe_hash=True, kw_only=True)
class Segment:
    """
    a segment inside a MIG
    """

    # Example:
    # pylint:disable=line-too-long
    # <S_NAD Name="MP-ID Absender" Description="DE3039: Zur Identifikation der Marktpartner wird die MP-ID angegeben." Counter="0100" Level="1" Number="00004" MaxRep_Std="1" MaxRep_Specification="1" Status_Std="M" Status_Specification="M" Example="NAD+MS+9900259000002::293&apos;">
    #     <D_3035 Name="Beteiligter, Qualifier" Description="" Status_Std="M" Status_Specification="M" Format_Std="an..3" Format_Specification="an..3">
    #        <Code Name="Dokumenten-/Nachrichtenaussteller bzw. -absender" Description="">MS</Code>
    #     </D_3035>
    #     <C_C082 Name="Identifikation des Beteiligten" Description="" Status_Std="C" Status_Specification="R">
    #       <D_3039 Name="MP-ID" Description="" Status_Std="M" Status_Specification="M" Format_Std="an..35" Format_Specification="an..35"/>
    #       <D_1131 Name="Codeliste, Code" Description="" Status_Std="C" Status_Specification="N" Format_Std="an..17" Format_Specification="an..17"/>
    #       <D_3055 Name="Verantwortliche Stelle für die Codepflege, Code" Description="" Status_Std="C" Status_Specification="R" Format_Std="an..3" Format_Specification="an..3">
    #         <Code Name="GS1" Description="">9</Code>
    #         <Code Name="DE, BDEW (Bundesverband der Energie- und Wasserwirtschaft e.V.)" Description="">293</Code>
    #      </D_3055>
    #   </C_C082>
    # </S_NAD>
    id: str  #: e.g. 'NAD'
    name: str  #: e.g. 'MP-ID Absender'
    description: str | None = None  # e.g. 'DE3039: Zur Identifikation der Marktpartner wird die MP-ID angegeben.'
    counter: str  #: e.g. '0100'
    level: int  #: e.g. 1
    number: str  #: e.g. '00004'
    max_rep_std: int  #: e.g. 1
    max_rep_specification: int  #: e.g. 1
    status_std: MigStatus
    status_specification: MigStatus
    example: str | None  #: e.g. "NAD+MS+9900259000002::293'"
    data_elements: list[DataElement | DataElementGroup]


@dataclass(kw_only=True, eq=True)
class SegmentGroup:
    """
    a "Segtmentgruppe"
    """

    # pylint:disable=line-too-long
    # Example:
    # <G_SG2 Name="MP-ID Empfänger" Counter="0090" Level="1" MaxRep_Std="99" MaxRep_Specification="1" Status_Std="C" Status_Specification="R">
    #   <S_NAD Name="MP-ID Empfänger" Description="DE3039: Zur Identifikation der Marktpartner wird die MP-ID angegeben." Counter="0100" Level="1" Number="00007" MaxRep_Std="1" MaxRep_Specification="1" Status_Std="M" Status_Specification="M" Example="NAD+MR+9900259000002::293&apos;">
    #     <D_3035 Name="Beteiligter, Qualifier" Description="" Status_Std="M" Status_Specification="M" Format_Std="an..3" Format_Specification="an..3">
    #        <Code Name="Nachrichtenempfänger" Description="">MR</Code>
    #     </D_3035>
    #     <C_C082 Name="Identifikation des Beteiligten" Description="" Status_Std="C" Status_Specification="R">
    #       <D_3039 Name="MP-ID" Description="" Status_Std="M" Status_Specification="M" Format_Std="an..35" Format_Specification="an..35"/>
    #       <D_1131 Name="Codeliste, Code" Description="" Status_Std="C" Status_Specification="N" Format_Std="an..17" Format_Specification="an..17"/>
    #       <D_3055 Name="Verantwortliche Stelle für die Codepflege, Code" Description="" Status_Std="C" Status_Specification="R" Format_Std="an..3" Format_Specification="an..3">
    #         <Code Name="GS1" Description="">9</Code>
    #         <Code Name="DE, BDEW (Bundesverband der Energie- und Wasserwirtschaft e.V.)" Description="">293</Code>
    #       </D_3055>
    #     </C_C082>
    #   </S_NAD>
    # </G_SG2>
    id: str  # e.g. 'SG2'
    name: str  # e.g. 'MP-ID Empfänger'
    counter: str  # e.g. '0090'
    level: int  # e.g. 1
    max_rep_std: int  # e.g. 99
    max_rep_specification: int  # e.g. 1
    status_std: MigStatus
    status_specification: MigStatus
    segments: list[Segment]
    segment_groups: list["SegmentGroup"]


@dataclass(kw_only=True, eq=True)
class MessageImplementationGuide:
    """
    message implementation guide (MIG)
    """

    veroeffentlichungsdatum: date
    """publishing date"""

    autor: str
    """author, most likely 'BDEW'"""

    versionsnummer: str
    """e.g. '1.1c'"""

    format: str  #: e.g. 'UTILTS'

    segments: list[Segment]
    segment_groups: list[SegmentGroup]
