"""Settings to launch the Hat Game on a server."""

import os
from pathlib import Path
from server.storage import get_storage
from the_hat_game.utils import get_project_root


CWD = Path(os.getcwd())
DATA_PATH = CWD / "texts"
PROJECT_GCS_ID = "mlops-dvc-demo"
BUCKET_SPLIT_TEXTS = "dmia-mlops-texts-vault"
BUCKET_LOGS = "dmia-mlops-logs"
BUCKET_DAILY = "dmia-mlops-texts"
GAME_SCOPE = "GLOBAL"  # Could be "GLOBAL" or "LOCAL"
STORAGE_CLIENT = get_storage(GAME_SCOPE, PROJECT_GCS_ID)

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1yHJ98wX3rPQeWdAEqXEHo4nU3z3Q60sGS4qlAwRP6Oo"
SAMPLE_RANGE_NAME = "Form Responses 1!A:D"

TOKEN_PATH = get_project_root() / "credentials" / "token_write.json"
HIDE_WARNINGS = False

COLUMN_TEAM = "Team name"
COLUMN_IP = "Team IP or URL (with port if necessary)"


def set_environ():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(CWD / "credentials" / "bucket_storage.json")


set_environ()
