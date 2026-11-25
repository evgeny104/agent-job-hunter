"""Ядро агента: цикл tool calling.

Получает сообщение пользователя → модель выбирает инструмент → агент исполняет
через реестр TOOLS → результат возвращается модели → повтор, пока модель
не даст финальный ответ. Лимит итераций защищает от бесконечного цикла.
"""

import json

from agent.llm import client, MODEL
from agent.prompts import SYSTEM_PROMPT
from agent.tools import TOOLS, TOOLS_SCHEMA

MAX_ITERATIONS = 20  # защита от бесконечного цикла


def run_agent(user_message: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    for _ in range(MAX_ITERATIONS):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS_SCHEMA,
        )
        msg = response.choices[0].message

        if msg.tool_calls:
            messages.append(msg)
            for call in msg.tool_calls:
                fn_name = call.function.name
                args = json.loads(call.function.arguments or "{}")
                print(f"  -> {fn_name}({json.dumps(args, ensure_ascii=False)[:120]})", flush=True)
                try:
                    result = TOOLS[fn_name](**args)
                except Exception as e:
                    result = {"error": f"{type(e).__name__}: {e}"}
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result, ensure_ascii=False, default=str),
                })
        else:
            return msg.content

    return "Достигнут лимит итераций — прервано. Попробуйте уточнить задачу."
