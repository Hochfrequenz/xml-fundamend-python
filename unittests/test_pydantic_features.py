import pytest

try:
    from pydantic import RootModel, TypeAdapter
except ImportError:
    pytest.skip("Only available with pydantic", allow_module_level=True)

from fundamend import Anwendungshandbuch, MessageImplementationGuide

from .example_ahb_utilts_11c import ahb_utilts_11c
from .example_ahb_utilts_11d import ahb_utilts_11d
from .example_migs import utilts_mig_11c, utilts_mig_11d


def test_json_schema_export_mig() -> None:
    adapter = TypeAdapter(MessageImplementationGuide)
    schema = adapter.json_schema()
    assert schema is not None


def test_json_schema_export_ahb() -> None:
    adapter = TypeAdapter(Anwendungshandbuch)
    schema = adapter.json_schema()
    assert schema is not None


@pytest.mark.parametrize("model", [utilts_mig_11d, utilts_mig_11c, ahb_utilts_11d, ahb_utilts_11c])
def test_json_dump(model: Anwendungshandbuch | MessageImplementationGuide) -> None:
    # https://docs.pydantic.dev/latest/concepts/dataclasses/#json-dumping
    if isinstance(model, Anwendungshandbuch):
        root_model = RootModel[Anwendungshandbuch](model)
    elif isinstance(model, MessageImplementationGuide):
        root_model = RootModel[MessageImplementationGuide](model)  # type:ignore[assignment]
    else:
        raise ValueError(f"Unexpected type: {model}")
    json_dict = root_model.model_dump(mode="json")
    assert json_dict is not None
