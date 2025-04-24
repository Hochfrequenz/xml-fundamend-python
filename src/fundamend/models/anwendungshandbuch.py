"""model classes for Anwendungshandbücher (AHB)"""

# pylint:disable=duplicate-code
# the structures are similar, still we decided against inheritance, so there's naturally a little bit of duplication

from datetime import date

from efoli import EdifactFormat

from fundamend.models.base import FundamendBaseModel


class Code(FundamendBaseModel):
    """
    A single code element inside an AHB DataElement, indicated by the `<Code>` tag.
    """

    # Example:
    # <Code Name="Netznutzungszeiten-Nachricht" Description="" AHB_Status="X">UTILTS</Code>
    # properties are similar to MIG data model, still we like to keep them separate instead of inheriting
    name: str  # e.g. 'Netznutzungszeiten-Nachricht'
    description: str | None = None  # e.g. ''
    value: str | None  # e.g. 'UTILTS'
    ahb_status: str  #: e.g. 'X' # new for AHB


class DataElement(FundamendBaseModel):
    """
    A single data element, German 'Datenelement' inside an AHB Segment, indicated by the `<D_xxxx>` tag.
    This element can contain a single or multiple Code elements.
    """

    # Example:
    # <D_0065 Name="Nachrichtentyp-Kennung">
    #   <Code Name="Netznutzungszeiten-Nachricht" Description="" AHB_Status="X">UTILTS</Code>
    # </D_0065>
    id: str  # e.g. 'D_0065'
    name: str  # e.g. 'Nachrichtentyp-Kennung'
    ahb_status: str | None  # e.g. 'X'
    codes: tuple[Code, ...]


class DataElementGroup(FundamendBaseModel):
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

    id: str  # e.g. 'C_C082'
    name: str  # e.g. 'Dokumenten-/Nachrichtenname'
    data_elements: tuple[DataElement, ...]


class Segment(FundamendBaseModel):
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
    data_elements: tuple[DataElement | DataElementGroup, ...]
    is_on_uebertragungsdatei_level: bool = False
    """
    true for e.g. S_UNA, S_UNB or S_UNZ which occur outside the regular AHB <M_FORMAT> structure.
    We decided against introducing another (mostly useless) layer around the actual body of the Anwendungsfall.
    This is only relevant (true) for MSCONS AHBs as of 2025-04-23 although the MIGs read like this _might_ also be true
    for REMADV and INVOIC. We all know, how (self-)consistent BDEW documents are, even if you pay for them.
    """


class SegmentGroup(FundamendBaseModel):
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
    id: str  #: e.g. 'SG6'
    name: str  #: e.g. 'Prüfidentifikator'
    ahb_status: str | None  #: e.g. 'Muss'
    elements: tuple["Segment | SegmentGroup", ...]


class Anwendungsfall(FundamendBaseModel):
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
    pruefidentifikator: str  #: e.g. '25001'
    beschreibung: str  #: e.g. 'Berechnungsformel'
    kommunikation_von: str  #: e.g. 'NB an MSB / LF'
    format: EdifactFormat  #: e.g. 'UTILTS'
    elements: tuple[Segment | SegmentGroup, ...]

    @property
    def is_outdated(self) -> bool:
        """
        the experts creating the XMLs thought it was a good idea to encode the information if something is there just
        for legacy reasons in the prüfidentifikator attribute - where else.
        It's not like they could've added just another attribute to indicate that.
        """
        return "##alt##" in self.pruefidentifikator.lower()  # table flip moment


class Bedingung(FundamendBaseModel):
    """Ein ConditionKeyConditionText Mapping"""

    nummer: str  #: e.g. '1'
    text: str  #: e.g. 'Nur MP-ID aus Sparte Strom'


class UbBedingung(FundamendBaseModel):
    """Eine UB-Bedingung"""

    # Example:
    # <UB_Bedingung Nummer="[UB1]">([931] ∧ [932] [490]) ⊻ ([931] ∧ [933] [491])</UB_Bedingung>
    nummer: str  #: e.g. 'UB1'
    text: str  #: e.g. '([931] ∧ [932] [490]) ⊻ ([931] ∧ [933] [491])'


class Paket(FundamendBaseModel):
    """Ein Bedingungspaket/PackageKeyConditionText Mapping"""

    # Example:
    # <Paket Nummer="[1P]">--</Paket>
    nummer: str  #: e.g. '1P'
    text: str  #: e.g. '--'


class Anwendungshandbuch(FundamendBaseModel):
    """
    Ein Anwendungshandbuch, indicated by the `<AHB` tag, bündelt verschiedene Nachrichtentypen/Anwendungsfälle im
    selben Format oder mit der selben regulatorischen Grundlage und stellt gemeinsame Pakete & Bedingungen bereit.
    """

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
    anwendungsfaelle: tuple[Anwendungsfall, ...]  #: die einzelnen Prüfidendifikatoren
    bedingungen: tuple[Bedingung, ...]
    ub_bedingungen: tuple[UbBedingung, ...]
    pakete: tuple[Paket, ...]
