from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict

try:
    import jsonschema
except ImportError:  # optional dependency
    jsonschema = None

def load_schema(schema_path: str) -> Dict[str, Any]:
    p = Path(schema_path)
    return json.loads(p.read_text(encoding="utf-8"))

def validate_payload(payload: Dict[str, Any], schema: Dict[str, Any]) -> None:
    if jsonschema is None:
        return  # keep scaffold lightweight; add jsonschema when we start enforcing
    jsonschema.validate(instance=payload, schema=schema)
