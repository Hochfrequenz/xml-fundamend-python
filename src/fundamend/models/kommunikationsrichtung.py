"""contains the Kommunikationsrichtung model"""

from fundamend.models.base import FundamendBaseModel


# needs to be separate file/module to avoid circular imports
class Kommunikationsrichtung(FundamendBaseModel):
    """
    a strongly typed representation of the 'Kommunikation_von' attribute of anwendungsfall
    """

    sender: str  #: e.g. "NB"
    empfaenger: str  #: e.g. "MSB"


__all__ = ["Kommunikationsrichtung"]
