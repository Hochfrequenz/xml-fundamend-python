from datetime import date
from pathlib import Path

import pytest

from fundamend.reader import AhbReader, MigReader

data_path: Path = Path(__file__).parent.parent / "xml-migs-and-ahbs"


def private_submodule_is_checked_out() -> bool:
    return any(data_path.iterdir())


@pytest.mark.parametrize(
    "ahb_xml_file_path, expected_date",
    [
        pytest.param(
            data_path / "APERAK" / "APERAK_AHB_2_3n_ausserordentliche_2024_07_26_2024_04_03.xml",
            date(2024, 7, 26),
        ),
        pytest.param(
            data_path / "COMDIS" / "COMDIS_AHB_1_0e_2023_10_24_2024_04_03.xml",
            date(2023, 10, 24),
        ),
        pytest.param(
            data_path / "COMDIS" / "COMDIS_AHB_1_0f_2024_06_19_2024_11_20.xml",
            date(2024, 6, 19),
        ),
        pytest.param(
            data_path / "CONTRL" / "CONTRL_AHB_2_3n_ausserordentliche_2024_07_26_2024_04_03.xml",
            date(2024, 7, 26),
        ),
        pytest.param(
            data_path / "IFTSTA" / "IFTSTA_AHB_2_0e_ausserordentliche_2024_07_26_2024_03_11.xml",
            date(2024, 7, 26),
        ),
        pytest.param(
            data_path / "INSRPT" / "INSRPT_AHB_1_1g_ausserordentliche_2024_07_26_2023_03_23.xml",
            date(2024, 7, 26),
        ),
        pytest.param(
            data_path / "INVOIC" / "INVOIC_AHB_2_5c_Fehlerkorrektur_2024_06_17_2024_06_17.xml",
            date(2024, 6, 17),
        ),
        pytest.param(
            data_path / "MSCONS" / "MSCONS_AHB_3_1d_ausserordentliche_2024_07_26_2024_04_03.xml",
            date(2024, 7, 26),
        ),
        pytest.param(
            data_path / "ORDCHG" / "ORDCHG_AHB_2_2_Fehlerkorrektur_2024_09_23_2024_09_23.xml",
            date(2024, 9, 23),
        ),
        pytest.param(
            data_path / "ORDRSP" / "ORDRSP_AHB_2_2_Fehlerkorrektur_2024_09_23_2024_09_23.xml",
            date(2024, 9, 23),
        ),
        pytest.param(
            data_path / "PARTIN" / "PARTIN_AHB_1_0d_Fehlerkorrektur_2024_03_10_2024_04_03.xml",
            date(2024, 7, 26),
        ),
        pytest.param(
            data_path / "PRICAT" / "PRICAT_AHB_2_0d_ausserordentliche_2024_07_26_2024_04_03.xml",
            date(2024, 7, 26),
        ),
        pytest.param(
            data_path / "REMADV" / "REMADV_AHB_2_5c_Fehlerkorrektur_2024_06_17_2024_06_17.xml",
            date(2024, 6, 17),
        ),
        pytest.param(
            data_path / "REQOTE" / "REQOTE_AHB_2_2_Fehlerkorrektur_2024_09_23_2024_09_23.xml",
            date(2024, 9, 23),
        ),
        pytest.param(
            data_path / "UTILMD" / "UTILMD_AHB_Gas_1_0_ausserordentliche_2024_07_26_2023_12_12.xml",
            date(2024, 7, 26),
        ),
        pytest.param(
            data_path / "UTILMD" / "UTILMD_AHB_Strom_1_2a_Fehlerkorrektur_2024_10_18_2024_10_18.xml",
            date(2024, 10, 18),
        ),
        pytest.param(
            data_path / "UTILMD" / "UTILMD_AHB_Strom_2_1_2024_10_01_2024_09_20.xml",
            date(2024, 10, 1),
        ),
        pytest.param(
            data_path / "UTILTS" / "UTILTS_AHB_1_0f_ausserordentliche_2024_07_26_2024_04_03.xml",
            date(2024, 7, 26),
        ),
        pytest.param(
            data_path / "UTILTS" / "UTILTS_AHB_1_1c_Lesefassung_2023_12_12_2023_12_12.xml",
            date(2023, 10, 24),
        ),
        pytest.param(
            data_path / "UTILTS" / "UTILTS_AHB_1_1d_Konsultationsfassung_2024_04_02_2024_04_02.xml",
            date(2024, 4, 2),
        ),
    ],
)
def test_read_ahb_xml(ahb_xml_file_path: Path, expected_date: date) -> None:
    if not private_submodule_is_checked_out():
        pytest.skip("Skipping test because of missing private submodule")
    reader = AhbReader(ahb_xml_file_path)
    actual = reader.get_publishing_date()
    assert actual == expected_date


def test_deserializing_all_ahbs() -> None:
    if not private_submodule_is_checked_out():
        pytest.skip("Skipping test because of missing private submodule")
    for ahb_file_path in data_path.rglob("**/*AHB*.xml"):
        reader = AhbReader(ahb_file_path)
        _ = reader.read()  # must not crash


@pytest.mark.parametrize(
    "mig_xml_file_path, expected_date",
    [
        pytest.param(
            data_path / "APERAK" / "APERAK_MIG_2_1h_ausserordentliche_2024_07_26_2022_10_01.xml",
            date(2024, 7, 26),
        ),
        pytest.param(
            data_path / "CONTRL" / "CONTRL_MIG_2_0b_ausserordentliche_2024_07_26_2022_10_01.xml",
            date(2024, 7, 26),
        ),
        pytest.param(
            data_path / "IFTSTA" / "IFTSTA_MIG_2_0e_auserordentliche_2024_07_26_2024_03_11.xml",
            date(2024, 7, 26),
        ),
        pytest.param(
            data_path / "INSRPT" / "INSRPT_MIG_1_1a_ausserordentliche_2024_07_26_2023_03_23.xml",
            date(2024, 7, 26),
        ),
        pytest.param(
            data_path / "INVOIC" / "INVOIC_MIG_2_8c_ausserordentliche_2024_07_26_2024_04_03.xml",
            date(2024, 7, 26),
        ),
        pytest.param(
            data_path / "MSCONS" / "MSCONS_MIG_2_4c_ausserordentliche_2024_07_26_2024_04_03.xml",
            date(2024, 7, 26),
        ),
        pytest.param(
            data_path / "ORDCHG" / "ORDCHG_MIG_1_1_ausserordentliche_2024_07_26_2023_10_01.xml",
            date(2024, 7, 26),
        ),
        pytest.param(
            data_path / "ORDERS" / "ORDERS_MIG_1_3_ausserordentliche_2024_07_26_2023_10_01.xml",
            date(2024, 7, 26),
        ),
        pytest.param(
            data_path / "ORDRSP" / "ORDRSP_MIG_1_3_ausserordentliche_2024_07_26_2023_10_01.xml",
            date(2024, 7, 26),
        ),
        pytest.param(
            data_path / "PARTIN" / "PARTIN_MIG_1_0d_ausserordentliche_2024_07_26_2024_04_03.xml",
            date(2024, 7, 26),
        ),
        pytest.param(
            data_path / "PRICAT" / "PRICAT_MIG_2_0c_Fehlerkorrektur_2024_06_17_2024_04_03.xml",
            date(2024, 6, 17),
        ),
        pytest.param(
            data_path / "QUOTES" / "QUOTES_MIG_1_3_ausserordentliche_2024_07_26_2023_10_01.xml",
            date(2024, 7, 26),
        ),
        pytest.param(
            data_path / "REMADV" / "REMADV_MIG_2_9c_ausserordentliche_2024_07_26_2024_04_03.xml",
            date(2024, 7, 26),
        ),
        pytest.param(
            data_path / "REQOTE" / "REQOTE_MIG_1_3_ausserordentliche_2024_07_26_2023_10_01.xml",
            date(2024, 7, 26),
        ),
        pytest.param(
            data_path / "UTILMD" / "UTILMD_MIG_Gas_1_0_ausserordendliche_2024_07_26_2023_12_12.xml",
            date(2024, 7, 26),
        ),
        pytest.param(
            data_path / "UTILMD" / "UTILMD_MIG_Strom_1_1a_Fehlerkorrektur_2024_07_12_2024_07_11.xml",
            date(2024, 9, 23),
        ),
        pytest.param(
            data_path / "UTILMD" / "UTILMD_MIG_Strom_2_1_2024_10_01_2024_09_20.xml",
            date(2024, 10, 1),
        ),
        pytest.param(
            data_path / "UTILTS" / "UTILTS_MIG_1_1c_Fehlerkorrektur_2024_12_13_2024_12_13.xml",
            date(2024, 12, 13),
        ),
        pytest.param(
            data_path / "UTILTS" / "UTILTS_MIG_1_1c_Lesefassung_2023_12_12_2023_12_12.xml",
            date(2023, 10, 24),
        ),
        pytest.param(
            data_path / "UTILTS" / "UTILTS_MIG_1_1d_Konsultationsfassung_2024_04_02_2024_04_02.xml",
            date(2024, 4, 2),
        ),
    ],
)
def test_read_mig_xml(mig_xml_file_path: Path, expected_date: date) -> None:
    if not private_submodule_is_checked_out():
        pytest.skip("Skipping test because of missing private submodule")
    reader = MigReader(mig_xml_file_path)
    actual = reader.get_publishing_date()
    assert actual == expected_date


def test_deserializing_all_migs() -> None:
    if not private_submodule_is_checked_out():
        pytest.skip("Skipping test because of missing private submodule")
    for mig_file_path in data_path.rglob("**/*MIG*.xml"):
        reader = MigReader(mig_file_path)
        _ = reader.read()  # must not crash
