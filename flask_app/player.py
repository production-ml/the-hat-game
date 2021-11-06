from collections import namedtuple
import requests

from the_hat_game.loggers import logger

HIDE_WARNINGS = True

PlayerDefinition = namedtuple("PlayerDefinition", ["name", "api"])


def validate_word_list(word_list):
    if not isinstance(word_list, list):
        return False
    for word in word_list:
        if not isinstance(word, str):
            return False
    return True


class ValidationError(Exception):
    pass


class AbstractPlayer:
    def __init__(self):
        raise NotImplementedError()

    def explain(self, word, n_words):
        raise NotImplementedError()

    def guess(self, words, n_words):
        raise NotImplementedError()


class LocalDummyPlayer(AbstractPlayer):
    def __init__(self):
        pass

    def explain(self, word, n_words):
        return "Hi! My name is LocalDummyPlayer! What's yours?".split()[:n_words]

    def guess(self, words, n_words):
        guessed_words = "I guess it's a word, but don't have any idea which one!".split()[:n_words]
        return {"word_list": guessed_words, "time": 0, "code": 200}


class RemotePlayer(AbstractPlayer):
    def __init__(self, url, timeout=1):
        self.url = url
        self.timeout = 1
        self.ping()

    def ping(self):
        try:
            response = requests.get(self.url, timeout=60)
            assert response.status_code == 200
        except Exception as exc:
            if not HIDE_WARNINGS:
                logger.warn(exc)

    def explain(self, word, n_words):
        try:
            response = requests.get(
                self.url + "/explain",
                {"word": word, "n_words": n_words},
                timeout=self.timeout,
            )
            word_list = response.json()
            if not validate_word_list(word_list):
                raise ValidationError("word_list must be a list of strings")
        except Exception as exc:
            # we don't need to hide ValidationError
            if not HIDE_WARNINGS or isinstance(exc, ValidationError):
                logger.warning(exc)
            word_list = []
        return word_list

    def guess(self, words, n_words):
        try:
            response = requests.get(
                self.url + "/guess",
                {"words": words, "n_words": n_words},
                timeout=self.timeout,
            )
            response_time = response.elapsed.total_seconds()
            response_code = response.status_code
            word_list = response.json()
            if not validate_word_list(word_list):
                raise ValidationError("word_list must be a list of strings")
        except Exception as exc:
            # we don't need to hide ValidationError
            if not HIDE_WARNINGS or isinstance(exc, ValidationError):
                logger.warning(exc)
            word_list = []
            response_time = 0
            response_code = None
        return {"word_list": word_list, "time": response_time, "code": response_code}


class LocalFasttextPlayer(AbstractPlayer):
    def __init__(self, model):
        self.model = model

    def find_words_for_sentence(self, sentence, n_closest):
        neighbours = self.model.get_nearest_neighbors(sentence)
        words = [word for similariry, word in neighbours][:n_closest]
        return words

    def explain(self, word, n_words):
        return self.find_words_for_sentence(word, n_words)

    def guess(self, words, n_words):
        words_for_sentence = self.find_words_for_sentence(" ".join(words), n_words)
        return {"word_list": words_for_sentence, "time": 0, "code": 200}
