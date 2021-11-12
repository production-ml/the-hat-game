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
        return words_for_sentence
