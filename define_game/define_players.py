from __future__ import print_function

import os

import fasttext
import pandas as pd

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from the_hat_game.utils import get_project_root
from the_hat_game.players import LocalFasttextPlayer, PlayerDefinition, RemotePlayer

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1yHJ98wX3rPQeWdAEqXEHo4nU3z3Q60sGS4qlAwRP6Oo"
SAMPLE_RANGE_NAME = "Form Responses 1!A:D"


def get_thehatgame_players():
    token_path = get_project_root() / "credentials" / "token_write.json"

    if os.path.exists(token_path):
        credentials = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        service = build("sheets", "v4", credentials=credentials)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME).execute()
        values = result.get("values", [])

        df = pd.DataFrame(values[1:], columns=values[0])

        players = [
            PlayerDefinition(row["Team name"], RemotePlayer(row["Team IP or URL (with port if necessary)"]))
            for i, row in df.iterrows()
        ]
        return players

def get_specific_players():
    
    """Function to get specific (local or remote) players to play the Hat Game locally.

    A suggested way: write your class for a local player, put it to the_hat_game folder.
    the_hat_game/players.py
    """

    fasttext_model = fasttext.load_model("models/2021_06_05_processed.model")
    player = LocalFasttextPlayer(model=fasttext_model)
    players = [
        PlayerDefinition('HerokuOrg team', RemotePlayer('https://obscure-everglades-02893.herokuapp.com')),
        # PlayerDefinition('Your trained remote player', RemotePlayer('http://35.246.139.13/')),
        PlayerDefinition('Local Player', player)]
    return players


def get_players(game_scope):
    if game_scope == 'GLOBAL':
        return get_thehatgame_players()
    
    if game_scope == 'LOCAL':
        return get_specific_players()
