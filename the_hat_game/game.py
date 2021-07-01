import logging
import multiprocessing as mp
import re
from collections import OrderedDict, defaultdict

import numpy as np
import pandas as pd
from IPython.display import display
from nltk.corpus import wordnet
from nltk.metrics.distance import edit_distance
from nltk.stem.snowball import SnowballStemmer

import the_hat_game.nltk_setup  # noqa: F401
from the_hat_game.loggers import c_handler, logger
from the_hat_game.players import RemotePlayer


class Game:
    def __init__(
        self,
        players,
        words,
        criteria,
        n_rounds,
        n_explain_words,
        n_guessing_words,
        random_state=None,
    ):
        assert len(players) >= 2
        assert criteria in ("hard", "soft")
        self.players = players
        self.words = words
        self.criteria = criteria
        self.n_rounds = n_rounds
        self.n_explain_words = n_explain_words
        self.n_guessing_words = n_guessing_words
        self.random_state = random_state
        self.stemmer = SnowballStemmer("english")

    def remove_repeated_words(self, words):
        unique_words = []
        for c in words:
            if c not in unique_words:
                unique_words.append(c)
        return unique_words

    def score_players(self, explainer_name, last_rounds):
        rewards = {player: self.n_explain_words + 1 - nround for player, nround in last_rounds.items()}
        rewards[explainer_name] = sum(rewards.values())
        return rewards

    def remove_same_rooted_words(self, word, word_list):
        root = self.stemmer.stem(word)
        cleared_word_list = [w for w in word_list if self.stemmer.stem(w) != root]
        return cleared_word_list

    @staticmethod
    def remove_non_existing_words(words):
        existing_words = [w for w in words if len(wordnet.synsets(w)) > 0]
        return existing_words

    def create_word_list(self, player, word, n_words):
        reported_words = player.explain(word, n_words)
        explain_words = reported_words[:]
        if self.criteria == "hard":
            explain_words = explain_words[:n_words]
        # lowercase
        explain_words = [w.lower() for w in explain_words]
        # remove all symbols except letters
        explain_words = [re.sub(r"[\W\d]", "", w) for w in explain_words]
        # remove all words which have word being explained as a substring
        explain_words = [w for w in explain_words if word not in w]
        # remove all words with too small levenstein distance from the word being explained
        explain_words = [w for w in explain_words if edit_distance(word, w) > 2]
        # remove all ''
        explain_words = [w for w in explain_words if w != ""]
        # remove repeated words
        explain_words = self.remove_repeated_words(explain_words)
        if self.criteria == "hard":
            explain_words = self.remove_same_rooted_words(word, explain_words)
            explain_words = self.remove_non_existing_words(explain_words)
        if self.criteria == "soft":
            explain_words = explain_words[:n_words]
        return reported_words, explain_words

    def check_criteria(self, word, guessed_words):
        if self.criteria == "soft":
            guessed = any([(word in c) and (edit_distance(word, c) < 3) for c in guessed_words])
        else:
            guessed = word in guessed_words
        return guessed

    @staticmethod
    def ask_player(player, question, word, n_words):
        method = getattr(player, question)
        return method(word, n_words)

    def ask_guessing_players(self, guessing_players, sentence):
        players_guesses = {}
        remote_guessing_players = []
        for player in guessing_players:
            if isinstance(player.api, RemotePlayer):
                remote_guessing_players.append(player)
            else:
                players_guesses[player.name] = player.api.guess(sentence, self.n_guessing_words)

        if len(remote_guessing_players) > 0:
            n_processes = np.fmin(len(remote_guessing_players), np.fmax(1, mp.cpu_count() - 1))
            pool = mp.Pool(n_processes)
            remote_players_guesses = pool.starmap(
                self.ask_player,
                [(p.api, "guess", sentence, self.n_guessing_words) for p in remote_guessing_players],
            )
            pool.close()

            players_guesses.update(
                zip(
                    [player.name for player in remote_guessing_players],
                    remote_players_guesses,
                )
            )
        return players_guesses

    def play_round(self, explaining_player, guessing_players, word, sentence):
        game_round = OrderedDict()
        results = {}
        logger.info(f"HOST: {sentence}")
        game_round.update({f'Explanation for "{word}" ({explaining_player.name})': sentence})

        # if False:
        #     for player in guessing_players:
        #         guessed_words = player.api.guess(sentence, self.n_guessing_words)
        #         guessed = self.check_criteria(word, guessed_words)
        #         results[player.name] = guessed
        #         logger.info(f'GUESSING PLAYER ({player.name}) to HOST: {guessed_words}')
        #         logger.info(f'HOST: {guessed}')
        #         game_round.update({f'Guess ({player.name})': guessed_words})
        # else:
        players_guesses = self.ask_guessing_players(guessing_players, sentence)

        for player in guessing_players:
            player_results = {}
            player_dict = players_guesses[player.name]
            guessed_words = player_dict['word_list']
            guessed = self.check_criteria(word, guessed_words)
            logger.info(f"GUESSING PLAYER ({player.name}) to HOST: {guessed_words}")
            logger.info(f"RESPONSE_TIME: {player_dict['time']}, RESPONSE_CODE: {player_dict['code']}")
            logger.info(f"HOST: {guessed}")
            game_round.update({f"Guess ({player.name})": guessed_words})
            player_results["guessed"] = guessed
            player_results["response_time"] = guessed
            player_results["response_code"] = player_dict['code']
            results[player.name] = player_results
        return game_round, results

    def play(self, explaining_player, guessing_players, word, criteria):

        logger.info(f'HOST to EXPLAINING PLAYER ({explaining_player.name}): the word is "{word}"')

        reported_words, guessing_by = self.create_word_list(explaining_player.api, word, self.n_explain_words)
        logger.info(f"EXPLAINING PLAYER ({explaining_player.name}) to HOST: my wordlist is {reported_words}")
        logger.info(
            f"HOST TO EXPLAINING PLAYER ({explaining_player.name}): cleaning your word list. Now the list is {guessing_by}"
        )

        df = []
        success_rounds = {}
        for iround in range(1, len(guessing_by) + 1):
            if len(guessing_players) == 0:
                break
            logger.info(f"\n===ROUND {iround}===\n")
            game_round, results_round = self.play_round(
                explaining_player=explaining_player,
                guessing_players=guessing_players,
                word=word,
                sentence=guessing_by[:iround],
            )
            for player in guessing_players[:]:
                if (player.name not in success_rounds) and results_round.get(player.name, False)["guessed"]:
                    success_rounds[player.name] = iround
                    guessing_players = [p for p in guessing_players if p != player]
            df.append(game_round)
        df = pd.DataFrame(df)
        scores = self.score_players(explaining_player.name, success_rounds)

        return df, scores, 

    def get_words(self, complete):
        if not complete:
            words = self.words[:]
            np.random.seed(self.random_state)
            np.random.shuffle(words)
        else:
            words = []
            for word in self.words:
                words.extend([word] * len(self.players))
        return words

    def get_n_rounds(self, complete):
        if complete:
            return len(self.words)
        else:
            return self.n_rounds

    @staticmethod
    def set_console_logging_level(verbose):
        if verbose == "print_logs":
            console_logging_level = logging.INFO
        else:
            console_logging_level = logging.WARNING
        c_handler.setLevel(console_logging_level)

    def run(self, verbose=False, complete=False):
        self.set_console_logging_level(verbose)

        self.run_words = self.get_words(complete=complete)
        self.run_rounds = self.get_n_rounds(complete=complete)

        igame = 0
        scores = []
        scores_status = defaultdict(int)
        for r in range(self.run_rounds):
            for explaining_player in self.players:
                guessing_players = [p for p in self.players if p != explaining_player]
                try:
                    word = self.run_words[igame]
                except IndexError:
                    break
                df, score = self.play(explaining_player, guessing_players, word, criteria=self.criteria)
                scores.append(score)
                scores_status[(explaining_player.name, "explaining")] += score.get(explaining_player.name, 0)
                for player in guessing_players:
                    scores_status[(player.name, "guessing")] += score.get(player.name, 0)
                igame += 1
                logger.info(f"\n\nSCORES: {score}")
                if verbose:
                    display(df)

        self.scores = pd.DataFrame(scores).fillna(0)
        self.scores.index.name = "game"

        self.scores_status = pd.Series(scores_status).unstack()

    def report_results(self, each_game=False):
        if each_game:
            print("=== Team scores in each game ===")
            display(self.scores)
        logger.debug(self.scores)

        print("=== Team scores, summary ===")
        self.summary = self.scores_status
        self.summary["total"] = self.scores.sum(axis=0)
        self.summary.sort_values("total", ascending=False, inplace=True)
        display(self.summary)
        logger.debug(self.summary)
