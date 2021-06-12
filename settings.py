import os
from pathlib import Path

from google.cloud import storage

CWD = Path(os.getcwd())
DATA_PATH = CWD / "texts"
PROJECT_GCS_ID = "mlops-dvc-demo"
BUCKET_SPLIT_TEXTS = "dmia-mlops-texts-vault"
BUCKET_LOGS = "dmia-mlops-logs"
BUCKET_DAILY = "dmia-mlops-texts"
VOCAB_PATH = CWD / "vocab" / "vocab.txt"

STORAGE_CLIENT = storage.Client(project=PROJECT_GCS_ID)

HIDE_WARNINGS = False

N_EXPLAIN_WORDS = 10
N_GUESSING_WORDS = 5
N_ROUNDS = 1
CRITERIA = "soft"

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]


SPREADSHEET = "2019-12 DMIA Hat (Responses)"


def set_environ():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(CWD / "credentials" / "bucket_storage.json")


set_environ()
