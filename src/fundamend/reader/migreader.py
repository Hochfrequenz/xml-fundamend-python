"""
the MigReader class in this module parses MIG XMLs and binds them to the data model
"""

import xml.etree.ElementTree as ET
from datetime import date, datetime
from pathlib import Path

from fundamend.models.messageimplementationguide import (
    Code,
    DataElement,
    DataElementGroup,
    MessageImplementationGuide,
    MigStatus,
    Segment,
    SegmentGroup,
)
from fundamend.reader.element_distinction import (
    _is_code,
    _is_data_element,
    _is_data_element_group,
    _is_segment,
    _is_segment_group,
    _is_uebertragungsdatei,
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
        description=element.attrib["Description"] or None,
        status_std=MigStatus(element.attrib["Status_Std"]),
        status_specification=MigStatus(element.attrib["Status_Specification"]),
        format_std=element.attrib["Format_Std"],
        format_specification=element.attrib["Format_Specification"],
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
        description=element.attrib["Description"] or None,
        status_std=MigStatus(element.attrib["Status_Std"]),
        status_specification=MigStatus(element.attrib["Status_Specification"]),
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
        description=element.attrib["Description"] or None,
        counter=element.attrib["Counter"],
        level=int(element.attrib["Level"]),
        max_rep_std=int(element.attrib["MaxRep_Std"]),
        max_rep_specification=int(element.attrib["MaxRep_Specification"]),
        status_std=MigStatus(element.attrib["Status_Std"]),
        status_specification=MigStatus(element.attrib["Status_Specification"]),
        example=element.attrib["Example"] or None,
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
        status_std=MigStatus(element.attrib["Status_Std"]),
        status_specification=MigStatus(element.attrib["Status_Specification"]),
        counter=element.attrib["Counter"],
        level=int(element.attrib["Level"]),
        max_rep_std=int(element.attrib["MaxRep_Std"]),
        max_rep_specification=int(element.attrib["MaxRep_Specification"]),
        segments=[s for s in segments_and_groups if isinstance(s, Segment)],
        segment_groups=[sg for sg in segments_and_groups if isinstance(sg, SegmentGroup)],
    )


def _get_first_tag_starting_with_m(element: ET.Element) -> ET.Element:
    for elem in element.iter():
        if elem.tag.startswith("M_"):
            return elem
    raise ValueError("No element starting with M_ found")


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

    def _get_format_root(self) -> ET.Element:
        actual_root = self._element_tree.getroot()
        if actual_root.tag == "Uebertragungsdatei":
            return actual_root.find("//*[starts-with(name(), 'M_')][1]")
        return actual_root

    def get_publishing_date(self) -> date:
        """
        returns the publishing date of the message implementation guide
        """
        root = self._element_tree.getroot()  # might be either <M_FORMAT> or <Uebertragungsdatei>
        raw_value = root.attrib["Veroeffentlichungsdatum"]  # e.g. '24.10.2023'
        result = datetime.strptime(raw_value, "%d.%m.%Y").date()
        return result

    def get_author(self) -> str:
        """
        returns the author of the message implementation guide
        """
        root = self._element_tree.getroot()  # might be either <M_FORMAT> or <Uebertragungsdatei>
        return root.attrib["Author"]

    def get_version(self) -> str:
        """
        returns the version of the message implementation guide
        """
        root = self._element_tree.getroot()  # might be either <M_FORMAT> or <Uebertragungsdatei>
        return root.attrib["Versionsnummer"]

    def get_format(self) -> str:
        """returns the format of the message implementation guide, e.g. 'UTILTS'"""
        root = self._element_tree.getroot()
        if _is_uebertragungsdatei(root):
            root = _get_first_tag_starting_with_m(root)
        return root.tag.lstrip("M_")  # converts 'M_UTILTS' to 'UTILTS'

    def _iter_segments_and_segment_groups(self, element: ET.Element) -> list[SegmentGroup | Segment]:
        """recursive function that builds a list of all segments and segment groups"""
        if _is_uebertragungsdatei(element):
            root = _get_first_tag_starting_with_m(element)
            return self._iter_segments_and_segment_groups(root)
        result: list[Segment | SegmentGroup] = []
        if _is_segment_group(element):
            result.append(_to_segment_group(element))
        elif _is_segment(element):
            result.append(_to_segment(element))
        return result

    def read(self) -> MessageImplementationGuide:
        """
        read the entire file and convert it to a MessageImplementationGuid instance
        """
        segments_and_groups = []
        root = self._element_tree.getroot()
        if _is_uebertragungsdatei(root):
            for elem in root.iter():
                if elem.tag.startswith("M_"):
                    root = elem
                    break
        for index, element in enumerate(root):
            if index == 0:
                continue
            segments_and_groups.extend(self._iter_segments_and_segment_groups(element))

        result = MessageImplementationGuide(
            veroeffentlichungsdatum=self.get_publishing_date(),
            autor=self.get_author(),
            versionsnummer=self.get_version(),
            format=self.get_format(),
            segments=[s for s in segments_and_groups if isinstance(s, Segment)],
            segment_groups=[s for s in segments_and_groups if isinstance(s, SegmentGroup)],
        )
        return result
