import os
from dotenv import load_dotenv
from telethon import TelegramClient
from config.settings import SESSION_FILE

load_dotenv()

client = TelegramClient(str(SESSION_FILE), int(os.getenv("TG_API_ID")), os.getenv("TG_API_HASH"))


async def scan_chats(chat_names: list[str], limit: int = 50) -> list[dict]:
    """Читает последние `limit` сообщений из указанных чатов."""
    results = []
    async with client:
        for chat in chat_names:
            try:
                entity = await client.get_entity(chat)
                messages = await client.get_messages(entity, limit=limit)
            except Exception as e:
                results.append({"chat": chat, "error": str(e)})
                continue  # <-- вот этого не хватало: переходим к следующему чату

            for m in messages:
                if m.text:
                    link = None
                    if getattr(entity, "username", None):
                        link = f"https://t.me/{entity.username}/{m.id}"
                    results.append({
                        "id": m.id,
                        "chat": chat,
                        "date": str(m.date),
                        "text": m.text,
                        "link": link,
                    })
    return results