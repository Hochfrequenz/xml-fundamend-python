from datetime import date
from pathlib import Path

import pytest

from fundamend.models.anwendungshandbuch import Anwendungsfall, Bedingung, Paket, UbBedingung
from fundamend.reader import AhbReader


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
    else:
        assert actual is None
