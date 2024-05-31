"""
wrapper around either pydantic.dataclass or stdlib dataclass
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dataclasses import dataclass
else:
    try:
        from pydantic.dataclasses import dataclass  # pylint:disable=unused-import
    except ImportError:
        from dataclasses import dataclass
__all__ = ["dataclass"]
