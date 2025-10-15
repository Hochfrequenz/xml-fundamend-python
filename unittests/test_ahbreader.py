from datetime import date
from pathlib import Path

import pytest
from syrupy.assertion import SnapshotAssertion

from fundamend.models.anwendungshandbuch import Anwendungsfall, Anwendungshandbuch, Bedingung, Paket, UbBedingung
from fundamend.reader import AhbReader

from .conftest import is_private_submodule_checked_out


@pytest.mark.parametrize(
    "ahb_xml_file_path, expected_date",
    [
        pytest.param(
            Path(__file__).parent / "example_files" / "UTILTS_AHB_1.1c_Lesefassung_2023_12_12_ZPbXedn.xml",
            date(2023, 10, 24),
        ),
        pytest.param(
            Path(__file__).parent / "example_files" / "UTILTS_AHB_1.1d_Konsultationsfassung_2024_04_02.xml",
            date(2024, 4, 2),
        ),
    ],
)
def test_get_publishing_date(ahb_xml_file_path: Path, expected_date: date) -> None:
    reader = AhbReader(ahb_xml_file_path)
    actual = reader.get_publishing_date()
    assert actual == expected_date


@pytest.mark.parametrize(
    "ahb_xml_file_path, expected",
    [
        pytest.param(
            Path(__file__).parent / "example_files" / "UTILTS_AHB_1.1c_Lesefassung_2023_12_12_ZPbXedn.xml", "BDEW"
        ),
        pytest.param(
            Path(__file__).parent / "example_files" / "UTILTS_AHB_1.1d_Konsultationsfassung_2024_04_02.xml", "BDEW"
        ),
    ],
)
def test_get_author(ahb_xml_file_path: Path, expected: str) -> None:
    reader = AhbReader(ahb_xml_file_path)
    actual = reader.get_author()
    assert actual == expected


@pytest.mark.parametrize(
    "ahb_xml_file_path, expected",
    [
        pytest.param(
            Path(__file__).parent / "example_files" / "UTILTS_AHB_1.1c_Lesefassung_2023_12_12_ZPbXedn.xml", "1.1c"
        ),
        pytest.param(
            Path(__file__).parent / "example_files" / "UTILTS_AHB_1.1d_Konsultationsfassung_2024_04_02.xml", "1.1d"
        ),
    ],
)
def test_get_version(ahb_xml_file_path: Path, expected: str) -> None:
    reader = AhbReader(ahb_xml_file_path)
    actual = reader.get_version()
    assert actual == expected


@pytest.mark.parametrize(
    "ahb_xml_file_path, expected_length",
    [
        pytest.param(
            Path(__file__).parent / "example_files" / "UTILTS_AHB_1.1c_Lesefassung_2023_12_12_ZPbXedn.xml", 88
        ),
    ],
)
def test_get_bedingungen(ahb_xml_file_path: Path, expected_length: int) -> None:
    reader = AhbReader(ahb_xml_file_path)
    actual = reader.get_bedingungen()
    assert len(actual) == expected_length
    assert all(isinstance(x, Bedingung) for x in actual)


@pytest.mark.parametrize(
    "ahb_xml_file_path, expected_length",
    [
        pytest.param(Path(__file__).parent / "example_files" / "UTILTS_AHB_1.1c_Lesefassung_2023_12_12_ZPbXedn.xml", 1),
    ],
)
def test_get_ub_bedingungen(ahb_xml_file_path: Path, expected_length: int) -> None:
    reader = AhbReader(ahb_xml_file_path)
    actual = reader.get_ub_bedingungen()
    assert len(actual) == expected_length
    assert all(isinstance(x, UbBedingung) for x in actual)


@pytest.mark.parametrize(
    "ahb_xml_file_path, expected_length",
    [
        pytest.param(Path(__file__).parent / "example_files" / "UTILTS_AHB_1.1c_Lesefassung_2023_12_12_ZPbXedn.xml", 1),
    ],
)
def test_get_pakete(ahb_xml_file_path: Path, expected_length: int) -> None:
    reader = AhbReader(ahb_xml_file_path)
    actual = reader.get_pakete()
    assert len(actual) == expected_length
    assert all(isinstance(x, Paket) for x in actual)
    assert not any(x for x in actual if x.nummer.startswith("["))
    assert not any(x for x in actual if x.nummer.endswith("]"))


@pytest.mark.parametrize(
    "ahb_xml_file_path, pruefidentifikator, expect_match",
    [
        pytest.param(
            Path(__file__).parent / "example_files" / "UTILTS_AHB_1.1c_Lesefassung_2023_12_12_ZPbXedn.xml",
            "25001",
            True,
        ),
        pytest.param(
            Path(__file__).parent / "example_files" / "UTILTS_AHB_1.1c_Lesefassung_2023_12_12_ZPbXedn.xml",
            "11001",
            False,
        ),
    ],
)
def test_get_anwendungsfall(ahb_xml_file_path: Path, pruefidentifikator: str, expect_match: bool) -> None:
    reader = AhbReader(ahb_xml_file_path)
    actual = reader.get_anwendungsfall(pruefidentifikator)
    if expect_match:
        assert actual is not None
        assert isinstance(actual, Anwendungsfall)
        assert actual.pruefidentifikator == pruefidentifikator
        if "UTILTS" in str(ahb_xml_file_path):
            assert actual.format == "UTILTS"
    else:
        assert actual is None


@pytest.mark.snapshot
@pytest.mark.parametrize(
    "ahb_xml_file_path",
    [
        pytest.param(
            Path(__file__).parent / "example_files" / "UTILTS_AHB_1.1c_Lesefassung_2023_12_12_ZPbXedn.xml",
            id="UTILTS_AHB_1.1c_Lesefassung_2023_12_12_ZPbXedn.xml",
        ),
        pytest.param(
            Path(__file__).parent / "example_files" / "UTILTS_AHB_1.1d_Konsultationsfassung_2024_04_02.xml",
            id="UTILTS_AHB_1.1d_Konsultationsfassung_2024_04_02.xml",
        ),
        pytest.param(
            Path(__file__).parent
            / "example_files"
            / "UTILTS_AHB_1.1d_Konsultationsfassung_2024_04_02_with_Uebertragungsdatei.xml",
            id="UTILTS_AHB_1.1d_Konsultationsfassung_2024_04_02_with_Uebertragungsdatei.xml",
        ),
    ],
)
def test_get_anwendungshandbuch(ahb_xml_file_path: Path, snapshot: SnapshotAssertion) -> None:
    reader = AhbReader(ahb_xml_file_path)
    actual = reader.read()
    assert actual is not None
    assert isinstance(actual, Anwendungshandbuch)
    assert len(actual.anwendungsfaelle) == 9
    assert {awf.pruefidentifikator for awf in actual.anwendungsfaelle} == {
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
    for awf in actual.anwendungsfaelle:
        assert any(awf.elements)
    snapshot.assert_match(actual)


@pytest.mark.parametrize(
    "ahb_xml_file_path",
    [
        pytest.param(
            Path(__file__).parent
            / "example_files"
            / "UTILTS_AHB_1.1d_Konsultationsfassung_2024_04_02_with_Uebertragungsdatei.xml",
            id="UTILTS_AHB_1.1d_Konsultationsfassung_2024_04_02_with_Uebertragungsdatei.xml",
        ),
    ],
)
def test_anwendungshandbuch_hashable(ahb_xml_file_path: Path) -> None:
    reader = AhbReader(ahb_xml_file_path)
    ahb = reader.read()
    assert isinstance(ahb, Anwendungshandbuch)
    hash_code = hash(ahb)
    assert isinstance(hash_code, int)
    hash_collection = set()
    hash_collection.add(ahb)


_xml_submodule_root: Path = Path(__file__).parent.parent / "xml-migs-and-ahbs"


@pytest.mark.snapshot()
def test_sanitizing_all_awf_beschreibungen(snapshot: SnapshotAssertion) -> None:
    """this test makes changes to the sanitation code visible."""
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")
    all_sanitized_awf_beschreibungen: set[str] = set()
    for ahb_file_path in _xml_submodule_root.rglob("**/*AHB*.xml"):
        reader = AhbReader(ahb_file_path)
        ahb = reader.read()
        for awf in ahb.anwendungsfaelle:
            if awf.is_outdated:
                continue
            all_sanitized_awf_beschreibungen.add(awf.beschreibung)
    # If you're unhappy with any specific entry in this list, better write a new unit test case in
    # test_utils.py / test_anwendungsfall_beschreibung_normalization (add more parametrization).
    # If the snapshot test fails because of updated data, just run
    # tox -e snapshots
    # and commit the updated .ambr file.
    distinct_beschreibungen_as_list = list(sorted(all_sanitized_awf_beschreibungen))
    snapshot.assert_match(distinct_beschreibungen_as_list)
