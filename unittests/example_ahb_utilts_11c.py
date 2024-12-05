# pylint:disable=line-too-long, too-many-lines
import datetime

from fundamend.models.anwendungshandbuch import (
    Anwendungsfall,
    Anwendungshandbuch,
    Bedingung,
    Code,
    DataElement,
    DataElementGroup,
    Paket,
    Segment,
    SegmentGroup,
    UbBedingung,
)

ahb_utilts_11c = Anwendungshandbuch(
    veroeffentlichungsdatum=datetime.date(2023, 10, 24),
    autor="BDEW",
    versionsnummer="1.1c",
    anwendungsfaelle=[
        Anwendungsfall(
            pruefidentifikator="25001",
            beschreibung="Berechnungsformel",
            kommunikation_von="NB an MSB / LF",
            format="UTILTS",
            segments=[
                Segment(
                    id="UNH",
                    name="Nachrichten-Kopfsegment",
                    number="00001",
                    ahb_status="Muss",
                    data_elements=[
                        DataElement(id="D_0062", name="Nachrichten-Referenznummer", codes=[]),
                        DataElementGroup(
                            id="C_S009",
                            name="Nachrichten-Kennung",
                            data_elements=[
                                DataElement(
                                    id="D_0065",
                                    name="Nachrichtentyp-Kennung",
                                    codes=[
                                        Code(
                                            name="Netznutzungszeiten-Nachricht",
                                            description=None,
                                            value="UTILTS",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                                DataElement(
                                    id="D_0052",
                                    name="Versionsnummer des Nachrichtentyps",
                                    codes=[Code(name="Entwurfs-Version", description=None, value="D", ahb_status="X")],
                                ),
                                DataElement(
                                    id="D_0054",
                                    name="Freigabenummer des Nachrichtentyps",
                                    codes=[
                                        Code(name="Ausgabe 2018 - A", description=None, value="18A", ahb_status="X")
                                    ],
                                ),
                                DataElement(
                                    id="D_0051",
                                    name="Verwaltende Organisation",
                                    codes=[Code(name="UN/CEFACT", description=None, value="UN", ahb_status="X")],
                                ),
                                DataElement(
                                    id="D_0057",
                                    name="Anwendungscode der zuständigen Organisation",
                                    codes=[
                                        Code(
                                            name="Versionsnummer der zugrundeliegenden BDEW-Nachrichtenbeschreibung",
                                            description=None,
                                            value="1.1c",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                Segment(
                    id="BGM",
                    name="Beginn der Nachricht",
                    number="00002",
                    ahb_status="Muss",
                    data_elements=[
                        DataElementGroup(
                            id="C_C002",
                            name="Dokumenten-/Nachrichtenname",
                            data_elements=[
                                DataElement(
                                    id="D_1001",
                                    name="Dokumentenname, Code",
                                    codes=[
                                        Code(name="Berechnungsformel", description=None, value="Z36", ahb_status="X")
                                    ],
                                )
                            ],
                        ),
                        DataElementGroup(
                            id="C_C106",
                            name="Dokumenten-/Nachrichten-Identifikation",
                            data_elements=[DataElement(id="D_1004", name="Dokumentennummer", codes=[])],
                        ),
                    ],
                ),
                Segment(
                    id="DTM",
                    name="Nachrichtendatum",
                    number="00003",
                    ahb_status="Muss",
                    data_elements=[
                        DataElementGroup(
                            id="C_C507",
                            name="Datum/Uhrzeit/Zeitspanne",
                            data_elements=[
                                DataElement(
                                    id="D_2005",
                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Funktion, Qualifier",
                                    codes=[
                                        Code(
                                            name="Dokumenten-/Nachrichtendatum/-zeit",
                                            description=None,
                                            value="137",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                                DataElement(id="D_2380", name="Datum oder Uhrzeit oder Zeitspanne, Wert", codes=[]),
                                DataElement(
                                    id="D_2379",
                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Format, Code",
                                    codes=[Code(name="CCYYMMDDHHMMZZZ", description=None, value="303", ahb_status="X")],
                                ),
                            ],
                        )
                    ],
                ),
                Segment(
                    id="UNT",
                    name="Nachrichten-Endesegment",
                    number="00031",
                    ahb_status="Muss",
                    data_elements=[
                        DataElement(id="D_0074", name="Anzahl der Segmente in einer Nachricht", codes=[]),
                        DataElement(id="D_0062", name="Nachrichten-Referenznummer", codes=[]),
                    ],
                ),
            ],
            segment_groups=[
                SegmentGroup(
                    id="2",
                    name="MP-ID Absender",
                    ahb_status="Muss",
                    segments=[
                        Segment(
                            id="NAD",
                            name="MP-ID Absender",
                            number="00004",
                            ahb_status="Muss",
                            data_elements=[
                                DataElement(
                                    id="D_3035",
                                    name="Beteiligter, Qualifier",
                                    codes=[
                                        Code(
                                            name="Dokumenten-/Nachrichtenaussteller bzw. -absender",
                                            description=None,
                                            value="MS",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                                DataElementGroup(
                                    id="C_C082",
                                    name="Identifikation des Beteiligten",
                                    data_elements=[
                                        DataElement(id="D_3039", name="MP-ID", codes=[]),
                                        DataElement(
                                            id="D_3055",
                                            name="Verantwortliche Stelle für die Codepflege, Code",
                                            codes=[
                                                Code(name="GS1", description=None, value="9", ahb_status="X"),
                                                Code(
                                                    name="DE, BDEW (Bundesverband der Energie- und Wasserwirtschaft e.V.)",
                                                    description=None,
                                                    value="293",
                                                    ahb_status="X",
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        )
                    ],
                    segment_groups=[
                        SegmentGroup(
                            id="3",
                            name="Kontaktinformationen",
                            ahb_status="Muss [2]\r\nKann",
                            segments=[
                                Segment(
                                    id="CTA",
                                    name="Ansprechpartner",
                                    number="00005",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_3139",
                                            name="Funktion des Ansprechpartners, Code",
                                            codes=[
                                                Code(
                                                    name="Informationskontakt",
                                                    description=None,
                                                    value="IC",
                                                    ahb_status="X",
                                                )
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C056",
                                            name="Kontaktangaben",
                                            data_elements=[
                                                DataElement(id="D_3412", name="Name vom Ansprechpartner", codes=[])
                                            ],
                                        ),
                                    ],
                                ),
                                Segment(
                                    id="COM",
                                    name="Kommunikationsverbindung",
                                    number="00006",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C076",
                                            name="Kommunikationsverbindung",
                                            data_elements=[
                                                DataElement(id="D_3148", name="Nummer / Adresse", codes=[]),
                                                DataElement(
                                                    id="D_3155",
                                                    name="Art des Kommunikationsmittels, Code",
                                                    codes=[
                                                        Code(
                                                            name="Elektronische Post",
                                                            description=None,
                                                            value="EM",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="Telefax",
                                                            description=None,
                                                            value="FX",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="Telefon",
                                                            description=None,
                                                            value="TE",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="weiteres Telefon",
                                                            description=None,
                                                            value="AJ",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="Handy",
                                                            description=None,
                                                            value="AL",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                            ],
                            segment_groups=[],
                        ),
                        SegmentGroup(
                            id="2",
                            name="MP-ID Empfänger",
                            ahb_status="Muss",
                            segments=[
                                Segment(
                                    id="NAD",
                                    name="MP-ID Empfänger",
                                    number="00007",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_3035",
                                            name="Beteiligter, Qualifier",
                                            codes=[
                                                Code(
                                                    name="Nachrichtenempfänger",
                                                    description=None,
                                                    value="MR",
                                                    ahb_status="X",
                                                )
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C082",
                                            name="Identifikation des Beteiligten",
                                            data_elements=[
                                                DataElement(id="D_3039", name="MP-ID", codes=[]),
                                                DataElement(
                                                    id="D_3055",
                                                    name="Verantwortliche Stelle für die Codepflege, Code",
                                                    codes=[
                                                        Code(name="GS1", description=None, value="9", ahb_status="X"),
                                                        Code(
                                                            name="DE, BDEW (Bundesverband der Energie- und Wasserwirtschaft e.V.)",
                                                            description=None,
                                                            value="293",
                                                            ahb_status="X",
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ],
                                )
                            ],
                            segment_groups=[],
                        ),
                        SegmentGroup(
                            id="5",
                            name="Vorgang",
                            ahb_status="Muss",
                            segments=[
                                Segment(
                                    id="IDE",
                                    name="Vorgang",
                                    number="00008",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_7495",
                                            name="Objekt, Qualifier",
                                            codes=[
                                                Code(name="Transaktion", description=None, value="24", ahb_status="X")
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C206",
                                            name="Identifikationsnummer",
                                            data_elements=[DataElement(id="D_7402", name="Vorgangsnummer", codes=[])],
                                        ),
                                    ],
                                ),
                                Segment(
                                    id="LOC",
                                    name="ID der Marktlokation",
                                    number="00009",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_3227",
                                            name="Ortsangabe, Qualifier",
                                            codes=[
                                                Code(name="Meldepunkt", description=None, value="172", ahb_status="X")
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C517",
                                            name="Ortsangabe",
                                            data_elements=[
                                                DataElement(id="D_3225", name="ID der Marktlokation", codes=[])
                                            ],
                                        ),
                                    ],
                                ),
                                Segment(
                                    id="DTM",
                                    name="Gültig ab",
                                    number="00010",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C507",
                                            name="Datum/Uhrzeit/Zeitspanne",
                                            data_elements=[
                                                DataElement(
                                                    id="D_2005",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Funktion, Qualifier",
                                                    codes=[
                                                        Code(
                                                            name="Gültigkeit, Beginndatum",
                                                            description=None,
                                                            value="157",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                                DataElement(
                                                    id="D_2380",
                                                    name="Datum oder Uhrzeit oder Zeitspanne, Wert",
                                                    codes=[],
                                                ),
                                                DataElement(
                                                    id="D_2379",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Format, Code",
                                                    codes=[
                                                        Code(
                                                            name="CCYYMMDDHHMMZZZ",
                                                            description=None,
                                                            value="303",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                                Segment(
                                    id="TS",
                                    name="Status der Berechnungsformel",
                                    number="00011",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C601",
                                            name="Statuskategorie",
                                            data_elements=[
                                                DataElement(
                                                    id="D_9015",
                                                    name="Statuskategorie, Code",
                                                    codes=[
                                                        Code(
                                                            name="Status der Berechnungsformel",
                                                            description=None,
                                                            value="Z23",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                )
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C555",
                                            name="Status",
                                            data_elements=[
                                                DataElement(
                                                    id="D_4405",
                                                    name="Status, Code",
                                                    codes=[
                                                        Code(
                                                            name="Berechnungsformel angefügt",
                                                            description="Die Berechnungsformel zur Ermittlung der Energiemenge einer Marktlokation ist in diesem Vorgang der UTILTS enthalten",
                                                            value="Z33",
                                                            ahb_status="X",
                                                        ),
                                                        Code(
                                                            name="Berechnungsformel muss beim Absender angefragt werden",
                                                            description="Die Berechnungsformel zur Ermittlung der Energiemenge der Marktlokation ist komplex und kann mit der UTILTS nicht übermittelt werden",
                                                            value="Z34",
                                                            ahb_status="X",
                                                        ),
                                                        Code(
                                                            name="Berechnungsformel besitzt keine Rechenoperation",
                                                            description="Die Berechnungsformel zur Ermittlung der Energiemenge der Marktlokation besitzt keine Rechenoperation, da es sich um eine 1:1 Beziehung zwischen der Markt- und Messlokation handelt.",
                                                            value="Z40",
                                                            ahb_status="X",
                                                        ),
                                                        Code(
                                                            name="Berechnungsformel nicht erforderlich",
                                                            description="Die Berechnungsformel zur Ermittlung der Energiemenge der Marktlokation ist nicht erforderlich, da keine Messlokation der Marktlokation (pauschale Marktlokation) zugeordnet ist.",
                                                            value="Z41",
                                                            ahb_status="X [18]",
                                                        ),
                                                    ],
                                                )
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                            segment_groups=[
                                SegmentGroup(
                                    id="6",
                                    name="Prüfidentifikator",
                                    ahb_status="Muss",
                                    segments=[
                                        Segment(
                                            id="RFF",
                                            name="Prüfidentifikator",
                                            number="00012",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElementGroup(
                                                    id="C_C506",
                                                    name="Referenz",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_1153",
                                                            name="Referenz, Qualifier",
                                                            codes=[
                                                                Code(
                                                                    name="Prüfidentifikator",
                                                                    description=None,
                                                                    value="Z13",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElement(
                                                            id="D_1154",
                                                            name="Referenz, Identifikation",
                                                            codes=[
                                                                Code(
                                                                    name="Berechnungsformel",
                                                                    description=None,
                                                                    value="25001",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                    ],
                                                )
                                            ],
                                        )
                                    ],
                                    segment_groups=[],
                                ),
                                SegmentGroup(
                                    id="7",
                                    name="Lieferrichtung",
                                    ahb_status="Muss",
                                    segments=[
                                        Segment(
                                            id="CCI",
                                            name="Lieferrichtung",
                                            number="00013",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElement(
                                                    id="D_7059",
                                                    name="Klassentyp, Code",
                                                    codes=[
                                                        Code(
                                                            name="Lieferrichtung",
                                                            description=None,
                                                            value="Z30",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                                DataElementGroup(
                                                    id="C_C240",
                                                    name="Merkmalsbeschreibung",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_7037",
                                                            name="Merkmal, Code",
                                                            codes=[
                                                                Code(
                                                                    name="Erzeugung",
                                                                    description=None,
                                                                    value="Z06",
                                                                    ahb_status="X",
                                                                ),
                                                                Code(
                                                                    name="Verbrauch",
                                                                    description=None,
                                                                    value="Z07",
                                                                    ahb_status="X",
                                                                ),
                                                            ],
                                                        )
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                    segment_groups=[],
                                ),
                                SegmentGroup(
                                    id="8",
                                    name="Energiemenge der Marktlokation",
                                    ahb_status="Muss [3]",
                                    segments=[
                                        Segment(
                                            id="EQ",
                                            name="Energiemenge der Marktlokation",
                                            number="00014",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElement(
                                                    id="D_1229",
                                                    name="Handlung, Code",
                                                    codes=[
                                                        Code(
                                                            name="Energiemenge der Marktlokation",
                                                            description=None,
                                                            value="Z36",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                )
                                            ],
                                        ),
                                        Segment(
                                            id="RFF",
                                            name="Referenz auf einen Rechenschritt",
                                            number="00015",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElementGroup(
                                                    id="C_C506",
                                                    name="Referenz",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_1153",
                                                            name="Referenz, Qualifier",
                                                            codes=[
                                                                Code(
                                                                    name="Rechenschritt",
                                                                    description=None,
                                                                    value="Z23",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElement(
                                                            id="D_1154", name="Rechenschrittidentifikator", codes=[]
                                                        ),
                                                    ],
                                                )
                                            ],
                                        ),
                                    ],
                                    segment_groups=[
                                        SegmentGroup(
                                            id="9",
                                            name="Verwendungszweck der Werte",
                                            ahb_status="Muss",
                                            segments=[
                                                Segment(
                                                    id="CCI",
                                                    name="Verwendungszweck der Werte",
                                                    number="00016",
                                                    ahb_status="Muss",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_7059",
                                                            name="Klassentyp, Code",
                                                            codes=[
                                                                Code(
                                                                    name="Verwendungszweck der Werte",
                                                                    description=None,
                                                                    value="Z27",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        )
                                                    ],
                                                ),
                                                Segment(
                                                    id="CAV",
                                                    name="Verwendungszweck der Werte",
                                                    number="00017",
                                                    ahb_status="Muss [2000]",
                                                    data_elements=[
                                                        DataElementGroup(
                                                            id="C_C889",
                                                            name="Merkmalswert",
                                                            data_elements=[
                                                                DataElement(
                                                                    id="D_7111",
                                                                    name="Merkmalswert, Code",
                                                                    codes=[
                                                                        Code(
                                                                            name="Netznutzungsabrechnung",
                                                                            description=None,
                                                                            value="Z84",
                                                                            ahb_status="X [1P0..1]",
                                                                        ),
                                                                        Code(
                                                                            name="Bilanzkreisabrechnung",
                                                                            description=None,
                                                                            value="Z85",
                                                                            ahb_status="X [1P0..1]",
                                                                        ),
                                                                        Code(
                                                                            name="Mehrmindermengenabrechnung",
                                                                            description=None,
                                                                            value="Z86",
                                                                            ahb_status="X [1P0..1]",
                                                                        ),
                                                                        Code(
                                                                            name="Übermittlung an das HKNR",
                                                                            description=None,
                                                                            value="Z92",
                                                                            ahb_status="X [1P0..1]",
                                                                        ),
                                                                        Code(
                                                                            name="Endkundenabrechnung",
                                                                            description=None,
                                                                            value="Z47",
                                                                            ahb_status="X [1P0..1]",
                                                                        ),
                                                                    ],
                                                                )
                                                            ],
                                                        )
                                                    ],
                                                ),
                                            ],
                                            segment_groups=[],
                                        )
                                    ],
                                ),
                                SegmentGroup(
                                    id="8",
                                    name="Bestandteil des Rechenschritts",
                                    ahb_status="Muss [3]",
                                    segments=[
                                        Segment(
                                            id="EQ",
                                            name="Bestandteil des Rechenschritts",
                                            number="00018",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElement(
                                                    id="D_1229",
                                                    name="Handlung, Code",
                                                    codes=[
                                                        Code(
                                                            name="Bestandteil des Rechenschritts",
                                                            description=None,
                                                            value="Z37",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                                DataElementGroup(
                                                    id="C_C286",
                                                    name="Information über eine Folge",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_1050", name="Rechenschrittidentifikator", codes=[]
                                                        )
                                                    ],
                                                ),
                                            ],
                                        ),
                                        Segment(
                                            id="RFF",
                                            name="Referenz auf die ID einer Messlokation",
                                            number="00019",
                                            ahb_status="Muss [6]",
                                            data_elements=[
                                                DataElementGroup(
                                                    id="C_C506",
                                                    name="Referenz",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_1153",
                                                            name="Referenz, Qualifier",
                                                            codes=[
                                                                Code(
                                                                    name="Messlokation",
                                                                    description=None,
                                                                    value="Z19",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElement(
                                                            id="D_1154", name="ID einer Messlokation", codes=[]
                                                        ),
                                                    ],
                                                )
                                            ],
                                        ),
                                        Segment(
                                            id="RFF",
                                            name="Referenz auf einen Rechenschritt",
                                            number="00020",
                                            ahb_status="Muss [5]",
                                            data_elements=[
                                                DataElementGroup(
                                                    id="C_C506",
                                                    name="Referenz",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_1153",
                                                            name="Referenz, Qualifier",
                                                            codes=[
                                                                Code(
                                                                    name="Rechenschritt",
                                                                    description=None,
                                                                    value="Z23",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElement(
                                                            id="D_1154", name="Rechenschrittidentifikator", codes=[]
                                                        ),
                                                    ],
                                                )
                                            ],
                                        ),
                                    ],
                                    segment_groups=[
                                        SegmentGroup(
                                            id="9",
                                            name="Mathematischer Operator",
                                            ahb_status="Muss",
                                            segments=[
                                                Segment(
                                                    id="CCI",
                                                    name="Mathematischer Operator",
                                                    number="00021",
                                                    ahb_status="Muss",
                                                    data_elements=[
                                                        DataElementGroup(
                                                            id="C_C240",
                                                            name="Merkmalsbeschreibung",
                                                            data_elements=[
                                                                DataElement(
                                                                    id="D_7037",
                                                                    name="Merkmal, Code",
                                                                    codes=[
                                                                        Code(
                                                                            name="Mathematischer Operator",
                                                                            description=None,
                                                                            value="Z86",
                                                                            ahb_status="X",
                                                                        )
                                                                    ],
                                                                )
                                                            ],
                                                        )
                                                    ],
                                                ),
                                                Segment(
                                                    id="CAV",
                                                    name="Operator / Operation",
                                                    number="00022",
                                                    ahb_status="Muss",
                                                    data_elements=[
                                                        DataElementGroup(
                                                            id="C_C889",
                                                            name="Merkmalswert",
                                                            data_elements=[
                                                                DataElement(
                                                                    id="D_7111",
                                                                    name="Merkmalswert, Code",
                                                                    codes=[
                                                                        Code(
                                                                            name="Addition",
                                                                            description="Die gemessene Energiemenge der referenzierten Messlokation oder das Ergebnis des referenzierten Rechenschritts wird in diesem Rechenschritt mittels Addition berücksichtigt.",
                                                                            value="Z69",
                                                                            ahb_status="X [11] ⊻ [15]",
                                                                        ),
                                                                        Code(
                                                                            name="Subtraktion",
                                                                            description="Die gemessene Energiemenge der referenzierten Messlokation oder das Ergebnis des referenzierten Rechenschritts wird in diesem Rechenschritt mittels Subtraktion berücksichtigt.",
                                                                            value="Z70",
                                                                            ahb_status="X [11]",
                                                                        ),
                                                                        Code(
                                                                            name="Divisor",
                                                                            description="Die gemessene Energiemenge der referenzierten Messlokation oder das Ergebnis des referenzierten Rechenschritts ist in diesem Rechenschritt der Divisor (Nenner des Bruchs).",
                                                                            value="Z80",
                                                                            ahb_status="X [13]",
                                                                        ),
                                                                        Code(
                                                                            name="Dividend",
                                                                            description="Die gemessene Energiemenge der referenzierten Messlokation oder das Ergebnis des referenzierten Rechenschritts ist in diesem Rechenschritt der Dividend (Zähler des Bruchs).",
                                                                            value="Z81",
                                                                            ahb_status="X [13]",
                                                                        ),
                                                                        Code(
                                                                            name="Faktor",
                                                                            description="Die gemessene Energiemenge der referenzierten Messlokation oder das Ergebnis des Rechenschritts wird in diesem Rechenschritt als ein Faktor einer Multiplikation berücksichtigt.",
                                                                            value="Z82",
                                                                            ahb_status="X [14]",
                                                                        ),
                                                                    ],
                                                                )
                                                            ],
                                                        )
                                                    ],
                                                ),
                                            ],
                                            segment_groups=[],
                                        ),
                                        SegmentGroup(
                                            id="9",
                                            name="Energieflussrichtung",
                                            ahb_status="Muss [7]",
                                            segments=[
                                                Segment(
                                                    id="CCI",
                                                    name="Energieflussrichtung",
                                                    number="00023",
                                                    ahb_status="Muss",
                                                    data_elements=[
                                                        DataElementGroup(
                                                            id="C_C240",
                                                            name="Merkmalsbeschreibung",
                                                            data_elements=[
                                                                DataElement(
                                                                    id="D_7037",
                                                                    name="Merkmal, Code",
                                                                    codes=[
                                                                        Code(
                                                                            name="Energieflussrichtung",
                                                                            description=None,
                                                                            value="Z87",
                                                                            ahb_status="X",
                                                                        )
                                                                    ],
                                                                )
                                                            ],
                                                        )
                                                    ],
                                                ),
                                                Segment(
                                                    id="CAV",
                                                    name="Energieflussrichtung",
                                                    number="00024",
                                                    ahb_status="Muss",
                                                    data_elements=[
                                                        DataElementGroup(
                                                            id="C_C889",
                                                            name="Merkmalswert",
                                                            data_elements=[
                                                                DataElement(
                                                                    id="D_7111",
                                                                    name="Merkmalswert, Code",
                                                                    codes=[
                                                                        Code(
                                                                            name="Verbrauch",
                                                                            description=None,
                                                                            value="Z71",
                                                                            ahb_status="X",
                                                                        ),
                                                                        Code(
                                                                            name="Erzeugung",
                                                                            description=None,
                                                                            value="Z72",
                                                                            ahb_status="X",
                                                                        ),
                                                                    ],
                                                                )
                                                            ],
                                                        )
                                                    ],
                                                ),
                                            ],
                                            segment_groups=[],
                                        ),
                                        SegmentGroup(
                                            id="9",
                                            name="Verlustfaktor Trafo",
                                            ahb_status="Soll [10] ∧ [7]",
                                            segments=[
                                                Segment(
                                                    id="CCI",
                                                    name="Verlustfaktor Trafo",
                                                    number="00025",
                                                    ahb_status="Muss",
                                                    data_elements=[
                                                        DataElementGroup(
                                                            id="C_C240",
                                                            name="Merkmalsbeschreibung",
                                                            data_elements=[
                                                                DataElement(
                                                                    id="D_7037",
                                                                    name="Merkmal, Code",
                                                                    codes=[
                                                                        Code(
                                                                            name="Verlustfaktor Trafo",
                                                                            description=None,
                                                                            value="Z16",
                                                                            ahb_status="X",
                                                                        )
                                                                    ],
                                                                )
                                                            ],
                                                        )
                                                    ],
                                                ),
                                                Segment(
                                                    id="CAV",
                                                    name="Verlustfaktor Trafo",
                                                    number="00026",
                                                    ahb_status="Muss",
                                                    data_elements=[
                                                        DataElementGroup(
                                                            id="C_C889",
                                                            name="Merkmalswert",
                                                            data_elements=[
                                                                DataElement(
                                                                    id="D_7111",
                                                                    name="Merkmalswert, Code",
                                                                    codes=[
                                                                        Code(
                                                                            name="Verlustfaktor",
                                                                            description=None,
                                                                            value="Z28",
                                                                            ahb_status="X",
                                                                        )
                                                                    ],
                                                                ),
                                                                DataElement(
                                                                    id="D_7110", name="Verlustfaktor Trafo", codes=[]
                                                                ),
                                                            ],
                                                        )
                                                    ],
                                                ),
                                            ],
                                            segment_groups=[],
                                        ),
                                        SegmentGroup(
                                            id="9",
                                            name="Verlustfaktor Leitung",
                                            ahb_status="Soll [10] ∧ [7]",
                                            segments=[
                                                Segment(
                                                    id="CCI",
                                                    name="Verlustfaktor Leitung",
                                                    number="00027",
                                                    ahb_status="Muss",
                                                    data_elements=[
                                                        DataElementGroup(
                                                            id="C_C240",
                                                            name="Merkmalsbeschreibung",
                                                            data_elements=[
                                                                DataElement(
                                                                    id="D_7037",
                                                                    name="Merkmal, Code",
                                                                    codes=[
                                                                        Code(
                                                                            name="Verlustfaktor Leitung",
                                                                            description=None,
                                                                            value="ZB2",
                                                                            ahb_status="X",
                                                                        )
                                                                    ],
                                                                )
                                                            ],
                                                        )
                                                    ],
                                                ),
                                                Segment(
                                                    id="CAV",
                                                    name="Verlustfaktor Leitung",
                                                    number="00028",
                                                    ahb_status="Muss",
                                                    data_elements=[
                                                        DataElementGroup(
                                                            id="C_C889",
                                                            name="Merkmalswert",
                                                            data_elements=[
                                                                DataElement(
                                                                    id="D_7111",
                                                                    name="Merkmalswert, Code",
                                                                    codes=[
                                                                        Code(
                                                                            name="Verlustfaktor",
                                                                            description=None,
                                                                            value="Z28",
                                                                            ahb_status="X",
                                                                        )
                                                                    ],
                                                                ),
                                                                DataElement(
                                                                    id="D_7110", name="Verlustfaktor Leitung", codes=[]
                                                                ),
                                                            ],
                                                        )
                                                    ],
                                                ),
                                            ],
                                            segment_groups=[],
                                        ),
                                        SegmentGroup(
                                            id="9",
                                            name="Aufteilungsfaktor Energiemenge",
                                            ahb_status="Soll [10] ∧ [7]",
                                            segments=[
                                                Segment(
                                                    id="CCI",
                                                    name="Aufteilungsfaktor Energiemenge",
                                                    number="00029",
                                                    ahb_status="Muss",
                                                    data_elements=[
                                                        DataElementGroup(
                                                            id="C_C240",
                                                            name="Merkmalsbeschreibung",
                                                            data_elements=[
                                                                DataElement(
                                                                    id="D_7037",
                                                                    name="Merkmal, Code",
                                                                    codes=[
                                                                        Code(
                                                                            name="Aufteilungsfaktor Energiemenge",
                                                                            description=None,
                                                                            value="ZG6",
                                                                            ahb_status="X",
                                                                        )
                                                                    ],
                                                                )
                                                            ],
                                                        )
                                                    ],
                                                ),
                                                Segment(
                                                    id="CAV",
                                                    name="Aufteilungsfaktor Energiemenge",
                                                    number="00030",
                                                    ahb_status="Muss",
                                                    data_elements=[
                                                        DataElementGroup(
                                                            id="C_C889",
                                                            name="Merkmalswert",
                                                            data_elements=[
                                                                DataElement(
                                                                    id="D_7111",
                                                                    name="Merkmalswert, Code",
                                                                    codes=[
                                                                        Code(
                                                                            name="Aufteilungsfaktor Energiemenge",
                                                                            description=None,
                                                                            value="ZH6",
                                                                            ahb_status="X",
                                                                        )
                                                                    ],
                                                                ),
                                                                DataElement(
                                                                    id="D_7110",
                                                                    name="Aufteilungsfaktor Energiemenge",
                                                                    codes=[],
                                                                ),
                                                            ],
                                                        )
                                                    ],
                                                ),
                                            ],
                                            segment_groups=[],
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                )
            ],
        ),
        Anwendungsfall(
            pruefidentifikator="25002",
            beschreibung="Ablehnung Berechnungsformel",
            kommunikation_von="MSB an NB",
            format="UTILTS",
            segments=[
                Segment(
                    id="UNH",
                    name="Nachrichten-Kopfsegment",
                    number="00032",
                    ahb_status="Muss",
                    data_elements=[
                        DataElement(id="D_0062", name="Nachrichten-Referenznummer", codes=[]),
                        DataElementGroup(
                            id="C_S009",
                            name="Nachrichten-Kennung",
                            data_elements=[
                                DataElement(
                                    id="D_0065",
                                    name="Nachrichtentyp-Kennung",
                                    codes=[
                                        Code(
                                            name="Netznutzungszeiten-Nachricht",
                                            description=None,
                                            value="UTILTS",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                                DataElement(
                                    id="D_0052",
                                    name="Versionsnummer des Nachrichtentyps",
                                    codes=[Code(name="Entwurfs-Version", description=None, value="D", ahb_status="X")],
                                ),
                                DataElement(
                                    id="D_0054",
                                    name="Freigabenummer des Nachrichtentyps",
                                    codes=[
                                        Code(name="Ausgabe 2018 - A", description=None, value="18A", ahb_status="X")
                                    ],
                                ),
                                DataElement(
                                    id="D_0051",
                                    name="Verwaltende Organisation",
                                    codes=[Code(name="UN/CEFACT", description=None, value="UN", ahb_status="X")],
                                ),
                                DataElement(
                                    id="D_0057",
                                    name="Anwendungscode der zuständigen Organisation",
                                    codes=[
                                        Code(
                                            name="Versionsnummer der zugrundeliegenden BDEW-Nachrichtenbeschreibung",
                                            description=None,
                                            value="1.1c",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                Segment(
                    id="BGM",
                    name="Beginn der Nachricht",
                    number="00033",
                    ahb_status="Muss",
                    data_elements=[
                        DataElementGroup(
                            id="C_C002",
                            name="Dokumenten-/Nachrichtenname",
                            data_elements=[
                                DataElement(
                                    id="D_1001",
                                    name="Dokumentenname, Code",
                                    codes=[
                                        Code(name="Berechnungsformel", description=None, value="Z36", ahb_status="X")
                                    ],
                                )
                            ],
                        ),
                        DataElementGroup(
                            id="C_C106",
                            name="Dokumenten-/Nachrichten-Identifikation",
                            data_elements=[DataElement(id="D_1004", name="Dokumentennummer", codes=[])],
                        ),
                    ],
                ),
                Segment(
                    id="DTM",
                    name="Nachrichtendatum",
                    number="00034",
                    ahb_status="Muss",
                    data_elements=[
                        DataElementGroup(
                            id="C_C507",
                            name="Datum/Uhrzeit/Zeitspanne",
                            data_elements=[
                                DataElement(
                                    id="D_2005",
                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Funktion, Qualifier",
                                    codes=[
                                        Code(
                                            name="Dokumenten-/Nachrichtendatum/-zeit",
                                            description=None,
                                            value="137",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                                DataElement(id="D_2380", name="Datum oder Uhrzeit oder Zeitspanne, Wert", codes=[]),
                                DataElement(
                                    id="D_2379",
                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Format, Code",
                                    codes=[Code(name="CCYYMMDDHHMMZZZ", description=None, value="303", ahb_status="X")],
                                ),
                            ],
                        )
                    ],
                ),
                Segment(
                    id="UNT",
                    name="Nachrichten-Endesegment",
                    number="00043",
                    ahb_status="Muss",
                    data_elements=[
                        DataElement(id="D_0074", name="Anzahl der Segmente in einer Nachricht", codes=[]),
                        DataElement(id="D_0062", name="Nachrichten-Referenznummer", codes=[]),
                    ],
                ),
            ],
            segment_groups=[
                SegmentGroup(
                    id="2",
                    name="MP-ID Absender",
                    ahb_status="Muss",
                    segments=[
                        Segment(
                            id="NAD",
                            name="MP-ID Absender",
                            number="00035",
                            ahb_status="Muss",
                            data_elements=[
                                DataElement(
                                    id="D_3035",
                                    name="Beteiligter, Qualifier",
                                    codes=[
                                        Code(
                                            name="Dokumenten-/Nachrichtenaussteller bzw. -absender",
                                            description=None,
                                            value="MS",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                                DataElementGroup(
                                    id="C_C082",
                                    name="Identifikation des Beteiligten",
                                    data_elements=[
                                        DataElement(id="D_3039", name="MP-ID", codes=[]),
                                        DataElement(
                                            id="D_3055",
                                            name="Verantwortliche Stelle für die Codepflege, Code",
                                            codes=[
                                                Code(name="GS1", description=None, value="9", ahb_status="X"),
                                                Code(
                                                    name="DE, BDEW (Bundesverband der Energie- und Wasserwirtschaft e.V.)",
                                                    description=None,
                                                    value="293",
                                                    ahb_status="X",
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        )
                    ],
                    segment_groups=[
                        SegmentGroup(
                            id="3",
                            name="Kontaktinformationen",
                            ahb_status="Muss",
                            segments=[
                                Segment(
                                    id="CTA",
                                    name="Ansprechpartner",
                                    number="00036",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_3139",
                                            name="Funktion des Ansprechpartners, Code",
                                            codes=[
                                                Code(
                                                    name="Informationskontakt",
                                                    description=None,
                                                    value="IC",
                                                    ahb_status="X",
                                                )
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C056",
                                            name="Kontaktangaben",
                                            data_elements=[
                                                DataElement(id="D_3412", name="Name vom Ansprechpartner", codes=[])
                                            ],
                                        ),
                                    ],
                                ),
                                Segment(
                                    id="COM",
                                    name="Kommunikationsverbindung",
                                    number="00037",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C076",
                                            name="Kommunikationsverbindung",
                                            data_elements=[
                                                DataElement(id="D_3148", name="Nummer / Adresse", codes=[]),
                                                DataElement(
                                                    id="D_3155",
                                                    name="Art des Kommunikationsmittels, Code",
                                                    codes=[
                                                        Code(
                                                            name="Elektronische Post",
                                                            description=None,
                                                            value="EM",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="Telefax",
                                                            description=None,
                                                            value="FX",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="Telefon",
                                                            description=None,
                                                            value="TE",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="weiteres Telefon",
                                                            description=None,
                                                            value="AJ",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="Handy",
                                                            description=None,
                                                            value="AL",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                            ],
                            segment_groups=[],
                        ),
                        SegmentGroup(
                            id="2",
                            name="MP-ID Empfänger",
                            ahb_status="Muss",
                            segments=[
                                Segment(
                                    id="NAD",
                                    name="MP-ID Empfänger",
                                    number="00038",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_3035",
                                            name="Beteiligter, Qualifier",
                                            codes=[
                                                Code(
                                                    name="Nachrichtenempfänger",
                                                    description=None,
                                                    value="MR",
                                                    ahb_status="X",
                                                )
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C082",
                                            name="Identifikation des Beteiligten",
                                            data_elements=[
                                                DataElement(id="D_3039", name="MP-ID", codes=[]),
                                                DataElement(
                                                    id="D_3055",
                                                    name="Verantwortliche Stelle für die Codepflege, Code",
                                                    codes=[
                                                        Code(name="GS1", description=None, value="9", ahb_status="X"),
                                                        Code(
                                                            name="DE, BDEW (Bundesverband der Energie- und Wasserwirtschaft e.V.)",
                                                            description=None,
                                                            value="293",
                                                            ahb_status="X",
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ],
                                )
                            ],
                            segment_groups=[],
                        ),
                        SegmentGroup(
                            id="5",
                            name="Vorgang",
                            ahb_status="Muss",
                            segments=[
                                Segment(
                                    id="IDE",
                                    name="Vorgang",
                                    number="00039",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_7495",
                                            name="Objekt, Qualifier",
                                            codes=[
                                                Code(name="Transaktion", description=None, value="24", ahb_status="X")
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C206",
                                            name="Identifikationsnummer",
                                            data_elements=[DataElement(id="D_7402", name="Vorgangsnummer", codes=[])],
                                        ),
                                    ],
                                ),
                                Segment(
                                    id="TS",
                                    name="Status der Antwort",
                                    number="00040",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C601",
                                            name="Statuskategorie",
                                            data_elements=[
                                                DataElement(
                                                    id="D_9015",
                                                    name="Statuskategorie, Code",
                                                    codes=[
                                                        Code(
                                                            name="Status der Antwort",
                                                            description=None,
                                                            value="E01",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                )
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C556",
                                            name="Statusanlaß",
                                            data_elements=[
                                                DataElement(id="D_9013", name="Code des Prüfschritts", codes=[]),
                                                DataElement(
                                                    id="D_1131",
                                                    name="Codeliste, Code",
                                                    codes=[
                                                        Code(
                                                            name="EBD Nr. E_0218",
                                                            description=None,
                                                            value="E_0218",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                            segment_groups=[
                                SegmentGroup(
                                    id="6",
                                    name="Prüfidentifikator",
                                    ahb_status="Muss",
                                    segments=[
                                        Segment(
                                            id="RFF",
                                            name="Prüfidentifikator",
                                            number="00041",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElementGroup(
                                                    id="C_C506",
                                                    name="Referenz",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_1153",
                                                            name="Referenz, Qualifier",
                                                            codes=[
                                                                Code(
                                                                    name="Prüfidentifikator",
                                                                    description=None,
                                                                    value="Z13",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElement(
                                                            id="D_1154",
                                                            name="Referenz, Identifikation",
                                                            codes=[
                                                                Code(
                                                                    name="Ablehnung Berechnungsformel",
                                                                    description=None,
                                                                    value="25002",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                    ],
                                                )
                                            ],
                                        )
                                    ],
                                    segment_groups=[],
                                ),
                                SegmentGroup(
                                    id="6",
                                    name="Referenz-Vorgangsnummer (aus Berechnungsformel)",
                                    ahb_status="Muss",
                                    segments=[
                                        Segment(
                                            id="RFF",
                                            name="Referenz Vorgangsnummer (aus Berechnungsformel)",
                                            number="00042",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElementGroup(
                                                    id="C_C506",
                                                    name="Referenz",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_1153",
                                                            name="Referenz, Qualifier",
                                                            codes=[
                                                                Code(
                                                                    name="Transaktions-Referenznummer",
                                                                    description=None,
                                                                    value="TN",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElement(id="D_1154", name="Vorgangsnummer", codes=[]),
                                                    ],
                                                )
                                            ],
                                        )
                                    ],
                                    segment_groups=[],
                                ),
                            ],
                        ),
                    ],
                )
            ],
        ),
        Anwendungsfall(
            pruefidentifikator="25003",
            beschreibung="Zustimmung Berechnungsformel",
            kommunikation_von="MSB an NB",
            format="UTILTS",
            segments=[
                Segment(
                    id="UNH",
                    name="Nachrichten-Kopfsegment",
                    number="00044",
                    ahb_status="Muss",
                    data_elements=[
                        DataElement(id="D_0062", name="Nachrichten-Referenznummer", codes=[]),
                        DataElementGroup(
                            id="C_S009",
                            name="Nachrichten-Kennung",
                            data_elements=[
                                DataElement(
                                    id="D_0065",
                                    name="Nachrichtentyp-Kennung",
                                    codes=[
                                        Code(
                                            name="Netznutzungszeiten-Nachricht",
                                            description=None,
                                            value="UTILTS",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                                DataElement(
                                    id="D_0052",
                                    name="Versionsnummer des Nachrichtentyps",
                                    codes=[Code(name="Entwurfs-Version", description=None, value="D", ahb_status="X")],
                                ),
                                DataElement(
                                    id="D_0054",
                                    name="Freigabenummer des Nachrichtentyps",
                                    codes=[
                                        Code(name="Ausgabe 2018 - A", description=None, value="18A", ahb_status="X")
                                    ],
                                ),
                                DataElement(
                                    id="D_0051",
                                    name="Verwaltende Organisation",
                                    codes=[Code(name="UN/CEFACT", description=None, value="UN", ahb_status="X")],
                                ),
                                DataElement(
                                    id="D_0057",
                                    name="Anwendungscode der zuständigen Organisation",
                                    codes=[
                                        Code(
                                            name="Versionsnummer der zugrundeliegenden BDEW-Nachrichtenbeschreibung",
                                            description=None,
                                            value="1.1c",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                Segment(
                    id="BGM",
                    name="Beginn der Nachricht",
                    number="00045",
                    ahb_status="Muss",
                    data_elements=[
                        DataElementGroup(
                            id="C_C002",
                            name="Dokumenten-/Nachrichtenname",
                            data_elements=[
                                DataElement(
                                    id="D_1001",
                                    name="Dokumentenname, Code",
                                    codes=[
                                        Code(name="Berechnungsformel", description=None, value="Z36", ahb_status="X")
                                    ],
                                )
                            ],
                        ),
                        DataElementGroup(
                            id="C_C106",
                            name="Dokumenten-/Nachrichten-Identifikation",
                            data_elements=[DataElement(id="D_1004", name="Dokumentennummer", codes=[])],
                        ),
                    ],
                ),
                Segment(
                    id="DTM",
                    name="Nachrichtendatum",
                    number="00046",
                    ahb_status="Muss",
                    data_elements=[
                        DataElementGroup(
                            id="C_C507",
                            name="Datum/Uhrzeit/Zeitspanne",
                            data_elements=[
                                DataElement(
                                    id="D_2005",
                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Funktion, Qualifier",
                                    codes=[
                                        Code(
                                            name="Dokumenten-/Nachrichtendatum/-zeit",
                                            description=None,
                                            value="137",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                                DataElement(id="D_2380", name="Datum oder Uhrzeit oder Zeitspanne, Wert", codes=[]),
                                DataElement(
                                    id="D_2379",
                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Format, Code",
                                    codes=[Code(name="CCYYMMDDHHMMZZZ", description=None, value="303", ahb_status="X")],
                                ),
                            ],
                        )
                    ],
                ),
                Segment(
                    id="UNT",
                    name="Nachrichten-Endesegment",
                    number="00055",
                    ahb_status="Muss",
                    data_elements=[
                        DataElement(id="D_0074", name="Anzahl der Segmente in einer Nachricht", codes=[]),
                        DataElement(id="D_0062", name="Nachrichten-Referenznummer", codes=[]),
                    ],
                ),
            ],
            segment_groups=[
                SegmentGroup(
                    id="2",
                    name="MP-ID Absender",
                    ahb_status="Muss",
                    segments=[
                        Segment(
                            id="NAD",
                            name="MP-ID Absender",
                            number="00047",
                            ahb_status="Muss",
                            data_elements=[
                                DataElement(
                                    id="D_3035",
                                    name="Beteiligter, Qualifier",
                                    codes=[
                                        Code(
                                            name="Dokumenten-/Nachrichtenaussteller bzw. -absender",
                                            description=None,
                                            value="MS",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                                DataElementGroup(
                                    id="C_C082",
                                    name="Identifikation des Beteiligten",
                                    data_elements=[
                                        DataElement(id="D_3039", name="MP-ID", codes=[]),
                                        DataElement(
                                            id="D_3055",
                                            name="Verantwortliche Stelle für die Codepflege, Code",
                                            codes=[
                                                Code(name="GS1", description=None, value="9", ahb_status="X"),
                                                Code(
                                                    name="DE, BDEW (Bundesverband der Energie- und Wasserwirtschaft e.V.)",
                                                    description=None,
                                                    value="293",
                                                    ahb_status="X",
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        )
                    ],
                    segment_groups=[
                        SegmentGroup(
                            id="3",
                            name="Kontaktinformationen",
                            ahb_status="Kann",
                            segments=[
                                Segment(
                                    id="CTA",
                                    name="Ansprechpartner",
                                    number="00048",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_3139",
                                            name="Funktion des Ansprechpartners, Code",
                                            codes=[
                                                Code(
                                                    name="Informationskontakt",
                                                    description=None,
                                                    value="IC",
                                                    ahb_status="X",
                                                )
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C056",
                                            name="Kontaktangaben",
                                            data_elements=[
                                                DataElement(id="D_3412", name="Name vom Ansprechpartner", codes=[])
                                            ],
                                        ),
                                    ],
                                ),
                                Segment(
                                    id="COM",
                                    name="Kommunikationsverbindung",
                                    number="00049",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C076",
                                            name="Kommunikationsverbindung",
                                            data_elements=[
                                                DataElement(id="D_3148", name="Nummer / Adresse", codes=[]),
                                                DataElement(
                                                    id="D_3155",
                                                    name="Art des Kommunikationsmittels, Code",
                                                    codes=[
                                                        Code(
                                                            name="Elektronische Post",
                                                            description=None,
                                                            value="EM",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="Telefax",
                                                            description=None,
                                                            value="FX",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="Telefon",
                                                            description=None,
                                                            value="TE",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="weiteres Telefon",
                                                            description=None,
                                                            value="AJ",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="Handy",
                                                            description=None,
                                                            value="AL",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                            ],
                            segment_groups=[],
                        ),
                        SegmentGroup(
                            id="2",
                            name="MP-ID Empfänger",
                            ahb_status="Muss",
                            segments=[
                                Segment(
                                    id="NAD",
                                    name="MP-ID Empfänger",
                                    number="00050",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_3035",
                                            name="Beteiligter, Qualifier",
                                            codes=[
                                                Code(
                                                    name="Nachrichtenempfänger",
                                                    description=None,
                                                    value="MR",
                                                    ahb_status="X",
                                                )
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C082",
                                            name="Identifikation des Beteiligten",
                                            data_elements=[
                                                DataElement(id="D_3039", name="MP-ID", codes=[]),
                                                DataElement(
                                                    id="D_3055",
                                                    name="Verantwortliche Stelle für die Codepflege, Code",
                                                    codes=[
                                                        Code(name="GS1", description=None, value="9", ahb_status="X"),
                                                        Code(
                                                            name="DE, BDEW (Bundesverband der Energie- und Wasserwirtschaft e.V.)",
                                                            description=None,
                                                            value="293",
                                                            ahb_status="X",
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ],
                                )
                            ],
                            segment_groups=[],
                        ),
                        SegmentGroup(
                            id="5",
                            name="Vorgang",
                            ahb_status="Muss",
                            segments=[
                                Segment(
                                    id="IDE",
                                    name="Vorgang",
                                    number="00051",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_7495",
                                            name="Objekt, Qualifier",
                                            codes=[
                                                Code(name="Transaktion", description=None, value="24", ahb_status="X")
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C206",
                                            name="Identifikationsnummer",
                                            data_elements=[DataElement(id="D_7402", name="Vorgangsnummer", codes=[])],
                                        ),
                                    ],
                                ),
                                Segment(
                                    id="TS",
                                    name="Status der Antwort",
                                    number="00052",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C601",
                                            name="Statuskategorie",
                                            data_elements=[
                                                DataElement(
                                                    id="D_9015",
                                                    name="Statuskategorie, Code",
                                                    codes=[
                                                        Code(
                                                            name="Status der Antwort",
                                                            description=None,
                                                            value="E01",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                )
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C556",
                                            name="Statusanlaß",
                                            data_elements=[
                                                DataElement(id="D_9013", name="Code des Prüfschritts", codes=[]),
                                                DataElement(
                                                    id="D_1131",
                                                    name="Codeliste, Code",
                                                    codes=[
                                                        Code(
                                                            name="EBD Nr. E_0218",
                                                            description=None,
                                                            value="E_0218",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                            segment_groups=[
                                SegmentGroup(
                                    id="6",
                                    name="Prüfidentifikator",
                                    ahb_status="Muss",
                                    segments=[
                                        Segment(
                                            id="RFF",
                                            name="Prüfidentifikator",
                                            number="00053",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElementGroup(
                                                    id="C_C506",
                                                    name="Referenz",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_1153",
                                                            name="Referenz, Qualifier",
                                                            codes=[
                                                                Code(
                                                                    name="Prüfidentifikator",
                                                                    description=None,
                                                                    value="Z13",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElement(
                                                            id="D_1154",
                                                            name="Referenz, Identifikation",
                                                            codes=[
                                                                Code(
                                                                    name="Zustimmung Berechnungsformel",
                                                                    description=None,
                                                                    value="25003",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                    ],
                                                )
                                            ],
                                        )
                                    ],
                                    segment_groups=[],
                                ),
                                SegmentGroup(
                                    id="6",
                                    name="Referenz-Vorgangsnummer (aus Berechnungsformel)",
                                    ahb_status="Muss",
                                    segments=[
                                        Segment(
                                            id="RFF",
                                            name="Referenz Vorgangsnummer (aus Berechnungsformel)",
                                            number="00054",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElementGroup(
                                                    id="C_C506",
                                                    name="Referenz",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_1153",
                                                            name="Referenz, Qualifier",
                                                            codes=[
                                                                Code(
                                                                    name="Transaktions-Referenznummer",
                                                                    description=None,
                                                                    value="TN",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElement(id="D_1154", name="Vorgangsnummer", codes=[]),
                                                    ],
                                                )
                                            ],
                                        )
                                    ],
                                    segment_groups=[],
                                ),
                            ],
                        ),
                    ],
                )
            ],
        ),
        Anwendungsfall(
            pruefidentifikator="25009",
            beschreibung="Übermittlung einer ausgerollten Leistungskurvendefinition",
            kommunikation_von="NB an LF / MSB\r\nLF an NB, MSB",
            format="UTILTS",
            segments=[
                Segment(
                    id="UNH",
                    name="Nachrichten-Kopfsegment",
                    number="00056",
                    ahb_status="Muss",
                    data_elements=[
                        DataElement(id="D_0062", name="Nachrichten-Referenznummer", codes=[]),
                        DataElementGroup(
                            id="C_S009",
                            name="Nachrichten-Kennung",
                            data_elements=[
                                DataElement(
                                    id="D_0065",
                                    name="Nachrichtentyp-Kennung",
                                    codes=[
                                        Code(
                                            name="Netznutzungszeiten-Nachricht",
                                            description=None,
                                            value="UTILTS",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                                DataElement(
                                    id="D_0052",
                                    name="Versionsnummer des Nachrichtentyps",
                                    codes=[Code(name="Entwurfs-Version", description=None, value="D", ahb_status="X")],
                                ),
                                DataElement(
                                    id="D_0054",
                                    name="Freigabenummer des Nachrichtentyps",
                                    codes=[
                                        Code(name="Ausgabe 2018 - A", description=None, value="18A", ahb_status="X")
                                    ],
                                ),
                                DataElement(
                                    id="D_0051",
                                    name="Verwaltende Organisation",
                                    codes=[Code(name="UN/CEFACT", description=None, value="UN", ahb_status="X")],
                                ),
                                DataElement(
                                    id="D_0057",
                                    name="Anwendungscode der zuständigen Organisation",
                                    codes=[
                                        Code(
                                            name="Versionsnummer der zugrundeliegenden BDEW-Nachrichtenbeschreibung",
                                            description=None,
                                            value="1.1c",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                Segment(
                    id="BGM",
                    name="Beginn der Nachricht",
                    number="00057",
                    ahb_status="Muss",
                    data_elements=[
                        DataElementGroup(
                            id="C_C002",
                            name="Dokumenten-/Nachrichtenname",
                            data_elements=[
                                DataElement(
                                    id="D_1001",
                                    name="Dokumentenname, Code",
                                    codes=[
                                        Code(
                                            name="Ausgerollte Leistungskurvendefinition",
                                            description=None,
                                            value="Z81",
                                            ahb_status="X",
                                        )
                                    ],
                                )
                            ],
                        ),
                        DataElementGroup(
                            id="C_C106",
                            name="Dokumenten-/Nachrichten-Identifikation",
                            data_elements=[DataElement(id="D_1004", name="Dokumentennummer", codes=[])],
                        ),
                    ],
                ),
                Segment(
                    id="DTM",
                    name="Nachrichtendatum",
                    number="00058",
                    ahb_status="Muss",
                    data_elements=[
                        DataElementGroup(
                            id="C_C507",
                            name="Datum/Uhrzeit/Zeitspanne",
                            data_elements=[
                                DataElement(
                                    id="D_2005",
                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Funktion, Qualifier",
                                    codes=[
                                        Code(
                                            name="Dokumenten-/Nachrichtendatum/-zeit",
                                            description=None,
                                            value="137",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                                DataElement(id="D_2380", name="Datum oder Uhrzeit oder Zeitspanne, Wert", codes=[]),
                                DataElement(
                                    id="D_2379",
                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Format, Code",
                                    codes=[Code(name="CCYYMMDDHHMMZZZ", description=None, value="303", ahb_status="X")],
                                ),
                            ],
                        )
                    ],
                ),
                Segment(
                    id="UNT",
                    name="Nachrichten-Endesegment",
                    number="00074",
                    ahb_status="Muss",
                    data_elements=[
                        DataElement(id="D_0074", name="Anzahl der Segmente in einer Nachricht", codes=[]),
                        DataElement(id="D_0062", name="Nachrichten-Referenznummer", codes=[]),
                    ],
                ),
            ],
            segment_groups=[
                SegmentGroup(
                    id="2",
                    name="MP-ID Absender",
                    ahb_status="Muss",
                    segments=[
                        Segment(
                            id="NAD",
                            name="MP-ID Absender",
                            number="00059",
                            ahb_status="Muss",
                            data_elements=[
                                DataElement(
                                    id="D_3035",
                                    name="Beteiligter, Qualifier",
                                    codes=[
                                        Code(
                                            name="Dokumenten-/Nachrichtenaussteller bzw. -absender",
                                            description=None,
                                            value="MS",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                                DataElementGroup(
                                    id="C_C082",
                                    name="Identifikation des Beteiligten",
                                    data_elements=[
                                        DataElement(id="D_3039", name="MP-ID", codes=[]),
                                        DataElement(
                                            id="D_3055",
                                            name="Verantwortliche Stelle für die Codepflege, Code",
                                            codes=[
                                                Code(name="GS1", description=None, value="9", ahb_status="X"),
                                                Code(
                                                    name="DE, BDEW (Bundesverband der Energie- und Wasserwirtschaft e.V.)",
                                                    description=None,
                                                    value="293",
                                                    ahb_status="X",
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        )
                    ],
                    segment_groups=[
                        SegmentGroup(
                            id="3",
                            name="Kontaktinformationen",
                            ahb_status="Kann",
                            segments=[
                                Segment(
                                    id="CTA",
                                    name="Ansprechpartner",
                                    number="00060",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_3139",
                                            name="Funktion des Ansprechpartners, Code",
                                            codes=[
                                                Code(
                                                    name="Informationskontakt",
                                                    description=None,
                                                    value="IC",
                                                    ahb_status="X",
                                                )
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C056",
                                            name="Kontaktangaben",
                                            data_elements=[
                                                DataElement(id="D_3412", name="Name vom Ansprechpartner", codes=[])
                                            ],
                                        ),
                                    ],
                                ),
                                Segment(
                                    id="COM",
                                    name="Kommunikationsverbindung",
                                    number="00061",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C076",
                                            name="Kommunikationsverbindung",
                                            data_elements=[
                                                DataElement(id="D_3148", name="Nummer / Adresse", codes=[]),
                                                DataElement(
                                                    id="D_3155",
                                                    name="Art des Kommunikationsmittels, Code",
                                                    codes=[
                                                        Code(
                                                            name="Elektronische Post",
                                                            description=None,
                                                            value="EM",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="Telefax",
                                                            description=None,
                                                            value="FX",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="Telefon",
                                                            description=None,
                                                            value="TE",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="weiteres Telefon",
                                                            description=None,
                                                            value="AJ",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="Handy",
                                                            description=None,
                                                            value="AL",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                            ],
                            segment_groups=[],
                        ),
                        SegmentGroup(
                            id="2",
                            name="MP-ID Empfänger",
                            ahb_status="Muss",
                            segments=[
                                Segment(
                                    id="NAD",
                                    name="MP-ID Empfänger",
                                    number="00062",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_3035",
                                            name="Beteiligter, Qualifier",
                                            codes=[
                                                Code(
                                                    name="Nachrichtenempfänger",
                                                    description=None,
                                                    value="MR",
                                                    ahb_status="X",
                                                )
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C082",
                                            name="Identifikation des Beteiligten",
                                            data_elements=[
                                                DataElement(id="D_3039", name="MP-ID", codes=[]),
                                                DataElement(
                                                    id="D_3055",
                                                    name="Verantwortliche Stelle für die Codepflege, Code",
                                                    codes=[
                                                        Code(name="GS1", description=None, value="9", ahb_status="X"),
                                                        Code(
                                                            name="DE, BDEW (Bundesverband der Energie- und Wasserwirtschaft e.V.)",
                                                            description=None,
                                                            value="293",
                                                            ahb_status="X",
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ],
                                )
                            ],
                            segment_groups=[],
                        ),
                        SegmentGroup(
                            id="5",
                            name="Vorgang",
                            ahb_status="Muss [523]",
                            segments=[
                                Segment(
                                    id="IDE",
                                    name="Vorgang",
                                    number="00063",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_7495",
                                            name="Objekt, Qualifier",
                                            codes=[
                                                Code(name="Transaktion", description=None, value="24", ahb_status="X")
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C206",
                                            name="Identifikationsnummer",
                                            data_elements=[DataElement(id="D_7402", name="Vorgangsnummer", codes=[])],
                                        ),
                                    ],
                                ),
                                Segment(
                                    id="LOC",
                                    name="Code der Definition",
                                    number="00064",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_3227",
                                            name="Ortsangabe, Qualifier",
                                            codes=[
                                                Code(
                                                    name="Code der Definition",
                                                    description=None,
                                                    value="Z09",
                                                    ahb_status="X",
                                                )
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C517",
                                            name="Ortsangabe",
                                            data_elements=[
                                                DataElement(id="D_3225", name="Code der Definition", codes=[])
                                            ],
                                        ),
                                    ],
                                ),
                                Segment(
                                    id="DTM",
                                    name="Gültigkeitsbeginn der ausgerollten Definition",
                                    number="00065",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C507",
                                            name="Datum/Uhrzeit/Zeitspanne",
                                            data_elements=[
                                                DataElement(
                                                    id="D_2005",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Funktion, Qualifier",
                                                    codes=[
                                                        Code(
                                                            name="Gültigkeitsbeginn",
                                                            description=None,
                                                            value="Z34",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                                DataElement(
                                                    id="D_2380",
                                                    name="Datum oder Uhrzeit oder Zeitspanne, Wert",
                                                    codes=[],
                                                ),
                                                DataElement(
                                                    id="D_2379",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Format, Code",
                                                    codes=[
                                                        Code(
                                                            name="CCYYMMDDHHMMZZZ",
                                                            description=None,
                                                            value="303",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                                Segment(
                                    id="DTM",
                                    name="Gültigkeitsende der ausgerollten Definition",
                                    number="00066",
                                    ahb_status="Muss [48]\r\nSoll [49] ∧ [37]",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C507",
                                            name="Datum/Uhrzeit/Zeitspanne",
                                            data_elements=[
                                                DataElement(
                                                    id="D_2005",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Funktion, Qualifier",
                                                    codes=[
                                                        Code(
                                                            name="Gültigkeitsende",
                                                            description=None,
                                                            value="Z35",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                                DataElement(
                                                    id="D_2380",
                                                    name="Datum oder Uhrzeit oder Zeitspanne, Wert",
                                                    codes=[],
                                                ),
                                                DataElement(
                                                    id="D_2379",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Format, Code",
                                                    codes=[
                                                        Code(
                                                            name="CCYYMMDDHHMMZZZ",
                                                            description=None,
                                                            value="303",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                                Segment(
                                    id="DTM",
                                    name="Versionsangabe",
                                    number="00067",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C507",
                                            name="Datum/Uhrzeit/Zeitspanne",
                                            data_elements=[
                                                DataElement(
                                                    id="D_2005",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Funktion, Qualifier",
                                                    codes=[
                                                        Code(
                                                            name="Fertigstellungsdatum/-zeit",
                                                            description=None,
                                                            value="293",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                                DataElement(
                                                    id="D_2380",
                                                    name="Datum oder Uhrzeit oder Zeitspanne, Wert",
                                                    codes=[],
                                                ),
                                                DataElement(
                                                    id="D_2379",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Format, Code",
                                                    codes=[
                                                        Code(
                                                            name="CCYYMMDDHHMMSSZZZ",
                                                            description=None,
                                                            value="304",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                            ],
                            segment_groups=[
                                SegmentGroup(
                                    id="6",
                                    name="Prüfidentifikator",
                                    ahb_status="Muss",
                                    segments=[
                                        Segment(
                                            id="RFF",
                                            name="Prüfidentifikator",
                                            number="00068",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElementGroup(
                                                    id="C_C506",
                                                    name="Referenz",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_1153",
                                                            name="Referenz, Qualifier",
                                                            codes=[
                                                                Code(
                                                                    name="Prüfidentifikator",
                                                                    description=None,
                                                                    value="Z13",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElement(
                                                            id="D_1154",
                                                            name="Referenz, Identifikation",
                                                            codes=[
                                                                Code(
                                                                    name="Ausgerollte Leistungskurvendefinition",
                                                                    description=None,
                                                                    value="25009",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                    ],
                                                )
                                            ],
                                        )
                                    ],
                                    segment_groups=[],
                                ),
                                SegmentGroup(
                                    id="6",
                                    name="Referenz auf Reklamation",
                                    ahb_status="Soll [26]",
                                    segments=[
                                        Segment(
                                            id="RFF",
                                            name="Referenz auf Reklamation",
                                            number="00069",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElementGroup(
                                                    id="C_C506",
                                                    name="Referenz",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_1153",
                                                            name="Referenz, Qualifier",
                                                            codes=[
                                                                Code(
                                                                    name="Beantragungsnummer",
                                                                    description=None,
                                                                    value="AGI",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElement(
                                                            id="D_1154", name="Referenz, Identifikation", codes=[]
                                                        ),
                                                    ],
                                                )
                                            ],
                                        )
                                    ],
                                    segment_groups=[],
                                ),
                                SegmentGroup(
                                    id="8",
                                    name="Leistungskurvendefinition",
                                    ahb_status="Muss [518] ∧ [519] ∧ ([520] ⊻ [521])",
                                    segments=[
                                        Segment(
                                            id="EQ",
                                            name="Leistungskurvendefinition",
                                            number="00070",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElement(
                                                    id="D_1229",
                                                    name="Handlung, Code",
                                                    codes=[
                                                        Code(
                                                            name="Ausgerollte Leistungskurvendefinition",
                                                            description=None,
                                                            value="Z74",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                )
                                            ],
                                        ),
                                        Segment(
                                            id="DTM",
                                            name="Leistungskurvenänderungszeitpunkt",
                                            number="00071",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElementGroup(
                                                    id="C_C507",
                                                    name="Datum/Uhrzeit/Zeitspanne",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_2005",
                                                            name="Datums- oder Uhrzeit- oder Zeitspannen-Funktion, Qualifier",
                                                            codes=[
                                                                Code(
                                                                    name="Leistungskurvenänderungszeitpunkt",
                                                                    description=None,
                                                                    value="Z45",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElement(
                                                            id="D_2380",
                                                            name="Datum oder Uhrzeit oder Zeitspanne, Wert",
                                                            codes=[],
                                                        ),
                                                        DataElement(
                                                            id="D_2379",
                                                            name="Datums- oder Uhrzeit- oder Zeitspannen-Format, Code",
                                                            codes=[
                                                                Code(
                                                                    name="CCYYMMDDHHMMZZZ",
                                                                    description=None,
                                                                    value="303",
                                                                    ahb_status="X [50] ∧ [528]",
                                                                ),
                                                                Code(
                                                                    name="HHMM",
                                                                    description=None,
                                                                    value="401",
                                                                    ahb_status="X [50] ∧ [527]",
                                                                ),
                                                            ],
                                                        ),
                                                    ],
                                                )
                                            ],
                                        ),
                                    ],
                                    segment_groups=[
                                        SegmentGroup(
                                            id="9",
                                            name="Leistungskurvendefinition",
                                            ahb_status="Muss",
                                            segments=[
                                                Segment(
                                                    id="CCI",
                                                    name="Code der Leistungskurvendefinition",
                                                    number="00072",
                                                    ahb_status=None,
                                                    data_elements=[
                                                        DataElement(id="D_7059", name="Klassentyp, Code", codes=[]),
                                                        DataElementGroup(
                                                            id="C_C240",
                                                            name="Merkmalsbeschreibung",
                                                            data_elements=[
                                                                DataElement(
                                                                    id="D_7037",
                                                                    name="Code der Leistungskurvendefinition",
                                                                    codes=[],
                                                                )
                                                            ],
                                                        ),
                                                    ],
                                                )
                                            ],
                                            segment_groups=[],
                                        ),
                                        SegmentGroup(
                                            id="11",
                                            name="oberer Schwellwert",
                                            ahb_status="Muss",
                                            segments=[
                                                Segment(
                                                    id="QTY",
                                                    name="oberer Schwellwert",
                                                    number="00073",
                                                    ahb_status="Muss",
                                                    data_elements=[
                                                        DataElementGroup(
                                                            id="C_C186",
                                                            name="Mengenangaben",
                                                            data_elements=[
                                                                DataElement(
                                                                    id="D_6063",
                                                                    name="Menge, Qualifier",
                                                                    codes=[
                                                                        Code(
                                                                            name="oberer Schwellwert",
                                                                            description=None,
                                                                            value="Z40",
                                                                            ahb_status="X",
                                                                        )
                                                                    ],
                                                                ),
                                                                DataElement(
                                                                    id="D_6060", name="Mengenangabe in %", codes=[]
                                                                ),
                                                                DataElement(
                                                                    id="D_6411",
                                                                    name="Maßeinheit, Code",
                                                                    codes=[
                                                                        Code(
                                                                            name="Prozent",
                                                                            description=None,
                                                                            value="P1",
                                                                            ahb_status="X",
                                                                        )
                                                                    ],
                                                                ),
                                                            ],
                                                        )
                                                    ],
                                                )
                                            ],
                                            segment_groups=[],
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                )
            ],
        ),
        Anwendungsfall(
            pruefidentifikator="25008",
            beschreibung="Übermittlung einer ausgerollten Schaltzeitdefinition",
            kommunikation_von="NB an LF / MSB\r\nLF an NB, MSB",
            format="UTILTS",
            segments=[
                Segment(
                    id="UNH",
                    name="Nachrichten-Kopfsegment",
                    number="00075",
                    ahb_status="Muss",
                    data_elements=[
                        DataElement(id="D_0062", name="Nachrichten-Referenznummer", codes=[]),
                        DataElementGroup(
                            id="C_S009",
                            name="Nachrichten-Kennung",
                            data_elements=[
                                DataElement(
                                    id="D_0065",
                                    name="Nachrichtentyp-Kennung",
                                    codes=[
                                        Code(
                                            name="Netznutzungszeiten-Nachricht",
                                            description=None,
                                            value="UTILTS",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                                DataElement(
                                    id="D_0052",
                                    name="Versionsnummer des Nachrichtentyps",
                                    codes=[Code(name="Entwurfs-Version", description=None, value="D", ahb_status="X")],
                                ),
                                DataElement(
                                    id="D_0054",
                                    name="Freigabenummer des Nachrichtentyps",
                                    codes=[
                                        Code(name="Ausgabe 2018 - A", description=None, value="18A", ahb_status="X")
                                    ],
                                ),
                                DataElement(
                                    id="D_0051",
                                    name="Verwaltende Organisation",
                                    codes=[Code(name="UN/CEFACT", description=None, value="UN", ahb_status="X")],
                                ),
                                DataElement(
                                    id="D_0057",
                                    name="Anwendungscode der zuständigen Organisation",
                                    codes=[
                                        Code(
                                            name="Versionsnummer der zugrundeliegenden BDEW-Nachrichtenbeschreibung",
                                            description=None,
                                            value="1.1c",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                Segment(
                    id="BGM",
                    name="Beginn der Nachricht",
                    number="00076",
                    ahb_status="Muss",
                    data_elements=[
                        DataElementGroup(
                            id="C_C002",
                            name="Dokumenten-/Nachrichtenname",
                            data_elements=[
                                DataElement(
                                    id="D_1001",
                                    name="Dokumentenname, Code",
                                    codes=[
                                        Code(
                                            name="Ausgerollte Schaltzeitdefinition",
                                            description=None,
                                            value="Z80",
                                            ahb_status="X",
                                        )
                                    ],
                                )
                            ],
                        ),
                        DataElementGroup(
                            id="C_C106",
                            name="Dokumenten-/Nachrichten-Identifikation",
                            data_elements=[DataElement(id="D_1004", name="Dokumentennummer", codes=[])],
                        ),
                    ],
                ),
                Segment(
                    id="DTM",
                    name="Nachrichtendatum",
                    number="00077",
                    ahb_status="Muss",
                    data_elements=[
                        DataElementGroup(
                            id="C_C507",
                            name="Datum/Uhrzeit/Zeitspanne",
                            data_elements=[
                                DataElement(
                                    id="D_2005",
                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Funktion, Qualifier",
                                    codes=[
                                        Code(
                                            name="Dokumenten-/Nachrichtendatum/-zeit",
                                            description=None,
                                            value="137",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                                DataElement(id="D_2380", name="Datum oder Uhrzeit oder Zeitspanne, Wert", codes=[]),
                                DataElement(
                                    id="D_2379",
                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Format, Code",
                                    codes=[Code(name="CCYYMMDDHHMMZZZ", description=None, value="303", ahb_status="X")],
                                ),
                            ],
                        )
                    ],
                ),
                Segment(
                    id="UNT",
                    name="Nachrichten-Endesegment",
                    number="00093",
                    ahb_status="Muss",
                    data_elements=[
                        DataElement(id="D_0074", name="Anzahl der Segmente in einer Nachricht", codes=[]),
                        DataElement(id="D_0062", name="Nachrichten-Referenznummer", codes=[]),
                    ],
                ),
            ],
            segment_groups=[
                SegmentGroup(
                    id="2",
                    name="MP-ID Absender",
                    ahb_status="Muss",
                    segments=[
                        Segment(
                            id="NAD",
                            name="MP-ID Absender",
                            number="00078",
                            ahb_status="Muss",
                            data_elements=[
                                DataElement(
                                    id="D_3035",
                                    name="Beteiligter, Qualifier",
                                    codes=[
                                        Code(
                                            name="Dokumenten-/Nachrichtenaussteller bzw. -absender",
                                            description=None,
                                            value="MS",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                                DataElementGroup(
                                    id="C_C082",
                                    name="Identifikation des Beteiligten",
                                    data_elements=[
                                        DataElement(id="D_3039", name="MP-ID", codes=[]),
                                        DataElement(
                                            id="D_3055",
                                            name="Verantwortliche Stelle für die Codepflege, Code",
                                            codes=[
                                                Code(name="GS1", description=None, value="9", ahb_status="X"),
                                                Code(
                                                    name="DE, BDEW (Bundesverband der Energie- und Wasserwirtschaft e.V.)",
                                                    description=None,
                                                    value="293",
                                                    ahb_status="X",
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        )
                    ],
                    segment_groups=[
                        SegmentGroup(
                            id="3",
                            name="Kontaktinformationen",
                            ahb_status="Kann",
                            segments=[
                                Segment(
                                    id="CTA",
                                    name="Ansprechpartner",
                                    number="00079",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_3139",
                                            name="Funktion des Ansprechpartners, Code",
                                            codes=[
                                                Code(
                                                    name="Informationskontakt",
                                                    description=None,
                                                    value="IC",
                                                    ahb_status="X",
                                                )
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C056",
                                            name="Kontaktangaben",
                                            data_elements=[
                                                DataElement(id="D_3412", name="Name vom Ansprechpartner", codes=[])
                                            ],
                                        ),
                                    ],
                                ),
                                Segment(
                                    id="COM",
                                    name="Kommunikationsverbindung",
                                    number="00080",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C076",
                                            name="Kommunikationsverbindung",
                                            data_elements=[
                                                DataElement(id="D_3148", name="Nummer / Adresse", codes=[]),
                                                DataElement(
                                                    id="D_3155",
                                                    name="Art des Kommunikationsmittels, Code",
                                                    codes=[
                                                        Code(
                                                            name="Elektronische Post",
                                                            description=None,
                                                            value="EM",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="Telefax",
                                                            description=None,
                                                            value="FX",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="Telefon",
                                                            description=None,
                                                            value="TE",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="weiteres Telefon",
                                                            description=None,
                                                            value="AJ",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="Handy",
                                                            description=None,
                                                            value="AL",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                            ],
                            segment_groups=[],
                        ),
                        SegmentGroup(
                            id="2",
                            name="MP-ID Empfänger",
                            ahb_status="Muss",
                            segments=[
                                Segment(
                                    id="NAD",
                                    name="MP-ID Empfänger",
                                    number="00081",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_3035",
                                            name="Beteiligter, Qualifier",
                                            codes=[
                                                Code(
                                                    name="Nachrichtenempfänger",
                                                    description=None,
                                                    value="MR",
                                                    ahb_status="X",
                                                )
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C082",
                                            name="Identifikation des Beteiligten",
                                            data_elements=[
                                                DataElement(id="D_3039", name="MP-ID", codes=[]),
                                                DataElement(
                                                    id="D_3055",
                                                    name="Verantwortliche Stelle für die Codepflege, Code",
                                                    codes=[
                                                        Code(name="GS1", description=None, value="9", ahb_status="X"),
                                                        Code(
                                                            name="DE, BDEW (Bundesverband der Energie- und Wasserwirtschaft e.V.)",
                                                            description=None,
                                                            value="293",
                                                            ahb_status="X",
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ],
                                )
                            ],
                            segment_groups=[],
                        ),
                        SegmentGroup(
                            id="5",
                            name="Vorgang",
                            ahb_status="Muss [522]",
                            segments=[
                                Segment(
                                    id="IDE",
                                    name="Vorgang",
                                    number="00082",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_7495",
                                            name="Objekt, Qualifier",
                                            codes=[
                                                Code(name="Transaktion", description=None, value="24", ahb_status="X")
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C206",
                                            name="Identifikationsnummer",
                                            data_elements=[DataElement(id="D_7402", name="Vorgangsnummer", codes=[])],
                                        ),
                                    ],
                                ),
                                Segment(
                                    id="LOC",
                                    name="Code der Definition",
                                    number="00083",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_3227",
                                            name="Ortsangabe, Qualifier",
                                            codes=[
                                                Code(
                                                    name="Code der Definition",
                                                    description=None,
                                                    value="Z09",
                                                    ahb_status="X",
                                                )
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C517",
                                            name="Ortsangabe",
                                            data_elements=[
                                                DataElement(id="D_3225", name="Code der Definition", codes=[])
                                            ],
                                        ),
                                    ],
                                ),
                                Segment(
                                    id="DTM",
                                    name="Gültigkeitsbeginn der ausgerollten Definition",
                                    number="00084",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C507",
                                            name="Datum/Uhrzeit/Zeitspanne",
                                            data_elements=[
                                                DataElement(
                                                    id="D_2005",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Funktion, Qualifier",
                                                    codes=[
                                                        Code(
                                                            name="Gültigkeitsbeginn",
                                                            description=None,
                                                            value="Z34",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                                DataElement(
                                                    id="D_2380",
                                                    name="Datum oder Uhrzeit oder Zeitspanne, Wert",
                                                    codes=[],
                                                ),
                                                DataElement(
                                                    id="D_2379",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Format, Code",
                                                    codes=[
                                                        Code(
                                                            name="CCYYMMDDHHMMZZZ",
                                                            description=None,
                                                            value="303",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                                Segment(
                                    id="DTM",
                                    name="Gültigkeitsende der ausgerollten Definition",
                                    number="00085",
                                    ahb_status="Muss [46]\r\nSoll [47] ∧ [37]",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C507",
                                            name="Datum/Uhrzeit/Zeitspanne",
                                            data_elements=[
                                                DataElement(
                                                    id="D_2005",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Funktion, Qualifier",
                                                    codes=[
                                                        Code(
                                                            name="Gültigkeitsende",
                                                            description=None,
                                                            value="Z35",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                                DataElement(
                                                    id="D_2380",
                                                    name="Datum oder Uhrzeit oder Zeitspanne, Wert",
                                                    codes=[],
                                                ),
                                                DataElement(
                                                    id="D_2379",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Format, Code",
                                                    codes=[
                                                        Code(
                                                            name="CCYYMMDDHHMMZZZ",
                                                            description=None,
                                                            value="303",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                                Segment(
                                    id="DTM",
                                    name="Versionsangabe",
                                    number="00086",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C507",
                                            name="Datum/Uhrzeit/Zeitspanne",
                                            data_elements=[
                                                DataElement(
                                                    id="D_2005",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Funktion, Qualifier",
                                                    codes=[
                                                        Code(
                                                            name="Fertigstellungsdatum/-zeit",
                                                            description=None,
                                                            value="293",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                                DataElement(
                                                    id="D_2380",
                                                    name="Datum oder Uhrzeit oder Zeitspanne, Wert",
                                                    codes=[],
                                                ),
                                                DataElement(
                                                    id="D_2379",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Format, Code",
                                                    codes=[
                                                        Code(
                                                            name="CCYYMMDDHHMMSSZZZ",
                                                            description=None,
                                                            value="304",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                            ],
                            segment_groups=[
                                SegmentGroup(
                                    id="6",
                                    name="Prüfidentifikator",
                                    ahb_status="Muss",
                                    segments=[
                                        Segment(
                                            id="RFF",
                                            name="Prüfidentifikator",
                                            number="00087",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElementGroup(
                                                    id="C_C506",
                                                    name="Referenz",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_1153",
                                                            name="Referenz, Qualifier",
                                                            codes=[
                                                                Code(
                                                                    name="Prüfidentifikator",
                                                                    description=None,
                                                                    value="Z13",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElement(
                                                            id="D_1154",
                                                            name="Referenz, Identifikation",
                                                            codes=[
                                                                Code(
                                                                    name="Ausgerollte Schaltzeitdefinition",
                                                                    description=None,
                                                                    value="25008",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                    ],
                                                )
                                            ],
                                        )
                                    ],
                                    segment_groups=[],
                                ),
                                SegmentGroup(
                                    id="6",
                                    name="Referenz auf Reklamation",
                                    ahb_status="Soll [26]",
                                    segments=[
                                        Segment(
                                            id="RFF",
                                            name="Referenz auf Reklamation",
                                            number="00088",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElementGroup(
                                                    id="C_C506",
                                                    name="Referenz",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_1153",
                                                            name="Referenz, Qualifier",
                                                            codes=[
                                                                Code(
                                                                    name="Beantragungsnummer",
                                                                    description=None,
                                                                    value="AGI",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElement(
                                                            id="D_1154", name="Referenz, Identifikation", codes=[]
                                                        ),
                                                    ],
                                                )
                                            ],
                                        )
                                    ],
                                    segment_groups=[],
                                ),
                                SegmentGroup(
                                    id="8",
                                    name="Schaltzeitdefinition",
                                    ahb_status="Muss [514] ∧ [515] ∧ ([516] ⊻ [517])",
                                    segments=[
                                        Segment(
                                            id="EQ",
                                            name="Schaltzeitdefinition",
                                            number="00089",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElement(
                                                    id="D_1229",
                                                    name="Handlung, Code",
                                                    codes=[
                                                        Code(
                                                            name="Ausgerollte Schaltzeitdefinition",
                                                            description=None,
                                                            value="Z73",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                )
                                            ],
                                        ),
                                        Segment(
                                            id="DTM",
                                            name="Schaltzeitänderungszeitpunkt",
                                            number="00090",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElementGroup(
                                                    id="C_C507",
                                                    name="Datum/Uhrzeit/Zeitspanne",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_2005",
                                                            name="Datums- oder Uhrzeit- oder Zeitspannen-Funktion, Qualifier",
                                                            codes=[
                                                                Code(
                                                                    name="Schaltzeitänderungszeitpunkt",
                                                                    description=None,
                                                                    value="Z44",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElement(
                                                            id="D_2380",
                                                            name="Datum oder Uhrzeit oder Zeitspanne, Wert",
                                                            codes=[],
                                                        ),
                                                        DataElement(
                                                            id="D_2379",
                                                            name="Datums- oder Uhrzeit- oder Zeitspannen-Format, Code",
                                                            codes=[
                                                                Code(
                                                                    name="CCYYMMDDHHMMZZZ",
                                                                    description=None,
                                                                    value="303",
                                                                    ahb_status="X [50] ∧ [528]",
                                                                ),
                                                                Code(
                                                                    name="HHMM",
                                                                    description=None,
                                                                    value="401",
                                                                    ahb_status="X [50] ∧ [527]",
                                                                ),
                                                            ],
                                                        ),
                                                    ],
                                                )
                                            ],
                                        ),
                                    ],
                                    segment_groups=[
                                        SegmentGroup(
                                            id="9",
                                            name="Schaltzeitdefinition",
                                            ahb_status="Muss",
                                            segments=[
                                                Segment(
                                                    id="CCI",
                                                    name="Code der Schaltzeitdefinition",
                                                    number="00091",
                                                    ahb_status=None,
                                                    data_elements=[
                                                        DataElement(id="D_7059", name="Klassentyp, Code", codes=[]),
                                                        DataElementGroup(
                                                            id="C_C240",
                                                            name="Merkmalsbeschreibung",
                                                            data_elements=[
                                                                DataElement(
                                                                    id="D_7037",
                                                                    name="Code der Schaltzeitdefinition",
                                                                    codes=[],
                                                                )
                                                            ],
                                                        ),
                                                    ],
                                                )
                                            ],
                                            segment_groups=[],
                                        ),
                                        SegmentGroup(
                                            id="9",
                                            name="Schalthandlung an der Lokation",
                                            ahb_status="Muss",
                                            segments=[
                                                Segment(
                                                    id="CCI",
                                                    name="Schalthandlung an der Lokation",
                                                    number="00092",
                                                    ahb_status="Muss",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_7059",
                                                            name="Klassentyp, Code",
                                                            codes=[
                                                                Code(
                                                                    name="Schalthandlung",
                                                                    description=None,
                                                                    value="Z58",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElementGroup(
                                                            id="C_C240",
                                                            name="Merkmalsbeschreibung",
                                                            data_elements=[
                                                                DataElement(
                                                                    id="D_7037",
                                                                    name="Merkmal, Code",
                                                                    codes=[
                                                                        Code(
                                                                            name="Leistung an der Lokation an",
                                                                            description=None,
                                                                            value="ZF4",
                                                                            ahb_status="X",
                                                                        ),
                                                                        Code(
                                                                            name="Leistung an der Lokation aus",
                                                                            description=None,
                                                                            value="ZF5",
                                                                            ahb_status="X",
                                                                        ),
                                                                    ],
                                                                )
                                                            ],
                                                        ),
                                                    ],
                                                )
                                            ],
                                            segment_groups=[],
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                )
            ],
        ),
        Anwendungsfall(
            pruefidentifikator="25005",
            beschreibung="Übermittlung einer ausgerollten Zählzeitdefinition",
            kommunikation_von="NB an LF / MSB\r\nLF an MSB",
            format="UTILTS",
            segments=[
                Segment(
                    id="UNH",
                    name="Nachrichten-Kopfsegment",
                    number="00094",
                    ahb_status="Muss",
                    data_elements=[
                        DataElement(id="D_0062", name="Nachrichten-Referenznummer", codes=[]),
                        DataElementGroup(
                            id="C_S009",
                            name="Nachrichten-Kennung",
                            data_elements=[
                                DataElement(
                                    id="D_0065",
                                    name="Nachrichtentyp-Kennung",
                                    codes=[
                                        Code(
                                            name="Netznutzungszeiten-Nachricht",
                                            description=None,
                                            value="UTILTS",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                                DataElement(
                                    id="D_0052",
                                    name="Versionsnummer des Nachrichtentyps",
                                    codes=[Code(name="Entwurfs-Version", description=None, value="D", ahb_status="X")],
                                ),
                                DataElement(
                                    id="D_0054",
                                    name="Freigabenummer des Nachrichtentyps",
                                    codes=[
                                        Code(name="Ausgabe 2018 - A", description=None, value="18A", ahb_status="X")
                                    ],
                                ),
                                DataElement(
                                    id="D_0051",
                                    name="Verwaltende Organisation",
                                    codes=[Code(name="UN/CEFACT", description=None, value="UN", ahb_status="X")],
                                ),
                                DataElement(
                                    id="D_0057",
                                    name="Anwendungscode der zuständigen Organisation",
                                    codes=[
                                        Code(
                                            name="Versionsnummer der zugrundeliegenden BDEW-Nachrichtenbeschreibung",
                                            description=None,
                                            value="1.1c",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                Segment(
                    id="BGM",
                    name="Beginn der Nachricht",
                    number="00095",
                    ahb_status="Muss",
                    data_elements=[
                        DataElementGroup(
                            id="C_C002",
                            name="Dokumenten-/Nachrichtenname",
                            data_elements=[
                                DataElement(
                                    id="D_1001",
                                    name="Dokumentenname, Code",
                                    codes=[
                                        Code(
                                            name="Ausgerollte Zählzeitdefinition",
                                            description=None,
                                            value="Z59",
                                            ahb_status="X",
                                        )
                                    ],
                                )
                            ],
                        ),
                        DataElementGroup(
                            id="C_C106",
                            name="Dokumenten-/Nachrichten-Identifikation",
                            data_elements=[DataElement(id="D_1004", name="Dokumentennummer", codes=[])],
                        ),
                    ],
                ),
                Segment(
                    id="DTM",
                    name="Nachrichtendatum",
                    number="00096",
                    ahb_status="Muss",
                    data_elements=[
                        DataElementGroup(
                            id="C_C507",
                            name="Datum/Uhrzeit/Zeitspanne",
                            data_elements=[
                                DataElement(
                                    id="D_2005",
                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Funktion, Qualifier",
                                    codes=[
                                        Code(
                                            name="Dokumenten-/Nachrichtendatum/-zeit",
                                            description=None,
                                            value="137",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                                DataElement(id="D_2380", name="Datum oder Uhrzeit oder Zeitspanne, Wert", codes=[]),
                                DataElement(
                                    id="D_2379",
                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Format, Code",
                                    codes=[Code(name="CCYYMMDDHHMMZZZ", description=None, value="303", ahb_status="X")],
                                ),
                            ],
                        )
                    ],
                ),
                Segment(
                    id="UNT",
                    name="Nachrichten-Endesegment",
                    number="00112",
                    ahb_status="Muss",
                    data_elements=[
                        DataElement(id="D_0074", name="Anzahl der Segmente in einer Nachricht", codes=[]),
                        DataElement(id="D_0062", name="Nachrichten-Referenznummer", codes=[]),
                    ],
                ),
            ],
            segment_groups=[
                SegmentGroup(
                    id="2",
                    name="MP-ID Absender",
                    ahb_status="Muss",
                    segments=[
                        Segment(
                            id="NAD",
                            name="MP-ID Absender",
                            number="00097",
                            ahb_status="Muss",
                            data_elements=[
                                DataElement(
                                    id="D_3035",
                                    name="Beteiligter, Qualifier",
                                    codes=[
                                        Code(
                                            name="Dokumenten-/Nachrichtenaussteller bzw. -absender",
                                            description=None,
                                            value="MS",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                                DataElementGroup(
                                    id="C_C082",
                                    name="Identifikation des Beteiligten",
                                    data_elements=[
                                        DataElement(id="D_3039", name="MP-ID", codes=[]),
                                        DataElement(
                                            id="D_3055",
                                            name="Verantwortliche Stelle für die Codepflege, Code",
                                            codes=[
                                                Code(name="GS1", description=None, value="9", ahb_status="X"),
                                                Code(
                                                    name="DE, BDEW (Bundesverband der Energie- und Wasserwirtschaft e.V.)",
                                                    description=None,
                                                    value="293",
                                                    ahb_status="X",
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        )
                    ],
                    segment_groups=[
                        SegmentGroup(
                            id="3",
                            name="Kontaktinformationen",
                            ahb_status="Kann",
                            segments=[
                                Segment(
                                    id="CTA",
                                    name="Ansprechpartner",
                                    number="00098",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_3139",
                                            name="Funktion des Ansprechpartners, Code",
                                            codes=[
                                                Code(
                                                    name="Informationskontakt",
                                                    description=None,
                                                    value="IC",
                                                    ahb_status="X",
                                                )
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C056",
                                            name="Kontaktangaben",
                                            data_elements=[
                                                DataElement(id="D_3412", name="Name vom Ansprechpartner", codes=[])
                                            ],
                                        ),
                                    ],
                                ),
                                Segment(
                                    id="COM",
                                    name="Kommunikationsverbindung",
                                    number="00099",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C076",
                                            name="Kommunikationsverbindung",
                                            data_elements=[
                                                DataElement(id="D_3148", name="Nummer / Adresse", codes=[]),
                                                DataElement(
                                                    id="D_3155",
                                                    name="Art des Kommunikationsmittels, Code",
                                                    codes=[
                                                        Code(
                                                            name="Elektronische Post",
                                                            description=None,
                                                            value="EM",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="Telefax",
                                                            description=None,
                                                            value="FX",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="Telefon",
                                                            description=None,
                                                            value="TE",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="weiteres Telefon",
                                                            description=None,
                                                            value="AJ",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="Handy",
                                                            description=None,
                                                            value="AL",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                            ],
                            segment_groups=[],
                        ),
                        SegmentGroup(
                            id="2",
                            name="MP-ID Empfänger",
                            ahb_status="Muss",
                            segments=[
                                Segment(
                                    id="NAD",
                                    name="MP-ID Empfänger",
                                    number="00100",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_3035",
                                            name="Beteiligter, Qualifier",
                                            codes=[
                                                Code(
                                                    name="Nachrichtenempfänger",
                                                    description=None,
                                                    value="MR",
                                                    ahb_status="X",
                                                )
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C082",
                                            name="Identifikation des Beteiligten",
                                            data_elements=[
                                                DataElement(id="D_3039", name="MP-ID", codes=[]),
                                                DataElement(
                                                    id="D_3055",
                                                    name="Verantwortliche Stelle für die Codepflege, Code",
                                                    codes=[
                                                        Code(name="GS1", description=None, value="9", ahb_status="X"),
                                                        Code(
                                                            name="DE, BDEW (Bundesverband der Energie- und Wasserwirtschaft e.V.)",
                                                            description=None,
                                                            value="293",
                                                            ahb_status="X",
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ],
                                )
                            ],
                            segment_groups=[],
                        ),
                        SegmentGroup(
                            id="5",
                            name="Vorgang",
                            ahb_status="Muss [505]",
                            segments=[
                                Segment(
                                    id="IDE",
                                    name="Vorgang",
                                    number="00101",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_7495",
                                            name="Objekt, Qualifier",
                                            codes=[
                                                Code(name="Transaktion", description=None, value="24", ahb_status="X")
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C206",
                                            name="Identifikationsnummer",
                                            data_elements=[DataElement(id="D_7402", name="Vorgangsnummer", codes=[])],
                                        ),
                                    ],
                                ),
                                Segment(
                                    id="LOC",
                                    name="Code der Definition",
                                    number="00102",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_3227",
                                            name="Ortsangabe, Qualifier",
                                            codes=[
                                                Code(
                                                    name="Code der Definition",
                                                    description=None,
                                                    value="Z09",
                                                    ahb_status="X",
                                                )
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C517",
                                            name="Ortsangabe",
                                            data_elements=[
                                                DataElement(id="D_3225", name="Code der Definition", codes=[])
                                            ],
                                        ),
                                    ],
                                ),
                                Segment(
                                    id="DTM",
                                    name="Gültigkeitsbeginn der ausgerollten Definition",
                                    number="00103",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C507",
                                            name="Datum/Uhrzeit/Zeitspanne",
                                            data_elements=[
                                                DataElement(
                                                    id="D_2005",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Funktion, Qualifier",
                                                    codes=[
                                                        Code(
                                                            name="Gültigkeitsbeginn",
                                                            description=None,
                                                            value="Z34",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                                DataElement(
                                                    id="D_2380",
                                                    name="Datum oder Uhrzeit oder Zeitspanne, Wert",
                                                    codes=[],
                                                ),
                                                DataElement(
                                                    id="D_2379",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Format, Code",
                                                    codes=[
                                                        Code(
                                                            name="CCYYMMDDHHMMZZZ",
                                                            description=None,
                                                            value="303",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                                Segment(
                                    id="DTM",
                                    name="Gültigkeitsende der ausgerollten Definition",
                                    number="00104",
                                    ahb_status="Muss [29]\r\nSoll [36] ∧ [37]",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C507",
                                            name="Datum/Uhrzeit/Zeitspanne",
                                            data_elements=[
                                                DataElement(
                                                    id="D_2005",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Funktion, Qualifier",
                                                    codes=[
                                                        Code(
                                                            name="Gültigkeitsende",
                                                            description=None,
                                                            value="Z35",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                                DataElement(
                                                    id="D_2380",
                                                    name="Datum oder Uhrzeit oder Zeitspanne, Wert",
                                                    codes=[],
                                                ),
                                                DataElement(
                                                    id="D_2379",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Format, Code",
                                                    codes=[
                                                        Code(
                                                            name="CCYYMMDDHHMMZZZ",
                                                            description=None,
                                                            value="303",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                                Segment(
                                    id="DTM",
                                    name="Versionsangabe",
                                    number="00105",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C507",
                                            name="Datum/Uhrzeit/Zeitspanne",
                                            data_elements=[
                                                DataElement(
                                                    id="D_2005",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Funktion, Qualifier",
                                                    codes=[
                                                        Code(
                                                            name="Fertigstellungsdatum/-zeit",
                                                            description=None,
                                                            value="293",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                                DataElement(
                                                    id="D_2380",
                                                    name="Datum oder Uhrzeit oder Zeitspanne, Wert",
                                                    codes=[],
                                                ),
                                                DataElement(
                                                    id="D_2379",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Format, Code",
                                                    codes=[
                                                        Code(
                                                            name="CCYYMMDDHHMMSSZZZ",
                                                            description=None,
                                                            value="304",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                            ],
                            segment_groups=[
                                SegmentGroup(
                                    id="6",
                                    name="Prüfidentifikator",
                                    ahb_status="Muss",
                                    segments=[
                                        Segment(
                                            id="RFF",
                                            name="Prüfidentifikator",
                                            number="00106",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElementGroup(
                                                    id="C_C506",
                                                    name="Referenz",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_1153",
                                                            name="Referenz, Qualifier",
                                                            codes=[
                                                                Code(
                                                                    name="Prüfidentifikator",
                                                                    description=None,
                                                                    value="Z13",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElement(
                                                            id="D_1154",
                                                            name="Referenz, Identifikation",
                                                            codes=[
                                                                Code(
                                                                    name="Ausgerollte Zählzeitdefinition",
                                                                    description=None,
                                                                    value="25005",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                    ],
                                                )
                                            ],
                                        )
                                    ],
                                    segment_groups=[],
                                ),
                                SegmentGroup(
                                    id="6",
                                    name="Referenz auf Reklamation",
                                    ahb_status="Soll [26]",
                                    segments=[
                                        Segment(
                                            id="RFF",
                                            name="Referenz auf Reklamation",
                                            number="00107",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElementGroup(
                                                    id="C_C506",
                                                    name="Referenz",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_1153",
                                                            name="Referenz, Qualifier",
                                                            codes=[
                                                                Code(
                                                                    name="Beantragungsnummer",
                                                                    description=None,
                                                                    value="AGI",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElement(
                                                            id="D_1154", name="Referenz, Identifikation", codes=[]
                                                        ),
                                                    ],
                                                )
                                            ],
                                        )
                                    ],
                                    segment_groups=[],
                                ),
                                SegmentGroup(
                                    id="8",
                                    name="Zählzeitdefinition",
                                    ahb_status="Muss [510] ∧ [511] ∧ ([512] ⊻ [513])",
                                    segments=[
                                        Segment(
                                            id="EQ",
                                            name="Zählzeitdefinition",
                                            number="00108",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElement(
                                                    id="D_1229",
                                                    name="Handlung, Code",
                                                    codes=[
                                                        Code(
                                                            name="Ausgerollte Zählzeitdefinition",
                                                            description=None,
                                                            value="Z43",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                )
                                            ],
                                        ),
                                        Segment(
                                            id="DTM",
                                            name="Zählzeitänderungszeitpunkt",
                                            number="00109",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElementGroup(
                                                    id="C_C507",
                                                    name="Datum/Uhrzeit/Zeitspanne",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_2005",
                                                            name="Datums- oder Uhrzeit- oder Zeitspannen-Funktion, Qualifier",
                                                            codes=[
                                                                Code(
                                                                    name="Zählzeitänderungszeitpunkt",
                                                                    description=None,
                                                                    value="Z33",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElement(
                                                            id="D_2380",
                                                            name="Datum oder Uhrzeit oder Zeitspanne, Wert",
                                                            codes=[],
                                                        ),
                                                        DataElement(
                                                            id="D_2379",
                                                            name="Datums- oder Uhrzeit- oder Zeitspannen-Format, Code",
                                                            codes=[
                                                                Code(
                                                                    name="CCYYMMDDHHMMZZZ",
                                                                    description=None,
                                                                    value="303",
                                                                    ahb_status="X [50] ∧ [528]",
                                                                ),
                                                                Code(
                                                                    name="HHMM",
                                                                    description=None,
                                                                    value="401",
                                                                    ahb_status="X [50] ∧ [527]",
                                                                ),
                                                            ],
                                                        ),
                                                    ],
                                                )
                                            ],
                                        ),
                                        Segment(
                                            id="RFF",
                                            name="Zählendes Register",
                                            number="00110",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElementGroup(
                                                    id="C_C506",
                                                    name="Referenz",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_1153",
                                                            name="Referenz, Qualifier",
                                                            codes=[
                                                                Code(
                                                                    name="Code des zählenden Registers",
                                                                    description=None,
                                                                    value="Z28",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElement(
                                                            id="D_1154", name="Code des zählenden Registers", codes=[]
                                                        ),
                                                    ],
                                                )
                                            ],
                                        ),
                                    ],
                                    segment_groups=[
                                        SegmentGroup(
                                            id="9",
                                            name="Zählzeitdefinition",
                                            ahb_status="Muss",
                                            segments=[
                                                Segment(
                                                    id="CCI",
                                                    name="Code der Zählzeitdefinition",
                                                    number="00111",
                                                    ahb_status=None,
                                                    data_elements=[
                                                        DataElement(id="D_7059", name="Klassentyp, Code", codes=[]),
                                                        DataElementGroup(
                                                            id="C_C240",
                                                            name="Merkmalsbeschreibung",
                                                            data_elements=[
                                                                DataElement(
                                                                    id="D_7037",
                                                                    name="Code der Zählzeitdefinition",
                                                                    codes=[],
                                                                )
                                                            ],
                                                        ),
                                                    ],
                                                )
                                            ],
                                            segment_groups=[],
                                        )
                                    ],
                                ),
                            ],
                        ),
                    ],
                )
            ],
        ),
        Anwendungsfall(
            pruefidentifikator="25007",
            beschreibung="Übermittlung Übersicht Leistungskurvendefinitionen",
            kommunikation_von="NB an LF / MSB\r\nLF an NB, MSB",
            format="UTILTS",
            segments=[
                Segment(
                    id="UNH",
                    name="Nachrichten-Kopfsegment",
                    number="00113",
                    ahb_status="Muss",
                    data_elements=[
                        DataElement(id="D_0062", name="Nachrichten-Referenznummer", codes=[]),
                        DataElementGroup(
                            id="C_S009",
                            name="Nachrichten-Kennung",
                            data_elements=[
                                DataElement(
                                    id="D_0065",
                                    name="Nachrichtentyp-Kennung",
                                    codes=[
                                        Code(
                                            name="Netznutzungszeiten-Nachricht",
                                            description=None,
                                            value="UTILTS",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                                DataElement(
                                    id="D_0052",
                                    name="Versionsnummer des Nachrichtentyps",
                                    codes=[Code(name="Entwurfs-Version", description=None, value="D", ahb_status="X")],
                                ),
                                DataElement(
                                    id="D_0054",
                                    name="Freigabenummer des Nachrichtentyps",
                                    codes=[
                                        Code(name="Ausgabe 2018 - A", description=None, value="18A", ahb_status="X")
                                    ],
                                ),
                                DataElement(
                                    id="D_0051",
                                    name="Verwaltende Organisation",
                                    codes=[Code(name="UN/CEFACT", description=None, value="UN", ahb_status="X")],
                                ),
                                DataElement(
                                    id="D_0057",
                                    name="Anwendungscode der zuständigen Organisation",
                                    codes=[
                                        Code(
                                            name="Versionsnummer der zugrundeliegenden BDEW-Nachrichtenbeschreibung",
                                            description=None,
                                            value="1.1c",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                Segment(
                    id="BGM",
                    name="Beginn der Nachricht",
                    number="00114",
                    ahb_status="Muss",
                    data_elements=[
                        DataElementGroup(
                            id="C_C002",
                            name="Dokumenten-/Nachrichtenname",
                            data_elements=[
                                DataElement(
                                    id="D_1001",
                                    name="Dokumentenname, Code",
                                    codes=[
                                        Code(
                                            name="Übersicht Leistungskurvendefinitionen",
                                            description=None,
                                            value="Z79",
                                            ahb_status="X",
                                        )
                                    ],
                                )
                            ],
                        ),
                        DataElementGroup(
                            id="C_C106",
                            name="Dokumenten-/Nachrichten-Identifikation",
                            data_elements=[DataElement(id="D_1004", name="Dokumentennummer", codes=[])],
                        ),
                    ],
                ),
                Segment(
                    id="DTM",
                    name="Nachrichtendatum",
                    number="00115",
                    ahb_status="Muss",
                    data_elements=[
                        DataElementGroup(
                            id="C_C507",
                            name="Datum/Uhrzeit/Zeitspanne",
                            data_elements=[
                                DataElement(
                                    id="D_2005",
                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Funktion, Qualifier",
                                    codes=[
                                        Code(
                                            name="Dokumenten-/Nachrichtendatum/-zeit",
                                            description=None,
                                            value="137",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                                DataElement(id="D_2380", name="Datum oder Uhrzeit oder Zeitspanne, Wert", codes=[]),
                                DataElement(
                                    id="D_2379",
                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Format, Code",
                                    codes=[Code(name="CCYYMMDDHHMMZZZ", description=None, value="303", ahb_status="X")],
                                ),
                            ],
                        )
                    ],
                ),
                Segment(
                    id="UNT",
                    name="Nachrichten-Endesegment",
                    number="00130",
                    ahb_status="Muss",
                    data_elements=[
                        DataElement(id="D_0074", name="Anzahl der Segmente in einer Nachricht", codes=[]),
                        DataElement(id="D_0062", name="Nachrichten-Referenznummer", codes=[]),
                    ],
                ),
            ],
            segment_groups=[
                SegmentGroup(
                    id="2",
                    name="MP-ID Absender",
                    ahb_status="Muss",
                    segments=[
                        Segment(
                            id="NAD",
                            name="MP-ID Absender",
                            number="00116",
                            ahb_status="Muss",
                            data_elements=[
                                DataElement(
                                    id="D_3035",
                                    name="Beteiligter, Qualifier",
                                    codes=[
                                        Code(
                                            name="Dokumenten-/Nachrichtenaussteller bzw. -absender",
                                            description=None,
                                            value="MS",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                                DataElementGroup(
                                    id="C_C082",
                                    name="Identifikation des Beteiligten",
                                    data_elements=[
                                        DataElement(id="D_3039", name="MP-ID", codes=[]),
                                        DataElement(
                                            id="D_3055",
                                            name="Verantwortliche Stelle für die Codepflege, Code",
                                            codes=[
                                                Code(name="GS1", description=None, value="9", ahb_status="X"),
                                                Code(
                                                    name="DE, BDEW (Bundesverband der Energie- und Wasserwirtschaft e.V.)",
                                                    description=None,
                                                    value="293",
                                                    ahb_status="X",
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        )
                    ],
                    segment_groups=[
                        SegmentGroup(
                            id="3",
                            name="Kontaktinformationen",
                            ahb_status="Kann",
                            segments=[
                                Segment(
                                    id="CTA",
                                    name="Ansprechpartner",
                                    number="00117",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_3139",
                                            name="Funktion des Ansprechpartners, Code",
                                            codes=[
                                                Code(
                                                    name="Informationskontakt",
                                                    description=None,
                                                    value="IC",
                                                    ahb_status="X",
                                                )
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C056",
                                            name="Kontaktangaben",
                                            data_elements=[
                                                DataElement(id="D_3412", name="Name vom Ansprechpartner", codes=[])
                                            ],
                                        ),
                                    ],
                                ),
                                Segment(
                                    id="COM",
                                    name="Kommunikationsverbindung",
                                    number="00118",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C076",
                                            name="Kommunikationsverbindung",
                                            data_elements=[
                                                DataElement(id="D_3148", name="Nummer / Adresse", codes=[]),
                                                DataElement(
                                                    id="D_3155",
                                                    name="Art des Kommunikationsmittels, Code",
                                                    codes=[
                                                        Code(
                                                            name="Elektronische Post",
                                                            description=None,
                                                            value="EM",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="Telefax",
                                                            description=None,
                                                            value="FX",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="Telefon",
                                                            description=None,
                                                            value="TE",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="weiteres Telefon",
                                                            description=None,
                                                            value="AJ",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="Handy",
                                                            description=None,
                                                            value="AL",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                            ],
                            segment_groups=[],
                        ),
                        SegmentGroup(
                            id="2",
                            name="MP-ID Empfänger",
                            ahb_status="Muss",
                            segments=[
                                Segment(
                                    id="NAD",
                                    name="MP-ID Empfänger",
                                    number="00119",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_3035",
                                            name="Beteiligter, Qualifier",
                                            codes=[
                                                Code(
                                                    name="Nachrichtenempfänger",
                                                    description=None,
                                                    value="MR",
                                                    ahb_status="X",
                                                )
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C082",
                                            name="Identifikation des Beteiligten",
                                            data_elements=[
                                                DataElement(id="D_3039", name="MP-ID", codes=[]),
                                                DataElement(
                                                    id="D_3055",
                                                    name="Verantwortliche Stelle für die Codepflege, Code",
                                                    codes=[
                                                        Code(name="GS1", description=None, value="9", ahb_status="X"),
                                                        Code(
                                                            name="DE, BDEW (Bundesverband der Energie- und Wasserwirtschaft e.V.)",
                                                            description=None,
                                                            value="293",
                                                            ahb_status="X",
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ],
                                )
                            ],
                            segment_groups=[],
                        ),
                        SegmentGroup(
                            id="5",
                            name="Vorgang",
                            ahb_status="Muss [2001]",
                            segments=[
                                Segment(
                                    id="IDE",
                                    name="Vorgang",
                                    number="00120",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_7495",
                                            name="Objekt, Qualifier",
                                            codes=[
                                                Code(name="Transaktion", description=None, value="24", ahb_status="X")
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C206",
                                            name="Identifikationsnummer",
                                            data_elements=[DataElement(id="D_7402", name="Vorgangsnummer", codes=[])],
                                        ),
                                    ],
                                ),
                                Segment(
                                    id="DTM",
                                    name="Gültig ab",
                                    number="00121",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C507",
                                            name="Datum/Uhrzeit/Zeitspanne",
                                            data_elements=[
                                                DataElement(
                                                    id="D_2005",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Funktion, Qualifier",
                                                    codes=[
                                                        Code(
                                                            name="Gültigkeit, Beginndatum",
                                                            description=None,
                                                            value="157",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                                DataElement(
                                                    id="D_2380",
                                                    name="Datum oder Uhrzeit oder Zeitspanne, Wert",
                                                    codes=[],
                                                ),
                                                DataElement(
                                                    id="D_2379",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Format, Code",
                                                    codes=[
                                                        Code(
                                                            name="CCYYMMDDHHMMZZZ",
                                                            description=None,
                                                            value="303",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                                Segment(
                                    id="DTM",
                                    name="Versionsangabe",
                                    number="00122",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C507",
                                            name="Datum/Uhrzeit/Zeitspanne",
                                            data_elements=[
                                                DataElement(
                                                    id="D_2005",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Funktion, Qualifier",
                                                    codes=[
                                                        Code(
                                                            name="Fertigstellungsdatum/-zeit",
                                                            description=None,
                                                            value="293",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                                DataElement(
                                                    id="D_2380",
                                                    name="Datum oder Uhrzeit oder Zeitspanne, Wert",
                                                    codes=[],
                                                ),
                                                DataElement(
                                                    id="D_2379",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Format, Code",
                                                    codes=[
                                                        Code(
                                                            name="CCYYMMDDHHMMSSZZZ",
                                                            description=None,
                                                            value="304",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                                Segment(
                                    id="TS",
                                    name="Status der Nutzung von Definitionen",
                                    number="00123",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C601",
                                            name="Statuskategorie",
                                            data_elements=[
                                                DataElement(
                                                    id="D_9015",
                                                    name="Statuskategorie, Code",
                                                    codes=[
                                                        Code(
                                                            name="Nutzung von Definitionen",
                                                            description=None,
                                                            value="Z36",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                )
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C555",
                                            name="Status",
                                            data_elements=[
                                                DataElement(
                                                    id="D_4405",
                                                    name="Status, Code",
                                                    codes=[
                                                        Code(
                                                            name="Definitionen werden verwendet",
                                                            description="Bei Zählzeitdefinitionen:\r\nDer NB bzw. LF nutzt Zählzeitdefinitionen für die Tarifierung von Werten. Die Liste der Zählzeitdefinitionen enthält somit Zählzeitdefinitionen.\r\n\r\nBei Schaltzeitdefinitionen:\r\nDer NB bzw. LF nutzt Schaltzeitdefinitionen. Die Liste der Schaltzeitdefinitionen enthält somit Schaltzeitdefinitionen.\r\n\r\nBei Leistungskurvendefinitionen:\r\nDer NB bzw. LF nutzt Leistungskurvendefinitionen. Die Liste der Leistungskurvendefinitionen enthält somit Leistungskurven.",
                                                            value="Z45",
                                                            ahb_status="X",
                                                        ),
                                                        Code(
                                                            name="Definitionen werden nicht verwendet",
                                                            description="Bei Zählzeitdefinitionen:\r\nDer NB nutzt keine Zählzeitdefinitionen für die Tarifierung von Werten. Die Liste der Zählzeitdefinitionen enthält somit keine Zählzeitdefinitionen.\r\n\r\nBei Schaltzeitdefinitionen:\r\nDer NB bzw. LF nutzt keine Schaltzeitdefinitionen. Die Liste der Schaltzeitdefinitionen enthält somit keine Schaltzeitdefinitionen.\r\n\r\nBei Leistungskurvendefinitionen:\r\nDer NB bzw. LF nutzt keine Leistungskurven. Die Liste der Leistungskurvendefinitionen enthält somit keine Leistungskurven.",
                                                            value="Z46",
                                                            ahb_status="X",
                                                        ),
                                                    ],
                                                )
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                            segment_groups=[
                                SegmentGroup(
                                    id="6",
                                    name="Prüfidentifikator",
                                    ahb_status="Muss",
                                    segments=[
                                        Segment(
                                            id="RFF",
                                            name="Prüfidentifikator",
                                            number="00124",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElementGroup(
                                                    id="C_C506",
                                                    name="Referenz",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_1153",
                                                            name="Referenz, Qualifier",
                                                            codes=[
                                                                Code(
                                                                    name="Prüfidentifikator",
                                                                    description=None,
                                                                    value="Z13",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElement(
                                                            id="D_1154",
                                                            name="Referenz, Identifikation",
                                                            codes=[
                                                                Code(
                                                                    name="Übersicht Leistungskurvendefinitionen",
                                                                    description=None,
                                                                    value="25007",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                    ],
                                                )
                                            ],
                                        )
                                    ],
                                    segment_groups=[],
                                ),
                                SegmentGroup(
                                    id="6",
                                    name="Referenz auf Reklamation",
                                    ahb_status="Soll [26]",
                                    segments=[
                                        Segment(
                                            id="RFF",
                                            name="Referenz auf Reklamation",
                                            number="00125",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElementGroup(
                                                    id="C_C506",
                                                    name="Referenz",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_1153",
                                                            name="Referenz, Qualifier",
                                                            codes=[
                                                                Code(
                                                                    name="Beantragungsnummer",
                                                                    description=None,
                                                                    value="AGI",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElement(
                                                            id="D_1154", name="Referenz, Identifikation", codes=[]
                                                        ),
                                                    ],
                                                )
                                            ],
                                        )
                                    ],
                                    segment_groups=[],
                                ),
                                SegmentGroup(
                                    id="8",
                                    name="Leistungskurvendefinition",
                                    ahb_status="Muss [24]",
                                    segments=[
                                        Segment(
                                            id="EQ",
                                            name="Leistungskurvendefinition",
                                            number="00126",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElement(
                                                    id="D_1229",
                                                    name="Handlung, Code",
                                                    codes=[
                                                        Code(
                                                            name="Leistungskurvendefinition",
                                                            description=None,
                                                            value="Z70",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                )
                                            ],
                                        )
                                    ],
                                    segment_groups=[
                                        SegmentGroup(
                                            id="9",
                                            name="Leistungskurvendefinition",
                                            ahb_status="Muss",
                                            segments=[
                                                Segment(
                                                    id="CCI",
                                                    name="Code der Leistungskurvendefinition",
                                                    number="00127",
                                                    ahb_status="Muss",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_7059",
                                                            name="Klassentyp, Code",
                                                            codes=[
                                                                Code(
                                                                    name="Code der Leistungskurvendefinition",
                                                                    description=None,
                                                                    value="Z53",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElementGroup(
                                                            id="C_C240",
                                                            name="Merkmalsbeschreibung",
                                                            data_elements=[
                                                                DataElement(
                                                                    id="D_7037",
                                                                    name="Code der Leistungskurvendefinition",
                                                                    codes=[],
                                                                )
                                                            ],
                                                        ),
                                                    ],
                                                ),
                                                Segment(
                                                    id="CAV",
                                                    name="Häufigkeit der Übermittlung",
                                                    number="00128",
                                                    ahb_status="Muss",
                                                    data_elements=[
                                                        DataElementGroup(
                                                            id="C_C889",
                                                            name="Merkmalswert",
                                                            data_elements=[
                                                                DataElement(
                                                                    id="D_7111",
                                                                    name="Merkmalswert, Code",
                                                                    codes=[
                                                                        Code(
                                                                            name="Häufigkeit der Übermittlung",
                                                                            description=None,
                                                                            value="ZE0",
                                                                            ahb_status="X",
                                                                        )
                                                                    ],
                                                                ),
                                                                DataElement(
                                                                    id="D_7110",
                                                                    name="Merkmalswert",
                                                                    codes=[
                                                                        Code(
                                                                            name="einmalig zu übermittelnde ausgerollte Definition",
                                                                            description="Es handelt sich um eine Leistungskurvendefinition mit identischen Leistungskurvenänderungszeitpunkten an allen Tagen über den gesamten Gültigkeitszeitraum. Diese Leistungskurvendefinition wird einmalig ausgerollt und übermittelt.",
                                                                            value="Z33",
                                                                            ahb_status="X",
                                                                        ),
                                                                        Code(
                                                                            name="jährlich zu übermittelnde ausgerollte Definition",
                                                                            description="Es handelt sich um eine Leistungskurvendefinition mit unterschiedlichen Leistungskurvenänderungszeitpunkten an den einzelnen Tagen über den gesamten Gültigkeitszeitraum. Diese Leistungskurvendefinition muss jedes Jahr ausgerollt und übermittelt werden.",
                                                                            value="Z34",
                                                                            ahb_status="X",
                                                                        ),
                                                                    ],
                                                                ),
                                                            ],
                                                        )
                                                    ],
                                                ),
                                                Segment(
                                                    id="CAV",
                                                    name="Übermittelbarkeit der ausgerollten Leistungskurvendefinition",
                                                    number="00129",
                                                    ahb_status="Muss",
                                                    data_elements=[
                                                        DataElementGroup(
                                                            id="C_C889",
                                                            name="Merkmalswert",
                                                            data_elements=[
                                                                DataElement(
                                                                    id="D_7111",
                                                                    name="Merkmalswert, Code",
                                                                    codes=[
                                                                        Code(
                                                                            name="Übermittelbarkeit der ausgerollten Definition",
                                                                            description=None,
                                                                            value="ZD5",
                                                                            ahb_status="X",
                                                                        )
                                                                    ],
                                                                ),
                                                                DataElement(
                                                                    id="D_7110",
                                                                    name="Merkmalswert",
                                                                    codes=[
                                                                        Code(
                                                                            name="elektronisch übermittelbar",
                                                                            description="Der LF bzw. NB übermittelt die ausgerollte Leistungskurvendefinition per EDIFACT mit dem Nachrichtenformat UTILTS.",
                                                                            value="Z23",
                                                                            ahb_status="X",
                                                                        ),
                                                                        Code(
                                                                            name="elektronisch nicht übermittelbar",
                                                                            description="Der LF bzw. NB übermittelt die ausgerollte Leistungskurvendefinition auf einem bilateral vereinbarten Weg. Dieser Weg wird hier nicht weiter beschrieben.",
                                                                            value="Z24",
                                                                            ahb_status="X",
                                                                        ),
                                                                    ],
                                                                ),
                                                            ],
                                                        )
                                                    ],
                                                ),
                                            ],
                                            segment_groups=[],
                                        )
                                    ],
                                ),
                            ],
                        ),
                    ],
                )
            ],
        ),
        Anwendungsfall(
            pruefidentifikator="25006",
            beschreibung="Übermittlung Übersicht Schaltzeitdefinitionen",
            kommunikation_von="NB an LF / MSB\r\nLF an NB, MSB",
            format="UTILTS",
            segments=[
                Segment(
                    id="UNH",
                    name="Nachrichten-Kopfsegment",
                    number="00131",
                    ahb_status="Muss",
                    data_elements=[
                        DataElement(id="D_0062", name="Nachrichten-Referenznummer", codes=[]),
                        DataElementGroup(
                            id="C_S009",
                            name="Nachrichten-Kennung",
                            data_elements=[
                                DataElement(
                                    id="D_0065",
                                    name="Nachrichtentyp-Kennung",
                                    codes=[
                                        Code(
                                            name="Netznutzungszeiten-Nachricht",
                                            description=None,
                                            value="UTILTS",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                                DataElement(
                                    id="D_0052",
                                    name="Versionsnummer des Nachrichtentyps",
                                    codes=[Code(name="Entwurfs-Version", description=None, value="D", ahb_status="X")],
                                ),
                                DataElement(
                                    id="D_0054",
                                    name="Freigabenummer des Nachrichtentyps",
                                    codes=[
                                        Code(name="Ausgabe 2018 - A", description=None, value="18A", ahb_status="X")
                                    ],
                                ),
                                DataElement(
                                    id="D_0051",
                                    name="Verwaltende Organisation",
                                    codes=[Code(name="UN/CEFACT", description=None, value="UN", ahb_status="X")],
                                ),
                                DataElement(
                                    id="D_0057",
                                    name="Anwendungscode der zuständigen Organisation",
                                    codes=[
                                        Code(
                                            name="Versionsnummer der zugrundeliegenden BDEW-Nachrichtenbeschreibung",
                                            description=None,
                                            value="1.1c",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                Segment(
                    id="BGM",
                    name="Beginn der Nachricht",
                    number="00132",
                    ahb_status="Muss",
                    data_elements=[
                        DataElementGroup(
                            id="C_C002",
                            name="Dokumenten-/Nachrichtenname",
                            data_elements=[
                                DataElement(
                                    id="D_1001",
                                    name="Dokumentenname, Code",
                                    codes=[
                                        Code(
                                            name="Übersicht Schaltzeitdefinitionen",
                                            description=None,
                                            value="Z78",
                                            ahb_status="X",
                                        )
                                    ],
                                )
                            ],
                        ),
                        DataElementGroup(
                            id="C_C106",
                            name="Dokumenten-/Nachrichten-Identifikation",
                            data_elements=[DataElement(id="D_1004", name="Dokumentennummer", codes=[])],
                        ),
                    ],
                ),
                Segment(
                    id="DTM",
                    name="Nachrichtendatum",
                    number="00133",
                    ahb_status="Muss",
                    data_elements=[
                        DataElementGroup(
                            id="C_C507",
                            name="Datum/Uhrzeit/Zeitspanne",
                            data_elements=[
                                DataElement(
                                    id="D_2005",
                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Funktion, Qualifier",
                                    codes=[
                                        Code(
                                            name="Dokumenten-/Nachrichtendatum/-zeit",
                                            description=None,
                                            value="137",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                                DataElement(id="D_2380", name="Datum oder Uhrzeit oder Zeitspanne, Wert", codes=[]),
                                DataElement(
                                    id="D_2379",
                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Format, Code",
                                    codes=[Code(name="CCYYMMDDHHMMZZZ", description=None, value="303", ahb_status="X")],
                                ),
                            ],
                        )
                    ],
                ),
                Segment(
                    id="UNT",
                    name="Nachrichten-Endesegment",
                    number="00148",
                    ahb_status="Muss",
                    data_elements=[
                        DataElement(id="D_0074", name="Anzahl der Segmente in einer Nachricht", codes=[]),
                        DataElement(id="D_0062", name="Nachrichten-Referenznummer", codes=[]),
                    ],
                ),
            ],
            segment_groups=[
                SegmentGroup(
                    id="2",
                    name="MP-ID Absender",
                    ahb_status="Muss",
                    segments=[
                        Segment(
                            id="NAD",
                            name="MP-ID Absender",
                            number="00134",
                            ahb_status="Muss",
                            data_elements=[
                                DataElement(
                                    id="D_3035",
                                    name="Beteiligter, Qualifier",
                                    codes=[
                                        Code(
                                            name="Dokumenten-/Nachrichtenaussteller bzw. -absender",
                                            description=None,
                                            value="MS",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                                DataElementGroup(
                                    id="C_C082",
                                    name="Identifikation des Beteiligten",
                                    data_elements=[
                                        DataElement(id="D_3039", name="MP-ID", codes=[]),
                                        DataElement(
                                            id="D_3055",
                                            name="Verantwortliche Stelle für die Codepflege, Code",
                                            codes=[
                                                Code(name="GS1", description=None, value="9", ahb_status="X"),
                                                Code(
                                                    name="DE, BDEW (Bundesverband der Energie- und Wasserwirtschaft e.V.)",
                                                    description=None,
                                                    value="293",
                                                    ahb_status="X",
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        )
                    ],
                    segment_groups=[
                        SegmentGroup(
                            id="3",
                            name="Kontaktinformationen",
                            ahb_status="Kann",
                            segments=[
                                Segment(
                                    id="CTA",
                                    name="Ansprechpartner",
                                    number="00135",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_3139",
                                            name="Funktion des Ansprechpartners, Code",
                                            codes=[
                                                Code(
                                                    name="Informationskontakt",
                                                    description=None,
                                                    value="IC",
                                                    ahb_status="X",
                                                )
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C056",
                                            name="Kontaktangaben",
                                            data_elements=[
                                                DataElement(id="D_3412", name="Name vom Ansprechpartner", codes=[])
                                            ],
                                        ),
                                    ],
                                ),
                                Segment(
                                    id="COM",
                                    name="Kommunikationsverbindung",
                                    number="00136",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C076",
                                            name="Kommunikationsverbindung",
                                            data_elements=[
                                                DataElement(id="D_3148", name="Nummer / Adresse", codes=[]),
                                                DataElement(
                                                    id="D_3155",
                                                    name="Art des Kommunikationsmittels, Code",
                                                    codes=[
                                                        Code(
                                                            name="Elektronische Post",
                                                            description=None,
                                                            value="EM",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="Telefax",
                                                            description=None,
                                                            value="FX",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="Telefon",
                                                            description=None,
                                                            value="TE",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="weiteres Telefon",
                                                            description=None,
                                                            value="AJ",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="Handy",
                                                            description=None,
                                                            value="AL",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                            ],
                            segment_groups=[],
                        ),
                        SegmentGroup(
                            id="2",
                            name="MP-ID Empfänger",
                            ahb_status="Muss",
                            segments=[
                                Segment(
                                    id="NAD",
                                    name="MP-ID Empfänger",
                                    number="00137",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_3035",
                                            name="Beteiligter, Qualifier",
                                            codes=[
                                                Code(
                                                    name="Nachrichtenempfänger",
                                                    description=None,
                                                    value="MR",
                                                    ahb_status="X",
                                                )
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C082",
                                            name="Identifikation des Beteiligten",
                                            data_elements=[
                                                DataElement(id="D_3039", name="MP-ID", codes=[]),
                                                DataElement(
                                                    id="D_3055",
                                                    name="Verantwortliche Stelle für die Codepflege, Code",
                                                    codes=[
                                                        Code(name="GS1", description=None, value="9", ahb_status="X"),
                                                        Code(
                                                            name="DE, BDEW (Bundesverband der Energie- und Wasserwirtschaft e.V.)",
                                                            description=None,
                                                            value="293",
                                                            ahb_status="X",
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ],
                                )
                            ],
                            segment_groups=[],
                        ),
                        SegmentGroup(
                            id="5",
                            name="Vorgang",
                            ahb_status="Muss [2001]",
                            segments=[
                                Segment(
                                    id="IDE",
                                    name="Vorgang",
                                    number="00138",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_7495",
                                            name="Objekt, Qualifier",
                                            codes=[
                                                Code(name="Transaktion", description=None, value="24", ahb_status="X")
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C206",
                                            name="Identifikationsnummer",
                                            data_elements=[DataElement(id="D_7402", name="Vorgangsnummer", codes=[])],
                                        ),
                                    ],
                                ),
                                Segment(
                                    id="DTM",
                                    name="Gültig ab",
                                    number="00139",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C507",
                                            name="Datum/Uhrzeit/Zeitspanne",
                                            data_elements=[
                                                DataElement(
                                                    id="D_2005",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Funktion, Qualifier",
                                                    codes=[
                                                        Code(
                                                            name="Gültigkeit, Beginndatum",
                                                            description=None,
                                                            value="157",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                                DataElement(
                                                    id="D_2380",
                                                    name="Datum oder Uhrzeit oder Zeitspanne, Wert",
                                                    codes=[],
                                                ),
                                                DataElement(
                                                    id="D_2379",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Format, Code",
                                                    codes=[
                                                        Code(
                                                            name="CCYYMMDDHHMMZZZ",
                                                            description=None,
                                                            value="303",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                                Segment(
                                    id="DTM",
                                    name="Versionsangabe",
                                    number="00140",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C507",
                                            name="Datum/Uhrzeit/Zeitspanne",
                                            data_elements=[
                                                DataElement(
                                                    id="D_2005",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Funktion, Qualifier",
                                                    codes=[
                                                        Code(
                                                            name="Fertigstellungsdatum/-zeit",
                                                            description=None,
                                                            value="293",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                                DataElement(
                                                    id="D_2380",
                                                    name="Datum oder Uhrzeit oder Zeitspanne, Wert",
                                                    codes=[],
                                                ),
                                                DataElement(
                                                    id="D_2379",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Format, Code",
                                                    codes=[
                                                        Code(
                                                            name="CCYYMMDDHHMMSSZZZ",
                                                            description=None,
                                                            value="304",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                                Segment(
                                    id="TS",
                                    name="Status der Nutzung von Definitionen",
                                    number="00141",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C601",
                                            name="Statuskategorie",
                                            data_elements=[
                                                DataElement(
                                                    id="D_9015",
                                                    name="Statuskategorie, Code",
                                                    codes=[
                                                        Code(
                                                            name="Nutzung von Definitionen",
                                                            description=None,
                                                            value="Z36",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                )
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C555",
                                            name="Status",
                                            data_elements=[
                                                DataElement(
                                                    id="D_4405",
                                                    name="Status, Code",
                                                    codes=[
                                                        Code(
                                                            name="Definitionen werden verwendet",
                                                            description="Bei Zählzeitdefinitionen:\r\nDer NB bzw. LF nutzt Zählzeitdefinitionen für die Tarifierung von Werten. Die Liste der Zählzeitdefinitionen enthält somit Zählzeitdefinitionen.\r\n\r\nBei Schaltzeitdefinitionen:\r\nDer NB bzw. LF nutzt Schaltzeitdefinitionen. Die Liste der Schaltzeitdefinitionen enthält somit Schaltzeitdefinitionen.\r\n\r\nBei Leistungskurvendefinitionen:\r\nDer NB bzw. LF nutzt Leistungskurvendefinitionen. Die Liste der Leistungskurvendefinitionen enthält somit Leistungskurven.",
                                                            value="Z45",
                                                            ahb_status="X",
                                                        ),
                                                        Code(
                                                            name="Definitionen werden nicht verwendet",
                                                            description="Bei Zählzeitdefinitionen:\r\nDer NB nutzt keine Zählzeitdefinitionen für die Tarifierung von Werten. Die Liste der Zählzeitdefinitionen enthält somit keine Zählzeitdefinitionen.\r\n\r\nBei Schaltzeitdefinitionen:\r\nDer NB bzw. LF nutzt keine Schaltzeitdefinitionen. Die Liste der Schaltzeitdefinitionen enthält somit keine Schaltzeitdefinitionen.\r\n\r\nBei Leistungskurvendefinitionen:\r\nDer NB bzw. LF nutzt keine Leistungskurven. Die Liste der Leistungskurvendefinitionen enthält somit keine Leistungskurven.",
                                                            value="Z46",
                                                            ahb_status="X",
                                                        ),
                                                    ],
                                                )
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                            segment_groups=[
                                SegmentGroup(
                                    id="6",
                                    name="Prüfidentifikator",
                                    ahb_status="Muss",
                                    segments=[
                                        Segment(
                                            id="RFF",
                                            name="Prüfidentifikator",
                                            number="00142",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElementGroup(
                                                    id="C_C506",
                                                    name="Referenz",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_1153",
                                                            name="Referenz, Qualifier",
                                                            codes=[
                                                                Code(
                                                                    name="Prüfidentifikator",
                                                                    description=None,
                                                                    value="Z13",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElement(
                                                            id="D_1154",
                                                            name="Referenz, Identifikation",
                                                            codes=[
                                                                Code(
                                                                    name="Übersicht Schaltzeitdefinitionen",
                                                                    description=None,
                                                                    value="25006",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                    ],
                                                )
                                            ],
                                        )
                                    ],
                                    segment_groups=[],
                                ),
                                SegmentGroup(
                                    id="6",
                                    name="Referenz auf Reklamation",
                                    ahb_status="Soll [26]",
                                    segments=[
                                        Segment(
                                            id="RFF",
                                            name="Referenz auf Reklamation",
                                            number="00143",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElementGroup(
                                                    id="C_C506",
                                                    name="Referenz",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_1153",
                                                            name="Referenz, Qualifier",
                                                            codes=[
                                                                Code(
                                                                    name="Beantragungsnummer",
                                                                    description=None,
                                                                    value="AGI",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElement(
                                                            id="D_1154", name="Referenz, Identifikation", codes=[]
                                                        ),
                                                    ],
                                                )
                                            ],
                                        )
                                    ],
                                    segment_groups=[],
                                ),
                                SegmentGroup(
                                    id="8",
                                    name="Schaltzeitdefinition",
                                    ahb_status="Muss [24]",
                                    segments=[
                                        Segment(
                                            id="EQ",
                                            name="Schaltzeitdefinition",
                                            number="00144",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElement(
                                                    id="D_1229",
                                                    name="Handlung, Code",
                                                    codes=[
                                                        Code(
                                                            name="Schaltzeitdefinition",
                                                            description=None,
                                                            value="Z69",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                )
                                            ],
                                        )
                                    ],
                                    segment_groups=[
                                        SegmentGroup(
                                            id="9",
                                            name="Schaltzeitdefinition",
                                            ahb_status="Muss",
                                            segments=[
                                                Segment(
                                                    id="CCI",
                                                    name="Code der Schaltzeitdefinition",
                                                    number="00145",
                                                    ahb_status="Muss",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_7059",
                                                            name="Klassentyp, Code",
                                                            codes=[
                                                                Code(
                                                                    name="Code der Schaltzeitdefinition",
                                                                    description=None,
                                                                    value="Z52",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElementGroup(
                                                            id="C_C240",
                                                            name="Merkmalsbeschreibung",
                                                            data_elements=[
                                                                DataElement(
                                                                    id="D_7037",
                                                                    name="Code der Schaltzeitdefinition",
                                                                    codes=[],
                                                                )
                                                            ],
                                                        ),
                                                    ],
                                                ),
                                                Segment(
                                                    id="CAV",
                                                    name="Häufigkeit der Übermittlung",
                                                    number="00146",
                                                    ahb_status="Muss",
                                                    data_elements=[
                                                        DataElementGroup(
                                                            id="C_C889",
                                                            name="Merkmalswert",
                                                            data_elements=[
                                                                DataElement(
                                                                    id="D_7111",
                                                                    name="Merkmalswert, Code",
                                                                    codes=[
                                                                        Code(
                                                                            name="Häufigkeit der Übermittlung",
                                                                            description=None,
                                                                            value="ZE0",
                                                                            ahb_status="X",
                                                                        )
                                                                    ],
                                                                ),
                                                                DataElement(
                                                                    id="D_7110",
                                                                    name="Merkmalswert",
                                                                    codes=[
                                                                        Code(
                                                                            name="einmalig zu übermittelnde ausgerollte Definition",
                                                                            description="Es handelt sich um eine Schaltzeitdefinition mit identischen Schaltzeitänderungszeitpunkten an allen Tagen über den gesamten Gültigkeitszeitraum. Diese Schaltzeitdefinitiont wird einmalig ausgerollt und übermittelt.",
                                                                            value="Z33",
                                                                            ahb_status="X",
                                                                        ),
                                                                        Code(
                                                                            name="jährlich zu übermittelnde ausgerollte Definition",
                                                                            description="Es handelt sich um eine Schaltzeitdefinition mit unterschiedlichen Schaltzeitänderungszeitpunkten an den einzelnen Tagen über den gesamten Gültigkeitszeitraum. Diese Schaltzeitdefinition muss jedes Jahr ausgerollt und übermittelt werden.",
                                                                            value="Z34",
                                                                            ahb_status="X",
                                                                        ),
                                                                    ],
                                                                ),
                                                            ],
                                                        )
                                                    ],
                                                ),
                                                Segment(
                                                    id="CAV",
                                                    name="Übermittelbarkeit der ausgerollten Schaltzeitdefinition",
                                                    number="00147",
                                                    ahb_status="Muss",
                                                    data_elements=[
                                                        DataElementGroup(
                                                            id="C_C889",
                                                            name="Merkmalswert",
                                                            data_elements=[
                                                                DataElement(
                                                                    id="D_7111",
                                                                    name="Merkmalswert, Code",
                                                                    codes=[
                                                                        Code(
                                                                            name="Übermittelbarkeit der ausgerollten Definition",
                                                                            description=None,
                                                                            value="ZD5",
                                                                            ahb_status="X",
                                                                        )
                                                                    ],
                                                                ),
                                                                DataElement(
                                                                    id="D_7110",
                                                                    name="Merkmalswert",
                                                                    codes=[
                                                                        Code(
                                                                            name="elektronisch übermittelbar",
                                                                            description="Der LF bzw. NB übermittelt die ausgerollte Schaltzeitdefinition per EDIFACT mit dem Nachrichtenformat UTILTS.",
                                                                            value="Z23",
                                                                            ahb_status="X",
                                                                        ),
                                                                        Code(
                                                                            name="elektronisch nicht übermittelbar",
                                                                            description="Der LF bzw. NB übermittelt die ausgerollte Schaltzeitdefinition auf einem bilateral vereinbarten Weg. Dieser Weg wird hier nicht weiter beschrieben.",
                                                                            value="Z24",
                                                                            ahb_status="X",
                                                                        ),
                                                                    ],
                                                                ),
                                                            ],
                                                        )
                                                    ],
                                                ),
                                            ],
                                            segment_groups=[],
                                        )
                                    ],
                                ),
                            ],
                        ),
                    ],
                )
            ],
        ),
        Anwendungsfall(
            pruefidentifikator="25004",
            beschreibung="Übermittlung Übersicht Zählzeitdefinitionen",
            kommunikation_von="NB an LF / MSB\r\nLF an MSB",
            format="UTILTS",
            segments=[
                Segment(
                    id="UNH",
                    name="Nachrichten-Kopfsegment",
                    number="00149",
                    ahb_status="Muss",
                    data_elements=[
                        DataElement(id="D_0062", name="Nachrichten-Referenznummer", codes=[]),
                        DataElementGroup(
                            id="C_S009",
                            name="Nachrichten-Kennung",
                            data_elements=[
                                DataElement(
                                    id="D_0065",
                                    name="Nachrichtentyp-Kennung",
                                    codes=[
                                        Code(
                                            name="Netznutzungszeiten-Nachricht",
                                            description=None,
                                            value="UTILTS",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                                DataElement(
                                    id="D_0052",
                                    name="Versionsnummer des Nachrichtentyps",
                                    codes=[Code(name="Entwurfs-Version", description=None, value="D", ahb_status="X")],
                                ),
                                DataElement(
                                    id="D_0054",
                                    name="Freigabenummer des Nachrichtentyps",
                                    codes=[
                                        Code(name="Ausgabe 2018 - A", description=None, value="18A", ahb_status="X")
                                    ],
                                ),
                                DataElement(
                                    id="D_0051",
                                    name="Verwaltende Organisation",
                                    codes=[Code(name="UN/CEFACT", description=None, value="UN", ahb_status="X")],
                                ),
                                DataElement(
                                    id="D_0057",
                                    name="Anwendungscode der zuständigen Organisation",
                                    codes=[
                                        Code(
                                            name="Versionsnummer der zugrundeliegenden BDEW-Nachrichtenbeschreibung",
                                            description=None,
                                            value="1.1c",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                Segment(
                    id="BGM",
                    name="Beginn der Nachricht",
                    number="00150",
                    ahb_status="Muss",
                    data_elements=[
                        DataElementGroup(
                            id="C_C002",
                            name="Dokumenten-/Nachrichtenname",
                            data_elements=[
                                DataElement(
                                    id="D_1001",
                                    name="Dokumentenname, Code",
                                    codes=[
                                        Code(
                                            name="Übersicht Zählzeitdefinitionen",
                                            description=None,
                                            value="Z60",
                                            ahb_status="X",
                                        )
                                    ],
                                )
                            ],
                        ),
                        DataElementGroup(
                            id="C_C106",
                            name="Dokumenten-/Nachrichten-Identifikation",
                            data_elements=[DataElement(id="D_1004", name="Dokumentennummer", codes=[])],
                        ),
                    ],
                ),
                Segment(
                    id="DTM",
                    name="Nachrichtendatum",
                    number="00151",
                    ahb_status="Muss",
                    data_elements=[
                        DataElementGroup(
                            id="C_C507",
                            name="Datum/Uhrzeit/Zeitspanne",
                            data_elements=[
                                DataElement(
                                    id="D_2005",
                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Funktion, Qualifier",
                                    codes=[
                                        Code(
                                            name="Dokumenten-/Nachrichtendatum/-zeit",
                                            description=None,
                                            value="137",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                                DataElement(id="D_2380", name="Datum oder Uhrzeit oder Zeitspanne, Wert", codes=[]),
                                DataElement(
                                    id="D_2379",
                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Format, Code",
                                    codes=[Code(name="CCYYMMDDHHMMZZZ", description=None, value="303", ahb_status="X")],
                                ),
                            ],
                        )
                    ],
                ),
                Segment(
                    id="UNT",
                    name="Nachrichten-Endesegment",
                    number="00173",
                    ahb_status="Muss",
                    data_elements=[
                        DataElement(id="D_0074", name="Anzahl der Segmente in einer Nachricht", codes=[]),
                        DataElement(id="D_0062", name="Nachrichten-Referenznummer", codes=[]),
                    ],
                ),
            ],
            segment_groups=[
                SegmentGroup(
                    id="2",
                    name="MP-ID Absender",
                    ahb_status="Muss",
                    segments=[
                        Segment(
                            id="NAD",
                            name="MP-ID Absender",
                            number="00152",
                            ahb_status="Muss",
                            data_elements=[
                                DataElement(
                                    id="D_3035",
                                    name="Beteiligter, Qualifier",
                                    codes=[
                                        Code(
                                            name="Dokumenten-/Nachrichtenaussteller bzw. -absender",
                                            description=None,
                                            value="MS",
                                            ahb_status="X",
                                        )
                                    ],
                                ),
                                DataElementGroup(
                                    id="C_C082",
                                    name="Identifikation des Beteiligten",
                                    data_elements=[
                                        DataElement(id="D_3039", name="MP-ID", codes=[]),
                                        DataElement(
                                            id="D_3055",
                                            name="Verantwortliche Stelle für die Codepflege, Code",
                                            codes=[
                                                Code(name="GS1", description=None, value="9", ahb_status="X"),
                                                Code(
                                                    name="DE, BDEW (Bundesverband der Energie- und Wasserwirtschaft e.V.)",
                                                    description=None,
                                                    value="293",
                                                    ahb_status="X",
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        )
                    ],
                    segment_groups=[
                        SegmentGroup(
                            id="3",
                            name="Kontaktinformationen",
                            ahb_status="Kann",
                            segments=[
                                Segment(
                                    id="CTA",
                                    name="Ansprechpartner",
                                    number="00153",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_3139",
                                            name="Funktion des Ansprechpartners, Code",
                                            codes=[
                                                Code(
                                                    name="Informationskontakt",
                                                    description=None,
                                                    value="IC",
                                                    ahb_status="X",
                                                )
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C056",
                                            name="Kontaktangaben",
                                            data_elements=[
                                                DataElement(id="D_3412", name="Name vom Ansprechpartner", codes=[])
                                            ],
                                        ),
                                    ],
                                ),
                                Segment(
                                    id="COM",
                                    name="Kommunikationsverbindung",
                                    number="00154",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C076",
                                            name="Kommunikationsverbindung",
                                            data_elements=[
                                                DataElement(id="D_3148", name="Nummer / Adresse", codes=[]),
                                                DataElement(
                                                    id="D_3155",
                                                    name="Art des Kommunikationsmittels, Code",
                                                    codes=[
                                                        Code(
                                                            name="Elektronische Post",
                                                            description=None,
                                                            value="EM",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="Telefax",
                                                            description=None,
                                                            value="FX",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="Telefon",
                                                            description=None,
                                                            value="TE",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="weiteres Telefon",
                                                            description=None,
                                                            value="AJ",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                        Code(
                                                            name="Handy",
                                                            description=None,
                                                            value="AL",
                                                            ahb_status="X [1P0..1]",
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                            ],
                            segment_groups=[],
                        ),
                        SegmentGroup(
                            id="2",
                            name="MP-ID Empfänger",
                            ahb_status="Muss",
                            segments=[
                                Segment(
                                    id="NAD",
                                    name="MP-ID Empfänger",
                                    number="00155",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_3035",
                                            name="Beteiligter, Qualifier",
                                            codes=[
                                                Code(
                                                    name="Nachrichtenempfänger",
                                                    description=None,
                                                    value="MR",
                                                    ahb_status="X",
                                                )
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C082",
                                            name="Identifikation des Beteiligten",
                                            data_elements=[
                                                DataElement(id="D_3039", name="MP-ID", codes=[]),
                                                DataElement(
                                                    id="D_3055",
                                                    name="Verantwortliche Stelle für die Codepflege, Code",
                                                    codes=[
                                                        Code(name="GS1", description=None, value="9", ahb_status="X"),
                                                        Code(
                                                            name="DE, BDEW (Bundesverband der Energie- und Wasserwirtschaft e.V.)",
                                                            description=None,
                                                            value="293",
                                                            ahb_status="X",
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ],
                                )
                            ],
                            segment_groups=[],
                        ),
                        SegmentGroup(
                            id="5",
                            name="Vorgang",
                            ahb_status="Muss [2001]",
                            segments=[
                                Segment(
                                    id="IDE",
                                    name="Vorgang",
                                    number="00156",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElement(
                                            id="D_7495",
                                            name="Objekt, Qualifier",
                                            codes=[
                                                Code(name="Transaktion", description=None, value="24", ahb_status="X")
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C206",
                                            name="Identifikationsnummer",
                                            data_elements=[DataElement(id="D_7402", name="Vorgangsnummer", codes=[])],
                                        ),
                                    ],
                                ),
                                Segment(
                                    id="DTM",
                                    name="Gültig ab",
                                    number="00157",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C507",
                                            name="Datum/Uhrzeit/Zeitspanne",
                                            data_elements=[
                                                DataElement(
                                                    id="D_2005",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Funktion, Qualifier",
                                                    codes=[
                                                        Code(
                                                            name="Gültigkeit, Beginndatum",
                                                            description=None,
                                                            value="157",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                                DataElement(
                                                    id="D_2380",
                                                    name="Datum oder Uhrzeit oder Zeitspanne, Wert",
                                                    codes=[],
                                                ),
                                                DataElement(
                                                    id="D_2379",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Format, Code",
                                                    codes=[
                                                        Code(
                                                            name="CCYYMMDDHHMMZZZ",
                                                            description=None,
                                                            value="303",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                                Segment(
                                    id="DTM",
                                    name="Versionsangabe",
                                    number="00158",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C507",
                                            name="Datum/Uhrzeit/Zeitspanne",
                                            data_elements=[
                                                DataElement(
                                                    id="D_2005",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Funktion, Qualifier",
                                                    codes=[
                                                        Code(
                                                            name="Fertigstellungsdatum/-zeit",
                                                            description=None,
                                                            value="293",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                                DataElement(
                                                    id="D_2380",
                                                    name="Datum oder Uhrzeit oder Zeitspanne, Wert",
                                                    codes=[],
                                                ),
                                                DataElement(
                                                    id="D_2379",
                                                    name="Datums- oder Uhrzeit- oder Zeitspannen-Format, Code",
                                                    codes=[
                                                        Code(
                                                            name="CCYYMMDDHHMMSSZZZ",
                                                            description=None,
                                                            value="304",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                                Segment(
                                    id="TS",
                                    name="Status der Nutzung von Definitionen",
                                    number="00159",
                                    ahb_status="Muss",
                                    data_elements=[
                                        DataElementGroup(
                                            id="C_C601",
                                            name="Statuskategorie",
                                            data_elements=[
                                                DataElement(
                                                    id="D_9015",
                                                    name="Statuskategorie, Code",
                                                    codes=[
                                                        Code(
                                                            name="Nutzung von Definitionen",
                                                            description=None,
                                                            value="Z36",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                )
                                            ],
                                        ),
                                        DataElementGroup(
                                            id="C_C555",
                                            name="Status",
                                            data_elements=[
                                                DataElement(
                                                    id="D_4405",
                                                    name="Status, Code",
                                                    codes=[
                                                        Code(
                                                            name="Definitionen werden verwendet",
                                                            description="Bei Zählzeitdefinitionen:\r\nDer NB bzw. LF nutzt Zählzeitdefinitionen für die Tarifierung von Werten. Die Liste der Zählzeitdefinitionen enthält somit Zählzeitdefinitionen.\r\n\r\nBei Schaltzeitdefinitionen:\r\nDer NB bzw. LF nutzt Schaltzeitdefinitionen. Die Liste der Schaltzeitdefinitionen enthält somit Schaltzeitdefinitionen.\r\n\r\nBei Leistungskurvendefinitionen:\r\nDer NB bzw. LF nutzt Leistungskurvendefinitionen. Die Liste der Leistungskurvendefinitionen enthält somit Leistungskurven.",
                                                            value="Z45",
                                                            ahb_status="X",
                                                        ),
                                                        Code(
                                                            name="Definitionen werden nicht verwendet",
                                                            description="Bei Zählzeitdefinitionen:\r\nDer NB nutzt keine Zählzeitdefinitionen für die Tarifierung von Werten. Die Liste der Zählzeitdefinitionen enthält somit keine Zählzeitdefinitionen.\r\n\r\nBei Schaltzeitdefinitionen:\r\nDer NB bzw. LF nutzt keine Schaltzeitdefinitionen. Die Liste der Schaltzeitdefinitionen enthält somit keine Schaltzeitdefinitionen.\r\n\r\nBei Leistungskurvendefinitionen:\r\nDer NB bzw. LF nutzt keine Leistungskurven. Die Liste der Leistungskurvendefinitionen enthält somit keine Leistungskurven.",
                                                            value="Z46",
                                                            ahb_status="X",
                                                        ),
                                                    ],
                                                )
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                            segment_groups=[
                                SegmentGroup(
                                    id="6",
                                    name="Prüfidentifikator",
                                    ahb_status="Muss",
                                    segments=[
                                        Segment(
                                            id="RFF",
                                            name="Prüfidentifikator",
                                            number="00160",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElementGroup(
                                                    id="C_C506",
                                                    name="Referenz",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_1153",
                                                            name="Referenz, Qualifier",
                                                            codes=[
                                                                Code(
                                                                    name="Prüfidentifikator",
                                                                    description=None,
                                                                    value="Z13",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElement(
                                                            id="D_1154",
                                                            name="Referenz, Identifikation",
                                                            codes=[
                                                                Code(
                                                                    name="Übersicht Zählzeitdefinitionen",
                                                                    description=None,
                                                                    value="25004",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                    ],
                                                )
                                            ],
                                        )
                                    ],
                                    segment_groups=[],
                                ),
                                SegmentGroup(
                                    id="6",
                                    name="Referenz auf Reklamation",
                                    ahb_status="Soll [26]",
                                    segments=[
                                        Segment(
                                            id="RFF",
                                            name="Referenz auf Reklamation",
                                            number="00161",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElementGroup(
                                                    id="C_C506",
                                                    name="Referenz",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_1153",
                                                            name="Referenz, Qualifier",
                                                            codes=[
                                                                Code(
                                                                    name="Beantragungsnummer",
                                                                    description=None,
                                                                    value="AGI",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElement(
                                                            id="D_1154", name="Referenz, Identifikation", codes=[]
                                                        ),
                                                    ],
                                                )
                                            ],
                                        )
                                    ],
                                    segment_groups=[],
                                ),
                                SegmentGroup(
                                    id="8",
                                    name="Zählzeitdefinition",
                                    ahb_status="Muss [24]",
                                    segments=[
                                        Segment(
                                            id="EQ",
                                            name="Zählzeitdefinition",
                                            number="00162",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElement(
                                                    id="D_1229",
                                                    name="Handlung, Code",
                                                    codes=[
                                                        Code(
                                                            name="Zählzeitdefinition",
                                                            description=None,
                                                            value="Z42",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                )
                                            ],
                                        )
                                    ],
                                    segment_groups=[
                                        SegmentGroup(
                                            id="9",
                                            name="Zählzeitdefinition",
                                            ahb_status="Muss",
                                            segments=[
                                                Segment(
                                                    id="CCI",
                                                    name="Code der Zählzeitdefinition",
                                                    number="00163",
                                                    ahb_status="Muss",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_7059",
                                                            name="Klassentyp, Code",
                                                            codes=[
                                                                Code(
                                                                    name="Code der Zählzeitdefinition",
                                                                    description=None,
                                                                    value="Z39",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElementGroup(
                                                            id="C_C240",
                                                            name="Merkmalsbeschreibung",
                                                            data_elements=[
                                                                DataElement(
                                                                    id="D_7037",
                                                                    name="Code der Zählzeitdefinition",
                                                                    codes=[],
                                                                )
                                                            ],
                                                        ),
                                                    ],
                                                ),
                                                Segment(
                                                    id="CAV",
                                                    name="Häufigkeit der Übermittlung",
                                                    number="00164",
                                                    ahb_status="Muss",
                                                    data_elements=[
                                                        DataElementGroup(
                                                            id="C_C889",
                                                            name="Merkmalswert",
                                                            data_elements=[
                                                                DataElement(
                                                                    id="D_7111",
                                                                    name="Merkmalswert, Code",
                                                                    codes=[
                                                                        Code(
                                                                            name="Häufigkeit der Übermittlung",
                                                                            description=None,
                                                                            value="ZE0",
                                                                            ahb_status="X",
                                                                        )
                                                                    ],
                                                                ),
                                                                DataElement(
                                                                    id="D_7110",
                                                                    name="Merkmalswert",
                                                                    codes=[
                                                                        Code(
                                                                            name="einmalig zu übermittelnde ausgerollte Definition",
                                                                            description="Es handelt sich um eine Zählzeitdefinition mit einem Zählzeitänderungszeitpunkt an allen Tagen je Zählzeitregister über den gesamten Gültigkeitszeitraum. Diese Zählzeitdefinition einmalig ausgerollt und übermittelt werden.",
                                                                            value="Z33",
                                                                            ahb_status="X",
                                                                        ),
                                                                        Code(
                                                                            name="jährlich zu übermittelnde ausgerollte Definition",
                                                                            description="Es handelt sich um eine Zählzeitdefinition mit unterschiedlichen Zählzeitänderungszeitpunkt je Zählzeitregister an den einzelnen Tagen über den gesamten Gültigkeitszeitraum. Diese Zählzeitdefinition muss jedes Jahr ausgerollt und übermittelt werden.",
                                                                            value="Z34",
                                                                            ahb_status="X",
                                                                        ),
                                                                    ],
                                                                ),
                                                            ],
                                                        )
                                                    ],
                                                ),
                                                Segment(
                                                    id="CAV",
                                                    name="Übermittelbarkeit der ausgerollten Zählzeitdefinition",
                                                    number="00165",
                                                    ahb_status="Muss",
                                                    data_elements=[
                                                        DataElementGroup(
                                                            id="C_C889",
                                                            name="Merkmalswert",
                                                            data_elements=[
                                                                DataElement(
                                                                    id="D_7111",
                                                                    name="Merkmalswert, Code",
                                                                    codes=[
                                                                        Code(
                                                                            name="Übermittelbarkeit der ausgerollten Definition",
                                                                            description=None,
                                                                            value="ZD5",
                                                                            ahb_status="X",
                                                                        )
                                                                    ],
                                                                ),
                                                                DataElement(
                                                                    id="D_7110",
                                                                    name="Merkmalswert",
                                                                    codes=[
                                                                        Code(
                                                                            name="elektronisch übermittelbar",
                                                                            description="Der LF bzw. NB übermittelt die ausgerollte Zählzeitdefinition per EDIFACT mit dem Nachrichtenformat UTILTS.",
                                                                            value="Z23",
                                                                            ahb_status="X",
                                                                        ),
                                                                        Code(
                                                                            name="elektronisch nicht übermittelbar",
                                                                            description="Der LF bzw.NB übermittelt die ausgerollte Zählzeitdefinition auf einem bilateral vereinbarten Weg. Dieser Weg wird hier nicht weiter beschrieben.",
                                                                            value="Z24",
                                                                            ahb_status="X",
                                                                        ),
                                                                    ],
                                                                ),
                                                            ],
                                                        )
                                                    ],
                                                ),
                                                Segment(
                                                    id="CAV",
                                                    name="Ermittlung des Leistungsmaximums bei atypischer Netznutzung",
                                                    number="00166",
                                                    ahb_status="Muss [22]",
                                                    data_elements=[
                                                        DataElementGroup(
                                                            id="C_C889",
                                                            name="Merkmalswert",
                                                            data_elements=[
                                                                DataElement(
                                                                    id="D_7111",
                                                                    name="Merkmalswert, Code",
                                                                    codes=[
                                                                        Code(
                                                                            name="Ermittlung des Leistungsmaximums bei atypischer Netznutzung",
                                                                            description=None,
                                                                            value="ZD4",
                                                                            ahb_status="X",
                                                                        )
                                                                    ],
                                                                ),
                                                                DataElement(
                                                                    id="D_7110",
                                                                    name="Merkmalswert",
                                                                    codes=[
                                                                        Code(
                                                                            name="Verwendung des Hochlastzeitfensters",
                                                                            description=None,
                                                                            value="Z25",
                                                                            ahb_status="X",
                                                                        ),
                                                                        Code(
                                                                            name="keine Verwendung des Hochlastzeitfensters",
                                                                            description=None,
                                                                            value="Z26",
                                                                            ahb_status="X",
                                                                        ),
                                                                    ],
                                                                ),
                                                            ],
                                                        )
                                                    ],
                                                ),
                                                Segment(
                                                    id="CAV",
                                                    name="Bestellbarkeit der Zählzeitdefinition",
                                                    number="00167",
                                                    ahb_status="Muss [22] ∧ [25]",
                                                    data_elements=[
                                                        DataElementGroup(
                                                            id="C_C889",
                                                            name="Merkmalswert",
                                                            data_elements=[
                                                                DataElement(
                                                                    id="D_7111",
                                                                    name="Merkmalswert, Code",
                                                                    codes=[
                                                                        Code(
                                                                            name="Bestellbarkeit der Zählzeitdefinition",
                                                                            description=None,
                                                                            value="ZD7",
                                                                            ahb_status="X",
                                                                        )
                                                                    ],
                                                                ),
                                                                DataElement(
                                                                    id="D_7110",
                                                                    name="Merkmalswert",
                                                                    codes=[
                                                                        Code(
                                                                            name="Zählzeitdefinition ist bestellbar",
                                                                            description=None,
                                                                            value="Z27",
                                                                            ahb_status="X",
                                                                        ),
                                                                        Code(
                                                                            name="Zählzeitdefinition ist nicht bestellbar",
                                                                            description=None,
                                                                            value="Z28",
                                                                            ahb_status="X",
                                                                        ),
                                                                    ],
                                                                ),
                                                            ],
                                                        )
                                                    ],
                                                ),
                                                Segment(
                                                    id="CAV",
                                                    name="Zählzeitdefinitionstyp",
                                                    number="00168",
                                                    ahb_status="Muss [22] ∧ [27]",
                                                    data_elements=[
                                                        DataElementGroup(
                                                            id="C_C889",
                                                            name="Merkmalswert",
                                                            data_elements=[
                                                                DataElement(
                                                                    id="D_7111",
                                                                    name="Merkmalswert, Code",
                                                                    codes=[
                                                                        Code(
                                                                            name="Zählzeitdefinitionstyp",
                                                                            description=None,
                                                                            value="ZD3",
                                                                            ahb_status="X",
                                                                        )
                                                                    ],
                                                                ),
                                                                DataElement(
                                                                    id="D_7110",
                                                                    name="Merkmalswert",
                                                                    codes=[
                                                                        Code(
                                                                            name="Wärmepumpe",
                                                                            description=None,
                                                                            value="Z29",
                                                                            ahb_status="X",
                                                                        ),
                                                                        Code(
                                                                            name="Nachtspeicherheizung",
                                                                            description=None,
                                                                            value="Z30",
                                                                            ahb_status="X",
                                                                        ),
                                                                        Code(
                                                                            name="Schwachlastzeitfenster",
                                                                            description=None,
                                                                            value="Z31",
                                                                            ahb_status="X",
                                                                        ),
                                                                        Code(
                                                                            name="sonstiger Zählzeitdefinitionstyp",
                                                                            description=None,
                                                                            value="Z32",
                                                                            ahb_status="X",
                                                                        ),
                                                                        Code(
                                                                            name="Hochlastzeitfenster",
                                                                            description=None,
                                                                            value="Z35",
                                                                            ahb_status="X",
                                                                        ),
                                                                    ],
                                                                ),
                                                                DataElement(
                                                                    id="D_7110",
                                                                    name="Beschreibung Zählzeitdefinitionstyp",
                                                                    codes=[],
                                                                ),
                                                            ],
                                                        )
                                                    ],
                                                ),
                                            ],
                                            segment_groups=[],
                                        )
                                    ],
                                ),
                                SegmentGroup(
                                    id="8",
                                    name="Register der Zählzeitdefinition",
                                    ahb_status="Muss [41] ∧ [2002]",
                                    segments=[
                                        Segment(
                                            id="EQ",
                                            name="Register der Zählzeitdefinition",
                                            number="00169",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElement(
                                                    id="D_1229",
                                                    name="Handlung, Code",
                                                    codes=[
                                                        Code(
                                                            name="Register der Zählzeitdefinition",
                                                            description=None,
                                                            value="Z41",
                                                            ahb_status="X",
                                                        )
                                                    ],
                                                )
                                            ],
                                        ),
                                        Segment(
                                            id="RFF",
                                            name="Referenz auf eine Zählzeitdefinition",
                                            number="00170",
                                            ahb_status="Muss",
                                            data_elements=[
                                                DataElementGroup(
                                                    id="C_C506",
                                                    name="Referenz",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_1153",
                                                            name="Referenz, Qualifier",
                                                            codes=[
                                                                Code(
                                                                    name="Code der Zählzeitdefinition",
                                                                    description=None,
                                                                    value="Z27",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElement(
                                                            id="D_1154", name="Code der Zählzeitdefinition", codes=[]
                                                        ),
                                                    ],
                                                )
                                            ],
                                        ),
                                    ],
                                    segment_groups=[
                                        SegmentGroup(
                                            id="9",
                                            name="Register",
                                            ahb_status="Muss",
                                            segments=[
                                                Segment(
                                                    id="CCI",
                                                    name="Code des Zählzeitregister",
                                                    number="00171",
                                                    ahb_status="Muss",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_7059",
                                                            name="Klassentyp, Code",
                                                            codes=[
                                                                Code(
                                                                    name="Code des Zählzeitregisters",
                                                                    description=None,
                                                                    value="Z38",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElementGroup(
                                                            id="C_C240",
                                                            name="Merkmalsbeschreibung",
                                                            data_elements=[
                                                                DataElement(
                                                                    id="D_7037",
                                                                    name="Code des Zählzeitregisters",
                                                                    codes=[],
                                                                )
                                                            ],
                                                        ),
                                                    ],
                                                )
                                            ],
                                            segment_groups=[],
                                        ),
                                        SegmentGroup(
                                            id="9",
                                            name="Schwachlastfähigkeit",
                                            ahb_status="Muss [22]",
                                            segments=[
                                                Segment(
                                                    id="CCI",
                                                    name="Schwachlastfähigkeit",
                                                    number="00172",
                                                    ahb_status="Muss",
                                                    data_elements=[
                                                        DataElement(
                                                            id="D_7059",
                                                            name="Klassentyp, Code",
                                                            codes=[
                                                                Code(
                                                                    name="Schwachlastfähigkeit",
                                                                    description=None,
                                                                    value="Z10",
                                                                    ahb_status="X",
                                                                )
                                                            ],
                                                        ),
                                                        DataElementGroup(
                                                            id="C_C240",
                                                            name="Merkmalsbeschreibung",
                                                            data_elements=[
                                                                DataElement(
                                                                    id="D_7037",
                                                                    name="Merkmal, Code",
                                                                    codes=[
                                                                        Code(
                                                                            name="Nicht-Schwachlast fähig",
                                                                            description=None,
                                                                            value="Z59",
                                                                            ahb_status="X",
                                                                        ),
                                                                        Code(
                                                                            name="Schwachlast fähig",
                                                                            description=None,
                                                                            value="Z60",
                                                                            ahb_status="X",
                                                                        ),
                                                                    ],
                                                                )
                                                            ],
                                                        ),
                                                    ],
                                                )
                                            ],
                                            segment_groups=[],
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                )
            ],
        ),
    ],
    bedingungen=[
        Bedingung(nummer="1", text="Nur MP-ID aus Sparte Strom"),
        Bedingung(
            nummer="2",
            text="Wenn SG5 STS+Z23+Z34 (Formel muss beim Absender angefragt werden) in einem SG5 IDE vorhanden",
        ),
        Bedingung(nummer="3", text="Wenn SG5 STS+Z23+Z33 (Formel angefügt) vorhanden"),
        Bedingung(
            nummer="5",
            text="Wenn das SG8 RFF+Z19 (Referenz auf eine Messlokation) in derselben SG8 SEQ+Z37 nicht vorhanden",
        ),
        Bedingung(
            nummer="6",
            text="Wenn das SG8 RFF+Z23 (Referenz auf Rechenschritt) in derselben SG8 SEQ+Z37 nicht vorhanden",
        ),
        Bedingung(
            nummer="7", text="Wenn in derselben SG8 SEQ+Z37 das SG8 RFF+Z19 (Referenz auf eine Messlokation) vorhanden"
        ),
        Bedingung(
            nummer="8",
            text="Rechenschrittidentifikator aus einem SG8 SEQ+Z37 (Bestandteil des Rechenschritts) DE1050 desselben SG5 IDE+24",
        ),
        Bedingung(
            nummer="9",
            text="Der hier angegebene Rechenschrittidentifikator darf nicht identisch mit dem Rechenschrittidentifikator aus diesem SG8 SEQ+Z37 DE1050 sein",
        ),
        Bedingung(nummer="10", text="wenn vorhanden"),
        Bedingung(
            nummer="11",
            text="Wenn in SG8 SEQ+Z37 SG9 CCI+++Z86 CAV+Z69/Z70 (Addition / Subtraktion) vorhanden, darf es in dem Vorgang beliebig viele weitere SG8 SEQ+Z37 mit identischem Rechenschrittidentifikator geben, die jedoch ausschließlich die Operatoren Z69/Z70 enthalten dürfen",
        ),
        Bedingung(
            nummer="13",
            text="Wenn in SG8 SEQ+Z37 SG9 CCI+++Z86 CAV+Z80/Z81 (Divisor / Dividend) vorhanden, muss in diesem Vorgang genau eine zweite SG8 SEQ+Z37 mit identischen Rechenschrittidentifikator vorhanden sein, sodass das eine SG8 SEQ+Z37 den Operator Z80 (Divisor) und das andere SG8 SEQ+Z37 den Operator Z81 (Dividend) enthält",
        ),
        Bedingung(
            nummer="14",
            text="Wenn in SG8 SEQ+Z37 SG9 CCI+++Z86 CAV+Z82 (Faktor) vorhanden, darf es in dem Vorgang beliebig viele weitere SG8 SEQ+Z37 mit identischem Rechenschrittidentifikator geben, die jedoch ausschließlich CAV+Z82 enthalten",
        ),
        Bedingung(
            nummer="15",
            text="Wenn in einem SG5 IDE+24 nur eine SEQ+Z37 mit einer SG8 RFF+Z19 (Messlokation) vorhanden ist",
        ),
        Bedingung(
            nummer="16",
            text="Der hier angegebene Code des Prüfschritt muss im EBD dem Cluster Zustimmung zugeordnet sein",
        ),
        Bedingung(
            nummer="17",
            text="Der hier angegebene Code des Prüfschritt muss im EBD dem Cluster Ablehnung zugeordnet sein",
        ),
        Bedingung(nummer="18", text="Wenn MP-ID in SG2 NAD+MR (Nachrichtenempfänger) in der Rolle LF"),
        Bedingung(
            nummer="21",
            text="Wenn in dieser CAV+ZD3 der Wert im DE7110 mit Z32 (sonstiger Zählzeitdefinitionstyp) vorhanden ist",
        ),
        Bedingung(nummer="22", text="Wenn MP-ID in SG2 NAD+MS (Nachrichtenabsender) in der Rolle NB"),
        Bedingung(nummer="24", text="Wenn SG5 STS+Z36+Z45 (Definitionen werden verwendet) vorhanden"),
        Bedingung(nummer="25", text="Wenn MP-ID in SG2 NAD+MR (Nachrichtenempfänger) in der Rolle LF"),
        Bedingung(nummer="26", text="sofern per ORDERS reklamiert"),
        Bedingung(nummer="27", text="Wenn in SG9 CAV+ZD4+Z26 (keine Verwendung des Hochlastzeitfensters) vorhanden"),
        Bedingung(
            nummer="29",
            text="Wenn in SG8 SEQ+Z43 DTM+Z33 (Zählzeitänderungszeitpunkt) im DE2379 der Code 303 vorhanden",
        ),
        Bedingung(
            nummer="30",
            text="Der Wert von CCYY in diesem DE muss genau um eins höher sein, als der Wert CCYY des SG5 DTM+Z34 (Gültigkeitsbeginn) DE2380",
        ),
        Bedingung(nummer="31", text="Wenn im DE2379 dieses Segments der Code 303 vorhanden"),
        Bedingung(
            nummer="32",
            text="Der Zeitpunkt in diesem DE muss ≥ dem Zeitpunkt aus dem DE2380 des Gültigkeitsbeginn der ausgerollten Definition (SG5 DTM+Z34) sein",
        ),
        Bedingung(
            nummer="33",
            text="Der Zeitpunkt in diesem DE muss ≤ dem Zeitpunkt aus dem DE2380 des Gültigkeitsende der ausgerollten Definition (SG5 DTM+Z35) sein",
        ),
        Bedingung(nummer="34", text="Wenn im DE2379 dieses Segments der Code 401 vorhanden"),
        Bedingung(
            nummer="36",
            text="Wenn in SG8 SEQ+Z43 DTM+Z33 (Zählzeitänderungszeitpunkt) im DE2379 der Code 401 vorhanden",
        ),
        Bedingung(nummer="37", text="Wenn ein Gültigkeitsende bereits angegeben werden kann."),
        Bedingung(nummer="41", text="Wenn SG8 SEQ+Z42 (Zählzeitdefinition) vorhanden"),
        Bedingung(
            nummer="42",
            text="Der in diesem Datenlement angegebene Code der Schaltzeitdefinition muss innerhalb eines Vorgangs (IDE) eindeutig sein.",
        ),
        Bedingung(
            nummer="43",
            text="Der in diesem Datenlement angegebene Code der Leistungskurvendefinition muss innerhalb eines Vorgangs (IDE) eindeutig sein.",
        ),
        Bedingung(
            nummer="44",
            text="Der in diesem Datenlement angegebene Code der Zählzeitdefinition muss innerhalb eines Vorgangs (IDE) eindeutig sein.",
        ),
        Bedingung(
            nummer="46",
            text="Wenn in SG8 SEQ+Z73 DTM+Z44 (Schaltzeitänderungszeitpunkt) im DE2379 der Code 303 vorhanden",
        ),
        Bedingung(
            nummer="47",
            text="Wenn in SG8 SEQ+Z73 DTM+Z44 (Schaltzeitänderungszeitpunkt) im DE2379 der Code 401 vorhanden",
        ),
        Bedingung(
            nummer="48",
            text="Wenn in SG8 SEQ+Z74 DTM+Z45 (Leistungskurvenänderungszeitpunkt) im DE2379 der Code 303 vorhanden",
        ),
        Bedingung(
            nummer="49",
            text="Wenn in SG8 SEQ+Z74 DTM+Z45 (Leistungskurvenänderungszeitpunkt) im DE2379 der Code 401 vorhanden",
        ),
        Bedingung(
            nummer="50",
            text="In jedem DE2379 dieses DTM-Segments innerhalb eines IDE+24 (Vorgangs) muss der gleiche Code angegeben werden",
        ),
        Bedingung(
            nummer="490",
            text="wenn Wert in diesem DE, an der Stelle CCYYMMDD ein Datum aus dem angegeben Zeitraum der Tabelle Kapitel 3.5 „Prozesszeitpunkt bei MESZ mit UTC“ ist",
        ),
        Bedingung(
            nummer="491",
            text="wenn Wert in diesem DE, an der Stelle CCYYMMDD ein Datum aus dem angegeben Zeitraum der Tabelle Kapitel 3.6 „Prozesszeitpunkt bei MEZ mit UTC“ ist",
        ),
        Bedingung(
            nummer="494",
            text="Das hier genannte Datum muss der Zeitpunkt sein, zu dem das Dokument erstellt wurde, oder ein Zeitpunkt, der davor liegt.",
        ),
        Bedingung(nummer="500", text="Hinweis: Zeitpunkt, ab dem die Berechnungsformel anzuwenden ist"),
        Bedingung(nummer="501", text="Hinweis: Verwendung der ID der Marktlokation"),
        Bedingung(nummer="502", text="Hinweis: Verwendung der ID der Messlokation"),
        Bedingung(
            nummer="504",
            text="Hinweis: Wert aus BGM+Z55 DE1004 der ORDERS mit der die Reklamation einer Definition erfolgt ist",
        ),
        Bedingung(nummer="505", text="Hinweis: Jede ausgerollte Zählzeitdefinition ist in einem eigenen IDE anzugeben"),
        Bedingung(nummer="506", text="Hinweis: Zeitpunkt, ab dem die Übersicht der Zählzeitdefinitionen gültig ist"),
        Bedingung(nummer="507", text="Hinweis: Es ist die Zeit nach der deutschen gesetzlichen Zeit anzugeben"),
        Bedingung(nummer="508", text="Hinweis: Zeitpunkt, ab dem die Übersicht der Schaltzeitdefinitionen gültig ist"),
        Bedingung(
            nummer="509", text="Hinweis: Zeitpunkt, ab dem die Übersicht der Leistungskurvendefinition gültig ist"
        ),
        Bedingung(
            nummer="510",
            text="Hinweis: Für jeden Zählzeitänderungszeitpunkt (SG8 DTM+Z33) ist diese Sementgruppe einmal anzugeben",
        ),
        Bedingung(
            nummer="511",
            text="Hinweis: Der Zählzeitänderungszeitpunkt (SG8DTM+Z33) dieser SG8 darf in keiner anderen SG8 „Zählzeitdefinition“ wiederholt werden",
        ),
        Bedingung(
            nummer="512",
            text="Hinweis: Wenn der Code 303 im DE2379 des Zählzeitänderungszeitpunkt (SG8 DTM+Z33) genutzt wird, muss genau ein Wert im DE2380 des Zählzeitänderungszeitpunkt (SG8 DTM+Z33) identisch mit dem Wert aus DE2380 des Gültigkeitsbeginn der ausgerollten Definition (SG5 DTM+Z34) sein",
        ),
        Bedingung(
            nummer="513",
            text="Hinweis: Wenn der Code 401 im DE2379 des Zählzeitänderungszeitpunkt (SG8 DTM+Z33) genutzt wird, muss genau ein Wert = 0000 im DE2380 des Zählzeitänderungszeitpunkt (SG8 DTM+Z33) sein",
        ),
        Bedingung(
            nummer="514",
            text="Hinweis: Für jeden Schaltzeitänderungszeitpunkt (SG8 DTM+Z44) ist diese Sementgruppe einmal anzugeben",
        ),
        Bedingung(
            nummer="515", text="Hinweis: Kein Schaltzeitänderungszeitpunkt (SG8 DTM+Z44) darf mehrfach vorkommen"
        ),
        Bedingung(
            nummer="516",
            text="Hinweis: Wenn der Code 303 im DE2379 des Schaltzeitänderungszeitpunkt (SG8 DTM+Z44) genutzt wird, muss genau ein Wert im DE2380 des Schaltzeitänderungszeitpunkt (SG8 DTM+Z44) identisch mit dem Wert aus DE2380 des Gültigkeitsbeginn der ausgerollten Definition (SG5 DTM+Z34) sein",
        ),
        Bedingung(
            nummer="517",
            text="Hinweis: Wenn der Code 401 im DE2379 des Schaltzeitänderungszeitpunkt (SG8 DTM+Z44) genutzt wird, muss genau ein Wert = 0000 im DE2380 des Schaltzeitänderungszeitpunkt (SG8 DTM+Z44) sein",
        ),
        Bedingung(
            nummer="518",
            text="Hinweis: Für jeden Leistungskurvenänderungszeitpunkt (SG8 DTM+Z45) ist diese Sementgruppe einmal anzugeben",
        ),
        Bedingung(
            nummer="519", text="Hinweis: Kein Leistungskurvenänderungszeitpunkt (SG8 DTM+Z45) darf mehrfach vorkommen"
        ),
        Bedingung(
            nummer="520",
            text="Hinweis: Wenn der Code 303 im DE2379 des Leistungskurvenänderungszeitpunkt (SG8 DTM+Z45) genutzt wird, muss genau ein Wert im DE2380 des Leistungskurvenänderungszeitpunkt (SG8 DTM+Z45) identisch mit dem Wert aus DE2380 des Gültigkeitsbeginn der ausgerollten Definition (SG5 DTM+Z34) sein",
        ),
        Bedingung(
            nummer="521",
            text="Hinweis: Wenn der Code 401 im DE2379 des Leistungskurvenänderungszeitpunkt (SG8 DTM+Z45)",
        ),
        Bedingung(
            nummer="522", text="Hinweis: Jede ausgerollte Schaltzeitdefinition ist in einem eigenen IDE anzugeben"
        ),
        Bedingung(
            nummer="523", text="Hinweis: Jede ausgerollte Leistungskurvendefinition ist in einem eigenen IDE anzugeben"
        ),
        Bedingung(nummer="524", text="Hinweis: Es ist der Code einer Zählzeitdefinition anzugeben"),
        Bedingung(nummer="525", text="Hinweis: Es ist der Code einer Schaltzeitdefinition anzugeben"),
        Bedingung(nummer="526", text="Hinweis: Es ist der Code einer Leistungskurvendefinition anzugeben"),
        Bedingung(
            nummer="527",
            text="Hinweis: Dieser Code ist anzugeben, wenn es sich um eine einmalig zu übermittelnde Definition handelt",
        ),
        Bedingung(
            nummer="528",
            text="Hinweis: Dieser Code ist anzugeben, wenn es sich um eine jährlich zu übermittelnde Definition handelt",
        ),
        Bedingung(nummer="912", text="Format: Wert kann mit maximal 6 Nachkommastellen angegeben werden"),
        Bedingung(nummer="913", text="Format: Mögliche Werte: 1 bis 99999"),
        Bedingung(nummer="914", text="Format: Möglicher Wert: > 0"),
        Bedingung(nummer="915", text="Format: Möglicher Wert: ≠ 1"),
        Bedingung(nummer="930", text="Format: max. 2 Nachkommastellen"),
        Bedingung(nummer="931", text="Format: ZZZ = +00"),
        Bedingung(nummer="932", text="Format: HHMM = 2200"),
        Bedingung(nummer="933", text="Format: HHMM = 2300"),
        Bedingung(nummer="947", text="Format: MMDDHHMM = 12312300"),
        Bedingung(nummer="950", text="Format: Marktlokations-ID"),
        Bedingung(nummer="951", text="Format: Zählpunktbezeichnung"),
        Bedingung(nummer="963", text="Format: Möglicher Wert: ≤ 100"),
        Bedingung(nummer="964", text="Format: HHMM ≥ 0000"),
        Bedingung(nummer="965", text="Format: HHMM ≤ 2359"),
        Bedingung(nummer="969", text="Format: Möglicher Wer: ≤ 1"),
        Bedingung(nummer="2000", text="Segment ist bis zu viermal je SG9 CCI+Z27 anzugeben"),
        Bedingung(nummer="2001", text="Segment bzw. Segmentgruppe ist genau einmal anzugeben"),
        Bedingung(
            nummer="2002",
            text="Für jeden Code der Zählzeit aus SG8 SEQ+Z42 (Zählzeitdefinition) SG9 CCI+Z39 (Code der Zählzeitdefinition) sind mindestens zwei Register anzugeben, bei denen in dieser SG8 das SG8 RFF+Z27 mit diesem Code gefüllt ist",
        ),
    ],
    ub_bedingungen=[UbBedingung(nummer="UB1", text="([931] ∧ [932] [490]) ⊻ ([931] ∧ [933] [491])")],
    pakete=[Paket(nummer="1P", text="--")],
)
