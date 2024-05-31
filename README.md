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

Dieses Repository enthält ein kleines Python-Paket, das die XML-Dateien einliest und als vollständig typisierte Python-Objekte zur Verfügung stellt, damit sich niemand mit XML herumschlagen muss.
Das ist alles.

Hochfrequenz stellt mit [migmose](https://github.com/Hochfrequenz/migmose) auch ein Tool bereit, das maschinenlesbare MIGs aus `.docx`-Dateien scraped.

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

Die vollständigen Beispiele finden sich in den [unittests](unittests).

### Verwendung mit Pydantic
Per default verwendet fundamend die [dataclasses aus der Python-Standardlibrary](https://docs.python.org/3/library/dataclasses.html).
Es lässt sich aber auch direkt mit [Pydantic](https://docs.pydantic.dev/latest/) und den [Pydantic dataclasses](https://docs.pydantic.dev/2.7/concepts/dataclasses/) verwenden.
Wenn entweder pydantic schon installiert ist, oder mittels
```bash
pip install fundamend[pydantic]
```
mit installiert wird, dann sind Datenmodelle, die von `AhbReader` und `MigReader` zurückgegeben werden, automatisch pydantic Objekte.

Mit Pydantic können die Ergebnisse auch leicht bspw. als JSON exportiert werden:
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

### JSON Schemas
Das fundamend Datenmodell ist auch als JSON Schema verfügbar: [`json_schemas`](json_schemas).

## Verwendung und Mitwirken
Der Code ist MIT-lizenziert und kann daher frei verwendet werden.
Wir freuen uns über Pull Requests an den main-Branch dieses Repositories.

## Hochfrequenz
Die [Hochfrequenz Unternehmensberatung GmbH](https://www.hochfrequenz.de) ist eine Beratung für Energieversorger im deutschsprachigen Raum.
Wir arbeiten größtenteils remote, haben aber auch Büros in Berlin, Bremen, Leipzig, Köln und Grünwald und attraktive [Stellenangebote](https://www.hochfrequenz.de/index.php/karriere/aktuelle-stellenausschreibungen/full-stack-entwickler).
