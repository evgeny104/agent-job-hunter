import asyncio
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import KEYWORDS_FILE, PROCESSED_TEST_FILE
from src.telegram_tools import scan_chats
from src.resume_tools import load_resume, match_vacancy
from src.state import load_processed, mark_processed
import src.state as state

state.STATE_FILE = PROCESSED_TEST_FILE  # тестовая память, не трогает боевую

CHAT = "@qa_jobs"  # замени на реальный чат: @username или название группы


def load_keywords() -> list[str]:
    text = KEYWORDS_FILE.read_text(encoding="utf-8")
    parts = re.split(r"[,\n]", text)
    return [p.strip().lower() for p in parts if p.strip()]


async def main():
    resume = load_resume()
    keywords = load_keywords()
    processed = load_processed()
    print(f"Ключевых слов: {len(keywords)}, в памяти: {len(processed)} сообщений", flush=True)

    msgs = await scan_chats(chat_names=[CHAT], limit=2)
    print(f"Получено сообщений: {len(msgs)}", flush=True)

    seen_ids = []  # всё, что увидели в этом запуске
    for m in msgs:
        if "error" in m:
            print(f"ОШИБКА чата {m['chat']}: {m['error']}", flush=True)
            continue
        seen_ids.append(m["id"])

        if m["id"] in processed:
            continue  # уже анализировали раньше

        text = m.get("text") or ""
        if "#вакансия" not in text.lower() and "#vacancy" not in text.lower():
            continue

        # быстрый фильтр по стеку — без вызова модели
        text_lower = text.lower()
        if not any(re.search(rf"\b{re.escape(kw)}\b", text_lower) for kw in keywords):
            continue

        print(f"\n[{m.get('date')}] {text[:60]}", flush=True)
        try:
            result = match_vacancy(resume, text)
            print(f"  >>> {result['score']}/100 | relevant={result['relevant']}", flush=True)
            print(f"  >>> стек: {result['stack_match']}", flush=True)
            print(f"  >>> причина: {result['reason']}", flush=True)
        except Exception as e:
            print(f"  !!! Ошибка модели: {type(e).__name__}: {e}", flush=True)

    mark_processed(seen_ids)  # запоминаем всё увиденное
    print("\nГотово. Память обновлена.", flush=True)


asyncio.run(main())