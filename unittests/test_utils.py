from pathlib import Path
from typing import Generator

import pytest

from fundamend import AhbReader
from fundamend.models.anwendungshandbuch import Anwendungsfall
from fundamend.models.kommunikationsrichtung import Kommunikationsrichtung
from fundamend.utils import parse_kommunikation_von

from .conftest import is_private_submodule_checked_out


@pytest.mark.parametrize(
    "original, expected",
    [
        pytest.param("", [], id="empty string = no directions"),
        pytest.param("LF an NB", [Kommunikationsrichtung(sender="LF", empfaenger="NB")], id="simple example"),
        pytest.param(
            "MSB an NB, LF",
            [
                Kommunikationsrichtung(sender="MSB", empfaenger="NB"),
                Kommunikationsrichtung(sender="MSB", empfaenger="LF"),
            ],
            id="two receivers, comma separated",
        ),
        pytest.param(
            "MSB an NB / LF",
            [
                Kommunikationsrichtung(sender="MSB", empfaenger="NB"),
                Kommunikationsrichtung(sender="MSB", empfaenger="LF"),
            ],
            id="two receivers, slash separated",
        ),
        pytest.param(
            "NB, LF an MSB",
            [
                Kommunikationsrichtung(sender="NB", empfaenger="MSB"),
                Kommunikationsrichtung(sender="LF", empfaenger="MSB"),
            ],
            id="two senders, comma separated",
        ),
        pytest.param(
            "NB / LF an MSB",
            [
                Kommunikationsrichtung(sender="NB", empfaenger="MSB"),
                Kommunikationsrichtung(sender="LF", empfaenger="MSB"),
            ],
            id="two senders, slash separated",
        ),
        pytest.param(
            "BIKO an NB / ÜNB",
            [
                Kommunikationsrichtung(sender="BIKO", empfaenger="NB"),
                Kommunikationsrichtung(sender="BIKO", empfaenger="ÜNB"),
            ],
            id="two receivers, slash separated but with Umlaut",
        ),
        pytest.param(
            "NB an LF\nMSB an LF, NB, ESA",
            [
                Kommunikationsrichtung(sender="NB", empfaenger="LF"),
                Kommunikationsrichtung(sender="MSB", empfaenger="LF"),
                Kommunikationsrichtung(sender="MSB", empfaenger="NB"),
                Kommunikationsrichtung(sender="MSB", empfaenger="ESA"),
            ],
            id="two lines",
        ),
        pytest.param(
            "NB an LF / MSB\r\nLF an NB, MSB",
            [
                Kommunikationsrichtung(sender="NB", empfaenger="LF"),
                Kommunikationsrichtung(sender="NB", empfaenger="MSB"),
                Kommunikationsrichtung(sender="LF", empfaenger="NB"),
                Kommunikationsrichtung(sender="LF", empfaenger="MSB"),
            ],
            id="two lines with mixed separators",
            # shit is real, I'm not making this up
        ),
        pytest.param(
            "MSB an NB/LF/ÜNB/MSB/ESA",
            [
                Kommunikationsrichtung(sender="MSB", empfaenger="NB"),
                Kommunikationsrichtung(sender="MSB", empfaenger="LF"),
                Kommunikationsrichtung(sender="MSB", empfaenger="ÜNB"),
                Kommunikationsrichtung(sender="MSB", empfaenger="MSB"),
                Kommunikationsrichtung(sender="MSB", empfaenger="ESA"),
            ],
            id="many receivers",
        ),
        pytest.param(
            "NB an LF, MSB an NB (Gas)",
            [
                Kommunikationsrichtung(sender="NB", empfaenger="LF"),
                Kommunikationsrichtung(sender="MSB", empfaenger="NB (Gas)"),
            ],
        ),
        pytest.param("NB (VNB)an NB (LPB)", [Kommunikationsrichtung(sender="NB (VNB)", empfaenger="NB (LPB)")]),
        pytest.param("Beteiligte aus Ursprungs-nachricht", None),
    ],
)
def test_parsing_kommunikation_von(original: str, expected: list[Kommunikationsrichtung] | None) -> None:
    actual = parse_kommunikation_von(original)
    assert actual == expected


def _all_anwendungsfaelle() -> Generator[Anwendungsfall, None, None]:
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")
    private_submodule_root = Path(__file__).parent.parent / "xml-migs-and-ahbs"
    assert private_submodule_root.exists() and private_submodule_root.is_dir()
    for ahb_file_path in private_submodule_root.rglob("**/*AHB*.xml"):
        ahb = AhbReader(ahb_file_path).read()
        for anwendungsfall in ahb.anwendungsfaelle:
            if anwendungsfall.is_outdated:
                continue
            yield anwendungsfall


def test_parsing_all_kommunikation_von_there_is() -> None:
    """loop over all AHB files and read the 'Kommunikation Von' Attribute of all the Anwendungsfälle"""
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")
    for anwendungsfall in _all_anwendungsfaelle():
        kommunikation_von = anwendungsfall.kommunikation_von
        if not isinstance(kommunikation_von, str):
            pytest.skip("Skipping test because 'Kommunikation Von' is not a string (anymore)")
        _ = parse_kommunikation_von(kommunikation_von)  # must not crash
