"""
models that work together with SQLModel+SQLAlchemy
you need to install fundamend[sqlmodels] to use this sub-package
"""

# the models here do NOT inherit from the original models, because I didn't manage to fix the issue that arise:
# <frozen abc>:106: in __new__
#     ???
# E   TypeError: Anwendungshandbuch.__init_subclass__() takes no keyword arguments
#
# or
#
# ..\.tox\dev\Lib\site-packages\sqlmodel\main.py:697: in get_sqlalchemy_type
#     raise ValueError(f"{type_} has no matching SQLAlchemy type")
# E   ValueError: <class 'fundamend.models.anwendungshandbuch.Anwendungshandbuch'> has no matching SQLAlchemy type
# => you need to keep the models in sync manually by now

from .ahbtabellen_view import AhbTabellenLine, create_ahbtabellen_view
from .ahbview import AhbHierarchyMaterialized, create_ahb_view, create_db_and_populate_with_ahb_view
from .anwendungshandbuch import (
    Anwendungsfall,
    Anwendungshandbuch,
    Bedingung,
    Code,
    DataElement,
    DataElementGroup,
    Segment,
    SegmentGroup,
)

__all__ = [
    "create_ahb_view",
    "AhbHierarchyMaterialized",
    "create_db_and_populate_with_ahb_view",
    "create_ahbtabellen_view",
    "AhbTabellenLine",
    "Code",
    "DataElement",
    "DataElementGroup",
    "Segment",
    "SegmentGroup",
    "Anwendungsfall",
    "Bedingung",
    "Anwendungshandbuch",
]
