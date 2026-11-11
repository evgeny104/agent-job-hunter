import json
from config.settings import PROCESSED_FILE

STATE_FILE = PROCESSED_FILE  # подменяется в тестах


def load_processed() -> set:
    if STATE_FILE.exists():
        with open(STATE_FILE, encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def mark_processed(ids: list) -> None:
    processed = load_processed()
    processed.update(ids)
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(list(processed), f)