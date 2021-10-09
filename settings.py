import os
from pathlib import Path

from define_game.define_storage import get_storage

CWD = Path(os.getcwd())
DATA_PATH = CWD / "texts"
PROJECT_GCS_ID = "mlops-dvc-demo"
BUCKET_SPLIT_TEXTS = "dmia-mlops-texts-vault"
BUCKET_LOGS = "dmia-mlops-logs"
BUCKET_DAILY = "dmia-mlops-texts"
# VOCAB_PATH = CWD / "vocab" / "vocab.txt"
VOCAB_PATH = CWD / "text_samples" / "nouns_top_50.txt"
GAME_SCOPE = "LOCAL" # Could be "GLOBAL" or "LOCAL"
STORAGE_CLIENT = get_storage(GAME_SCOPE)

HIDE_WARNINGS = False

N_EXPLAIN_WORDS = 10
N_GUESSING_WORDS = 5
N_ROUNDS = 1
CRITERIA = "soft"

# SCOPE = [
#     "https://spreadsheets.google.com/feeds",
#     "https://www.googleapis.com/auth/drive",
# ]


# SPREADSHEET = "2019-12 DMIA Hat (Responses)"


def set_environ():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(CWD / "credentials" / "bucket_storage.json")


set_environ()
