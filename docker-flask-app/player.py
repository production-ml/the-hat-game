import numpy as np
import pandas as pd
import fasttext
from sklearn.metrics.pairwise import cosine_similarity


class AbstractPlayer:
    def __init__(self):
        raise NotImplementedError()

    def explain(self, word, n_words):
        raise NotImplementedError()
        
    def guess(self, words, n_words):
        raise NotImplementedError()


class LocalFasttextPlayer(AbstractPlayer):
    def __init__(self, model):
        self.model = model
        self.words = model.get_words()
        self.matrix = np.concatenate([model[word].reshape(1, -1) for word in self.words], axis=0)

    def find_words_for_vector(self, vector, n_closest):
        sims = cosine_similarity(vector.reshape(1, -1), self.matrix).ravel()
        word_sims = pd.Series(sims, index=self.model.get_words()).sort_values(ascending=False)
        return list(word_sims.head(n_closest).index)
    
    def find_words_for_sentence(self, sentence, n_closest):
        vector = self.model.get_sentence_vector(sentence)
        return self.find_words_for_vector(vector, n_closest)
    
    def explain(self, word, n_words):
        return self.find_words_for_sentence(word, n_words)
    
    def guess(self, words, n_words):
        return self.find_words_for_sentence(' '.join(words), n_words)
