from typing import List
import numpy as np
from . import aa_letters


def to_string(seqmat, remove_gaps: bool = True):
    a = [''.join([aa_letters[np.argmax(aa)] for aa in seq]) for seq in seqmat]
    return [x.replace('-', '') for x in a] if remove_gaps else a


def greedy_decode_1d(arr1d) -> np.ndarray:
    """

    Returns
    -------
    numpy.ndarray
    """
    a: np.ndarray = np.zeros(arr1d.shape)
    i = np.argmax(arr1d)
    a[i] = 1
    return a


def greedy_decode(pred_mat):
    return np.apply_along_axis(greedy_decode_1d, -1, pred_mat)


def _decode_nonar(generator, z, remove_gaps: bool = False, alphabet_size: int = 21, conditions=None):
    xp = generator.predict(z) if conditions is None else generator.predict([z, conditions])
    x = greedy_decode(xp)
    return to_string(x, remove_gaps=remove_gaps)


def _decode_ar(generator, z, remove_gaps: bool = False, alphabet_size: int = 21,
               sample_func=None, conditions=None):
    original_dim, alphabet_size = generator.output_shape[1], generator.output_shape[-1]
    x: np.ndarray = np.zeros((z.shape[0], original_dim, alphabet_size))
    start: int = 0
    i: int
    for i in range(start, original_dim):
        # iteration is over positions in sequence, which can't be parallelized
        pred = generator.predict([z, x]) if conditions is None else generator.predict([z, conditions, x])
        pos_pred = pred[:, i, :]
        if sample_func is None:
            pred_ind = pos_pred.argmax(-1)  # convert probability to index
        else:
            pred_ind = sample_func(pos_pred)
        j: int
        for j, p in enumerate(pred_ind):
            x[j, i, p] = 1

    seqs = to_string(x, remove_gaps=remove_gaps)
    return seqs


def batch_temp_sample(preds, temperature: float = 1.0) -> np.ndarray:
    """

    Returns
    -------
    numpy.ndarray
    """
    batch_sampled_aas: List[np.ndarray] = []
    for s in preds:
        batch_sampled_aas.append(temp_sample_outputs(s, temperature=temperature))
    out: np.ndarray = np.array(batch_sampled_aas)
    return out


def temp_sample_outputs(preds, temperature: float = 1.0):
    # https://github.com/keras-team/keras/blob/master/examples/lstm_text_generation.py
    # helper function to sample an index from a probability array N.B. this works on single prob array (i.e. array for one sequence at one timestep)
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds: np.ndarray = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)
