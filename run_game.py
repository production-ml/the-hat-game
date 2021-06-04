import time

import numpy as np
import pandas as pd

from settings import CRITERIA, N_EXPLAIN_WORDS, N_GUESSING_WORDS  # , N_ROUNDS
from the_hat_game.game import Game
from the_hat_game.google import get_players
from the_hat_game.players import PlayerDefinition, RemotePlayer

if __name__ == "__main__":

    # read all words
    WORDS = []
    for vocabulary_path in [
        "text_samples/verbs_top_50.txt",
        "text_samples/nouns_top_50.txt",
        "text_samples/adjectives_top_50.txt",
    ]:
        with open(vocabulary_path) as f:
            words = f.readlines()
            words = [word.strip() for word in words]
            WORDS.extend(words)

    while True:
        data = get_players()

        players = [
            PlayerDefinition(row["Team name"], RemotePlayer(row["Team IP or URL (with port if necessary)"]))
            for i, row in data.iterrows()
        ]

        # put one word for each team in a hat
        np.random.shuffle(WORDS)
        words_in_hat = WORDS[: len(players)]

        # play the hat game
        print("\n\nStarting the new game")
        game = Game(
            players, words_in_hat, CRITERIA, len(words_in_hat), N_EXPLAIN_WORDS, N_GUESSING_WORDS, random_state=0
        )

        game_start = pd.Timestamp.now()
        game.run(verbose=True, complete=False)
        game_end = pd.Timestamp.now()
        game.report_results()
        print(f"Game started at {game_start}. Game lasted for {game_end - game_start}")
        time.sleep(60 * 5)
