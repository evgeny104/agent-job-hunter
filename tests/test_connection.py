import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("KIMI_API_KEY"),
    base_url=os.getenv("KIMI_BASE_URL"),
)

# 1. Список доступных моделей
models = client.models.list()
print("Доступные модели:")
for m in models.data:
    print(" -", m.id)

# 2. Пробный вызов
resp = client.chat.completions.create(
    model=os.getenv("KIMI_MODEL"),
    messages=[{"role": "user", "content": "Скажи привет одним словом"}],
)
print("\nОтвет модели:", resp.choices[0].message.content)
