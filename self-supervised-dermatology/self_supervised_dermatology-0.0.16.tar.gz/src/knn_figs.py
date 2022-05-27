import pandas as pd
import numpy as np
import torch
import copy
import torchvision.transforms as transforms
import matplotlib
import matplotlib.pyplot as plt

from tqdm import tqdm
from pathlib import Path
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import RandomOverSampler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import f1_score
from torch.utils.data import DataLoader

from src.pkg import Embedder
from src.datasets.downstream.fitzpatrick17_dataset import Fitzpatrick17kDataset
from src.datasets.downstream.ham10000_dataset import HAM10000Dataset
from src.datasets.downstream.pad_ufes_20_dataset import PADUFES20Dataset
from src.datasets.utils import get_train_validation_data_loaders


def sample_x_point_of_class(df, n_samples: int, label_col: str):
    #nsamples = min(df[label_col].value_counts().values)
    res = pd.DataFrame()
    for val in df[label_col].unique():
        df_samp = df.loc[df[label_col] == val].sample(n_samples)
        res = pd.concat([res, df_samp], ignore_index=True).sample(frac=1)
    return res


def eval_knn(train_ds, test_ds, lbl_col, path, l_samples=[10, 100, 500, 1000, None]):
    # create the test loader
    test_dataset = DataLoader(test_ds,
                              batch_size=256,
                              num_workers=20,
                              drop_last=False,
                              shuffle=False)
    # store the f1 scores for the models
    f1_scores = {}
    for model_name in ['ibot', 'colorme', 'imagenet']:
        print(model_name)
        model = Embedder.load_pretrained(model_name, return_info=False)
        model = model.cuda()
        model.eval()

        # embed test data
        test_emb_space = []
        test_labels = []
        for batch, label in tqdm(test_dataset):
            batch = batch.cuda()
            with torch.no_grad():
                emb = model(batch)
                test_emb_space.append(emb)
                test_labels.append(label)
        test_emb_space = torch.concat(test_emb_space).cpu().squeeze()
        test_labels = torch.concat(test_labels).cpu().squeeze()

        # KNN
        f1_scores[model_name] = {}
        f1_scores[model_name]['max_f1'] = []
        f1_scores[model_name]['std_f1'] = []
        f1_scores[model_name]['mean_f1'] = []
        for n_samples in l_samples:
            l_f1s = []
            repeats = 50
            if l_samples is None:
                repeats = 3
            for r in range(repeats):
                print(f'Repeats: {r}/{repeats}')
                t_ds = copy.deepcopy(train_ds)
                if n_samples is not None:
                    t_ds.meta_data = sample_x_point_of_class(
                        t_ds.meta_data, n_samples, lbl_col)

                train_dataset = DataLoader(t_ds,
                                           batch_size=256,
                                           num_workers=20,
                                           drop_last=False,
                                           shuffle=False)

                emb_space = []
                labels = []
                for batch, label in tqdm(train_dataset):
                    batch = batch.cuda()
                    with torch.no_grad():
                        emb = model(batch)
                        emb_space.append(emb)
                        labels.append(label)
                emb_space = torch.concat(emb_space).cpu().squeeze()
                labels = torch.concat(labels).cpu().squeeze()

                poss_f1 = []
                for n_neigh in [1, 5, 10, 20, 30, 50, 100, 200]:
                    try:
                        neigh = KNeighborsClassifier(n_neighbors=n_neigh,
                                                     metric='cosine')
                        neigh.fit(emb_space.squeeze(), labels)
                        f1 = f1_score(test_labels,
                                      neigh.predict(test_emb_space),
                                      average='macro') * 100
                    except Exception:
                        continue
                    poss_f1.append(f1)

                max_f1 = np.max(poss_f1)
                print(max_f1)
                l_f1s.append(max_f1)

            f1_scores[model_name]['max_f1'].append(np.max(l_f1s))
            f1_scores[model_name]['std_f1'].append(np.std(l_f1s))
            f1_scores[model_name]['mean_f1'].append(np.mean(l_f1s))

    ticks = [x if x is not None else 'All' for x in l_samples]
    plot_results(f1_scores, path=path, ticks=ticks)
    return f1_scores


def plot_results(f1_scores, path, title='', ticks=[10, 100, 500, 1000, 'All']):
    plt.rcParams["figure.figsize"] = (6, 6)

    plt.plot(f1_scores['ibot']['max_f1'][:-1] + [None],
             '*--',
             label='iBOT',
             markersize=10,
             color='orange')
    plt.plot([None] * len(ticks[:-1]) + [f1_scores['ibot']['max_f1'][-1]],
             'X',
             markersize=10,
             color='orange')
    plt.fill_between(np.array(range(len(ticks) - 1)),
                     np.array(f1_scores['ibot']['max_f1'][:-1]) -
                     np.array(f1_scores['ibot']['std_f1'][:-1]),
                     np.array(f1_scores['ibot']['max_f1'][:-1]) +
                     np.array(f1_scores['ibot']['std_f1'][:-1]),
                     alpha=0.2,
                     color='orange')

    plt.plot(f1_scores['colorme']['max_f1'][:-1] + [None],
             '*--',
             label='ColorMe',
             markersize=10,
             color='green')
    plt.plot([None] * len(ticks[:-1]) + [f1_scores['colorme']['max_f1'][-1]],
             'X',
             markersize=10,
             color='green')
    plt.fill_between(np.array(range(len(ticks) - 1)),
                     np.array(f1_scores['colorme']['max_f1'][:-1]) -
                     np.array(f1_scores['colorme']['std_f1'][:-1]),
                     np.array(f1_scores['colorme']['max_f1'][:-1]) +
                     np.array(f1_scores['colorme']['std_f1'][:-1]),
                     alpha=0.2,
                     color='green')

    plt.plot(f1_scores['imagenet']['max_f1'][:-1] + [None],
             '*--',
             markersize=10,
             label='ImageNet',
             color='royalblue')
    plt.plot([None] * len(ticks[:-1]) + [f1_scores['imagenet']['max_f1'][-1]],
             'X',
             markersize=10,
             color='royalblue')
    plt.fill_between(np.array(range(len(ticks) - 1)),
                     np.array(f1_scores['imagenet']['max_f1'][:-1]) -
                     np.array(f1_scores['imagenet']['std_f1'][:-1]),
                     np.array(f1_scores['imagenet']['max_f1'][:-1]) +
                     np.array(f1_scores['imagenet']['std_f1'][:-1]),
                     alpha=0.2,
                     color='royalblue')

    plt.xticks(np.arange(len(ticks)), ticks)
    fmt = '%.0f%%'
    yticks = matplotlib.ticker.FormatStrFormatter(fmt)
    plt.gca().yaxis.set_major_formatter(yticks)
    plt.legend()
    if title != '':
        plt.title(title)
    plt.ylabel('Macro F1 score')
    plt.xlabel('N.o. samples per class')
    plt.show()
    plt.savefig(path, bbox_inches="tight")
    plt.clf()
    plt.cla()


if __name__ == "__main__":
    SEED = 42
    np.random.seed(SEED)
    plt.rc('font', family='serif', size=22)

    transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
    ])

    # PAD-UFES-20
    dataset_path = Path('data/PAD-UFES-20/')
    csv_path = dataset_path / 'metadata.csv'
    root_path = dataset_path / 'images'
    dataset = PADUFES20Dataset(csv_path, root_path, transform)
    lbl_col = 'diagnostic'

    train_ds = copy.deepcopy(dataset)
    test_ds = copy.deepcopy(dataset)
    train_ds.meta_data, test_ds.meta_data = train_test_split(dataset.meta_data,
                                                             test_size=0.15,
                                                             random_state=SEED)

    oversample = RandomOverSampler()
    train_ds.meta_data, _ = oversample.fit_resample(
        train_ds.meta_data, train_ds.meta_data[lbl_col])
    train_ds.meta_data[lbl_col].value_counts()

    f1_scores_pad = eval_knn(train_ds, test_ds, lbl_col, 'knn_pad_ufes_20.jpg',
                             [10, 50, 100, 500, None])

    # HAM10000Dataset
    dataset_path = Path('data/HAM10000/')
    csv_path = dataset_path / 'HAM10000_metadata.csv'
    dataset = HAM10000Dataset(csv_path, dataset_path, transform)
    lbl_col = 'cell_type_idx'

    train_ds = copy.deepcopy(dataset)
    test_ds = copy.deepcopy(dataset)
    train_ds.meta_data, test_ds.meta_data = train_test_split(dataset.meta_data,
                                                             test_size=0.15,
                                                             random_state=SEED)

    oversample = RandomOverSampler()
    train_ds.meta_data, _ = oversample.fit_resample(
        train_ds.meta_data, train_ds.meta_data[lbl_col])
    train_ds.meta_data[lbl_col].value_counts()

    f1_scores_ham = eval_knn(train_ds, test_ds, lbl_col, 'knn_ham10000.jpg',
                             [10, 50, 100, 500, None])

    # Fitzpatrick17k
    dataset_path = Path('data/fitzpatrick17k/')
    csv_path = dataset_path / 'fitzpatrick17k.csv'
    dataset = Fitzpatrick17kDataset(csv_path, dataset_path, transform)
    lbl_col = 'lbl_high'

    train_ds = copy.deepcopy(dataset)
    test_ds = copy.deepcopy(dataset)
    train_ds.meta_data, test_ds.meta_data = train_test_split(dataset.meta_data,
                                                             test_size=0.15,
                                                             random_state=SEED)

    oversample = RandomOverSampler()
    train_ds.meta_data, _ = oversample.fit_resample(
        train_ds.meta_data, train_ds.meta_data[lbl_col])
    train_ds.meta_data[lbl_col].value_counts()

    f1_scores_fitz = eval_knn(train_ds, test_ds, lbl_col, 'knn_fitz.jpg',
                              [10, 50, 100, 500, None])
