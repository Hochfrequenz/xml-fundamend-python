from typing import Optional

import pytest

from fundamend.utils import remove_unnecessary_hyphens


@pytest.mark.parametrize(
    "argument,expected",
    [
        pytest.param("Summen-zeitreihe", "Summenzeitreihe", id="13003"),
        pytest.param("EEG-Überführungs-ZR", "EEG-Überführungs-ZR", id="13005"),
        pytest.param("TEP vergh. Werte Referenz-messung", "TEP vergh. Werte Referenzmessung", id="13012"),
        pytest.param(
            "marktlokations- scharfe Allokationsliste Gas (MMMA)",
            "marktlokations- scharfe Allokationsliste Gas (MMMA)",
            id="13013",
        ),
        pytest.param(
            "marktlokations- scharfe bilanzierte Menge Strom / Gas (MMMA)",
            "marktlokations- scharfe bilanzierte Menge Strom / Gas (MMMA)",
            id="13014",
        ),
        pytest.param(
            "Arbeit Leistungs-max. Kalenderjahr vor Lieferbeginn",
            "Arbeit Leistungsmax. Kalenderjahr vor Lieferbeginn",
            id="13015",
        ),
        pytest.param("Energie-menge u. Leistungs-max. (Strom)", "Energiemenge u. Leistungsmax. (Strom)", id="13016"),
        pytest.param(
            "Lastgang Messlokation, Netzkoppel-punkt, Netzlokation",
            "Lastgang Messlokation, Netzkoppelpunkt, Netzlokation",
            id="13018",
        ),
        pytest.param("Energie-menge (Strom)", "Energiemenge (Strom)", id="13019"),
        pytest.param("Ausfallarbeits-überführungszeitreihe", "Ausfallarbeitsüberführungszeitreihe", id="13020"),
        pytest.param(
            "Redispatch 2.0 Ausfallarbeits-summenzeitreihe", "Redispatch 2.0 Ausfallarbeitssummenzeitreihe", id="13023"
        ),
        pytest.param(
            "EEG-Überführungs-ZR aufgrund Ausfallarbeit", "EEG-Überführungs-ZR aufgrund Ausfallarbeit", id="13026"
        ),
        pytest.param("Grundlage POG-Ermittlung", "Grundlage POG-Ermittlung", id="13028"),
        pytest.param(
            "Ab-/Bestellung BK-SZR auf Aggregationsebene RZ",
            "Ab-/Bestellung BK-SZR auf Aggregationsebene RZ",
            id="17207",
        ),
        pytest.param("Anforderung Clearingliste ÜNB-DZR", "Anforderung Clearingliste ÜNB-DZR", id="17208"),
        pytest.param(
            "Bestäti-gung der Ab-/Bestellung von Werten", "Bestätigung der Ab-/Bestellung von Werten", id="19011"
        ),
        pytest.param("Ablehnung der Ab-/Bestellung von Werten", "Ablehnung der Ab-/Bestellung von Werten", id="19012"),
        pytest.param(
            "Bestäti-gung der Stornier-ung einer Bestellung", "Bestätigung der Stornierung einer Bestellung", id="19013"
        ),
        pytest.param(
            "Ablehnung der Stornier-ung einer Bestellung", "Ablehnung der Stornierung einer Bestellung", id="19014"
        ),
        pytest.param("Bestätigung Sperr-/Entsperrauftrag", "Bestätigung Sperr-/Entsperrauftrag", id="19116"),
        pytest.param("Ablehnung Sperr-/Entsperrauftrag", "Ablehnung Sperr-/Entsperrauftrag", id="19117"),
        pytest.param(
            "Bestätigung Stornierung Sperr-/Entsperrauftrag",
            "Bestätigung Stornierung Sperr-/Entsperrauftrag",
            id="19128",
        ),
        pytest.param(
            "Ablehnung Stornierung Sperr-/Entsperrauftrag", "Ablehnung Stornierung Sperr-/Entsperrauftrag", id="19129"
        ),
        pytest.param(
            "Ablehnung Ab-/Bestellung Aggregationsebene", "Ablehnung Ab-/Bestellung Aggregationsebene", id="19204"
        ),
        pytest.param("Status-meldung", "Statusmeldung", id="21003"),
        pytest.param("Status-meldung", "Statusmeldung", id="21004"),
        pytest.param("Status-meldung", "Statusmeldung", id="21005"),
        pytest.param("Status-meldung", "Statusmeldung", id="21009"),
        pytest.param("Status-meldung", "Statusmeldung", id="21010"),
        pytest.param("Status-meldung", "Statusmeldung", id="21011"),
        pytest.param("Status-meldung", "Statusmeldung", id="21012"),
        pytest.param("Status-meldung", "Statusmeldung", id="21013"),
        pytest.param("Status-meldung", "Statusmeldung", id="21024"),
        pytest.param("Status-meldung", "Statusmeldung", id="21025"),
        pytest.param("Status-meldung", "Statusmeldung", id="21026"),
        pytest.param("Status-meldung", "Statusmeldung", id="21027"),
        pytest.param("Vorabinfor-mation", "Vorabinformation", id="21029"),
        pytest.param("iMS-Ersteinbau-zust.", "iMS-Ersteinbauzust.", id="21030"),
        pytest.param("Bestellungsantwort / -mitteilung", "Bestellungsantwort / -mitteilung", id="21043"),
        pytest.param("Bearbeitungs-standsmeldung", "Bearbeitungsstandsmeldung", id="21047"),
        pytest.param("Störungs-meldung", "Störungsmeldung", id="23001"),
        pytest.param("Bestäti-gung", "Bestätigung", id="23004"),
        pytest.param("Informations-meldung", "Informationsmeldung", id="23005"),
        pytest.param("Ergebnis-bericht", "Ergebnisbericht", id="23008"),
        pytest.param("Informations-meldung", "Informationsmeldung", id="23009"),
        pytest.param("Informations-meldung", "Informationsmeldung", id="23011"),
        pytest.param("Informations-meldung", "Informationsmeldung", id="23012"),
        pytest.param(
            "Übermittlung der Ausgleichs-energiepreise", "Übermittlung der Ausgleichsenergiepreise", id="27001"
        ),
        pytest.param(
            "Preisblatt Messstellenbe-trieb / Konfigurationen",
            "Preisblatt Messstellenbetrieb / Konfigurationen",
            id="27002a",
        ),
        pytest.param("Preisblätter MSB-Leistungen", "Preisblätter MSB-Leistungen", id="27002b"),
        pytest.param("Preisblätter NB-Leistungen", "Preisblätter NB-Leistungen", id="27003"),
        pytest.param("Abschlags-rechnung", "Abschlagsrechnung", id="31001"),
        pytest.param("NN-Rechnung", "NN-Rechnung", id="31002"),
        pytest.param("WiM-Rechnung", "WiM-Rechnung", id="31003"),
        pytest.param("MMM-Rechnung", "MMM-Rechnung", id="31005"),
        pytest.param("MMM-selbst ausgest. Rechnung", "MMM-selbst ausgest. Rechnung", id="31006"),
        pytest.param("Aggreg. MMM-Rechnung", "Aggreg. MMM-Rechnung", id="31007"),
        pytest.param("Aggreg. MMM-selbst ausgest. Rechnung", "Aggreg. MMM-selbst ausgest. Rechnung", id="31008"),
        pytest.param("MSB-Rechnung", "MSB-Rechnung", id="31009"),
        pytest.param("Stornierung Sperr-/Entsperrauftrag", "Stornierung Sperr-/Entsperrauftrag", id="39000"),
        pytest.param("Abmelde-anfrage des NB", "Abmeldeanfrage des NB", id="44010"),
        pytest.param("Bestätigung Abmelde-anfrage", "Bestätigung Abmeldeanfrage", id="44011"),
        pytest.param("Ablehnung Abmelde-anfrage", "Ablehnung Abmeldeanfrage", id="44012"),
        pytest.param(
            "Bestands-liste zugeordnete Marktlokationenen", "Bestandsliste zugeordnete Marktlokationenen", id="44019"
        ),
        pytest.param("Änderungs-meldung zur Bestands-liste", "Änderungsmeldung zur Bestandsliste", id="44020"),
        pytest.param(
            "Antwort auf Änderungs-meldung zur Bestands-liste",
            "Antwort auf Änderungsmeldung zur Bestandsliste",
            id="44021",
        ),
        pytest.param("Antwort auf die Geschäftsdaten-anfrage", "Antwort auf die Geschäftsdatenanfrage", id="44060"),
        pytest.param("Stammdaten zur Markt-lokation", "Stammdaten zur Marktlokation", id="44103"),
        pytest.param(
            "Aktualisierte Stammdaten zur Markt-lokation", "Aktualisierte Stammdaten zur Marktlokation", id="44104"
        ),
        pytest.param(
            "Ablehnung auf Stammdaten zur Markt-lokation", "Ablehnung auf Stammdaten zur Marktlokation", id="44105"
        ),
        pytest.param("Anfrage an MSB mit Abhängig-keiten", "Anfrage an MSB mit Abhängigkeiten", id="44143"),
        pytest.param("Anfrage an MSB mit Abhängig-keiten", "Anfrage an MSB mit Abhängigkeiten", id="44147"),
        pytest.param("Anfrage an MSB mit Abhängig-keiten", "Anfrage an MSB mit Abhängigkeiten", id="44148"),
        pytest.param("Verpflicht-ungsanfrage / Aufforderung", "Verpflichtungsanfrage / Aufforderung", id="44168"),
        pytest.param("Bestätigung Verpflicht-ungsanfrage", "Bestätigung Verpflichtungsanfrage", id="44169"),
        pytest.param("Ablehnung Verpflicht-ungsanfrage", "Ablehnung Verpflichtungsanfrage", id="44170"),
        pytest.param("#nv# Anfrage an MSB mit Abhängig-keiten", "#nv# Anfrage an MSB mit Abhängigkeiten", id="44172"),
        pytest.param("Änderung der Marktlokations-struktur", "Änderung der Marktlokationsstruktur", id="44175"),
        pytest.param(
            "Antwort auf Änderung der Marktlokations-struktur",
            "Antwort auf Änderung der Marktlokationsstruktur",
            id="44176",
        ),
        pytest.param("Anfrage der Markt-lokations-struktur", "Anfrage der Marktlokationsstruktur", id="44180"),
        pytest.param(
            "Antwort auf Anfrage der Markt-lokations-struktur",
            "Antwort auf Anfrage der Marktlokationsstruktur",
            id="44181",
        ),
        pytest.param(
            "Ablehnung der Anfrage der Markt-lokations-struktur",
            "Ablehnung der Anfrage der Marktlokationsstruktur",
            id="44182",
        ),
        pytest.param("Abmeldung / Beendig-ung der Zuordnung", "Abmeldung / Beendigung der Zuordnung", id="55007"),
        pytest.param("Abmelde-anfrage des NB", "Abmeldeanfrage des NB", id="55010"),
        pytest.param("Bestätigung Abmelde-anfrage", "Bestätigung Abmeldeanfrage", id="55011"),
        pytest.param("Ablehnung Abmelde-anfrage", "Ablehnung Abmeldeanfrage", id="55012"),
        pytest.param("Deaktivier-ung von ZP", "Deaktivierung von ZP", id="55063"),
        pytest.param("Lieferanten-clearingliste", "Lieferantenclearingliste", id="55065"),
        pytest.param(
            "Korrekturliste zur Lieferanten-clearingliste", "Korrekturliste zur Lieferantenclearingliste", id="55066"
        ),
        pytest.param("Aktivierung der Zuordnungs-ermächtigung", "Aktivierung der Zuordnungsermächtigung", id="55071"),
        pytest.param(
            "Deaktivierung der Zuordnungs-ermächtigung", "Deaktivierung der Zuordnungsermächtigung", id="55072"
        ),
        pytest.param("Antwort auf Stammdaten-änderung", "Antwort auf Stammdatenänderung", id="55076"),
        pytest.param("Bestätig-ung Anmeldung", "Bestätigung Anmeldung", id="55078"),
        pytest.param(
            "Bestätig-ung Anmeldung Neuanl. u. LW m. Trbild. b. N-EE+N-KWKG",
            "Bestätigung Anmeldung Neuanl. u. LW m. Trbild. b. N-EE+N-KWKG",
            id="55079",
        ),
        pytest.param("Abmelde-anfrage des NB", "Abmeldeanfrage des NB", id="55086"),
        pytest.param("Bestätigung Abmelde-anfrage", "Bestätigung Abmeldeanfrage", id="55087"),
        pytest.param("Ablehnung Abmelde-anfrage", "Ablehnung Abmeldeanfrage", id="55088"),
        pytest.param(
            "Stammdaten zur ver-brauchenden Markt-lokation", "Stammdaten zur verbrauchenden Marktlokation", id="55103"
        ),
        pytest.param(
            "Aktualisierte Stammdaten zur ver-brauchenden Markt-lokation",
            "Aktualisierte Stammdaten zur verbrauchenden Marktlokation",
            id="55104",
        ),
        pytest.param(
            "Ablehnung auf Stammdaten zur ver-brauchenden Markt-lokation",
            "Ablehnung auf Stammdaten zur verbrauchenden Marktlokation",
            id="55105",
        ),
        pytest.param(
            "Stamm-daten zur erzeugenden Markt-lokation", "Stammdaten zur erzeugenden Marktlokation", id="55106"
        ),
        pytest.param(
            "Aktualisierte Stammdaten zur erzeugenden Markt-lokation",
            "Aktualisierte Stammdaten zur erzeugenden Marktlokation",
            id="55107",
        ),
        pytest.param(
            "Ablehnung auf Stamm-daten zur erzeugenden Markt-lokation",
            "Ablehnung auf Stammdaten zur erzeugenden Marktlokation",
            id="55108",
        ),
        pytest.param("Änderung der Prognose-grundlage", "Änderung der Prognosegrundlage", id="55126a"),
        pytest.param("Abr.-Daten BK-Abr. verb. Malo", "Abr.-Daten BK-Abr. verb. Malo", id="55126b"),
        pytest.param("Anfrage an MSB mit Abhängig-keiten", "Anfrage an MSB mit Abhängigkeiten", id="55143"),
        pytest.param("Anfrage an MSB mit Abhängig-keiten", "Anfrage an MSB mit Abhängigkeiten", id="55147"),
        pytest.param("Anfrage an MSB mit Abhängig-keiten", "Anfrage an MSB mit Abhängigkeiten", id="55148"),
        pytest.param(
            "Bila.rel. Anfrage an NB ohne Abhängig-keiten", "Bila.rel. Anfrage an NB ohne Abhängigkeiten", id="55153"
        ),
        pytest.param(
            "Rückmeldung/Anfrage Abr.-Daten BK-Abr. verb. MaLo",
            "Rückmeldung/Anfrage Abr.-Daten BK-Abr. verb. MaLo",
            id="55156",
        ),
        pytest.param("Verpflicht-ungsanfrage / Aufforderung", "Verpflichtungsanfrage / Aufforderung", id="55168"),
        pytest.param("Bestätigung Verpflicht-ungsanfrage", "Bestätigung Verpflichtungsanfrage", id="55169"),
        pytest.param("Ablehnung Verpflicht-ungsanfrage", "Ablehnung Verpflichtungsanfrage", id="55170"),
        pytest.param("Anfrage an MSB mit Abhängig-keiten", "Anfrage an MSB mit Abhängigkeiten", id="55172"),
        pytest.param("Änderung der Lokations-bündelstruktur", "Änderung der Lokationsbündelstruktur", id="55173"),
        pytest.param(
            "Antwort auf Änderung der Lokations-bündelstruktur",
            "Antwort auf Änderung der Lokationsbündelstruktur",
            id="55174",
        ),
        pytest.param("Änderung der Marktlokations-struktur", "Änderung der Marktlokationsstruktur", id="55175"),
        pytest.param(
            "Antwort auf Änderung der Marktlokations-struktur",
            "Antwort auf Änderung der Marktlokationsstruktur",
            id="55176",
        ),
        pytest.param("Anfrage der Lokations-bündelstruktur", "Anfrage der Lokationsbündelstruktur", id="55177"),
        pytest.param(
            "Antwort auf Anfrage der Lokations-bündelstruktur",
            "Antwort auf Anfrage der Lokationsbündelstruktur",
            id="55178",
        ),
        pytest.param("Anfrage der Markt-lokations-struktur", "Anfrage der Marktlokationsstruktur", id="55180"),
        pytest.param(
            "Antwort auf Anfrage der Markt-lokations-struktur",
            "Antwort auf Anfrage der Marktlokationsstruktur",
            id="55181",
        ),
        pytest.param(
            "Ablehnung der Anfrage der Markt-lokations-struktur",
            "Ablehnung der Anfrage der Marktlokationsstruktur",
            id="55182",
        ),
        pytest.param("Stammdaten-synchron-isation vom NB", "Stammdatensynchronisation vom NB", id="55185"),
        pytest.param("Stammdaten-synchron-isation vom LF", "Stammdatensynchronisation vom LF", id="55186"),
        pytest.param("Stammdaten-synchron-isation vom ÜNB", "Stammdatensynchronisation vom ÜNB", id="55187"),
        pytest.param(
            "Beendigung der Aggregat-ionsverant-wortung vom NB",
            "Beendigung der Aggregationsverantwortung vom NB",
            id="55188",
        ),
        pytest.param(
            "Beendigung der Aggregat-ionsverant-wortung vom LF",
            "Beendigung der Aggregationsverantwortung vom LF",
            id="55189",
        ),
        pytest.param(
            "Beendigung der Aggregat-ionsverant-wortung vom ÜNB",
            "Beendigung der Aggregationsverantwortung vom ÜNB",
            id="55190",
        ),
        pytest.param("Antwort auf die Geschäftsdaten-anfrage", "Antwort auf die Geschäftsdatenanfrage", id="55194"),
        pytest.param("Bilanzierungs-gebiets-clearing-liste", "Bilanzierungsgebietsclearingliste", id="55195"),
        pytest.param(
            "Antwort auf Bilanzierungs-gebiets-clearing-liste",
            "Antwort auf Bilanzierungsgebietsclearingliste",
            id="55196",
        ),
        pytest.param("Aktivierung ZP LF-AASZR", "Aktivierung ZP LF-AASZR", id="55199"),
        pytest.param("Deaktivierung ZP LF-AASZR", "Deaktivierung ZP LF-AASZR", id="55200"),
        pytest.param("LF-AACL", "LF-AACL", id="55201"),
        pytest.param("Korrekturliste LF-AACL", "Korrekturliste LF-AACL", id="55202"),
        pytest.param("Antwort auf die Geschäftsdaten-anfrage", "Antwort auf die Geschäftsdatenanfrage", id="55215"),
        pytest.param("Abr.-Daten NNA", "Abr.-Daten NNA", id="55218"),
        pytest.param("Rückmeldung/Anfrage Abr.-Daten NNA", "Rückmeldung/Anfrage Abr.-Daten NNA", id="55220"),
        pytest.param("Änderung Blindabr.-Daten der NeLo", "Änderung Blindabr.-Daten der NeLo", id="55225"),
        pytest.param(
            "Rückmeldung/Anfrage Blindabr.-Daten der NeLo", "Rückmeldung/Anfrage Blindabr.-Daten der NeLo", id="55227"
        ),
        pytest.param("Änderung Blindabr.-Daten der NeLo", "Änderung Blindabr.-Daten der NeLo", id="55230"),
        pytest.param(
            "Rückmeldung/Anfrage Blindabr.-Daten der NeLo", "Rückmeldung/Anfrage Blindabr.-Daten der NeLo", id="55232"
        ),
        pytest.param(
            "Änderung vom MSB für MSB-Abrechnungsdaten des MSB an der Marktlokation",
            "Änderung vom MSB für MSB-Abrechnungsdaten des MSB an der Marktlokation",
            id="55557a",
        ),
        pytest.param("Änderung MSB-Abr.-Daten der MaLo", "Änderung MSB-Abr.-Daten der MaLo", id="55557b"),
        pytest.param(
            "Anfrage zur MSB-Abrechnungsdaten vom MSB an der Marktlokation",
            "Anfrage zur MSB-Abrechnungsdaten vom MSB an der Marktlokation",
            id="55559a",
        ),
        pytest.param(
            "Rückmeldung/Anfrage MSB-Abr.-Daten der MaLo", "Rückmeldung/Anfrage MSB-Abr.-Daten der MaLo", id="55559b"
        ),
        pytest.param("Abr.-Daten BK-Abr. verb. MaLo", "Abr.-Daten BK-Abr. verb. MaLo", id="55613"),
        pytest.param(
            "Rückmeldung/Anfrage Abr.-Daten BK-Abr. verb. MaLo",
            "Rückmeldung/Anfrage Abr.-Daten BK-Abr. verb. MaLo",
            id="55614",
        ),
        pytest.param("Stammdaten BK-Treue", "Stammdaten BK-Treue", id="55670"),
        pytest.param("Rückmeldung auf Stammdaten BK-Treue", "Rückmeldung auf Stammdaten BK-Treue", id="55671"),
        pytest.param("Abr.-Daten BK-Abr. erz. Malo", "Abr.-Daten BK-Abr. erz. Malo", id="55672"),
        pytest.param(
            "Rückmeldung/Anfrage Abr.-Daten BK-Abr. erz. Malo",
            "Rückmeldung/Anfrage Abr.-Daten BK-Abr. erz. Malo",
            id="55673",
        ),
        pytest.param("Abr.-Daten BK-Abr. erz. Malo", "Abr.-Daten BK-Abr. erz. Malo", id="55674"),
        pytest.param(
            "Rückmeldung/Anfrage Abr.-Daten BK-Abr. erz. Malo",
            "Rückmeldung/Anfrage Abr.-Daten BK-Abr. erz. Malo",
            id="55675",
        ),
        pytest.param("Änderung Paket-ID der Malo", "Änderung Paket-ID der Malo", id="55691"),
        pytest.param("Rückmeldung/Anfrage Paket-ID der Malo", "Rückmeldung/Anfrage Paket-ID der Malo", id="55692"),
        pytest.param(None, None, id="None"),
        pytest.param("", "", id="empty string"),
    ],
)
def test_sanitization_hyphens(argument: Optional[str], expected: Optional[str]) -> None:
    actual = remove_unnecessary_hyphens(argument)
    assert actual == expected
