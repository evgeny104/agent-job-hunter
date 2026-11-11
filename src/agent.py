import json
from src.llm import client, MODEL

# --- Инструменты агента ---

def get_current_datetime() -> str:
    """Возвращает текущие дату и время."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Таблица соответствия: имя функции -> сама функция
TOOLS = {
    "get_current_datetime": get_current_datetime,
}

# Описание инструментов для модели (формат OpenAI)
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": "Возвращает текущие дату и время",
            "parameters": {"type": "object", "properties": {}},
        },
    }
]


def run_agent(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS_SCHEMA,
        )
        msg = response.choices[0].message

        # Если модель хочет вызвать инструменты
        if msg.tool_calls:
            messages.append(msg)  # добавляем запрос модели в историю
            for call in msg.tool_calls:
                fn_name = call.function.name
                args = json.loads(call.function.arguments or "{}")
                print(f"🔧 Агент вызывает: {fn_name}({args})")
                result = TOOLS[fn_name](**args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": str(result),
                })
        else:
            return msg.content  # финальный ответ


if __name__ == "__main__":
    answer = run_agent("Который сейчас час? Ответь и скажи, откуда ты это узнал.")
    print("\n🤖 Агент:", answer)