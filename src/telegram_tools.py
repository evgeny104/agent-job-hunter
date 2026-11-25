import os
from dotenv import load_dotenv
from telethon import TelegramClient
from config.settings import SESSION_FILE

load_dotenv()


def new_client() -> TelegramClient:
    """Новый клиент на каждый вызов: Telethon привязывает соединение
    к event loop, поэтому нельзя переиспользовать клиента между asyncio.run()."""
    return TelegramClient(str(SESSION_FILE), int(os.getenv("TG_API_ID")), os.getenv("TG_API_HASH"))


async def send_to_saved(text: str) -> str:
    """Отправляет сообщение в «Избранное» (Saved Messages) пользователя."""
    async with new_client() as client:
        await client.send_message("me", text)
    return "Отправлено в «Избранное»"


def load_chat_names() -> list[str]:
    """Список чатов для сканирования из .env: TG_CHATS=@qa_jobs,@chat2."""
    raw = os.getenv("TG_CHATS", "")
    return [c.strip() for c in raw.split(",") if c.strip()]


async def scan_chats(chat_names: list[str], limit: int = 50) -> list[dict]:
    """Читает последние `limit` сообщений из указанных чатов."""
    results = []
    async with new_client() as client:
        for chat in chat_names:
            try:
                entity = await client.get_entity(chat)
                messages = await client.get_messages(entity, limit=limit)
            except Exception as e:
                results.append({"chat": chat, "error": str(e)})
                continue  # ошибка в одном чате не прерывает скан остальных

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
