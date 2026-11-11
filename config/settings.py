from pathlib import Path

#Идея: все пути живут в одном месте. Перенесёшь файл — правишь только здесь.
BASE_DIR = Path(__file__).resolve().parent.parent

SESSION_FILE = BASE_DIR / "tg_session.session"

DATA_DIR = BASE_DIR / "data"
RESUME_FILE = DATA_DIR / "resume" / "rm.txt"
KEYWORDS_FILE = DATA_DIR / "keywords.txt"
COVER_LETTER_FILE = DATA_DIR / "cover_letter_template.txt"

VAR_DIR = BASE_DIR / "var"
PROCESSED_FILE = VAR_DIR / "processed.json"

REPORTS_DIR = BASE_DIR / "reports"

# Тестовый режим: пишем память в отдельный файл
PROCESSED_TEST_FILE = VAR_DIR / "processed_test.json"