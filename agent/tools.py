"""Инструменты агента: адаптеры над модулями tools/ + реестр TOOLS/TOOLS_SCHEMA.

Агент (agent/agent.py) вызывает инструменты по имени, не зная деталей реализации.
"""

import asyncio
import re

from config.settings import KEYWORDS_FILE
from tools.state import load_processed, mark_processed
from tools.telegram_tools import scan_chats, load_chat_names, send_to_saved
from tools.resume_tools import load_resume, match_vacancy
from tools.letter_tools import load_template, adapt_letter
from tools.report_tools import save_report, build_summary

# --- Кэш данных кандидата (грузим лениво, один раз) ---
_resume_cache = None
_keywords_cache = None


def _resume() -> str:
    global _resume_cache
    if _resume_cache is None:
        _resume_cache = load_resume()
    return _resume_cache


def _keywords() -> list[str]:
    global _keywords_cache
    if _keywords_cache is None:
        parts = re.split(r"[,\n]", KEYWORDS_FILE.read_text(encoding="utf-8"))
        _keywords_cache = [p.strip().lower() for p in parts if p.strip()]
    return _keywords_cache


# --- Инструменты ---

def tool_scan_chats(limit: int = 20) -> list[dict]:
    """Сканирует чаты из TG_CHATS (.env), отдаёт новые вакансии кандидата."""
    chats = load_chat_names()
    if not chats:
        return [{"error": "В .env не задан TG_CHATS (через запятую, напр. @qa_jobs,@chat2)"}]

    msgs = asyncio.run(scan_chats(chats, limit))
    keywords = _keywords()
    processed = load_processed()
    seen, result = [], []

    for m in msgs:
        if "error" in m:
            continue
        seen.append(m["id"])
        if m["id"] in processed:
            continue
        text = (m.get("text") or "").strip()
        if "#вакансия" not in text.lower() and "#vacancy" not in text.lower():
            continue
        if not any(re.search(rf"\b{re.escape(kw)}\b", text.lower()) for kw in keywords):
            continue
        result.append({
            "id": m["id"], "chat": m["chat"],
            "date": m["date"], "text": text, "link": m.get("link"),
        })

    if seen:
        mark_processed(seen)
    return result


def tool_match_vacancy(vacancy_text: str) -> dict:
    """Оценивает вакансию относительно резюме: score 0-100, relevant (>= 60)."""
    return match_vacancy(_resume(), vacancy_text)


def tool_adapt_letter(vacancy_text: str) -> str:
    """Адаптирует сопроводительное письмо под вакансию."""
    return adapt_letter(_resume(), vacancy_text, load_template())


def tool_save_report(entries: list[dict]) -> str:
    """Сохраняет отчёт в reports/ГГГГ-ММ-ДД/report.txt."""
    path = save_report(entries)
    return f"Отчёт сохранён: {path}"


def tool_send_summary(entries: list[dict]) -> str:
    """Отправляет сводку по вакансиям в «Избранное» Telegram."""
    return asyncio.run(send_to_saved(build_summary(entries)))


TOOLS = {
    "scan_chats": tool_scan_chats,
    "match_vacancy": tool_match_vacancy,
    "adapt_letter": tool_adapt_letter,
    "save_report": tool_save_report,
    "send_summary": tool_send_summary,
}

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "scan_chats",
            "description": "Сканирует чаты с вакансиями (список из TG_CHATS в .env), "
                           "возвращает новые непросмотренные сообщения с хэштегами "
                           "#вакансия/#vacancy и совпадением по ключевым словам стека",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "сколько сообщений на чат читать, по умолчанию 20"}
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "match_vacancy",
            "description": "Оценивает релевантность вакансии резюме кандидата",
            "parameters": {
                "type": "object",
                "properties": {
                    "vacancy_text": {"type": "string", "description": "полный текст вакансии"}
                },
                "required": ["vacancy_text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "adapt_letter",
            "description": "Адаптирует сопроводительное письмо под конкретную вакансию",
            "parameters": {
                "type": "object",
                "properties": {
                    "vacancy_text": {"type": "string", "description": "полный текст вакансии"}
                },
                "required": ["vacancy_text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_report",
            "description": "Сохраняет отчёт по вакансиям в reports/ГГГГ-ММ-ДД/report.txt",
            "parameters": {
                "type": "object",
                "properties": {
                    "entries": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "список вакансий: link, score, relevant, stack_match, reason, letter",
                    }
                },
                "required": ["entries"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_summary",
            "description": "Отправляет краткую сводку по вакансиям пользователю в Telegram",
            "parameters": {
                "type": "object",
                "properties": {
                    "entries": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "список вакансий с полями score, relevant, link, stack_match",
                    }
                },
                "required": ["entries"],
            },
        },
    },
]
