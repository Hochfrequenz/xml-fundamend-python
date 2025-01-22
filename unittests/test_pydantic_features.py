from pathlib import Path

import pytest
from pydantic import RootModel, TypeAdapter

from fundamend import AhbReader, Anwendungshandbuch, MessageImplementationGuide, MigReader

ahb_utilts_11c = AhbReader(
    Path(__file__).parent / "example_files" / "UTILTS_AHB_1.1c_Lesefassung_2023_12_12_ZPbXedn.xml"
).read()
ahb_utilts_11d = AhbReader(
    Path(__file__).parent / "example_files" / "UTILTS_AHB_1.1d_Konsultationsfassung_2024_04_02.xml"
).read()
utilts_mig_11c = MigReader(
    Path(__file__).parent / "example_files" / "UTILTS_MIG_1.1c_Lesefassung_2023_12_12.xml"
).read()
utilts_mig_11d = MigReader(
    Path(__file__).parent / "example_files" / "UTILTS_MIG_1.1d_Konsultationsfassung_2024_04_02.xml"
).read()


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
