"""shared logic between MIG and AHB reader to distinguish elements from the XML"""

import xml.etree.ElementTree as ET


def _is_segment_group(element: ET.Element) -> bool:
    """
    returns True if the given element is a segment group
    """
    return element.tag.startswith("G_SG")


def _is_segment(element: ET.Element) -> bool:
    """
    returns True if the given element is a segment
    """
    return element.tag.startswith("S_")


def _is_data_element_group(element: ET.Element) -> bool:
    """
    returns True if the given element is a data element group
    """
    return element.tag.startswith("C_")


def _is_data_element(element: ET.Element) -> bool:
    """
    returns True if the given element is a data element
    """
    return element.tag.startswith("D_")


def _is_code(element: ET.Element) -> bool:
    """
    returns True if the given element is a code
    """
    return element.tag == "Code"


def _is_format(element: ET.Element) -> bool:
    """returns true if element is wrapper around an anwendungsfall"""
    return element.tag.startswith("M_")


def _is_anwendungsfall(element: ET.Element) -> bool:
    """returns true iff the element is an AHB anwendungsfall"""
    return element.tag == "AWF"
