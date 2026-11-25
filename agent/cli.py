"""Точка входа: интерактивный диалог с агентом.

Запуск из корня проекта: python -m agent.cli
"""

import sys

from agent.agent import run_agent


def main():
    # консоль Windows (cp1251) не выводит эмодзи из текста вакансий
    sys.stdout.reconfigure(errors="replace")
    sys.stderr.reconfigure(errors="replace")
    print("Job-hunter агент. Команды: «проверь чаты», «оцени вакансию: <текст>». Выход: exit")
    while True:
        try:
            user = input("\nВы: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user:
            continue
        if user.lower() in ("exit", "выход", "quit"):
            break
        print("\nАгент:", run_agent(user), flush=True)


if __name__ == "__main__":
    main()
