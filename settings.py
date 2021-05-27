import os
from pathlib import Path

from google.cloud import storage

CWD = Path(os.getcwd())
DATA_PATH = CWD / "data"
PROJECT_GCS_ID = "ml-production-308519"
BUCKET_SPLIT_TEXTS = "ml-production-text"
BUCKET_LOGS = "mp-production-logs"
BUCKET_DAILY = "ml-production-daily"

STORAGE_CLIENT = storage.Client(project=PROJECT_GCS_ID)

HIDE_WARNINGS = False

N_EXPLAIN_WORDS = 10
N_GUESSING_WORDS = 5
N_ROUNDS = 1
CRITERIA = "hard"

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

SECRETS_FILE = "credentials/DMIAGoogleForms-0b606aca4a07.json"
SPREADSHEET = "2019-12 DMIA Hat (Responses)"


def set_environ():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(CWD / "credentials" / "cred.json")


set_environ()
