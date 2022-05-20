from typing import List, Union, Dict
import numpy as np
import pandas as pd
from . import aa_letters


def seq_to_one_hot(sequence: str, aa_key: Dict[str, int]) -> np.ndarray:
    """

    Parameters
    ----------
    sequence : str
    aa_key : Dict[str, int]

    Returns
    -------
    numpy.ndarray
    """
    arr: np.ndarray = np.zeros((len(sequence), len(aa_key)))
    j: int
    for j, c in enumerate(sequence):
        err: KeyError
        try:
            arr[j, aa_key[c]] = 1
        except KeyError as err:
            print("Invalid sequence letter")
            exit(err)
    return arr


def to_one_hot(seqlist: Union[str, List[str]], alphabet: List[str] = aa_letters) -> np.ndarray:
    """

    Parameters
    ----------
    seqlist : List[str]
    alphabet : List[str]

    Returns
    -------
    numpy.ndarray
    """
    aa_key: Dict[str, int] = {l: i for i, l in enumerate(alphabet)}
    if type(seqlist) == str:
        return seq_to_one_hot(seqlist, aa_key)
    else:
        encoded_seqs: List[np.ndarray] = []
        prot: str
        for prot in seqlist:
            encoded_seqs.append(seq_to_one_hot(prot, aa_key))
        return np.stack(encoded_seqs)


def right_pad(seqlist, target_length=None):
    if target_length is None:
        return seqlist
    assert isinstance(target_length, int), 'Unknown format for argument padding'
    # handle padding either integer or character representations of sequences
    pad_char = '-' if isinstance(seqlist[0], str) else [0] if isinstance(seqlist[0], list) else None
    return [seq + pad_char * (target_length - len(seq)) for seq in seqlist]


def one_hot_generator(seqlist, conditions=None, batch_size: int = 32,
                      padding: int = 504, shuffle: bool = True, alphabet: List[str] = aa_letters):
    if type(seqlist) == pd.Series:
        seqlist = seqlist.values
    if type(seqlist) == list:
        seqlist = np.array(seqlist)
    if type(conditions) == list:
        conditions = np.array(conditions)

    epoch: int = 0

    while True:
        # shuffle
        if shuffle:
            perm: np.ndarray = np.random.permutation(len(seqlist))
            prots = seqlist[perm]
            if conditions is not None:
                conds = conditions[perm]
        else:
            prots = seqlist
            conds = conditions

        i: int
        for i in range(len(prots) // batch_size):
            batch: np.ndarray = to_one_hot(right_pad(prots[i * batch_size:(i + 1) * batch_size], padding),
                                           alphabet=alphabet)
            if conditions is not None:
                yield [batch, conds[i * batch_size:(i + 1) * batch_size]], batch
            else:
                yield batch, batch

        epoch += 1
