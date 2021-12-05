import logging
import os
import random
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from emoji import emojize

from flask_app.player import LocalDummyPlayer, LocalFasttextPlayer  # noqa: F401
from settings import CRITERIA, N_EXPLAIN_WORDS, N_GUESSING_WORDS, VOCAB_PATH
from the_hat_game.game import Game
from the_hat_game.loggers import logger
from the_hat_game.players import PlayerDefinition, RemotePlayer

if __name__ == "__main__":

    # uncomment this to get reproducible runs:
    # random.seed(0)

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
    print(emojize(f":top_hat: Words we will use for the game: {sorted(WORDS)[:10]} and {len(WORDS) - 10} more."))

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
    )

    game_start = pd.Timestamp.now()
    game.run(verbose="print_logs", complete=False)
    game_end = pd.Timestamp.now()
    game.report_results()
    print(f"Game started at {game_start}. Game lasted for {game_end - game_start}")

    logger.removeHandler(single_handler)

    os.remove(logfile)
