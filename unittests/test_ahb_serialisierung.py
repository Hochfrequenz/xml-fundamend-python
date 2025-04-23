from datetime import date
from pathlib import Path

import pytest

from fundamend.models.anwendungshandbuch import Segment as AhbSegment
from fundamend.reader import AhbReader, MigReader

from .conftest import is_private_submodule_checked_out

data_path: Path = Path(__file__).parent.parent / "xml-migs-and-ahbs"


@pytest.mark.parametrize(
    "ahb_xml_file_path, expected_date",
    [
        pytest.param(
            data_path / "FV2410" / "UTILTS_AHB_1_0_Fehlerkorrektur_20250218.xml",
            date(2025, 2, 18),
        ),
    ],
)
def test_read_ahb_xml(ahb_xml_file_path: Path, expected_date: date) -> None:
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")
    reader = AhbReader(ahb_xml_file_path)
    actual = reader.get_publishing_date()
    assert actual == expected_date


def test_deserializing_all_ahbs() -> None:
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")
    for ahb_file_path in data_path.rglob("**/*AHB*.xml"):
        reader = AhbReader(ahb_file_path)
        _ = reader.read()  # must not crash


@pytest.mark.parametrize(
    "mig_xml_file_path, expected_date",
    [
        pytest.param(
            data_path / "FV2410" / "UTILTS_MIG_1.1e_Fehlerkorrektur_20241213.xml",
            date(2024, 12, 13),
        ),
    ],
)
def test_read_mig_xml(mig_xml_file_path: Path, expected_date: date) -> None:
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")
    reader = MigReader(mig_xml_file_path)
    actual = reader.get_publishing_date()
    assert actual == expected_date


def test_deserializing_all_migs() -> None:
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")
    for mig_file_path in data_path.rglob("**/*MIG*.xml"):
        reader = MigReader(mig_file_path)
        _ = reader.read()  # must not crash


def test_uebertragungsdatei_level_flag_is_set() -> None:
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")
    reader = AhbReader(data_path / "FV2504" / "MSCONS_AHB_3_1f_Fehlerkorrektur_20250320.xml")
    ahb13012 = [awf for awf in reader.read().anwendungsfaelle if awf.pruefidentifikator == "13012"][0]
    unb_segment = ahb13012.elements[0]
    assert isinstance(unb_segment, AhbSegment) and unb_segment.id == "UNB"
    unz_segment = ahb13012.elements[-1]
    assert isinstance(unz_segment, AhbSegment) and unz_segment.id == "UNZ"
    unh_segment = [s for s in ahb13012.elements if isinstance(s, AhbSegment) and s.id == "UNH"][0]
    assert unb_segment.is_on_uebertragungsdatei_level
    assert unz_segment.is_on_uebertragungsdatei_level
    assert not unh_segment.is_on_uebertragungsdatei_level
