"""
the AhbReader class in this module parses AHB XMLs and binds them to the data model
"""

import xml.etree.ElementTree as ET
from datetime import date, datetime
from pathlib import Path

from fundamend.models.anwendungshandbuch import (
    Anwendungshandbuch,
    Code,
    DataElement,
    DataElementGroup,
    Segment,
    SegmentGroup,
)
from fundamend.reader.element_distinction import (
    _is_code,
    _is_data_element,
    _is_data_element_group,
    _is_segment,
    _is_segment_group,
)


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
        codes=codes,
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
        data_elements=data_elements,
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
        id=element.tag.lstrip("S_"),
        name=element.attrib["Name"],
        number=element.attrib["Number"],
        data_elements=data_elements,
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
        id=element.tag.lstrip("G_SG"),
        name=element.attrib["Name"],
        segments=[s for s in segments_and_groups if isinstance(s, Segment)],
        segment_groups=[sg for sg in segments_and_groups if isinstance(sg, SegmentGroup)],
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

    # def get_format(self) -> str:
    #    """returns the format of the message implementation guide, e.g. 'UTILTS'"""
    #    root_tag: str = self._element_tree.getroot().tag
    #    return root_tag.lstrip("M_")  # converts 'M_UTILTS' to 'UTILTS'

    def _iter_segments_and_segment_groups(self, element: ET.Element) -> list[SegmentGroup | Segment]:
        """recursive function that builds a list of all segments and segment groups"""
        result: list[Segment | SegmentGroup] = []
        if _is_segment_group(element):
            result.append(_to_segment_group(element))
        elif _is_segment(element):
            result.append(_to_segment(element))
        return result

    def read(self) -> Anwendungshandbuch:
        """
        read the entire file and convert it to a MessageImplementationGuid instance
        """
        segments_and_groups = []
        for index, element in enumerate(self._element_tree.getroot()):
            if index == 0:
                continue
            segments_and_groups.extend(self._iter_segments_and_segment_groups(element))

        result = Anwendungshandbuch(
            veroeffentlichungsdatum=self.get_publishing_date(),
            autor=self.get_author(),
            versionsnummer=self.get_version(),
            format=self.get_format(),
            segments=[s for s in segments_and_groups if isinstance(s, Segment)],
            segment_groups=[s for s in segments_and_groups if isinstance(s, SegmentGroup)],
        )
        return result
