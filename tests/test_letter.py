import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.resume_tools import load_resume
from tools.letter_tools import load_template, adapt_letter

VACANCY = """#вакансия
Ищем Middle AQA (Python) в финтех-проект.

Стек: Python, pytest, Playwright, Docker, Kafka, REST API, PostgreSQL, GitLab CI.

Задачи: выстраивать E2E и интеграционное тестирование микросервисов,
писать автотесты на бэкенд и фронтенд, поддерживать CI.

Опыт от 2 лет, готовность разбираться в предметной области финтеха."""

resume = load_resume()
template = load_template()

print(f"Шаблон: {len(template)} символов, резюме загружено")
letter = adapt_letter(resume, VACANCY, template)
print("\n--- ГОТОВОЕ ПИСЬМО ---\n")
print(letter)
