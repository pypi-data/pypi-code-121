import os
import urllib.request
from pathlib import Path
from typing import TextIO, List
from zipfile import ZipFile
import numpy as np
import pandas as pd
from .utils import aa_letters
from .utils.data_loaders import to_one_hot
from .load_files import s_length, load_sequence
from keras.models import model_from_json
from .SearchSQOutput import SearchSQOutput
from tqdm import tqdm, trange
import silence_tensorflow.auto


# Flag to disable progress bars
no_pbar: bool = False

# get the sequence length for each protein family that we have
seq_lengths = pd.read_csv(s_length, usecols=['name', 'size'])
aa_key: dict = {l: i for i, l in enumerate(aa_letters)}


def get_AA(n):
    """ Get Amino Acid letter from the one hot encoded version of it

    """
    return list(aa_key.keys())[list(aa_key.values()).index(n)]


class DownloadProgressBar(tqdm):
    def update_to(self, b: int = 1, bsize: int = 1, tsize: int = None):
        """

        Parameters
        ----------
        b : int
        bsize : int
        tsize : int
        """
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_url(url: str, output_path: str):
    """

    Parameters
    ----------
    url : str
        URL to download
    output_path : str
        Filename
    """
    t: DownloadProgressBar
    with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=url.split('/')[-1], disable=no_pbar) as t:
        urllib.request.urlretrieve(url, filename=output_path, reporthook=t.update_to)


def check_files():
    """ If the trained network files don't already exist, download them

    """
    if not Path('Trained_networks').exists():
        download_url('https://github.com/cfogel/Trained_networks/releases/download/Trained_networks/Trained_networks.zip', 'downloaded_file.zip')
        zf: ZipFile
        with ZipFile('downloaded_file.zip') as zf:
            for member in tqdm(zf.infolist(), desc='Extracting', leave=False, disable=no_pbar):
                zf.extract(member, 'Trained_networks')
        os.remove('downloaded_file.zip')


class SearchSQ:

    seq: str
    result: SearchSQOutput

    def __init__(self, seq: str):
        """

        Parameters
        ----------
        seq : str
            Filename of sequence
        """
        check_files()
        self.seq = seq
        self.result = self.do_search()

    def do_search(self) -> SearchSQOutput:
        """ Find best matching protein family

        Returns
        -------
        SearchSQOutput
        """
        protein_seq: str = load_sequence(self.seq)
        max_acc: float = 0
        chosen_family: str = 'none'

        # loop over all the trained networks and find the one with highest reconstruction accuracy
        i: int
        for i in trange(0, len(seq_lengths), total=len(seq_lengths), leave=False, disable=no_pbar):
            test_seq: str = protein_seq

            # skip the families with shorter protein sequence length
            if int(seq_lengths['size'][i]) < len(test_seq):
                continue

            # Not all families in sequence_lengths are in Trained_networks
            if Path('Trained_networks/' + seq_lengths['name'][i] + '.json').exists():

                # load the trained network
                json_file: TextIO = open('Trained_networks/' + seq_lengths['name'][i] + '.json', 'r')
                loaded_model_json: str = json_file.read()
                json_file.close()
                loaded_model = model_from_json(loaded_model_json)

                # load weights into new model
                loaded_model.load_weights('Trained_networks/' + seq_lengths['name'][i] + '_weights.h5')

                # add left and right gaps to get the same size sequence as the sequences used for training this network
                left_gaps: int = int((int(seq_lengths['size'][i]) - len(test_seq)) / 2)
                right_gaps: int = int(seq_lengths['size'][i]) - len(test_seq) - left_gaps
                test_seq = (left_gaps * '-') + test_seq + (right_gaps * '-')
                seq_length: int = len(test_seq)

                # use the one hot encoded version of the protein sequence
                single_msa_seq: List[str] = [test_seq]
                x_test: np.ndarray = to_one_hot(single_msa_seq)
                x_test = x_test.reshape((len(x_test), np.prod(x_test.shape[1:])))

                # reconstruct the new protein sequence with the network
                a: np.ndarray = loaded_model.predict(x_test, steps=1)
                a = a.reshape(len(single_msa_seq), seq_length, 21)

                # x is the reconstructed sequence
                x = np.vectorize(get_AA)(np.argmax(a, axis=-1))
                x = np.array(x).tolist()
                k: int
                for k in range(0, len(x)):
                    x[k] = ''.join(x[k])
                count: int = 0

                # find the reconstruction accuracy
                j: int
                for j in range(0, len(x[0])):
                    if x[0][j] == single_msa_seq[0][j]:
                        count = count + 1
                acc: float = count / len(x[0])

                # update the max accuracy and the chosen family name
                if acc > max_acc:
                    max_acc = acc
                    chosen_family = seq_lengths['name'][i]
        return SearchSQOutput(self.seq, chosen_family, str(max_acc))
