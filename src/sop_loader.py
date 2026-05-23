import json
from pathlib import Path
from typing import Any, Dict


def load_sop(path: str = "data/sop.json") -> Dict[str, Any]:
    sop_path = Path(path)
    if not sop_path.exists():
        raise FileNotFoundError(f"SOP file not found: {sop_path}")
    with sop_path.open("r", encoding="utf-8") as file:
        return json.load(file)
