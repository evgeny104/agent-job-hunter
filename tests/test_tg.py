import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.telegram_tools import scan_chats

CHAT = "@qa_jobs"  # замени на свой чат: @username или название группы


async def main():
    msgs = await scan_chats(chat_names=[CHAT], limit=5)
    for m in msgs:
        if "error" in m:
            print(f"ОШИБКА чата {m['chat']}: {m['error']}")
            continue
        print(m.get("date"), "|", (m.get("text") or "")[:100])

asyncio.run(main())
