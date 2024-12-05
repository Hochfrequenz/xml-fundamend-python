from pathlib import Path

import pytest

_SKIP_TESTS = False
try:
    from typer.testing import CliRunner

    runner = CliRunner()
    from fundamend.cli import app
except ImportError:
    _SKIP_TESTS = True


def _copy_xml_file(inpath: Path, outpath: Path) -> None:
    with open(outpath, encoding="utf-8", mode="w") as outfile:
        with open(inpath, encoding="utf-8", mode="r") as infile:
            outfile.write(infile.read())


def test_cli_single_file_mig(tmp_path: Path) -> None:
    if _SKIP_TESTS:
        pytest.skip("Seems like typer is not installed")
    original_mig_file = Path(__file__).parent / "example_files" / "UTILTS_MIG_1.1c_Lesefassung_2023_12_12.xml"
    tmp_mig_path = tmp_path / "my_mig.xml"
    _copy_xml_file(original_mig_file, tmp_mig_path)
    result = runner.invoke(app, ["--xml-path", str(tmp_mig_path.absolute())])
    assert result.exit_code == 0
    assert (tmp_path / "my_mig.json").exists()


def test_cli_single_file_ahb(tmp_path: Path) -> None:
    if _SKIP_TESTS:
        pytest.skip("Seems like typer is not installed")
    original_ahb_file = Path(__file__).parent / "example_files" / "UTILTS_AHB_1.1d_Konsultationsfassung_2024_04_02.xml"
    tmp_ahb_path = tmp_path / "my_ahb.xml"
    _copy_xml_file(original_ahb_file, tmp_ahb_path)
    result = runner.invoke(app, ["--xml-path", str(tmp_ahb_path)])
    assert result.exit_code == 0
    assert (tmp_path / "my_ahb.json").exists()


def test_cli_directory(tmp_path: Path) -> None:
    if _SKIP_TESTS:
        pytest.skip("Seems like typer is not installed")
    original_mig_file = Path(__file__).parent / "example_files" / "UTILTS_MIG_1.1c_Lesefassung_2023_12_12.xml"
    tmp_mig_path = tmp_path / "my_mig.xml"
    original_ahb_file = Path(__file__).parent / "example_files" / "UTILTS_AHB_1.1d_Konsultationsfassung_2024_04_02.xml"
    tmp_ahb_path = tmp_path / "my_ahb.xml"
    _copy_xml_file(original_ahb_file, tmp_ahb_path)
    _copy_xml_file(original_mig_file, tmp_mig_path)
    result = runner.invoke(app, ["--xml-path", str(tmp_path)])
    assert result.exit_code == 0
    assert (tmp_path / "my_mig.json").exists()
    assert (tmp_path / "my_ahb.json").exists()
