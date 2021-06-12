import logging
import os
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from data.utils import upload_blob
from settings import BUCKET_LOGS, CRITERIA, N_EXPLAIN_WORDS, N_GUESSING_WORDS, VOCAB_PATH
from the_hat_game.game import Game
from the_hat_game.google import get_players
from the_hat_game.loggers import logger
from the_hat_game.players import PlayerDefinition, RemotePlayer

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

        data = get_players()

        players = [
            PlayerDefinition(row["Team name"], RemotePlayer(row["Team IP or URL (with port if necessary)"]))
            for i, row in data.iterrows()
        ]

        # put one word for each team in a hat
        np.random.shuffle(WORDS)
        words_in_hat = WORDS[: len(players)]
        print(f"Words in hat: {words_in_hat}")

        # play the hat game
        print("\n\nStarting the new game")
        game = Game(
            players, words_in_hat, CRITERIA, len(words_in_hat), N_EXPLAIN_WORDS, N_GUESSING_WORDS, random_state=0
        )

        game_start = pd.Timestamp.now()
        game.run(verbose="print_logs", complete=False)
        game_end = pd.Timestamp.now()
        game.report_results()
        print(f"Game started at {game_start}. Game lasted for {game_end - game_start}")

        logger.removeHandler(single_handler)

        upload_blob(BUCKET_LOGS, logfile, str(Path(logfile).name))

        os.remove(logfile)

        time.sleep(60 * 5)
