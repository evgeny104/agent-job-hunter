import asyncio
import os
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

client = TelegramClient(
    "tg_session",
    int(os.getenv("TG_API_ID")),
    os.getenv("TG_API_HASH"),
)

async def main():
    phone = os.getenv("TG_PHONE")
    try:
        await client.connect()
        sent = await client.send_code_request(phone)
        print("Запрос кода отправлен успешно.")
        print("Тип отправки:", sent.type)
    except Exception as e:
        print("ОШИБКА:", type(e).__name__, "-", e)
    finally:
        await client.disconnect()

asyncio.run(main())