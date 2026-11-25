import json
from config.settings import PROCESSED_FILE

STATE_FILE = PROCESSED_FILE  # путь по умолчанию, можно переопределить параметром


def load_processed(state_file=None) -> set:
    path = state_file or STATE_FILE
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def mark_processed(ids: list, state_file=None) -> None:
    path = state_file or STATE_FILE
    processed = load_processed(path)
    processed.update(ids)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(list(processed), f)
