import json
from pathlib import Path


def load_settings():
    path = (
        Path(__file__).resolve().parent.parent
        / "config"
        / "settings.json"
    )

    if not path.is_file():
        return {}

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)