from __future__ import print_function

import os

import pandas as pd
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from the_hat_game.utils import get_project_root

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1yHJ98wX3rPQeWdAEqXEHo4nU3z3Q60sGS4qlAwRP6Oo"
SAMPLE_RANGE_NAME = "Form Responses 1!A:D"


def get_players():
    token_path = get_project_root() / "credentials" / "token_write.json"

    if os.path.exists(token_path):
        credentials = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        service = build("sheets", "v4", credentials=credentials)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME).execute()
        values = result.get("values", [])

        df = pd.DataFrame(values[1:], columns=values[0])

        return df
