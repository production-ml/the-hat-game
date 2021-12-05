from __future__ import print_function

import os
import os.path

import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from settings_server import (  # GOOGLE_APPLICATION_CREDENTIALS,
    COLUMN_IP,
    COLUMN_TEAM,
    SAMPLE_RANGE_NAME,
    SAMPLE_SPREADSHEET_ID,
    SCOPES,
)
from the_hat_game.players import PlayerDefinition, RemotePlayer


# first you need to create credentials.json
# here https://developers.google.com/workspace/guides/create-credentials#create_a_oauth_client_id_credential
# code below is copied from
# https://developers.google.com/sheets/api/quickstart/python
# or it works without all of what's commented? xD
def get_global_players():

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("sheets", "v4", credentials=creds)

    # credentials = Credentials.from_authorized_user_file(GOOGLE_APPLICATION_CREDENTIALS, SCOPES)
    # service = build("sheets", "v4")  # , credentials=credentials)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME).execute()
    values = result.get("values", [])

    df = pd.DataFrame(values[1:], columns=values[0])

    players = [PlayerDefinition(row[COLUMN_TEAM], RemotePlayer(row[COLUMN_IP])) for i, row in df.iterrows()]
    return players
