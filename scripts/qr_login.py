import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
from telethon import TelegramClient
import qrcode
from config.settings import SESSION_FILE

load_dotenv()

client = TelegramClient(
    str(SESSION_FILE),
    int(os.getenv("TG_API_ID")),
    os.getenv("TG_API_HASH"),
)

async def main():
    await client.connect()
    while not await client.is_user_authorized():
        qr = await client.qr_login()
        img = qrcode.make(qr.url)
        img.save("qr_login.png")
        print("QR-код сохранён в qr_login.png — отсканируй его из Telegram")
        print("Настройки → Устройства → Подключить устройство")
        await qr.wait()
    print("Авторизация успешна!")
    await client.disconnect()

asyncio.run(main())