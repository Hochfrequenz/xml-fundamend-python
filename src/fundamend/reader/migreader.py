"""
the MigReader class in this module parses MIG XMLs and binds them to the data model
"""

import xml.etree.ElementTree as ET
from datetime import date, datetime
from pathlib import Path

from efoli import EdifactFormat

from fundamend.models.messageimplementationguide import (
    Code,
    DataElement,
    DataElementGroup,
    MessageImplementationGuide,
    MigStatus,
    Segment,
    SegmentGroup,
    Uebertragungsdatei,
)
from fundamend.reader.element_distinction import (
    _is_code,
    _is_data_element,
    _is_data_element_group,
    _is_format,
    _is_segment,
    _is_segment_group,
    _is_uebertragungsdatei,
)
from fundamend.utils import lstrip


def _to_code(element: ET.Element) -> Code:
    assert _is_code(element)
    return Code(name=element.attrib["Name"], description=element.attrib["Description"] or None, value=element.text)


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
        description=element.attrib["Description"] or None,
        status_std=MigStatus(element.attrib["Status_Std"]),
        status_specification=MigStatus(element.attrib["Status_Specification"]),
        format_std=element.attrib["Format_Std"],
        format_specification=element.attrib["Format_Specification"],
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
        description=element.attrib["Description"] or None,
        status_std=MigStatus(element.attrib["Status_Std"]),
        status_specification=MigStatus(element.attrib["Status_Specification"]),
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
    return Segment(
        id=lstrip("S_", element.tag),
        name=element.attrib["Name"],
        description=element.attrib["Description"] or None,
        counter=element.attrib["Counter"],
        level=int(element.attrib["Level"]),
        max_rep_std=int(element.attrib["MaxRep_Std"]),
        max_rep_specification=int(element.attrib["MaxRep_Specification"]),
        status_std=MigStatus(element.attrib["Status_Std"]),
        status_specification=MigStatus(element.attrib["Status_Specification"]),
        example=element.attrib["Example"] or None,
        number=element.attrib["Number"],
        data_elements=tuple(data_elements),
    )


def _iter_segments_and_segment_groups(element: ET.Element) -> list[SegmentGroup | Segment]:
    """recursive function that builds a list of all segments and segment groups"""
    result: list[Segment | SegmentGroup] = []
    if _is_segment_group(element):
        result.append(_to_segment_group(element))
    elif _is_segment(element):
        result.append(_to_segment(element))
    return result


def get_publishing_date(element: ET.Element) -> date:
    """
    returns the publishing date of the message implementation guide
    """
    raw_value = element.attrib["Veroeffentlichungsdatum"]  # e.g. '24.10.2023'
    result = datetime.strptime(raw_value, "%d.%m.%Y").date()
    return result


def get_author(element: ET.Element) -> str:
    """
    returns the author of the message implementation guide
    """
    return element.attrib["Author"]


def get_version(element: ET.Element) -> str:
    """
    returns the version of the message implementation guide
    """
    return element.attrib["Versionsnummer"]


def get_format(element: ET.Element) -> EdifactFormat:
    """returns the format of the message implementation guide, e.g. 'UTILTS'"""
    return EdifactFormat(lstrip("M_", element.tag))  # converts 'M_UTILTS' to 'UTILTS'


def _to_message_implementation_guide(
    element: ET.Element,
    veroeffentlichungsdatum: date | None = None,
    autor: str | None = None,
    versionsnummer: str | None = None,
) -> MessageImplementationGuide:
    assert _is_format(element)
    segments_and_groups: list[Segment | SegmentGroup] = []
    for child in element:
        segments_and_groups.extend(_iter_segments_and_segment_groups(child))

    result = MessageImplementationGuide(
        veroeffentlichungsdatum=veroeffentlichungsdatum or get_publishing_date(element),
        autor=autor or get_author(element),
        versionsnummer=versionsnummer or get_version(element),
        format=get_format(element),
        elements=tuple(segments_and_groups),
    )
    return result


def _to_uebertragungsdatei(element: ET.Element) -> Uebertragungsdatei:
    assert _is_uebertragungsdatei(element)
    sub_elements: list[Segment | MessageImplementationGuide] = []
    veroeffentlichungsdatum = get_publishing_date(element)
    autor = get_author(element)
    versionsnummer = get_version(element)
    for child in element:
        if _is_segment(child):
            sub_elements.append(_to_segment(child))
        elif _is_format(child):
            sub_elements.append(
                _to_message_implementation_guide(
                    child, veroeffentlichungsdatum=veroeffentlichungsdatum, autor=autor, versionsnummer=versionsnummer
                )
            )
        else:
            raise ValueError(f"unexpected element: {child.tag}")
    return Uebertragungsdatei(
        veroeffentlichungsdatum=veroeffentlichungsdatum,
        autor=autor,
        versionsnummer=versionsnummer,
        elements=tuple(sub_elements),
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
        status_std=MigStatus(element.attrib["Status_Std"]),
        status_specification=MigStatus(element.attrib["Status_Specification"]),
        counter=element.attrib["Counter"],
        level=int(element.attrib["Level"]),
        max_rep_std=int(element.attrib["MaxRep_Std"]),
        max_rep_specification=int(element.attrib["MaxRep_Specification"]),
        elements=tuple(segments_and_groups),
    )


# pylint:disable=too-few-public-methods
class MigReader:
    """
    Accesses information from an XML based message implementation guide
    """

    def __init__(self, xml_path: Path):
        """
        initialize by providing the path to the XML file
        """
        self._xml_path = xml_path
        self._element_tree = ET.parse(self._xml_path)

    def read(self) -> MessageImplementationGuide | Uebertragungsdatei:
        """
        read the entire file and convert it to a MessageImplementationGuide or Uebertragungsdatei instance
        """

        root = self._element_tree.getroot()
        if _is_uebertragungsdatei(root):
            return _to_uebertragungsdatei(root)
        if _is_format(root):
            return _to_message_implementation_guide(root)
        raise ValueError(f"unexpected root element: {root.tag}")
