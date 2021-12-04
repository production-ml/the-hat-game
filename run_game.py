import json
import logging
import os
import random
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from flask_app.player import LocalDummyPlayer, LocalFasttextPlayer  # noqa: F401
from settings import CRITERIA, GAME_SCOPE, N_EXPLAIN_WORDS, N_GUESSING_WORDS
from the_hat_game.game import Game
from the_hat_game.loggers import logger
from the_hat_game.players import PlayerDefinition, RemotePlayer

if GAME_SCOPE == "GLOBAL":
    from settings_server import GLOBAL_VOCAB_PATH as VOCAB_PATH
else:
    from settings import LOCAL_VOCAB_PATH as VOCAB_PATH


def upload_callback(payload, name):
    from the_hat_game.game import dump_locally

    dump_locally(payload, name)
    if GAME_SCOPE != "LOCAL":
        from server.mongo import upload

        if GAME_SCOPE == "TEST":
            name = "test_" + name
        upload(payload, name)


if __name__ == "__main__":

    # # read all words
    # WORDS = []
    # for vocabulary_path in [
    #     "text_samples/verbs_top_50.txt",
    #     "text_samples/nouns_top_50.txt",
    #     "text_samples/adjectives_top_50.txt",
    # ]:
    #     with open(vocabulary_path) as f:
    #         words = f.readlines()
    #         words = [word.strip() for word in words]
    #         WORDS.extend(words)
    # print(f"Words we will use for the game: {sorted(WORDS)}")

    # uncomment this to get reproducible runs:
    # random.seed(0)

    while True:
        logfile = f"logs/game_run_{datetime.now().strftime('%y%m%d_%H%M')}.log"
        single_handler = logging.FileHandler(logfile, mode="w")
        single_handler.setLevel(logging.DEBUG)
        single_handler_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        single_handler.setFormatter(single_handler_format)
        logger.addHandler(single_handler)

        WORDS = []
        with open(Path(VOCAB_PATH)) as f:
            words = f.readlines()
            words = [word.strip() for word in words]
            WORDS.extend(words)
        print(f"Words we will use for the game: {sorted(WORDS)[:10]}")

        if GAME_SCOPE == "GLOBAL":
            from server.players import get_global_players

            players = get_global_players()
        elif GAME_SCOPE == "TEST":
            players = []
            with open("players.json") as f:
                for p, u in json.load(f).items():
                    players.append(PlayerDefinition(p, RemotePlayer(u)))
        elif GAME_SCOPE == "LOCAL":
            # define player list manually. Example:
            players = [
                PlayerDefinition("HerokuOrg", RemotePlayer("https://obscure-everglades-02893.herokuapp.com")),
                PlayerDefinition("Local Dummy Junior", LocalDummyPlayer()),
                PlayerDefinition("Local Dummy Senior", LocalDummyPlayer()),
            ]

        # shuffle players
        np.random.shuffle(players)

        # put one word for each team in a hat
        # np.random.shuffle(WORDS)
        words_in_hat = random.choices(WORDS, k=len(players) * 1)
        print(f"Words in hat: {words_in_hat}")

        # play the hat game
        print("\n\nStarting the new game")
        game = Game(
            players,
            words_in_hat,
            CRITERIA,
            n_rounds=len(words_in_hat) // len(players),
            n_explain_words=N_EXPLAIN_WORDS,
            n_guessing_words=N_GUESSING_WORDS,
            random_state=0,
            logging_callback=upload_callback,
        )

        game_start = pd.Timestamp.now()
        game.run(verbose="print_logs", complete=False)
        game_end = pd.Timestamp.now()
        game.report_results()
        print(f"Game started at {game_start}. Game lasted for {game_end - game_start}")

        if GAME_SCOPE == "GLOBAL":
            from server.data import upload_blob
            from settings_server import BUCKET_LOGS

            upload_blob(BUCKET_LOGS, logfile, str(Path(logfile).name))

        logger.removeHandler(single_handler)

        os.remove(logfile)

        if GAME_SCOPE == "GLOBAL":
            time.sleep(15 * 60)
        else:
            break
