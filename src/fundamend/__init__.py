"""
fundamend contains Formate und Datenmodelle für die Energiewirtschaft in Deutschland.
pip install xml-fundamend
"""

from .models import MessageImplementationGuide
from .reader import MigReader

__all__ = ["MigReader", "MessageImplementationGuide"]
