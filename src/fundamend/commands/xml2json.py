import json
from pathlib import Path

import typer
from pydantic import RootModel
from rich.console import Console
from typing_extensions import Annotated

from fundamend import AhbReader, Anwendungshandbuch, MessageImplementationGuide, MigReader

app = typer.Typer(name="xml2json", help="Convert XML(s) by BDEW to JSON(s)")


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
def main(
    xml_path: Annotated[
        Path,
        typer.Option(
            exists=True,
            file_okay=True,
            dir_okay=True,
            writable=True,
            readable=True,
            resolve_path=True,
        ),
    ],
) -> None:
    """
    converts the xml file from xml_in_path to a json file next to the .xml
    """
    assert xml_path.exists()  # ensured by typer
    if xml_path.is_dir():
        for _xml_path in xml_path.rglob("*.xml"):
            _convert_to_json_file(_xml_path)
    else:
        _convert_to_json_file(xml_path)
