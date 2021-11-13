import json
import logging
import multiprocessing as mp
import re
import traceback
from collections import defaultdict
from datetime import datetime
from typing import OrderedDict

import numpy as np
import pandas as pd
from IPython.display import display
from nltk.corpus import wordnet
from nltk.metrics.distance import edit_distance
from nltk.stem.snowball import SnowballStemmer

import the_hat_game.nltk_setup  # noqa: F401
from the_hat_game.loggers import c_handler, dump_locally, logger
from the_hat_game.players import RemotePlayer


def send_data(data, filename):
    with open(filename, "w") as f:
        f.write(json.dumps(data))
        f.write("\n")


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
        logging_callback=dump_locally,
    ):
        assert len(players) >= 2
        assert criteria in ("hard", "soft")
        assert n_rounds <= len(words) // len(players), (
            f"For {n_rounds} rounds and {len(players)} players"
            "you need at least {n_rounds * len(players)} words, but you have only {len(words)}"
        )
        self.players = players
        self.words = words
        self.criteria = criteria
        self.n_rounds = n_rounds
        self.n_explain_words = n_explain_words
        self.n_guessing_words = n_guessing_words
        self.random_state = random_state
        self.logging_callback = logging_callback
        self.stemmer = SnowballStemmer("english")
        self.game_info = OrderedDict(
            timestamp=datetime.utcnow(),
            players={p.name: p.api.url if isinstance(p.api, RemotePlayer) else None for p in players},
            words=words,
            criteria=criteria,
            n_rounds=n_rounds,
            n_explain_words=n_explain_words,
            n_guessing_words=n_guessing_words,
        )

    def score_players(self, explainer_name, successfull_attempts):
        rewards = {player.name: 0 for player in self.players}
        for player, attempt in successfull_attempts.items():
            rewards[player] += self.n_explain_words + 1 - attempt
        rewards[explainer_name] = sum(rewards.values())
        return rewards

    def remove_same_rooted_words(self, word, word_list):
        root = self.stemmer.stem(word)
        return [w for w in word_list if self.stemmer.stem(w) != root]

    @staticmethod
    def remove_non_existing_words(words):
        return [w for w in words if len(wordnet.synsets(w)) > 0]

    @staticmethod
    def remove_repeated_words(words):
        unique_words = []
        for c in words:
            if c not in unique_words:
                unique_words.append(c)
        return unique_words

    def create_word_list(self, player, word, n_words):
        reported_words = player.explain(word, n_words)
        explain_words = reported_words[:]
        if self.criteria == "hard":
            explain_words = explain_words[:n_words]
        explain_words = [w.lower() for w in explain_words]
        # remove all symbols except letters
        explain_words = [re.sub(r"[\W\d]", "", w) for w in explain_words]
        # remove all words which have word being explained as a substring
        explain_words = [w for w in explain_words if word not in w]
        # remove all words with too small levenstein distance from the word being explained
        explain_words = [w for w in explain_words if edit_distance(word, w) > 2]
        explain_words = [w for w in explain_words if w != ""]
        explain_words = self.remove_repeated_words(explain_words)
        if self.criteria == "hard":
            explain_words = self.remove_same_rooted_words(word, explain_words)
            explain_words = self.remove_non_existing_words(explain_words)
        if self.criteria == "soft":
            explain_words = explain_words[:n_words]
        return reported_words, explain_words

    def check_criteria(self, word, guessed_words):
        if self.criteria == "soft":
            return any((word in c) and (edit_distance(word, c) < 3) for c in guessed_words)
        else:
            return word in guessed_words

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

        if remote_guessing_players:
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

    def play_attempt(self, guessing_players, word, sentence):
        results = {}
        logger.info(f"HOST: {sentence}")

        players_guesses = self.ask_guessing_players(guessing_players, sentence)

        for player in guessing_players:
            player_results = {}
            player_dict = players_guesses[player.name]
            # local players may return just list. This quick fix allows that
            if isinstance(player_dict, list):
                player_dict = dict(word_list=player_dict)
            guessed_words = player_dict["word_list"]
            guessed = self.check_criteria(word, guessed_words)
            logger.info(f"({str(guessed):5}) GUESSING PLAYER ({player.name}) to HOST: {guessed_words}")
            # logger.info(f"RESPONSE_TIME: {player_dict['time']}, RESPONSE_CODE: {player_dict['code']}")
            player_results["words"] = guessed_words
            player_results["guessed"] = guessed
            player_results["response_time"] = player_dict.get("time", np.nan)
            player_results["response_200"] = player_dict.get("code", None) == 200
            results[player.name] = player_results
        return results

    def play_iteration(self, explaining_player, guessing_players, word):

        logger.info(f'HOST to EXPLAINING PLAYER ({explaining_player.name}): the word is "{word}"')

        reported_words, guessing_by = self.create_word_list(explaining_player.api, word, self.n_explain_words)
        logger.info(f"EXPLAINING PLAYER ({explaining_player.name}) to HOST: my wordlist is {reported_words}")
        logger.info(
            f"HOST TO EXPLAINING PLAYER ({explaining_player.name}): cleaning your word list. Now the list is {guessing_by}"
        )

        df = []
        success_attempts = {}
        metrics = defaultdict(dict)
        iteration_info = OrderedDict(
            timestamp=datetime.utcnow(),
            explaining_player=explaining_player.name,
            guessing_players=[p.name for p in guessing_players],
            word=word,
            reported_words=reported_words,
            guessing_by=guessing_by,
            attempts=[],
        )
        for i in range(1, len(guessing_by) + 1):
            if len(guessing_players) == 0:
                break
            logger.info(f"\n===ATTEMPT {i}===\n")
            results = self.play_attempt(
                guessing_players=guessing_players,
                word=word,
                sentence=guessing_by[:i],
            )
            for player in [explaining_player] + guessing_players:
                player_results = results.get(player.name, dict())
                for metric in player_results.keys():
                    if metric not in ("guessed", "words"):
                        metrics[player.name][metric] = metrics[player.name].get(metric, list()) + [
                            player_results[metric]
                        ]
                        # metrics[(player.name, metric)] = metrics.get((player.name, metric), list()) + [
                        #     player_results[metric]
                        # ]
            for player in guessing_players[:]:
                if (player.name not in success_attempts) and results.get(player.name, dict()).get("guessed", False):
                    success_attempts[player.name] = i
                    guessing_players = [p for p in guessing_players if p != player]
            iteration_info["attempts"].append(results)
            df.append(results)

        scores = self.score_players(explaining_player.name, success_attempts)
        iteration_info["scores"] = scores
        self.logging_callback({"game_timestamp": self.game_info["timestamp"], **iteration_info}, "iteration")
        df = pd.DataFrame(df)
        for p in metrics:
            for m in metrics[p]:
                metrics[p][m] = np.mean(metrics[p][m])
        iteration_info["metrics"] = metrics
        return df, scores, iteration_info

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
        self.game_info["iterations"] = []
        for r in range(self.run_rounds):
            players = self.players[:]
            # shuffle players to average randomness with some players' services
            # breaking at some point and taking time to get back up
            np.random.shuffle(players)
            for explaining_player in players:
                guessing_players = [p for p in players if p != explaining_player]
                try:
                    word = self.run_words[igame]
                except IndexError:
                    logger.info("HOST: No words left in the hat. Ending the game.")
                    break
                df, score, iteration_info = self.play_iteration(explaining_player, guessing_players, word)
                iteration_info["round"] = r
                self.game_info["iterations"].append(iteration_info)
                scores.append(score)
                scores_status[(explaining_player.name, "explaining")] += score.get(explaining_player.name, 0)
                for player in guessing_players:
                    scores_status[(player.name, "guessing")] += score.get(player.name, 0)
                igame += 1
                logger.info(f"\n\nSCORES: {score}")
                if verbose:
                    display(df)

        scores_dict = defaultdict(dict)
        for (p, a), s in scores_status.items():
            scores_dict[p][a] = s
        self.game_info["scores"] = scores_dict
        try:
            self.logging_callback(self.game_info, "game")
        except:  # noqa: E722
            traceback.print_exc()
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
        # self.summary = pd.concat([self.summary, self.metrics], axis=1)
        display(self.summary)
        logger.debug(self.summary)
