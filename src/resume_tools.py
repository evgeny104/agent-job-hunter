import json
from config.settings import RESUME_FILE
from src.llm import client, MODEL


def load_resume() -> str:
    """Читает текст резюме из файла, путь — в config/settings.py."""
    if not RESUME_FILE.exists():
        raise FileNotFoundError(f"Файл резюме не найден: {RESUME_FILE}")
    print(f"Загружено резюме: {RESUME_FILE.name}")
    return RESUME_FILE.read_text(encoding="utf-8")


def match_vacancy(resume: str, vacancy_text: str) -> dict:
    """Оценивает релевантность вакансии резюме. Возвращает dict."""
    prompt = f"""Сравни вакансию с резюме кандидата.

РЕЗЮМЕ:
{resume[:6000]}

ВАКАНСИЯ:
{vacancy_text[:4000]}

Оцени, подходит ли эта вакансия кандидату. Ответь строго JSON:
{{
  "is_vacancy": true/false,      // является ли текст вообще вакансией
  "relevant": true/false,        // релевантна ли она резюме (score >= 60)
  "score": 0-100,                // процент совпадения стека и опыта
  "stack_match": ["..."],        // какие технологии совпали
  "reason": "краткое объяснение"
}}"""

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return json.loads(resp.choices[0].message.content)
