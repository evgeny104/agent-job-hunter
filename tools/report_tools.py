from datetime import date
from pathlib import Path
from config.settings import REPORTS_DIR


def save_report(entries: list[dict], day: str | None = None) -> Path:
    """Сохраняет отчёт по вакансиям в reports/ГГГГ-ММ-ДД/report.txt.

    entries — список словарей: link, score, relevant, stack_match, reason, letter.
    """
    day = day or date.today().isoformat()
    folder = REPORTS_DIR / day
    folder.mkdir(parents=True, exist_ok=True)

    lines = [f"Отчёт по вакансиям за {day}", "=" * 40, ""]
    for e in entries:
        lines.append(f"Вакансия: {e.get('link') or e.get('title', '(без ссылки)')}")
        lines.append(f"Score: {e.get('score', '?')}/100 | relevant={e.get('relevant')}")
        lines.append(f"Стек: {', '.join(e.get('stack_match') or [])}")
        lines.append(f"Причина: {e.get('reason', '')}")
        lines.append("")
        lines.append("Сопроводительное письмо:")
        lines.append(e.get("letter") or "(не сгенерировано)")
        lines.append("")
        lines.append("-" * 40)
        lines.append("")

    path = folder / "report.txt"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def build_summary(entries: list[dict], day: str | None = None) -> str:
    """Короткая сводка для уведомления в Telegram."""
    day = day or date.today().isoformat()
    total = len(entries)
    relevant = [e for e in entries if e.get("relevant")]
    lines = [f"Job-hunter за {day}: найдено {total}, подходящих — {len(relevant)}.", ""]
    for e in relevant:
        lines.append(f"• {e.get('score', '?')}/100 — {e.get('link') or 'вакансия без ссылки'}")
        lines.append(f"  стек: {', '.join((e.get('stack_match') or [])[:5])}")
    if relevant:
        lines.append("")
        lines.append(f"Письма и детали: reports/{day}/report.txt")
    return "\n".join(lines)
