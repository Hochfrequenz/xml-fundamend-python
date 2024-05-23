"""
This a docstring for the module.
"""

import xml.etree.ElementTree as ET
from datetime import date, datetime
from pathlib import Path

from bamx.models.messageimplementationguide import MessageImplementationGuide


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

    def get_publishing_date(self) -> date:
        """
        returns the publishing date of the message implementation guide
        """
        raw_value = self._element_tree.getroot().attrib["Veroeffentlichungsdatum"]  # e.g. '24.10.2023'
        result = datetime.strptime(raw_value, "%d.%m.%Y").date()
        return result

    def get_author(self) -> str:
        """
        returns the author of the message implementation guide
        """
        return self._element_tree.getroot().attrib["Author"]

    def get_version(self) -> str:
        """
        returns the version of the message implementation guide
        """
        return self._element_tree.getroot().attrib["Versionsnummer"]

    def read(self) -> MessageImplementationGuide:
        """
        read the entire file and convert it to a MessageImplementationGuid instance
        """
        result = MessageImplementationGuide(
            veroeffentlichungsdatum=self.get_publishing_date(),
            autor=self.get_author(),
            versionsnummer=self.get_version(),
        )
        return result
