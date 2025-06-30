"""
Contains the command to convert XML files to JSON files.
"""

import re
from itertools import groupby
from pathlib import Path
from typing import Iterator, Literal

import typer
from typing_extensions import Annotated

from fundamend import AhbReader, Anwendungshandbuch, MessageImplementationGuide, MigReader
from fundamend.commands.app import app
from fundamend.sanitize import sanitize_ahb

FORMAT_AND_TYPE_REGEX = re.compile(r"^([A-Z]+)_(AHB|MIG)_(?:(Gas|Strom)_)?")


def _write_ahb_models_splitted(
    model: Anwendungshandbuch,
    ahb_dir: Path,
    *,
    compressed: bool = False,
) -> None:
    """Writes the given Anwendungshandbuch model to multiple JSON files, one for each Anwendungsfall."""
    ahb_dir.mkdir(parents=True, exist_ok=True)
    for anwendungsfall in model.anwendungsfaelle:
        json_file_path = ahb_dir / f"{anwendungsfall.pruefidentifikator}.json"
        with open(json_file_path, encoding="utf-8", mode="w") as outfile:
            outfile.write(anwendungsfall.model_dump_json(indent=None if compressed else 2))

    # Write meta file
    ahb_meta_file_path = ahb_dir / "meta.json"
    with open(ahb_meta_file_path, encoding="utf-8", mode="w") as outfile:
        outfile.write(model.model_dump_json(exclude={"anwendungsfaelle"}, indent=None if compressed else 2))


def _write_model_to_json_file(
    model: Anwendungshandbuch | MessageImplementationGuide,
    xml_file_path: Path,
    *,
    compressed: bool = False,
    split_ahb: bool = False,
) -> None:
    """Writes the given model to a JSON file at the specified path."""
    if split_ahb:
        if not isinstance(model, Anwendungshandbuch):
            raise ValueError("split_ahb can only be used with Anwendungshandbuch models")
        ahb_dir = xml_file_path.with_suffix("")
        _write_ahb_models_splitted(model, ahb_dir, compressed=compressed)
        typer.echo(f"Successfully converted {xml_file_path} to multiple JSON files in {ahb_dir}")
    else:
        json_file_path = xml_file_path.with_suffix(".json")
        with open(json_file_path, encoding="utf-8", mode="w") as outfile:
            outfile.write(model.model_dump_json(indent=None if compressed else 2))
        typer.echo(f"Successfully converted {xml_file_path} to JSON {json_file_path}")


def _convert_to_json_files(
    mig_xml_file_path: Path, ahb_xml_file_path: Path, sanitize: bool = False
) -> tuple[MessageImplementationGuide, Anwendungshandbuch]:
    """converts the given XML file to a JSON file and returns the path of the latter"""
    if not mig_xml_file_path.is_file():  # pragma: no cover
        raise ValueError(f"The given path {mig_xml_file_path.absolute()} is not a file")
    if not ahb_xml_file_path.is_file():  # pragma: no cover
        raise ValueError(f"The given path {ahb_xml_file_path.absolute()} is not a file")

    mig_model = MigReader(mig_xml_file_path).read()
    ahb_model = AhbReader(ahb_xml_file_path).read()

    # Do sanitization if requested
    if sanitize:
        sanitize_ahb(mig_model, ahb_model)

    return mig_model, ahb_model


def xml2json_dir_mode(
    xml_path: Path, sanitize: bool = False, compressed: bool = False, split_ahb: bool = False
) -> None:
    """
    Converts all XML files in the given directory to JSON files.
    The function expects to find pairs of MIG and AHB XML files in the directory.
    The XML file names must match the pattern `<FORMAT>_<AHB|MIG>_[<Gas|Strom>_]*.xml`.
    """

    def groupby_key(path_and_match: tuple[Path, re.Match[str] | None]) -> str:
        assert path_and_match[1] is not None
        return path_and_match[1].group(1) + (path_and_match[1].group(3) or "")

    def sort_key(path_and_match: tuple[Path, re.Match[str] | None]) -> str:
        assert path_and_match[1] is not None
        return groupby_key(path_and_match) + path_and_match[1].group(2)

    def xmls_and_matches() -> Iterator[tuple[Path, re.Match[str]]]:
        for _xml_path in xml_path.rglob("*.xml"):
            match = FORMAT_AND_TYPE_REGEX.match(_xml_path.name)
            if match is None:  # pragma: no cover
                raise ValueError("XML file name does not match expected format: " + str(_xml_path))
            yield _xml_path, match

    for _, _xmls_and_matches in groupby(sorted(xmls_and_matches(), key=sort_key), key=groupby_key):
        _xmls_and_matches_list = list(_xmls_and_matches)
        assert len(_xmls_and_matches_list) == 2, (
            "Expected exactly two XML files (AHB + MIG) for each format and powert type, but found: "
            f"{_xmls_and_matches_list}"
        )
        assert (
            _xmls_and_matches_list[0][1].group(2) == "AHB" and _xmls_and_matches_list[1][1].group(2) == "MIG"
        ), f"Expected AHB on first and a MIG on second position, but found: {_xmls_and_matches_list}"
        ahb_path = _xmls_and_matches_list[0][0]
        mig_path = _xmls_and_matches_list[1][0]
        mig, ahb = _convert_to_json_files(mig_path, ahb_path, sanitize=sanitize)
        _write_model_to_json_file(mig, mig_path.with_suffix(".json"), compressed=compressed)
        _write_model_to_json_file(ahb, ahb_path.with_suffix(".json"), compressed=compressed, split_ahb=split_ahb)


def xml2json_file_mode(
    xml_path: Path, sanitize: bool = False, compressed: bool = False, split_ahb: bool = False
) -> None:
    """
    Converts a single XML file to JSON.
    The function expects to find the corresponding AHB or MIG file in the same directory.

    The XML file names must match the pattern `<FORMAT>_<AHB|MIG>_[<Gas|Strom>_]*.xml`.
    """
    match = FORMAT_AND_TYPE_REGEX.match(xml_path.name)
    if match is None:  # pragma: no cover
        raise ValueError("XML file name does not match expected format: " + str(xml_path))
    match_type: Literal["MIG", "AHB"] = match.group(2)  # type: ignore[assignment]
    match_type_other: Literal["MIG", "AHB"] = "AHB" if match_type == "MIG" else "MIG"
    pattern_other = f"{match.group(1)}_{match_type_other}_"
    if match.group(3) is not None:
        pattern_other += f"{match.group(3)}_"
    pattern_other += "*.xml"

    other_matches = list(xml_path.parent.glob(pattern_other))
    if len(other_matches) == 0:  # pragma: no cover
        raise ValueError(
            f"No other XML file found in the same directory as {xml_path} matching pattern {pattern_other}"
        )
    if len(other_matches) > 1:  # pragma: no cover
        raise ValueError(
            f"Multiple other XML files found in the same directory as {xml_path} matching pattern "
            f"{pattern_other}: {other_matches}"
        )
    if match_type == "MIG":
        mig, ahb = _convert_to_json_files(xml_path, other_matches[0], sanitize=sanitize)
        _write_model_to_json_file(mig, xml_path.with_suffix(".json"), compressed=compressed)
    else:
        mig, ahb = _convert_to_json_files(other_matches[0], xml_path, sanitize=sanitize)
        _write_model_to_json_file(ahb, xml_path.with_suffix(".json"), compressed=compressed, split_ahb=split_ahb)


@app.command()
def xml2json(
    xml_path: Annotated[
        Path,
        typer.Option(
            ...,
            "--xml-path",
            "-p",
            exists=True,
            file_okay=True,
            dir_okay=True,
            writable=True,
            readable=True,
            resolve_path=True,
        ),
    ],
    sanitize: Annotated[
        bool,
        typer.Option(
            ...,
            "--sanitize",
            "-s",
            help="Sanitize the MIG or AHB before writing the resulting JSON. As of now, it does two things:\n"
            '1) Data elements or groups which are stated as "unused" in the MIG are missing in the AHB. '
            "The sanitization will add them to the AHB to enable easy parallel iteration over MIG and AHB. \n"
            "2) The five data elements C_C080 D_3036 model names. But in AHB there is only one D_3036 with "
            'description "Name". The sanitization will add four extra D_3036 data elements to prevent reading'
            "raster errors.",
        ),
    ] = False,
    compressed: Annotated[
        bool,
        typer.Option(
            ...,
            "--compressed",
            "-c",
            help="If set, the output JSON files will contain no whitespace outside of strings. If not set"
            " (default), the output JSON files will be pretty-printed with an indentation of one space.",
        ),
    ] = False,
    split_ahb: Annotated[
        bool,
        typer.Option(
            ...,
            "--split-ahb",
            "-a",
            help="If set, the AHB will be split into multiple files, one for each Anwendungsfall. "
            "The files will be named `<Prüfidentifikator>.json` in a directory named after the AHB file's "
            "name (without the extension). It will contain an additional `meta.json` file containing the fields of "
            "`Anwendungshandbuch` except for `anwendungsfaelle`.",
        ),
    ] = False,
) -> None:
    """
    Converts the xml file(s) from `xml_in_path` to a json file next to the `*.xml`.
    If `xml_in_path` is a directory, it will search for all XML files in the directory and its subdirectories.

    All xml files must follow the naming convention `/^(?P<FORMAT>[A-Z]+)_(AHB|MIG)_((Gas|Strom)_)?.*\\.xml$/`
    """
    if xml_path.is_dir():
        xml2json_dir_mode(xml_path, sanitize=sanitize, compressed=compressed, split_ahb=split_ahb)
    else:
        xml2json_file_mode(xml_path, sanitize=sanitize, compressed=compressed, split_ahb=split_ahb)
