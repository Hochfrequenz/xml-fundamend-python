"""contains the entrypoint for the command line interface"""

import json
import sys
from pathlib import Path

import typer
from pydantic import RootModel
from rich.console import Console

from fundamend import AhbReader, Anwendungshandbuch, MessageImplementationGuide, MigReader

app = typer.Typer(help="Convert XML(s) by BDEW to JSON(s)")
err_console = Console(stderr=True)  # https://typer.tiangolo.com/tutorial/printing/#printing-to-standard-error


def _convert_to_json_file(xml_file_path: Path) -> Path:
    """converts the given XML file to a JSON file and returns the path of the latter"""
    if not xml_file_path.is_file():
        raise ValueError(f"The given path {xml_file_path.absolute()} is not a file")
    is_ahb = "ahb" in xml_file_path.stem.lower()
    is_mig = "mig" in xml_file_path.stem.lower()
    if is_ahb and is_mig:
        raise ValueError(f"Cannot detect if {xml_file_path} is an AHB or MIG")
    root_model: RootModel[Anwendungshandbuch] | RootModel[MessageImplementationGuide]
    if is_ahb:
        ahb_model = AhbReader(xml_file_path).read()
        root_model = RootModel[Anwendungshandbuch](ahb_model)
    elif is_mig:
        mig_model = MigReader(xml_file_path).read()
        root_model = RootModel[MessageImplementationGuide](mig_model)
    else:
        raise ValueError(f"Seems like {xml_file_path} is neither an AHB nor a MIG")
    out_dict = root_model.model_dump(mode="json")
    json_file_path = xml_file_path.with_suffix(".json")
    with open(json_file_path, encoding="utf-8", mode="w") as outfile:
        json.dump(out_dict, outfile, indent=True, ensure_ascii=False)
    print(f"Successfully converted {xml_file_path} file to JSON {json_file_path}")
    return json_file_path


@app.command()
def main(xml_in_path: Path) -> None:
    """
    converts the xml file from xml_in_path to a json file next to the .xml
    """
    if not xml_in_path.exists():
        err_console.print(f"The path {xml_in_path.absolute()} does not exist")
        sys.exit(1)
    if xml_in_path.is_dir():
        for xml_path in xml_in_path.rglob("*.xml"):
            _convert_to_json_file(xml_path)
    else:
        _convert_to_json_file(xml_in_path)

def cli() -> None:
    """entry point of the script defined in pyproject.toml"""
    main()