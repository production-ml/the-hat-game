from __future__ import print_function

import os

import pandas as pd

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from the_hat_game.players import PlayerDefinition, RemotePlayer
from settings_server import (
    SCOPES, SAMPLE_SPREADSHEET_ID,
    SAMPLE_RANGE_NAME, TOKEN_PATH,
    COLUMN_TEAM, COLUMN_IP)


def get_thehatgame_players():

    if os.path.exists(TOKEN_PATH):
        credentials = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
        service = build("sheets", "v4", credentials=credentials)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME).execute()
        values = result.get("values", [])

        df = pd.DataFrame(values[1:], columns=values[0])

        players = [
            PlayerDefinition(row[COLUMN_TEAM], RemotePlayer(row[COLUMN_IP]))
            for i, row in df.iterrows()
        ]
        return players
