
import json
from pathlib import Path
from typing import Dict

from src.schema.submit_test import TestSession

test_sessions: Dict[str, TestSession] = {}

JSON_PATH = Path("test_results.json")

def save_to_file():
    data = {k: v.dict() for k, v in test_sessions.items()}
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_from_file():
    if JSON_PATH.exists():
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
            for key, val in raw.items():
                test_sessions[key] = TestSession(**val)
