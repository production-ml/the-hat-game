from collections import namedtuple

import numpy as np
import pandas as pd

from settings import CRITERIA, N_EXPLAIN_WORDS, N_GUESSING_WORDS  # , N_ROUNDS
from the_hat_game.game import Game
from the_hat_game.google import get_players
from the_hat_game.players import RemotePlayer

if __name__ == "__main__":

    player = namedtuple("player", ["name", "api"])

    data = get_players()

    PLAYERS = [player(row["Team name"], RemotePlayer(row["Team IP or URL"])) for i, row in data.iterrows()]

    while True:
        N_WORDS = 8
        WORDS = []
        for vocabulary_path in [
            #     'text_samples/verbs_top_50.txt',
            "text_samples/nouns_top_50.txt",
            #     'text_samples/adjectives_top_50.txt',
        ]:
            print(vocabulary_path)
            with open(vocabulary_path) as f:
                words = f.readlines()
                np.random.shuffle(words)
                words = [word.strip() for word in words][:N_WORDS]
                WORDS.extend(words)

        game = Game(
            PLAYERS,
            WORDS,
            CRITERIA,
            len(WORDS),
            N_EXPLAIN_WORDS,
            N_GUESSING_WORDS,
            random_state=0,
        )

        game_start = pd.Timestamp.now()
        game.run(verbose=True, complete=False)
        game_end = pd.Timestamp.now()
        # display(game_end - game_start)
