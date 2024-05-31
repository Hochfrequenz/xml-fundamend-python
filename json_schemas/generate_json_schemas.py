import json
import pathlib

try:
    from pydantic import TypeAdapter
except ImportError as import_error:
    import_error.msg += " Did you install pydantic or fundamend[pydantic]?"
    raise
from fundamend import Anwendungshandbuch, MessageImplementationGuide

for fundamend_type in [MessageImplementationGuide, Anwendungshandbuch]:
    this_directory = pathlib.Path(__file__).parent.absolute()
    file_name = fundamend_type.__name__ + ".schema.json"  # pylint:disable=invalid-name
    file_path = this_directory / file_name
    schema = TypeAdapter(fundamend_type).json_schema()
    with open(file_path, "w", encoding="utf-8") as json_schema_file:
        json.dump(schema, json_schema_file, ensure_ascii=False, sort_keys=True, indent=4)
