import math
import os


class GibberishDetector:
    gibberish_model = eval(open("gib_model.json").read())
    letters_probability_matrix = gibberish_model['mat']
    threshold = 0.0188
    accepted_chars = 'abcdefghijklmnopqrstuvwxyz '
    pos = dict([(char, idx) for idx, char in enumerate(accepted_chars)])

    @staticmethod
    def normalize(sentence: str) -> list:
        return [char.lower() for char in sentence if char.lower() in GibberishDetector.accepted_chars]

    @staticmethod
    def ngram(n: int, sentence: str) -> str:
        filtered = GibberishDetector.normalize(sentence)
        for start in range(0, len(filtered) - n + 1):
            yield ''.join(filtered[start:start + n])

    @staticmethod
    def generate_gibberish_model(file_path: str) -> dict:
        assert os.path.splitext(file_path)[1] == 'txt'

        k = len(GibberishDetector.accepted_chars)
        counts = [[10 for i in range(k)] for i in range(k)]
        for line in open(file_path):
            for a, b in GibberishDetector.ngram(2, line):
                counts[GibberishDetector.pos[a]][GibberishDetector.pos[b]] += 1
        for i, row in enumerate(counts):
            s = float(sum(row))
            for j in range(len(row)):
                row[j] = math.log(row[j] / s)
        return {'mat': counts}

    @staticmethod
    def get_gibberish_prob(sentence: str) -> float:
        log_prob = 0.0
        transition_ct = 0
        for a, b in GibberishDetector.ngram(2, sentence):
            log_prob += GibberishDetector.letters_probability_matrix[GibberishDetector.pos[a]][GibberishDetector.pos[b]]
            transition_ct += 1
        if transition_ct == 0:
            return 'Empty String'
        return math.exp(log_prob / (transition_ct or 1))

    @staticmethod
    def detect_gibberish(sentence: str) -> bool:
        prob_non_gibberish = GibberishDetector.get_gibberish_prob(sentence)
        if prob_non_gibberish == 'Empty String':
            return 0, True
        return prob_non_gibberish, prob_non_gibberish < GibberishDetector.threshold