"""Settings to launch the Hat Game on a server."""

import os
from pathlib import Path

from server.storage import get_storage

# from the_hat_game.utils import get_project_root

TEST = False
PAUSE_MINUTES = 0
BIG_GAME_IN = 2
CWD = Path(os.getcwd())
DATA_PATH = CWD / "texts"
VOCAB_PATH = CWD / "vocab" / "top1000words.txt"
PROJECT_GCS_ID = os.environ.get("PROJECT_GCS_ID")
BUCKET_SPLIT_TEXTS = "dmia-mlops-texts-vault"
BUCKET_LOGS = "hat-logs"
BUCKET_DAILY = "dmia-mlops-texts"
STORAGE_CLIENT = get_storage(PROJECT_GCS_ID)
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = os.environ.get("SAMPLE_SPREADSHEET_ID")
SAMPLE_RANGE_NAME = "Form Responses 1!A:D"

# TOKEN_PATH = get_project_root() / "credentials" / "token_write.json"
HIDE_WARNINGS = True

COLUMN_TEAM = "Team name"
COLUMN_IP = "Team IP or URL (with port if necessary)"
