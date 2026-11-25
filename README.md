# agent-job-hunter

Персональный LLM-агент поиска работы (Kimi + Telethon): сам сканирует
Telegram-чаты с вакансиями, оценивает релевантность резюме, адаптирует
сопроводительное письмо, сохраняет отчёт и присылает сводку в Telegram.

## Как работает агент

Агентный цикл (tool calling): модель сама планирует действия и вызывает инструменты.

```
пользователь: «проверь чаты»
        │
        ▼
  ┌─ LLM: выбирает инструмент ──┐
  │  scan_chats ──► match_vacancy (для каждой вакансии)
  │  adapt_letter (score >= 60) ──► save_report ──► send_summary
  └─ LLM: итоговый ответ ◄──────┘
```

Пять инструментов: `scan_chats`, `match_vacancy`, `adapt_letter`,
`save_report`, `send_summary`. Дешёвые фильтры (память обработанных,
хэштеги `#вакансия`/`#vacancy`, ключевые слова стека) отсекают мусор до
вызова LLM. Пример реального запуска: 13 вакансий → 5 релевантных
(score 60–92) с готовыми письмами → отчёт в `reports/2026-11-25/report.txt`.

**Стек:** Python 3, Telethon (userbot), OpenAI SDK + Kimi `k3.1-pro`, python-dotenv.

## Быстрый старт

```bash
pip install -r requirements.txt
cp .env.example .env        # затем заполнить своими значениями
```

В `.env`: `KIMI_API_KEY` / `KIMI_BASE_URL` / `KIMI_MODEL` (ключ Kimi),
`TG_API_ID` / `TG_API_HASH` (https://my.telegram.org/apps),
`TG_CHATS=@qa_jobs,@chat2` — чаты для сканирования. `TG_PHONE` — только
для диагностики `scripts/diag_tg.py`.

Что создать локально (в git не попадает):

1. **`.env`** — из шаблона выше.
2. **Сессия Telegram** — `python scripts/qr_login.py`, отсканировать
   `qr_login.png` в Telegram (Настройки → Устройства → Подключить устройство).
3. **Резюме** — свой `.txt` в `data/resume/` (читается первый файл).
4. **Шаблон письма** — `cp data/cover_letter_template.example.txt data/cover_letter_template.txt`,
   заменить плейсхолдеры `{...}` на свои данные.

## Запуск

```bash
python src/agent.py          # агент: диалог по команде («проверь чаты», exit — выход)
python tests/test_tg.py      # только сканирование чата
python tests/test_match.py   # пайплайн матчинга на тестовой памяти
python tests/test_letter.py  # генерация письма для тестовой вакансии
```

Тесты пишут память в `var/processed_test.json`, агент — в `var/processed.json`.

## Структура

```
config/settings.py      # все пути проекта
scripts/qr_login.py     # авторизация Telegram по QR
scripts/diag_tg.py      # диагностика отправки кода
src/agent.py            # агент: системный промпт, tool calling, лимит итераций
src/telegram_tools.py   # scan_chats(), send_to_saved() — новый клиент на вызов
src/resume_tools.py     # load_resume(), match_vacancy() (score 0–100, JSON)
src/letter_tools.py     # load_template(), adapt_letter()
src/report_tools.py     # save_report(), build_summary()
src/state.py            # память обработанных message_id
data/keywords.txt       # стек для пре-фильтра
```

## Особенности

- У `k3.1-pro` `temperature` только 1; `response_format=json_object` работает.
- Чтение чатов — только userbot (Telethon), Bot API не подходит.
- Telethon привязывает соединение к event loop — поэтому клиент создаётся
  на каждый вызов, иначе scan и send в одном запуске падают.
- Ошибка одного чата или инструмента не прерывает работу агента.
- Цикл агента ограничен `MAX_ITERATIONS` — защита от бесконечных вызовов.
