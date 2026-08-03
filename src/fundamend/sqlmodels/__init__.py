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

from .ahb_formatversion_diff_view import AhbFormatversionDiffLine, DiffStatus, create_ahb_formatversion_diff_view
from .ahb_pruefi_diff_view import AhbPruefiDiffLine, create_ahb_pruefi_diff_view
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
from .messageimplementationguide import (
    MessageImplementationGuide,
    MigCode,
    MigDataElement,
    MigDataElementGroup,
    MigSegment,
    MigSegmentGroup,
    MigSegmentGroupLink,
)
from .mig_diff_view import MigDiffLine, create_mig_diff_view
from .migview import MigHierarchyMaterialized, create_db_and_populate_with_mig_view, create_mig_view

__all__ = [
    "AhbFormatversionDiffLine",
    "AhbHierarchyMaterialized",
    "AhbPruefiDiffLine",
    "AhbTabellenLine",
    "Anwendungsfall",
    "Anwendungshandbuch",
    "Bedingung",
    "Code",
    "DataElement",
    "DataElementGroup",
    "DiffStatus",
    "MessageImplementationGuide",
    "MigCode",
    "MigDataElement",
    "MigDataElementGroup",
    "MigDiffLine",
    "MigHierarchyMaterialized",
    "MigSegment",
    "MigSegmentGroup",
    "MigSegmentGroupLink",
    "Segment",
    "SegmentGroup",
    "create_ahb_formatversion_diff_view",
    "create_ahb_pruefi_diff_view",
    "create_ahb_view",
    "create_ahbtabellen_view",
    "create_db_and_populate_with_ahb_view",
    "create_db_and_populate_with_mig_view",
    "create_mig_diff_view",
    "create_mig_view",
]
