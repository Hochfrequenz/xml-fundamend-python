"""classes that represent MIGs"""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, eq=True, order=True, unsafe_hash=True, kw_only=True)
class MessageImplementationGuide:
    """
    message implementation guide (MIG)
    """

    veroeffentlichungsdatum: date
    """
    publishing date
    """
    autor: str
    """author, most likely 'BDEW'"""

    versionsnummer: str
    """e.g. '1.1c'"""
