from config.settings import COVER_LETTER_FILE
from agent.llm import client, MODEL


def load_template(path=COVER_LETTER_FILE) -> str:
    """Читает шаблон сопроводительного письма."""
    if not path.exists():
        raise FileNotFoundError(
            f"Нет шаблона письма: {path}\n"
            "Скопируйте data/cover_letter_template.example.txt и перепишите под себя."
        )
    return path.read_text(encoding="utf-8").strip()


def adapt_letter(resume: str, vacancy_text: str, template: str) -> str:
    """Адаптирует шаблон письма под конкретную вакансию. Возвращает готовый текст."""
    prompt = f"""Ты — карьерный консультант. Адаптируй сопроводительное письмо под вакансию.

РЕЗЮМЕ КАНДИДАТА:
{resume[:6000]}

ВАКАНСИЯ:
{vacancy_text[:4000]}

ТЕКУЩИЙ ШАБЛОН ПИСЬМА:
{template}

Задача: перепиши шаблон под эту вакансию. Правила:
1. Сохрани структуру и деловой тон шаблона (приветствие → опыт → призыв → подпись).
2. В среднем абзаце подчеркни опыт и стек, которые релевантны именно этой вакансии.
3. Не выдумывай навыки и опыт, которых нет в резюме.
4. Подпись оставь как в шаблоне.
5. Ответь только текстом письма, без пояснений."""

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content.strip()
