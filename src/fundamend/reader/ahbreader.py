"""
the AhbReader class in this module parses AHB XMLs and binds them to the data model
"""

import re
import xml.etree.ElementTree as ET
from datetime import date, datetime
from pathlib import Path

from fundamend.models.anwendungshandbuch import (
    Anwendungsfall,
    Anwendungshandbuch,
    Bedingung,
    Code,
    DataElement,
    DataElementGroup,
    Paket,
    Segment,
    SegmentGroup,
    UbBedingung,
)
from fundamend.reader.element_distinction import (
    _is_anwendungsfall,
    _is_code,
    _is_data_element,
    _is_data_element_group,
    _is_format,
    _is_segment,
    _is_segment_group,
    _is_uebertragungsdatei,
)
from fundamend.utils import lstrip, strip

# pylint:disable=duplicate-code
# yes, it's very similar to the MigReader


def _to_code(element: ET.Element) -> Code:
    assert _is_code(element)
    value = element.text
    if value is not None:
        value = value.strip()
    return Code(
        name=element.attrib["Name"],
        description=element.attrib["Description"] or None,
        value=value,
        ahb_status=element.attrib["AHB_Status"],
    )


def _to_bedingung(element: ET.Element) -> Bedingung:
    return Bedingung(
        nummer=strip("[", element.attrib["Nummer"], "]"),
        text=(element.text or "").strip(),
    )


def _to_ub_bedingung(element: ET.Element) -> UbBedingung:
    return UbBedingung(
        nummer=strip("[", element.attrib["Nummer"], "]"),
        text=(element.text or "").strip(),
    )


def _to_paket(element: ET.Element) -> Paket:
    return Paket(
        nummer=strip("[", element.attrib["Nummer"], "]"),
        text=(element.text or "").strip(),
    )


_pruefi_pattern = re.compile(r"\d{5}")


def _is_valid_pruefidentifikator(pruefidentifikator: str) -> bool:
    """
    returns true if the passed object looks like a pruefinentifikator
    """
    if pruefidentifikator is None:
        return False
    if not isinstance(pruefidentifikator, str):
        return False  # this prevents users from accidentally passing integers
    return _pruefi_pattern.match(pruefidentifikator) is not None


def _to_data_element(element: ET.Element) -> DataElement:
    assert _is_data_element(element)
    codes = []
    for child in element:
        if _is_code(child):
            codes.append(_to_code(child))
        else:
            raise ValueError(f"unexpected element: {child.tag}")
    return DataElement(
        id=element.tag,
        name=element.attrib["Name"],
        codes=tuple(codes),
    )


def _to_data_element_group(element: ET.Element) -> DataElementGroup:
    assert _is_data_element_group(element)
    data_elements = []
    for child in element:
        if _is_data_element(child):
            data_elements.append(_to_data_element(child))
        else:
            raise ValueError(f"unexpected element: {child.tag}")
    return DataElementGroup(
        id=element.tag,
        name=element.attrib["Name"],
        data_elements=tuple(data_elements),
    )


def _to_segment(element: ET.Element) -> Segment:
    assert _is_segment(element)
    data_elements: list[DataElement | DataElementGroup] = []
    for child in element:
        if _is_data_element_group(child):
            data_elements.append(_to_data_element_group(child))
        elif _is_data_element(child):
            data_elements.append(_to_data_element(child))
        else:
            raise ValueError(f"unexpected element: {child.tag}")
    ahb_status: str | None = None
    if "AHB_Status" in element.attrib and element.attrib["AHB_Status"].strip():
        ahb_status = element.attrib["AHB_Status"]
    return Segment(
        id=lstrip("S_", element.tag),
        name=element.attrib["Name"],
        number=element.attrib["Number"],
        ahb_status=ahb_status,
        data_elements=tuple(data_elements),
    )


def _to_segment_group(element: ET.Element) -> SegmentGroup:
    assert _is_segment_group(element)
    segments_and_groups: list[SegmentGroup | Segment] = []
    for child in element:
        if _is_segment_group(child):
            segments_and_groups.append(_to_segment_group(child))
        elif _is_segment(child):
            segments_and_groups.append(_to_segment(child))
        else:
            raise ValueError(f"unexpected element: {child.tag}")
    return SegmentGroup(
        id=lstrip("G_SG", element.tag),
        name=element.attrib["Name"],
        ahb_status=(
            element.attrib["AHB_Status"].strip() or None
            if "AHB_Status" in element.attrib and element.attrib["AHB_Status"] is not None
            else None
        ),
        elements=tuple(list(segments_and_groups)),
    )


class AhbReader:
    """
    Accesses information from an XML based Anwendungshandbuch
    """

    def __init__(self, xml_path: Path):
        """
        initialize by providing the path to the XML file
        """
        self._xml_path = xml_path
        self._element_tree = ET.parse(self._xml_path)

    def get_publishing_date(self) -> date:
        """
        returns the publishing date of the message implementation guide
        """
        raw_value = self._element_tree.getroot().attrib["Veroeffentlichungsdatum"]  # e.g. '02.04.2024'
        result = datetime.strptime(raw_value, "%d.%m.%Y").date()
        return result

    def get_author(self) -> str:
        """
        returns the author of the AHB
        """
        return self._element_tree.getroot().attrib["Author"]

    def get_version(self) -> str:
        """
        returns the version of the AHB
        """
        return self._element_tree.getroot().attrib["Versionsnummer"]

    def get_bedingungen(self) -> list[Bedingung]:
        """returns the plain bedingungen"""
        return [_to_bedingung(x) for x in self._element_tree.getroot().find("Bedingungen")]  # type:ignore[union-attr]

    def get_ub_bedingungen(self) -> list[UbBedingung]:
        """returns the UB Bedingungen"""
        return [
            _to_ub_bedingung(x) for x in self._element_tree.getroot().find("UB_Bedingungen")  # type:ignore[union-attr]
        ]

    def get_pakete(self) -> list[Paket]:
        """returns the package definitions"""
        return [_to_paket(x) for x in self._element_tree.getroot().find("Pakete")]  # type:ignore[union-attr]

    def get_anwendungsfall(self, pruefidentifikator: str) -> Anwendungsfall | None:
        """find the anwendungsfall matching the pruefidentifikator or return None"""
        if not _is_valid_pruefidentifikator(pruefidentifikator):
            raise ValueError(f"invalid pruefidentifikator: {pruefidentifikator}")
        for element in self._element_tree.getroot():
            if element.tag != "AWF":
                continue
            if element.attrib["Pruefidentifikator"] != pruefidentifikator:
                continue
            if element.tag == "AWF" and element.attrib["Pruefidentifikator"] == pruefidentifikator:
                return self._read_anwendungsfall(element)
        return None

    def get_anwendungsfaelle(self) -> list[Anwendungsfall]:
        """finds all anwendungsfaelle in the XML file"""
        result: list[Anwendungsfall] = []
        for element in self._element_tree.getroot():
            if element.tag != "AWF":
                continue
            result.append(self._read_anwendungsfall(element))
        return result

    def _iter_segments_and_segment_groups(self, element: ET.Element) -> list[SegmentGroup | Segment]:
        """recursive function that builds a list of all segments and segment groups"""
        result: list[Segment | SegmentGroup] = []
        should_go_deeper = _is_anwendungsfall(element) or _is_format(element) or _is_uebertragungsdatei(element)
        if should_go_deeper:
            for sub_element in element:
                result.extend(self._iter_segments_and_segment_groups(sub_element))
        if _is_segment_group(element):
            result.append(_to_segment_group(element))
        elif _is_segment(element):
            result.append(_to_segment(element))
        return result

    def _read_anwendungsfall(self, original_element: ET.Element) -> Anwendungsfall:
        segments_and_groups = []
        for element in original_element:
            segments_and_groups.extend(self._iter_segments_and_segment_groups(element))
        format_element = original_element[0]
        if _is_uebertragungsdatei(format_element):
            format_element = original_element[0][0]
        return Anwendungsfall(
            pruefidentifikator=original_element.attrib["Pruefidentifikator"],
            beschreibung=original_element.attrib["Beschreibung"],
            kommunikation_von=original_element.attrib["Kommunikation_von"],
            format=lstrip("M_", format_element.tag),
            elements=tuple(segments_and_groups),
        )

    def read(self) -> Anwendungshandbuch:
        """
        read the entire file and convert it to a MessageImplementationGuid instance
        """

        result = Anwendungshandbuch(
            veroeffentlichungsdatum=self.get_publishing_date(),
            autor=self.get_author(),
            versionsnummer=self.get_version(),
            bedingungen=tuple(self.get_bedingungen()),
            ub_bedingungen=tuple(self.get_ub_bedingungen()),
            pakete=tuple(self.get_pakete()),
            anwendungsfaelle=tuple(self.get_anwendungsfaelle()),
        )
        return result
