# FUNDAMEND - Formate und DAtenModelle für die ENergiewirtschaft in Deutschland

Dieses Repository enthält das Python-Paket `fundamend`, das XML-basierte MIGs und AHBs als Python-Objekte einliest.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python Versions (officially) supported](https://img.shields.io/pypi/pyversions/fundamend.svg)
![Pypi status badge](https://img.shields.io/pypi/v/fundamend)
![Unittests status badge](https://github.com/Hochfrequenz/xml-fundamend-python/workflows/Unittests/badge.svg)
![Coverage status badge](https://github.com/Hochfrequenz/xml-fundamend-python/workflows/Coverage/badge.svg)
![Linting status badge](https://github.com/Hochfrequenz/xml-fundamend-python/workflows/Linting/badge.svg)
![Black status badge](https://github.com/Hochfrequenz/xml-fundamend-python/workflows/Formatting/badge.svg)

## Sinn und Zweck
Seit 2024 bietet der BDEW (endlich) maschinenlesbare MIG- und AHB-Spezifikationen an, wo zuvor nur PDF oder Word-Dateien veröffentlicht wurden.
Das ist ein wichtiger Schritt für eine echte Digitalisierung der Marktkommunikation im deutschen Energiemarkt.

Die nun maschinenlesbaren Informationen über den Aufbau von EDIFACT-Nachrichten sind XML-basiert.

Dieses Repository enthält ein kleines Python-Paket, das die XML-Dateien einliest und als vollständig typisierte Python-Objekte zur Verfügung stellt, damit sich niemand mit XML herumschlagen muss (also am Ende des Tages Model Binding).
Das ist alles.

Hochfrequenz stellt mit [migmose](https://github.com/Hochfrequenz/migmose) und [kohlrahbi](https://github.com/Hochfrequenz/kohlrahbi) auch Tools bereit, um maschinenlesbare MIGs bzw. AHBs aus `.docx`-Dateien zu scrapen.

## Installation und Verwendung
Das Paket ist auf PyPI verfügbar und kann mit pip installiert werden:
```bash
pip install fundamend
```

### Message Implementation Guides (MIG) deserialisieren
```python
from pathlib import Path
from fundamend import MigReader, MessageImplementationGuide

# Angenommen, mig_utilts.xml enthält:
# <?xml version="1.0" encoding="UTF-8"?>
# <M_UTILTS Versionsnummer="1.1c"
#    Veroeffentlichungsdatum="24.10.2023"
#    Author="BDEW">
# ...
# </M_UTILTS>

reader = MigReader(Path("pfad/zur/mig_utils.xml"))
mig = reader.read()
assert isinstance(mig, MessageImplementationGuide)
assert mig.format == "UTILTS"
```

### Anwendungshandbuch (AHB) deserialisieren
```python
from pathlib import Path
from fundamend import AhbReader, Anwendungshandbuch

# Angenommen, ahb_utilts.xml enthält:
# <?xml version="1.0" encoding="UTF-8"?>
# <AHB Versionsnummer="1.1d"
#    Veroeffentlichungsdatum="02.04.2024"
#    Author="BDEW">
#    <AWF Pruefidentifikator="25001" Beschreibung="Berechnungsformel" Kommunikation_von="NB an MSB / LF">
#    ...
#   </AWF>
# </AHB>

reader = AhbReader(Path("pfad/zur/ahb_utils.xml"))
ahb = reader.read()
assert isinstance(ahb, Anwendungshandbuch)
assert {awf.pruefidentifikator for awf in ahb.anwendungsfaelle} == {
    "25001",
    "25002",
    "25003",
    "25004",
    "25005",
    "25006",
    "25007",
    "25008",
    "25009",
}
```

Die vollständigen Beispiele finden sich in den [unittests](unittests):
- Beispiel [AHB UTILTS](unittests/example_ahb_utilts_11d.py)
- Beispiel [MIG UTILTS](https://github.com/Hochfrequenz/xml-fundamend-python/blob/main/unittests/example_migs.py)

### Pydantic
Die Datenmodelle, die von `AhbReader` und `MigReader` zurückgegeben werden, sind pydantic Objekte.

Mit Pydantic können die Ergebnisse auch leicht bspw. als JSON exportiert werden (was auch über ein CLI-Tool im nächsten Abschnitt) noch einfacher möglich ist.
```python
from pathlib import Path

from pydantic import RootModel
from fundamend import Anwendungshandbuch, AhbReader

ahb = AhbReader(Path("UTILTS_AHB_1.1d_Konsultationsfassung_2024_04_02.xml")).read()
ahb_json = RootModel[Anwendungshandbuch](ahb).model_dump(mode="json")
```

Das Ergebnis sieht dann so aus:
```json
{
  "veroeffentlichungsdatum": "2024-04-02",
  "autor": "BDEW",
  "versionsnummer": "1.1d",
  "anwendungsfaelle": [
    {
      "pruefidentifikator": "25001",
      "beschreibung": "Berechnungsformel",
      "kommunikation_von": "NB an MSB / LF",
      "format": "UTILTS",
      "segments": [
        {
          "id": "UNH",
          "name": "Nachrichten-Kopfsegment",
          "number": "00001",
          "ahb_status": "Muss",
          "data_elements": [
            {
              "id": "D_0062",
              "name": "Nachrichten-Referenznummer",
              "codes": []
            },
```

### SQL Models
Die Daten aus den XML-Dateien (Stand 2025-02-10 nur AHBs) lassen sich auch in Datenbanken persistieren.
Die dazu verwendeten [SQLModel](https://sqlmodel.tiangolo.com/)-Klassen lassen sich mit `fundamend[sqlmodel]` installieren.
Instanzen der Pydantic-Klassen lassen sich in SQL-Models überführen und umgekehrt:
```python
from fundamend.models.anwendungshandbuch import Anwendungshandbuch as PydanticAnwendunghandbuch
from fundamend.sqlmodels.anwendungshandbuch import Anwendungshandbuch as SqlAnwendungshandbuch

my_sql_model = SqlAnwendungshandbuch.from_model(pydantic_ahb)
pydantic_ahb = my_sql_model.to_model()
```

#### Befüllen einer Datenbank mit AHB-Informationen
In den XML-Rohdaten sind die Informationen aus den AHBs theoretisch beliebig tief verschachtelt, weil jede Segmentgruppe ihrerseits wieder Segmentgruppen enthalten kann.
Diese Rekursion ist so auch in den SQL-Model-Klassen und der Datenbank abgebildet.
Dieses Paket liefert eine Hilfsfunktion, die die AHBs wieder "flach" zieht, sodass die Datenstruktur mit den flachen AHBs aus bspw. den PDF-Dateien vergleichbar ist, ohne jedoch die Strukturinformationen zu verlieren.
Dazu wird eine rekursive Common Table Expression (CTE) verwendet, um eine zusätzliche Hilfstabelle `ahb_hierarchy_materialized` zu befüllen.

```python
# pip install fundamend[sqlmodel]
from pathlib import Path
from fundamend.sqlmodels.ahbview import create_db_and_populate_with_ahb_view
from fundamend.sqlmodels.anwendungshandbuch import AhbHierarchyMaterialized
from sqlmodel import Session, create_engine, select
ahb_paths = [
    Path("UTILTS_AHB_1.1c_Lesefassung_2023_12_12_ZPbXedn.xml"),
    # add more AHB XML files here
]
sqlite_file = create_db_and_populate_with_ahb_view(ahb_paths) # copy the file to somewhere else if necessary
engine = create_engine(f"sqlite:///{sqlite_file}")
with Session(bind=engine) as session:
    stmt = select(AhbHierarchyMaterialized).where(AhbHierarchyMaterialized.pruefidentifikator == "25001").order_by(
            AhbHierarchyMaterialized.sort_path
        )
    results = session.exec(stmt).all()
```
oder in plain SQL:
```sql
-- sqlite dialect
SELECT path,
       type,
       segmentgroup_name,
       segmentgroup_ahb_status,
       segment_id,
       segment_name,
       segment_ahb_status,
       dataelementgroup_id,
       dataelementgroup_name,
       dataelement_id,
       dataelement_name,
       dataelement_ahb_status,
       code_value,
       code_name,
       code_ahb_status
FROM ahb_hierarchy_materialized
WHERE pruefidentifikator = '25001'
ORDER BY sort_path;
```
<details>
<summary>Ergebnisse des `SELECT`</summary>
<br>
... 125 andere Zeilen ...

| path | type | segmentgroup\_name | segmentgroup\_ahb\_status | segment\_id | segment\_name | segment\_ahb\_status | dataelementgroup\_id | dataelementgroup\_name | dataelement\_id | dataelement\_name | dataelement\_ahb\_status | code\_value |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Vorgang &gt; Bestandteil des Rechenschritts | segment\_group | Bestandteil des Rechenschritts | Muss \[2006\] | null | null | null | null | null | null | null | null | null |
| Vorgang &gt; Bestandteil des Rechenschritts &gt; Bestandteil des Rechenschritts | segment | Bestandteil des Rechenschritts | Muss \[2006\] | SEQ | Bestandteil des Rechenschritts | Muss | null | null | null | null | null | null |
| Vorgang &gt; Bestandteil des Rechenschritts &gt; Bestandteil des Rechenschritts &gt; Handlung, Code | dataelement | Bestandteil des Rechenschritts | Muss \[2006\] | SEQ | Bestandteil des Rechenschritts | Muss | null | null | D\_1229 | Handlung, Code | null | null |
| Vorgang &gt; Bestandteil des Rechenschritts &gt; Bestandteil des Rechenschritts &gt; Handlung, Code &gt; Bestandteil des Rechenschritts | code | Bestandteil des Rechenschritts | Muss \[2006\] | SEQ | Bestandteil des Rechenschritts | Muss | null | null | D\_1229 | Handlung, Code | null | Z37 |
| Vorgang &gt; Bestandteil des Rechenschritts &gt; Bestandteil des Rechenschritts &gt; Information über eine Folge | dataelementgroup | Bestandteil des Rechenschritts | Muss \[2006\] | SEQ | Bestandteil des Rechenschritts | Muss | C\_C286 | Information über eine Folge | null | null | null | null |
| Vorgang &gt; Bestandteil des Rechenschritts &gt; Bestandteil des Rechenschritts &gt; Information über eine Folge &gt; Rechenschrittidentifikator | dataelement | Bestandteil des Rechenschritts | Muss \[2006\] | SEQ | Bestandteil des Rechenschritts | Muss | C\_C286 | Information über eine Folge | D\_1050 | Rechenschrittidentifikator | X \[913\] | null |
| Vorgang &gt; Bestandteil des Rechenschritts &gt; Referenz auf eine Zeitraum-ID | segment | Bestandteil des Rechenschritts | Muss \[2006\] | RFF | Referenz auf eine Zeitraum-ID | Muss | null | null | null | null | null | null |
| Vorgang &gt; Bestandteil des Rechenschritts &gt; Referenz auf eine Zeitraum-ID &gt; Referenz | dataelementgroup | Bestandteil des Rechenschritts | Muss \[2006\] | RFF | Referenz auf eine Zeitraum-ID | Muss | C\_C506 | Referenz | null | null | null | null |
| Vorgang &gt; Bestandteil des Rechenschritts &gt; Referenz auf eine Zeitraum-ID &gt; Referenz &gt; Referenz, Qualifier | dataelement | Bestandteil des Rechenschritts | Muss \[2006\] | RFF | Referenz auf eine Zeitraum-ID | Muss | C\_C506 | Referenz | D\_1153 | Referenz, Qualifier | null | null |
| Vorgang &gt; Bestandteil des Rechenschritts &gt; Referenz auf eine Zeitraum-ID &gt; Referenz &gt; Referenz, Qualifier &gt; Referenz auf Zeitraum-ID | code | Bestandteil des Rechenschritts | Muss \[2006\] | RFF | Referenz auf eine Zeitraum-ID | Muss | C\_C506 | Referenz | D\_1153 | Referenz, Qualifier | null | Z46 |
| Vorgang &gt; Bestandteil des Rechenschritts &gt; Referenz auf eine Zeitraum-ID &gt; Referenz &gt; Referenz auf Zeitraum-ID | dataelement | Bestandteil des Rechenschritts | Muss \[2006\] | RFF | Referenz auf eine Zeitraum-ID | Muss | C\_C506 | Referenz | D\_1154 | Referenz auf Zeitraum-ID | X \[914\] ∧ \[937\] \[59\] | null |

...
</details>

<details>
<summary>Finde heraus, welche Zeilen in einem Prüfidentifikator zwischen zwei Versionen hinzukommen</summary>
<br>
    
```sql
    with fv2504 as (SELECT *
                FROM ahb_hierarchy_materialized
                WHERE pruefidentifikator = '55014'
                  and edifact_format_version = 'FV2504'
                ORDER BY sort_path ASC),
     fv2410 as (SELECT *
                FROM ahb_hierarchy_materialized
                WHERE pruefidentifikator = '55014'
                  and edifact_format_version = 'FV2410'
                ORDER BY sort_path ASC)
SELECT fv2504.path
FROM fv2504
         LEFT JOIN fv2410 on fv2504.id_path = fv2410.id_path
WHERE fv2410.id is null -- alle zeilen, die so im fv2410 ahb nicht vorhanden waren
ORDER BY fv2504.sort_path;
```

</details>

### CLI Tool für XML➡️JSON Konvertierung
Mit
```bash
pip install fundamend[cli]
```
Kann ein CLI-Tool in der entsprechenden venv installiert werden, das einzelne MIG- und AHB-XML-Dateien in entsprechende JSONs konvertiert:
```bash
(myvenv): xml2json --xml-path path/to/mig.xml
```
erzeugt `path/to/mig.json`. Und
```bash
(myvenv): xml2json --xml-path path/to/my/directory
```
konvertiert alle XML-Dateien im entsprechenden Verzeichnis.

### JSON Schemas
Das fundamend Datenmodell ist auch als JSON Schema verfügbar: [`json_schemas`](json_schemas).

## Verwendung und Mitwirken
Der Code ist MIT-lizenziert und kann daher frei verwendet werden.
Wir freuen uns über Pull Requests an den main-Branch dieses Repositories.

## Hochfrequenz
Die [Hochfrequenz Unternehmensberatung GmbH](https://www.hochfrequenz.de) ist eine Beratung für Energieversorger im deutschsprachigen Raum.
Wir arbeiten größtenteils remote, haben aber auch Büros in Berlin, Bremen, Leipzig, Köln und Grünwald und attraktive [Stellenangebote](https://www.hochfrequenz.de/index.php/karriere/aktuelle-stellenausschreibungen/full-stack-entwickler).
