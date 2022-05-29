import pandas as pd
import numpy as np
import torch
import sqlite3
import sklearn.model_selection


def get_data_split(n: int,
                   split_ratio: float = 0.2,
                   random_seed: int = 42):
    # set seed for reproducibility
    if random_seed:
        torch.manual_seed(random_seed)
    # random indicies
    idx = torch.randperm(n)
    n_valid = int(n * split_ratio)
    idx_valid = idx[:n_valid]
    idx_train = idx[n_valid:]
    return idx_train, idx_valid


class BaseDataset(torch.utils.data.Dataset):
    def __init__(self):
        pass

    def get_validation_set(self):
        if self.idx_valid is not None:
            return self.X[self.idx_valid], self.y[self.idx_valid]
        else:
            return None, None

    def get_class_weights(self):
        cnts = torch.bincount(self.y)
        cnts = torch.maximum(cnts, torch.tensor(1))
        weights = cnts.sum() / (len(cnts) * cnts)
        return weights

    def num_classes(self):
        return len(self.labels)

    def num_features(self):
        return self.X.shape[-1]

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, rowidx):
        return self.X[self.indices[rowidx]], self.y[self.indices[rowidx]]


class GermEval17(BaseDataset):
    """ ABSD-Relevance, -Sentiment, -Category
    Examples:
    ---------
    dset = GermEval17(
        preprocesser, task="Relevance", test=False,
        early_stopping=True, split_ratio=0.1)
    X_valid, y_valid = dset.get_validation_set()
    n_classes = dset.num_classes()
    dgen = torch.utils.data.DataLoader(
        dset, **{'batch_size': 64, 'shuffle': True, 'num_workers': 6})
    for X, y in dgen: break
    """
    def __init__(self,
                 preprocesser,
                 datafolder: str = "datasets",
                 task: int = 1,
                 test: bool = False,
                 early_stopping: bool = False,
                 split_ratio: float = 0.2,
                 random_seed: int = 42):
        assert task in ["Relevance", "Sentiment", "Category"]
        self.colidx = int(
            ["Relevance", "Sentiment", "Category"].index(task) + 2)

        if task == "Relevance":
            self.labels = [False, True]
        elif task == "Sentiment":
            self.labels = ['negative', 'neutral', 'positive']
        elif task == "Category":
            self.labels = [
                'Image', 'Informationen', 'Connectivity',
                'Auslastung_und_Platzangebot', 'Service_und_Kundenbetreuung',
                'Gastronomisches_Angebot', 'Allgemein', 'Design',
                'Sonstige_Unregelmässigkeiten', 'Gepäck', 'DB_App_und_Website',
                'Atmosphäre', 'Zugfahrt', 'Ticketkauf', 'nan',
                'Reisen_mit_Kindern', 'Barrierefreiheit', 'Sicherheit',
                'Toiletten', 'Komfort_und_Ausstattung']

        # read data
        split = "test" if test else "train"
        data = pd.read_csv(
            f"{datafolder}/germeval17/{split}.tsv",
            sep="\t", header=None).values
        data[:, 4] = [str(s).split(":")[0] for s in data[:, 4]]
        # bad examples to be removed
        idxbad = [i for i, x in enumerate(data[:, 1])
                  if not isinstance(x, str)]
        data = np.delete(data, idxbad, axis=0)

        # preprocess
        self.X = preprocesser(data[:, 1].astype(str).tolist())
        if not isinstance(self.X, torch.Tensor):
            self.X = torch.tensor(self.X)
        self.y = torch.tensor(
            [self.labels.index(row[self.colidx]) for row in data])
        # prepare data split
        if early_stopping and split == "train":
            self.indices, self.idx_valid = get_data_split(
                self.X.shape[0], random_seed=random_seed)
        else:
            self.indices = torch.tensor(range(self.X.shape[0]))
            self.idx_valid = None


class GermEval18(BaseDataset):
    """ OL18A, OL18B
    Examples:
    ---------
    dset = GermEval18(
        preprocesser, task="A", test=False,
        early_stopping=True, split_ratio=0.1)
    X_valid, y_valid = dset.get_validation_set()
    n_classes = dset.num_classes()
    dgen = torch.utils.data.DataLoader(
        dset, **{'batch_size': 64, 'shuffle': True, 'num_workers': 6})
    for X, y in dgen: break
    """
    def __init__(self,
                 preprocesser,
                 datafolder: str = "datasets",
                 task: int = 1,
                 test: bool = False,
                 early_stopping: bool = False,
                 split_ratio: float = 0.2,
                 random_seed: int = 42):
        assert task in ["A", "B", "C"]
        self.colidx = int(["A", "B", "C"].index(task) + 1)

        if task == "A":
            self.labels = ['OFFENSE', 'OTHER']
        elif task == "B":
            self.labels = ['PROFANITY', 'INSULT', 'ABUSE', 'OTHER']

        # read data
        split = "test" if test else "train"
        data = pd.read_csv(
            f"{datafolder}/germeval18/{split}.txt",
            sep="\t", header=None).values
        # preprocess
        self.X = preprocesser(data[:, 0].astype(str).tolist())
        if not isinstance(self.X, torch.Tensor):
            self.X = torch.tensor(self.X)
        self.y = torch.tensor(
            [self.labels.index(row[self.colidx]) for row in data])

        # prepare data split
        if early_stopping and split == "train":
            self.indices, self.idx_valid = get_data_split(
                self.X.shape[0], random_seed=random_seed)
        else:
            self.indices = torch.tensor(range(self.X.shape[0]))
            self.idx_valid = None


class GermEval19(BaseDataset):
    """ OL19A, OL19B, OL19C
    Examples:
    ---------
    dset = GermEval19(
        preprocesser, task="A", test=False,
        early_stopping=True, split_ratio=0.1)
    X_valid, y_valid = dset.get_validation_set()
    n_classes = dset.num_classes()
    dgen = torch.utils.data.DataLoader(
        dset, **{'batch_size': 64, 'shuffle': True, 'num_workers': 6})
    for X, y in dgen: break
    """
    def __init__(self,
                 preprocesser,
                 datafolder: str = "datasets",
                 task: int = 1,
                 test: bool = False,
                 early_stopping: bool = False,
                 split_ratio: float = 0.2,
                 random_seed: int = 42):
        assert task in ["A", "B", "C"]
        self.colidx = int(["A", "B", "C"].index(task) + 1)

        if task == "A":
            self.labels = ['OFFENSE', 'OTHER']
            fsuf = "12"
        elif task == "B":
            self.labels = ['PROFANITY', 'INSULT', 'ABUSE', 'OTHER']
            fsuf = "12"
        elif task == "C":
            self.labels = ['EXPLICIT', 'IMPLICIT']
            fsuf = "3"

        # read data
        split = "gold" if test else "train"
        data = pd.read_csv(
            f"{datafolder}/germeval19/{split}{fsuf}.txt",
            sep="\t", header=None).values
        # preprocess
        self.X = preprocesser(data[:, 0].astype(str).tolist())
        if not isinstance(self.X, torch.Tensor):
            self.X = torch.tensor(self.X)
        self.y = torch.tensor(
            [self.labels.index(row[self.colidx]) for row in data])

        # prepare data split
        if early_stopping and split == "train":
            self.indices, self.idx_valid = get_data_split(
                self.X.shape[0], random_seed=random_seed)
        else:
            self.indices = torch.tensor(range(self.X.shape[0]))
            self.idx_valid = None


class GermEval21(BaseDataset):
    """ TOXIC, ENGAGE FCLAIM
    Examples:
    ---------
    dset = GermEval21(
        preprocesser, task="TOXIC", test=False,
        early_stopping=True, split_ratio=0.1)
    X_valid, y_valid = dset.get_validation_set()
    n_classes = dset.num_classes()
    dgen = torch.utils.data.DataLoader(
        dset, **{'batch_size': 64, 'shuffle': True, 'num_workers': 6})
    for X, y in dgen: break
    """
    def __init__(self,
                 preprocesser,
                 datafolder: str = "datasets",
                 task: str = "TOXIC",
                 test: bool = False,
                 early_stopping: bool = False,
                 split_ratio: float = 0.2,
                 random_seed: int = 42):
        assert task in ["TOXIC", "ENGAGE", "FCLAIM"]
        self.colidx = int(["TOXIC", "ENGAGE", "FCLAIM"].index(task) + 2)

        # read data
        split = "test" if test else "train"
        data = pd.read_csv(f"{datafolder}/germeval21/{split}.csv").values
        # preprocess
        self.X = preprocesser(data[:, 1].astype(str).tolist())
        if not isinstance(self.X, torch.Tensor):
            self.X = torch.tensor(self.X)
        self.y = torch.tensor([row[self.colidx] for row in data])

        # prepare data split
        if early_stopping and split == "train":
            self.indices, self.idx_valid = get_data_split(
                self.X.shape[0], random_seed=random_seed)
        else:
            self.indices = torch.tensor(range(self.X.shape[0]))
            self.idx_valid = None

    def num_classes(self):
        return 2


class GermEval21vmwe(BaseDataset):
    """ VMWE
    Examples:
    ---------
    dset = GermEval21vmwe(
        preprocesser, test=False,
        early_stopping=True, split_ratio=0.1)
    X_valid, y_valid = dset.get_validation_set()
    n_classes = dset.num_classes()
    dgen = torch.utils.data.DataLoader(
        dset, **{'batch_size': 64, 'shuffle': True, 'num_workers': 6})
    for X, y in dgen: break
    """
    def __init__(self,
                 preprocesser,
                 datafolder: str = "datasets",
                 test: bool = False,
                 early_stopping: bool = False,
                 split_ratio: float = 0.2,
                 random_seed: int = 42):
        # self.labels = ['figuratively', 'literally', 'both', 'undecidable']
        self.labels = ['figuratively', 'literally']

        # read data
        split = "test" if test else "train"
        data = pd.read_csv(
            f"{datafolder}/germeval21vmwe/{split}.tsv",
            sep="\t", header=None).values
        # bad examples to be removed
        idxbad = [i for i, x in enumerate(data[:, 2])
                  if x not in self.labels]
        data = np.delete(data, idxbad, axis=0)

        # preprocess
        self.X = preprocesser(data[:, 3].astype(str).tolist())
        if not isinstance(self.X, torch.Tensor):
            self.X = torch.tensor(self.X)
        self.y = torch.tensor([self.labels.index(row[2]) for row in data])

        # prepare data split
        if early_stopping and split == "train":
            self.indices, self.idx_valid = get_data_split(
                self.X.shape[0], random_seed=random_seed)
        else:
            self.indices = torch.tensor(range(self.X.shape[0]))
            self.idx_valid = None

    def num_classes(self):
        return 2


def merge_mio(a, b):
    s = ""
    if isinstance(a, str):
        s += a
        s += ". "
    if isinstance(b, str):
        s += b
    return s


class MillionSentiment(BaseDataset):
    """ Million Dataset
    Examples:
    ---------
    dset = MillionSentiment(
        preprocesser, test=False,
        early_stopping=True, split_ratio=0.1)
    X_valid, y_valid = dset.get_validation_set()
    n_classes = dset.num_classes()
    dgen = torch.utils.data.DataLoader(
        dset, **{'batch_size': 64, 'shuffle': True, 'num_workers': 6})
    for X, y in dgen: break
    """
    def __init__(self,
                 preprocesser,
                 datafolder: str = "datasets",
                 test: bool = False,
                 early_stopping: bool = False,
                 split_ratio: float = 0.2,
                 random_seed: int = 42):
        # self.labels = ['negative', 'neural', 'positive']
        # read data
        con = sqlite3.connect(f"{datafolder}/1mio/corpus.sqlite3")
        cur = con.cursor()
        res = cur.execute("""
        SELECT
            Posts.Headline,
            Posts.Body,
            SUM(IIF(Category='SentimentNeutral', Value, 0)),
            SUM(IIF(Category='SentimentNegative', Value, 0)),
            SUM(IIF(Category='SentimentPositive', Value, 0))
        FROM Annotations
        INNER JOIN Posts ON Posts.ID_Post=Annotations.ID_Post
        WHERE Category='SentimentNegative'
        OR Category='SentimentNeutral'
        OR Category='SentimentPositive'
        GROUP BY Annotations.ID_Post
        """)
        dat = [(merge_mio(row[0], row[1]), np.argmax(row[2:])) for row in res]
        dat = [(x, y) for x, y in dat if len(x) > 0]
        X = [str(row[0]) for row in dat]
        y = [int(row[1]) for row in dat]

        # data split
        if test:
            _, X, _, y = sklearn.model_selection.train_test_split(
                X, y, test_size=0.5, random_state=random_seed, stratify=y)
        else:
            X, _, y, _ = sklearn.model_selection.train_test_split(
                X, y, test_size=0.5, random_state=random_seed, stratify=y)

        # preprocess
        self.X = preprocesser(X)
        if not isinstance(self.X, torch.Tensor):
            self.X = torch.tensor(self.X)
        self.y = torch.tensor(y)

        # prepare data split
        if early_stopping and (not test):
            self.indices, self.idx_valid = get_data_split(
                self.X.shape[0], random_seed=random_seed)
        else:
            self.indices = torch.tensor(range(self.X.shape[0]))
            self.idx_valid = None

    def num_classes(self):
        return 3


class MillionBinary(BaseDataset):
    """ Million Dataset
    Tasks:
    ------
    MIO-O: 'OffTopic'
    MIO-I: 'Inappropriate'
    MIO-D: 'Discriminating'
    MIO-F: 'PossiblyFeedback'
    MIO-P: 'PersonalStories'
    MIO-A: 'ArgumentsUsed'

    Examples:
    ---------
    dset = MillionBinary(
        preprocesser, test=False, task='OffTopic',
        early_stopping=True, split_ratio=0.1)
    X_valid, y_valid = dset.get_validation_set()
    n_classes = dset.num_classes()
    dgen = torch.utils.data.DataLoader(
        dset, **{'batch_size': 64, 'shuffle': True, 'num_workers': 6})
    for X, y in dgen: break
    """
    def __init__(self,
                 preprocesser,
                 datafolder: str = "datasets",
                 task: str = "OffTopic",
                 test: bool = False,
                 early_stopping: bool = False,
                 split_ratio: float = 0.2,
                 random_seed: int = 42):
        # self.labels = ['negative', 'neural', 'positive']
        # task
        t1 = ['MIO-O', 'MIO-I', 'MIO-D', 'MIO-F', 'MIO-P', 'MIO-A']
        t2 = ['OffTopic', 'Inappropriate', 'Discriminating',
              'PossiblyFeedback', 'PersonalStories', 'ArgumentsUsed']
        if task in t1:
            idx = t1.index(task)
            task = t2[idx]
        if task not in t2:
            raise Exception(f"task='{task}' does not exist")

        # read data
        con = sqlite3.connect(f"{datafolder}/1mio/corpus.sqlite3")
        cur = con.cursor()
        res = cur.execute(f"""
        SELECT
            Posts.Headline,
            Posts.Body,
            AVG(Annotations.Value) >= 0.5
        FROM Annotations
        INNER JOIN Posts ON Posts.ID_Post=Annotations.ID_Post
        WHERE Annotations.Category='{task}'
        GROUP BY Annotations.ID_Post
        """)
        dat = [(merge_mio(row[0], row[1]), row[2]) for row in res]
        dat = [(x, y) for x, y in dat if len(x) > 0]
        X = [str(row[0]) for row in dat]
        y = [int(row[1]) for row in dat]

        # data split
        if test:
            _, X, _, y = sklearn.model_selection.train_test_split(
                X, y, test_size=0.5, random_state=random_seed, stratify=y)
        else:
            X, _, y, _ = sklearn.model_selection.train_test_split(
                X, y, test_size=0.5, random_state=random_seed, stratify=y)

        # preprocess
        self.X = preprocesser(X)
        if not isinstance(self.X, torch.Tensor):
            self.X = torch.tensor(self.X)
        self.y = torch.tensor(y)

        # prepare data split
        if early_stopping and (not test):
            self.indices, self.idx_valid = get_data_split(
                self.X.shape[0], random_seed=random_seed)
        else:
            self.indices = torch.tensor(range(self.X.shape[0]))
            self.idx_valid = None

    def num_classes(self):
        return 2


class SBCHisSwiss(BaseDataset):
    """ SB-CH, chatmania, Swiss German detection
    Examples:
    ---------
    dset = SBCHisSwiss(
        preprocesser, test=False,
        early_stopping=True, split_ratio=0.1)
    X_valid, y_valid = dset.get_validation_set()
    n_classes = dset.num_classes()
    dgen = torch.utils.data.DataLoader(
        dset, **{'batch_size': 64, 'shuffle': True, 'num_workers': 6})
    for X, y in dgen: break
    """
    def __init__(self,
                 preprocesser,
                 datafolder: str = "datasets",
                 test: bool = False,
                 early_stopping: bool = False,
                 split_ratio: float = 0.2,
                 random_seed: int = 42):
        # read data
        df1 = pd.read_csv(f"{datafolder}/sbch/sentiment.csv")
        df2 = pd.read_csv(f"{datafolder}/sbch/chatmania.csv")
        df1['sentence_id'] = df1['sentence_id'].astype(int)
        df2['sentence_id'] = df2['sentence_id'].astype(int)
        df = df2.merge(df1, how="inner", on="sentence_id")
        y = (df["un"] == 0).astype(int).tolist()
        X = df['sentence_text'].astype(str).tolist()

        # data split
        if test:
            _, X, _, y = sklearn.model_selection.train_test_split(
                X, y, test_size=0.5, random_state=random_seed, stratify=y)
        else:
            X, _, y, _ = sklearn.model_selection.train_test_split(
                X, y, test_size=0.5, random_state=random_seed, stratify=y)

        # preprocess
        self.X = preprocesser(X)
        if not isinstance(self.X, torch.Tensor):
            self.X = torch.tensor(self.X)
        self.y = torch.tensor(y)

        # prepare data split
        if early_stopping and (not test):
            self.indices, self.idx_valid = get_data_split(
                self.X.shape[0], random_seed=random_seed)
        else:
            self.indices = torch.tensor(range(self.X.shape[0]))
            self.idx_valid = None

    def num_classes(self):
        return 2


class SBCHsenti(BaseDataset):
    """ SB-CH, chatmania, Sentiment Analysis, only comments detected as swiss
    Examples:
    ---------
    dset = SBCHsenti(
        preprocesser, test=False,
        early_stopping=True, split_ratio=0.1)
    X_valid, y_valid = dset.get_validation_set()
    n_classes = dset.num_classes()
    dgen = torch.utils.data.DataLoader(
        dset, **{'batch_size': 64, 'shuffle': True, 'num_workers': 6})
    for X, y in dgen: break
    """
    def __init__(self,
                 preprocesser,
                 datafolder: str = "datasets",
                 test: bool = False,
                 early_stopping: bool = False,
                 split_ratio: float = 0.2,
                 random_seed: int = 42):
        # read data
        df1 = pd.read_csv(f"{datafolder}/sbch/sentiment.csv")
        df2 = pd.read_csv(f"{datafolder}/sbch/chatmania.csv")
        df1['sentence_id'] = df1['sentence_id'].astype(int)
        df2['sentence_id'] = df2['sentence_id'].astype(int)
        df = df2.merge(df1, how="inner", on="sentence_id")
        # remove non-swiss comments
        mask_isswiss = df["un"] == 0
        df = df[mask_isswiss]
        # remove examples without sentiment
        mask_hasval = df[['neut', 'neg', 'pos']].sum(axis=1) > 0
        df = df[mask_hasval]
        # merge sentiment frequencies to class label
        y = df[['neut', 'neg', 'pos']].apply(
            lambda row: np.argmax(row), axis=1).tolist()
        X = df['sentence_text'].astype(str).tolist()

        # data split
        if test:
            _, X, _, y = sklearn.model_selection.train_test_split(
                X, y, test_size=0.5, random_state=random_seed, stratify=y)
        else:
            X, _, y, _ = sklearn.model_selection.train_test_split(
                X, y, test_size=0.5, random_state=random_seed, stratify=y)

        # preprocess
        self.X = preprocesser(X)
        if not isinstance(self.X, torch.Tensor):
            self.X = torch.tensor(self.X)
        self.y = torch.tensor(y)

        # prepare data split
        if early_stopping and (not test):
            self.indices, self.idx_valid = get_data_split(
                self.X.shape[0], random_seed=random_seed)
        else:
            self.indices = torch.tensor(range(self.X.shape[0]))
            self.idx_valid = None

    def num_classes(self):
        return 3


class LSDC(BaseDataset):
    """ The Low Saxon Dialect Classification (LSDC) dataset

    Notes:
    ------
    - Lower Prussia (NPR) is excluded because extinct
    - Gronings (GRO) is excluded because not enough examples

    Examples:
    ---------
    dset = LSDC(
        preprocesser, test=False,
        early_stopping=True, split_ratio=0.1)
    X_valid, y_valid = dset.get_validation_set()
    n_classes = dset.num_classes()
    dgen = torch.utils.data.DataLoader(
        dset, **{'batch_size': 64, 'shuffle': True, 'num_workers': 6})
    for X, y in dgen: break
    """
    def __init__(self,
                 preprocesser,
                 datafolder: str = "datasets",
                 test: bool = False,
                 early_stopping: bool = False,
                 split_ratio: float = 0.2,
                 random_seed: int = 42):
        # excluded: 'NPR' (extinct dialect), 'GRO' (lack of data)
        self.labels = ['ACH', 'DRE', 'HAM', 'HOL', 'MAR', 'MKB', 'MON',
                       'NNI', 'OFL', 'OFR', 'OVY', 'OWL', 'SUD', 'TWE']
        # read data
        split = "test" if test else "train"
        data = pd.read_csv(
            f"{datafolder}/lsdc/{split}.tsv",
            sep="\t", header=None).values

        # bad examples to be removed
        idxbad = [i for i, x in enumerate(data[:, 0])
                  if x not in self.labels]
        data = np.delete(data, idxbad, axis=0)

        # preprocess
        self.X = preprocesser(data[:, 2].astype(str).tolist())
        if not isinstance(self.X, torch.Tensor):
            self.X = torch.tensor(self.X)
        self.y = torch.tensor(
            [self.labels.index(row[0]) for row in data])
        # prepare data split
        if early_stopping and split == "train":
            self.indices, self.idx_valid = get_data_split(
                self.X.shape[0], random_seed=random_seed)
        else:
            self.indices = torch.tensor(range(self.X.shape[0]))
            self.idx_valid = None


class ArchiMob(BaseDataset):
    """ ArchiMob corpus
    Examples:
    ---------
    dset = ArchiMob(
        preprocesser, test=False,
        early_stopping=True, split_ratio=0.1)
    X_valid, y_valid = dset.get_validation_set()
    n_classes = dset.num_classes()
    dgen = torch.utils.data.DataLoader(
        dset, **{'batch_size': 64, 'shuffle': True, 'num_workers': 6})
    for X, y in dgen: break
    """
    def __init__(self,
                 preprocesser,
                 datafolder: str = "datasets",
                 test: bool = False,
                 early_stopping: bool = False,
                 split_ratio: float = 0.2,
                 random_seed: int = 42):
        self.labels = ['BE', 'BS', 'ZH', 'LU']
        # read data
        if test:
            data = pd.read_csv(
                f"{datafolder}/archimob/gold.tsv",
                sep="\t", header=None).values
        else:
            data1 = pd.read_csv(
                f"{datafolder}/archimob/train.tsv",
                sep="\t", header=None).values
            data2 = pd.read_csv(
                f"{datafolder}/archimob/dev.tsv",
                sep="\t", header=None).values
            data = np.vstack([data1, data2])

        # preprocess
        self.X = preprocesser(data[:, 0].astype(str).tolist())
        if not isinstance(self.X, torch.Tensor):
            self.X = torch.tensor(self.X)
        self.y = torch.tensor(
            [self.labels.index(row[1]) for row in data])

        # prepare data split
        if early_stopping and (not test):
            self.indices, self.idx_valid = get_data_split(
                self.X.shape[0], random_seed=random_seed)
        else:
            self.indices = torch.tensor(range(self.X.shape[0]))
            self.idx_valid = None
