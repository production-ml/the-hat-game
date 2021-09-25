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
        return "I guess it's a word, but don't have any idea which one!".split()[:n_words]
