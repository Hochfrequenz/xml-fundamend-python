from datetime import date
from pathlib import Path

import pytest

from bamx.reader import MigReader


@pytest.mark.parametrize(
    "mig_xml_file_path, expected_date",
    [
        pytest.param(
            Path(__file__).parent / "example_files" / "UTILTS_MIG_1.1c_Lesefassung_2023_12_12.xml", date(2023, 10, 24)
        ),
        pytest.param(
            Path(__file__).parent / "example_files" / "UTILTS_MIG_1.1d_Konsultationsfassung_2024_04_02.xml",
            date(2024, 4, 2),
        ),
    ],
)
def test_get_publishing_date(mig_xml_file_path: Path, expected_date: date) -> None:
    reader = MigReader(mig_xml_file_path)
    actual = reader.get_publishing_date()
    assert actual == expected_date


@pytest.mark.parametrize(
    "mig_xml_file_path, expected",
    [
        pytest.param(Path(__file__).parent / "example_files" / "UTILTS_MIG_1.1c_Lesefassung_2023_12_12.xml", "BDEW"),
        pytest.param(
            Path(__file__).parent / "example_files" / "UTILTS_MIG_1.1d_Konsultationsfassung_2024_04_02.xml", "BDEW"
        ),
    ],
)
def test_get_author(mig_xml_file_path: Path, expected: str) -> None:
    reader = MigReader(mig_xml_file_path)
    actual = reader.get_author()
    assert actual == expected


@pytest.mark.parametrize(
    "mig_xml_file_path, expected",
    [
        pytest.param(Path(__file__).parent / "example_files" / "UTILTS_MIG_1.1c_Lesefassung_2023_12_12.xml", "1.1c"),
        pytest.param(
            Path(__file__).parent / "example_files" / "UTILTS_MIG_1.1d_Konsultationsfassung_2024_04_02.xml", "1.1d"
        ),
    ],
)
def test_get_version(mig_xml_file_path: Path, expected: str) -> None:
    reader = MigReader(mig_xml_file_path)
    actual = reader.get_version()
    assert actual == expected
