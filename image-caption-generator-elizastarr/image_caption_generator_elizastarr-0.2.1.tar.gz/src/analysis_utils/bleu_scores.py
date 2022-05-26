import pandas as pd
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction


def get_bleu_scores(true, predicted, smoothing: int = 0, independent: bool = True):
    if independent:
        w = [(1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)]
    else:
        w = [
            (1, 0, 0, 0),
            (0.5, 0.5, 0, 0),
            (0.33, 0.33, 0.33, 0),
            (0.25, 0.25, 0.25, 0.25),
        ]

    if smoothing == 1:
        s_f = SmoothingFunction().method1
    elif smoothing == 2:
        s_f = SmoothingFunction().method2
    elif smoothing == 3:
        s_f = SmoothingFunction().method3
    elif smoothing == 4:
        s_f = SmoothingFunction().method4
    elif smoothing == 5:
        s_f = SmoothingFunction().method5
    elif smoothing == 6:
        s_f = SmoothingFunction().method6
    elif smoothing == 7:
        s_f = SmoothingFunction().method7
    else:
        s_f = SmoothingFunction().method0

    bleu_scores = []

    # use smoothing functions to avoid 0 scores when no ngram overlaps are found
    for reference, hypothesis in zip(true, predicted):
        image_scores = []
        image_scores.append(
            sentence_bleu([reference], hypothesis, weights=w[0], smoothing_function=s_f)
        )
        image_scores.append(
            sentence_bleu([reference], hypothesis, weights=w[1], smoothing_function=s_f)
        )
        image_scores.append(
            sentence_bleu([reference], hypothesis, weights=w[2], smoothing_function=s_f)
        )
        image_scores.append(
            sentence_bleu([reference], hypothesis, weights=w[3], smoothing_function=s_f)
        )
        bleu_scores.append(image_scores)

    bleu_scores = pd.DataFrame(
        data=bleu_scores, columns=["BLEU-1", "BLEU-2", "BLEU-3", "BLEU-4"]
    )
    return bleu_scores
