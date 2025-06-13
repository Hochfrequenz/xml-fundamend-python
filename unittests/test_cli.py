import shutil
from pathlib import Path
from typing import Iterator

import pytest

_SKIP_TESTS = False
try:
    from typer.testing import CliRunner

    runner = CliRunner()
    from fundamend.__main__ import app
except ImportError:
    _SKIP_TESTS = True


@pytest.fixture(scope="function")
def example_files_lesefassung(tmp_path: Path) -> Iterator[Path]:
    if _SKIP_TESTS:
        pytest.skip("Seems like typer is not installed")
    copied_files_path = tmp_path / "example_files"
    copied_files_path.mkdir(parents=True, exist_ok=True)
    original_files = Path(__file__).parent / "example_files"
    for file in original_files.glob("*Lesefassung*.xml"):
        shutil.copyfile(file, copied_files_path / file.name)
    yield copied_files_path
    shutil.rmtree(copied_files_path)


@pytest.fixture(scope="function")
def example_files_konsulationsfassung_without_uebertragungsdatei(tmp_path: Path) -> Iterator[Path]:
    if _SKIP_TESTS:
        pytest.skip("Seems like typer is not installed")
    copied_files_path = tmp_path / "example_files"
    copied_files_path.mkdir(parents=True, exist_ok=True)
    original_files = Path(__file__).parent / "example_files"
    for file in original_files.glob("*Konsultationsfassung*.xml"):
        if "Uebertragungsdatei" not in file.name:
            shutil.copyfile(file, copied_files_path / file.name)
    yield copied_files_path
    shutil.rmtree(copied_files_path)


@pytest.fixture(scope="function")
def example_files_fehlerkorrektur(tmp_path: Path) -> Iterator[Path]:
    if _SKIP_TESTS:
        pytest.skip("Seems like typer is not installed")
    copied_files_path = tmp_path / "example_files"
    copied_files_path.mkdir(parents=True, exist_ok=True)
    original_files = Path(__file__).parent / "example_files"
    for file in original_files.glob("*Fehlerkorrektur*.xml"):
        shutil.copyfile(file, copied_files_path / file.name)
    yield copied_files_path
    shutil.rmtree(copied_files_path)


def test_cli_single_file_mig(example_files_lesefassung: Path) -> None:
    if _SKIP_TESTS:
        pytest.skip("Seems like typer is not installed")
    mig_path = example_files_lesefassung / "UTILTS_MIG_1.1c_Lesefassung_2023_12_12.xml"

    result = runner.invoke(app, ["--xml-path", str(mig_path.absolute())], catch_exceptions=False)
    assert result.exit_code == 0
    assert mig_path.with_suffix(".json").exists()
    mig_path.with_suffix(".json").unlink()  # Clean up the created JSON file after the test


def test_cli_single_file_ahb(example_files_konsulationsfassung_without_uebertragungsdatei: Path) -> None:
    if _SKIP_TESTS:
        pytest.skip("Seems like typer is not installed")
    ahb_path = (
        example_files_konsulationsfassung_without_uebertragungsdatei
        / "UTILTS_AHB_1.1d_Konsultationsfassung_2024_04_02.xml"
    )

    result = runner.invoke(app, ["--xml-path", str(ahb_path.absolute())], catch_exceptions=False)
    assert result.exit_code == 0
    assert ahb_path.with_suffix(".json").exists()
    ahb_path.with_suffix(".json").unlink()  # Clean up the created JSON file after the test


def test_cli_directory(example_files_lesefassung: Path) -> None:
    if _SKIP_TESTS:
        pytest.skip("Seems like typer is not installed")
    mig_path = example_files_lesefassung / "UTILTS_MIG_1.1c_Lesefassung_2023_12_12.xml"
    ahb_path = example_files_lesefassung / "UTILTS_AHB_1.1c_Lesefassung_2023_12_12_ZPbXedn.xml"

    result = runner.invoke(app, ["--xml-path", str(example_files_lesefassung.absolute())], catch_exceptions=False)
    assert result.exit_code == 0
    assert mig_path.with_suffix(".json").exists()
    assert ahb_path.with_suffix(".json").exists()
    mig_path.with_suffix(".json").unlink()  # Clean up the created JSON file after the test
    ahb_path.with_suffix(".json").unlink()  # Clean up the created JSON file after the test


def test_cli_directory_with_sanitize_compressed(example_files_fehlerkorrektur: Path, tmp_path: Path) -> None:
    if _SKIP_TESTS:
        pytest.skip("Seems like typer is not installed")
    # mig_path = example_files_lesefassung / "UTILTS_MIG_1.1c_Lesefassung_2023_12_12.xml"
    # ahb_path = example_files_lesefassung / "UTILTS_AHB_1.1c_Lesefassung_2023_12_12_ZPbXedn.xml"
    mig_path = example_files_fehlerkorrektur / "UTILTS_MIG_1_1e_Fehlerkorrektur_20241018.xml"
    ahb_path = example_files_fehlerkorrektur / "UTILTS_AHB_1_0_Fehlerkorrektur_20250218.xml"

    result = runner.invoke(
        app,
        ["-cp", str(example_files_fehlerkorrektur.absolute())],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert mig_path.with_suffix(".json").exists()
    assert ahb_path.with_suffix(".json").exists()

    mig_json_copy = tmp_path / mig_path.with_suffix(".json").name
    ahb_json_copy = tmp_path / ahb_path.with_suffix(".json").name
    shutil.copyfile(mig_path.with_suffix(".json"), mig_json_copy)
    shutil.copyfile(ahb_path.with_suffix(".json"), ahb_json_copy)

    result = runner.invoke(
        app,
        ["-scp", str(example_files_fehlerkorrektur.absolute())],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert mig_path.with_suffix(".json").exists()
    assert ahb_path.with_suffix(".json").exists()

    assert mig_json_copy.read_text("utf-8") != mig_path.read_text("utf-8")
    assert ahb_json_copy.read_text("utf-8") != ahb_path.read_text("utf-8")

    mig_path.with_suffix(".json").unlink()  # Clean up the created JSON file after the test
    ahb_path.with_suffix(".json").unlink()  # Clean up the created JSON file after the test
    mig_json_copy.with_suffix(".json").unlink()  # Clean up the copied JSON files after the test
    ahb_json_copy.with_suffix(".json").unlink()  # Clean up the copied JSON files after the test
