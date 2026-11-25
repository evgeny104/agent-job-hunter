# agent-job-hunter

Персональный LLM-агент поиска работы: сам сканирует Telegram-чаты с вакансиями,
оценивает их по вашему резюме, пишет сопроводительные письма и сохраняет отчёты.

## Что понадобится

Два ключа. Получение занимает 5–10 минут.

1. **Ключ Kimi** (для LLM) — https://platform.moonshot.ai → регистрация →
   API Keys → создать ключ.
2. **Ключи Telegram** — https://my.telegram.org/apps → Create application →
   скопируйте `api_id` и `api_hash`.

## Настройка и первый запуск

**Шаг 1.** Клонируйте репозиторий и перейдите в папку проекта.

**Шаг 2.** Установите зависимости: `pip install -r requirements.txt`

**Шаг 3.** Создайте файл конфигурации из шаблона: `cp .env.example .env`

**Шаг 4.** Откройте `.env` и заполните три значения:
- `KIMI_API_KEY` — ваш ключ Kimi
- `TG_API_ID`, `TG_API_HASH` — с my.telegram.org
- `TG_CHATS` — чаты для сканирования, напр. `@qa_jobs,@chat2`

**Шаг 5.** Авторизуйтесь в Telegram: `python scripts/qr_login.py`
Отсканируйте `qr_login.png` в Telegram: Настройки → Устройства → Подключить устройство.

**Шаг 6.** Положите резюме: любой `.txt` файл в папку `data/resume/`
(читается первый файл по алфавиту).

**Шаг 7.** Создайте шаблон письма: `cp data/cover_letter_template.example.txt data/cover_letter_template.txt`
Замените в нём плейсхолдеры `{ВАША СПЕЦИАЛИЗАЦИЯ}` и `{ВАШЕ ИМЯ}` на свои данные.

**Шаг 8.** Запустите агента: `python -m agent.cli`
Напишите ему: `проверь чаты`. Выход: `exit`.

## Как работает агент

Агентный цикл (tool calling): модель сама выбирает инструменты и планирует шаги.

```
Вы: «проверь чаты»
        │
        ▼
  scan_chats ──► match_vacancy (для каждой вакансии)
        │
        ▼
  adapt_letter (если score >= 60) ──► save_report ──► send_summary
        │
        ▼
  Агент: итоговый ответ
```

**Пять инструментов:** `scan_chats`, `match_vacancy`, `adapt_letter`,
`save_report`, `send_summary`.

**Дешёвые фильтры до вызова LLM:** память обработанных сообщений, хэштеги
`#вакансия`/`#vacancy`, ключевые слова стека из `data/keywords.txt`.

**Результат работы:** отчёт в `reports/ГГГГ-ММ-ДД/report.txt` (ссылка, оценка,
стек, причина, готовое письмо) + краткая сводка в ваше «Избранное» в Telegram.

**Реальный запуск:** 13 вакансий → 5 релевантных (score 60–92) с письмами.

**Стек:** Python 3, Telethon (userbot), OpenAI SDK + Kimi `k3.1-pro`.

## Проверка отдельных частей

```bash
python tests/test_connection.py  # 1. связь с Kimi (список моделей + ответ)
python tests/test_tg.py          # 2. сканирование чата (даты и тексты)
python tests/test_match.py       # 3. оценка вакансий (score, стек, причина)
python tests/test_letter.py      # 4. генерация письма для тестовой вакансии
```

Тесты пишут память в `var/processed_test.json`, агент — в `var/processed.json`.

## Структура проекта

Разделение по принципу агента и инструментов (tool boundaries):
директория `agent/` — мозг, `tools/` — руки.

```
agent/                  # ядро агента (планирование и цикл)
  cli.py                # точка входа: диалог с агентом
  agent.py              # цикл tool calling, лимит итераций
  prompts.py            # системный промпт job-hunter
  tools.py              # инструменты + их описания (TOOLS/TOOLS_SCHEMA)
  llm.py                # клиент Kimi
tools/                  # инструменты агента (исполнение, без логики агента)
  telegram_tools.py     # интеграция с Telegram: scan_chats, send_to_saved
  resume_tools.py       # резюме + match_vacancy (score 0–100)
  letter_tools.py       # load_template, adapt_letter
  report_tools.py       # save_report, build_summary
  state.py              # память обработанных message_id
config/settings.py      # все пути проекта
scripts/qr_login.py     # авторизация Telegram по QR-коду
scripts/diag_tg.py      # диагностика отправки кода (нужен TG_PHONE в .env)
data/keywords.txt       # ваш стек для пре-фильтра
data/cover_letter_template.example.txt  # образец письма
```

## Особенности

- Чтение чатов — только userbot (Telethon), Bot API не подходит.
- Ошибка одного чата или инструмента не прерывает работу агента.
- Цикл агента ограничен `MAX_ITERATIONS = 20` — защита от бесконечных вызовов.
- Telethon-клиент создаётся на каждый вызов: соединение привязывается
  к event loop, переиспользование клиента ломало отправку уведомлений.
- `.env`, сессии, резюме и личный шаблон письма в git не попадают.
