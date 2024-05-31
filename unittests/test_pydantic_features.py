import pytest

try:
    from pydantic import TypeAdapter
except ImportError:
    pytest.skip("Only available with pydantic", allow_module_level=True)

from fundamend import Anwendungshandbuch, MessageImplementationGuide


def test_json_schema_export_mig() -> None:
    adapter = TypeAdapter(MessageImplementationGuide)
    schema = adapter.json_schema()
    assert schema is not None


def test_json_schema_export_ahb() -> None:
    adapter = TypeAdapter(Anwendungshandbuch)
    schema = adapter.json_schema()
    assert schema is not None
