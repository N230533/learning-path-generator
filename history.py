import json
import os
from datetime import datetime

HISTORY_FILE = "history.json"


def load_history() -> list[dict]:
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_entry(topic: str, level: str, hours: int, path: list[dict]) -> dict:
    history = load_history()
    now = datetime.now()
    entry = {
        "id": now.strftime("%Y%m%d%H%M%S%f"),
        "time": now.strftime("%d %b %Y, %I:%M %p"),
        "topic": topic,
        "level": level,
        "hours": hours,
        "path": path,
    }
    history.insert(0, entry)  # newest first
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    return entry


def clear_history() -> None:
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)