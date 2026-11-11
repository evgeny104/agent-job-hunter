# agent-job-hunter

> **Статус: MVP, в активной разработке.** Ядро работает: сканирование чатов,
> фильтры, LLM-оценка вакансий. В работе: письма, отчёты, агентный цикл — см. Roadmap.

Персональный агент поиска работы на базе LLM Kimi: сканирует Telegram-чаты
с вакансиями, отбирает подходящие под стек кандидата и оценивает их через LLM.

## Как это работает

```
scan_chats() → пропуск обработанных → фильтр #вакансия/#vacancy
             → пре-фильтр по keywords.txt → match_vacancy() (LLM: score 0–100)
```

Дешёвые фильтры отсекают мусор до вызова LLM — Kimi вызывается только для
кандидатов, прошедших отбор. Дальше по roadmap: адаптация сопроводительного
письма и отчёты в `reports/ГГГГ-ММ-ДД/`.

**Стек:** Python 3, Telethon (userbot), OpenAI SDK + Kimi `k3.1-pro`, python-dotenv.

## Быстрый старт

```bash
pip install -r requirements.txt
cp .env.example .env        # затем заполнить .env своими значениями
```

В `.env` нужны: `KIMI_API_KEY` / `KIMI_BASE_URL` / `KIMI_MODEL` (ключ Kimi),
`TG_API_ID` / `TG_API_HASH` (https://my.telegram.org/apps).
`TG_PHONE` — только для диагностики `scripts/diag_tg.py`.

Что создать локально (в git это не попадает):

1. **`.env`** — из шаблона выше.
2. **Сессия Telegram** — `python scripts/qr_login.py`, отсканировать
   `qr_login.png` в Telegram (Настройки → Устройства → Подключить устройство).
   Появится `tg_session.session`.
3. **Резюме** — положить свой `.txt` в `data/resume/` (читается первый файл).

## Запуск

```bash
python tests/test_tg.py        # только сканирование чата @qa_jobs
python tests/test_match.py     # полный MVP-пайплайн на тестовой памяти
```

Чат для сканирования задаётся константой `CHAT` в этих скриптах.
Тесты пишут память в `var/processed_test.json`, боевой режим — `var/processed.json`.

## Структура

```
config/settings.py      # все пути проекта
scripts/qr_login.py     # авторизация Telegram по QR
scripts/diag_tg.py      # диагностика отправки кода
src/llm.py              # клиент Kimi
src/telegram_tools.py   # scan_chats(): id, chat, date, text, link
src/resume_tools.py     # load_resume(), match_vacancy()
src/state.py            # память обработанных message_id
src/agent.py            # скелет агента с tool calling (Этап 7)
data/keywords.txt       # стек для пре-фильтра
```

## Особенности

- У `k3.1-pro` `temperature` только 1; `response_format=json_object` работает.
- Чтение чатов — только userbot (Telethon), Bot API не подходит.
- Ошибка одного чата не прерывает сканирование остальных.

## Roadmap

- [x] Этапы 1–4: настройки, LLM, сканирование, память, match-оценка — MVP работает
- [ ] Этап 5: `src/letter_tools.py` — адаптация сопроводительного письма
- [ ] Этап 6: `src/report_tools.py` — отчёты в `reports/ГГГГ-ММ-ДД/`
- [ ] Этап 7: полный агент в `src/agent.py` (tool calling: scan/match/adapt/save)
