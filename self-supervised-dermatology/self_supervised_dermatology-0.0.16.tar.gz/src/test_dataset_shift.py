import argparse
import torch
import numpy as np
import matplotlib.pyplot as plt
import torchvision.models as models
from pathlib import Path
from scipy import stats
from sklearn.decomposition import PCA
from torch.utils.data import DataLoader
from torchvision import transforms

from src.datasets.encrypted_image_folder import EncryptedImageFolder
from src.datasets.utils import get_train_validation_data_loaders


my_parser = argparse.ArgumentParser(
    description='Tests if there is a possible dataset shift.')
my_parser.add_argument('--body_loc_path',
                       type=str,
                       required=True,
                       help='Path to the body loc dataset.')
args = my_parser.parse_args()


def embed_dataset(
    model,
    dataset,
    device,
) -> torch.Tensor:
    # evaluate model on val set
    model.eval()
    with torch.no_grad():
        embeddings = []
        for img, _ in dataset:
            img = img.to(device)
            # get the embeddings
            emb = model(img)
            emb = emb.squeeze()
            # add info to lists
            embeddings.append(emb.cpu().numpy())
    # create (concat) our embedding space
    embeddings = np.concatenate(embeddings, axis=0)
    embeddings = torch.Tensor(embeddings)
    return embeddings


def check_dataset_shift_assumption(model, train_set, val_set, test_set,
                                   test_set2, device):
    train_emb = embed_dataset(model=model, dataset=train_set, device=device)
    val_emb = embed_dataset(model=model, dataset=val_set, device=device)
    test_emb = embed_dataset(model=model, dataset=test_set, device=device)
    test2_emb = embed_dataset(model=model, dataset=test_set2, device=device)

    # define PCA for transforming the embedding space
    # into independent random variables
    pca = PCA(n_components=None)
    # compute PCA for the spaces
    train_emb = torch.Tensor(pca.fit_transform(train_emb))
    plt.plot(np.cumsum(pca.explained_variance_ratio_))
    plt.xlabel('Number of components')
    plt.ylabel('Explained Variance')
    plt.title('Explained variance TRAIN')
    plt.show()
    plt.savefig('explained_var_train.png')

    val_emb = torch.Tensor(pca.fit_transform(val_emb))
    test_emb = torch.Tensor(pca.fit_transform(test_emb))
    test2_emb = torch.Tensor(pca.fit_transform(test2_emb))

    # get min / max of each feature
    mins = torch.cat([train_emb, val_emb, test_emb, test2_emb]).min(dim=0).values
    maxs = torch.cat([train_emb, val_emb, test_emb, test2_emb]).max(dim=0).values

    div_train_val = []
    div_val_test = []
    div_train_test = []
    div_test_test = []
    for d in range(train_emb.shape[1]):
        # convert each feature dimension into normalized histogram
        # that can be used as a distrbution
        train_feat_hist = torch.histogram(
            train_emb[:, d],
            bins=100,
            range=(float(mins[d].numpy()), float(maxs[d].numpy())))
        train_feat_hist = train_feat_hist.hist / train_emb.shape[0]
        train_feat_hist = torch.clip(train_feat_hist, min=1e-7, max=1)

        val_feat_hist = torch.histogram(
            val_emb[:, d],
            bins=100,
            range=(float(mins[d].numpy()), float(maxs[d].numpy())))
        val_feat_hist = val_feat_hist.hist / val_emb.shape[0]
        val_feat_hist = torch.clip(val_feat_hist, min=1e-7, max=1)

        test_feat_hist = torch.histogram(
            test_emb[:, d],
            bins=100,
            range=(float(mins[d].numpy()), float(maxs[d].numpy())))
        test_feat_hist = test_feat_hist.hist / test_emb.shape[0]
        test_feat_hist = torch.clip(test_feat_hist, min=1e-7, max=1)

        test2_feat_hist = torch.histogram(
            test2_emb[:, d],
            bins=100,
            range=(float(mins[d].numpy()), float(maxs[d].numpy())))
        test2_feat_hist = test2_feat_hist.hist / test_emb.shape[0]
        test2_feat_hist = torch.clip(test2_feat_hist, min=1e-7, max=1)

        # KL divergence between train / val / test
        kl_train_val = (
            train_feat_hist *
            torch.log(train_feat_hist / val_feat_hist)).sum(dim=-1)
        kl_val_test = (
            val_feat_hist *
            torch.log(val_feat_hist / test_feat_hist)).sum(dim=-1)
        kl_train_test = (
            train_feat_hist *
            torch.log(train_feat_hist / test_feat_hist)).sum(dim=-1)
        kl_test_test = (
            test_feat_hist *
            torch.log(test_feat_hist / test2_feat_hist)).sum(dim=-1)

        div_train_val.append(kl_train_val)
        div_val_test.append(kl_val_test)
        div_train_test.append(kl_train_test)
        div_test_test.append(kl_test_test)

    div_train_val = torch.tensor(div_train_val)
    div_val_test = torch.tensor(div_val_test)
    div_train_test = torch.tensor(div_train_test)
    div_test_test = torch.tensor(div_test_test)
    print('*' * 20 + ' Inspect Datasets ' + '*' * 20)
    print(f'Featurewise KL divergence between TRAIN and VAL, '
          f'mean: {div_train_val.mean()}, std: {div_train_val.std()}')
    print(f'Featurewise KL divergence between VAL and TEST, '
          f'mean: {div_val_test.mean()}, std: {div_val_test.std()}')
    print(f'Featurewise KL divergence between TRAIN and TEST, '
          f'mean: {div_train_test.mean()}, std: {div_train_test.std()}')
    print(f'Featurewise KL divergence between TEST and TEST2, '
          f'mean: {div_test_test.mean()}, std: {div_test_test.std()}')

    # compare val train and test set
    t_value, p_value = stats.ttest_1samp(div_val_test,
                                         div_train_val.mean(),
                                         alternative='two-sided')
    print(f'Test statistic is {t_value}')
    print(f'p-value for two-sided test is {p_value}')
    alpha = 0.05
    if p_value <= alpha:
        print(f'Since p-value ({p_value}) < alpha ({alpha}),'
              ' reject null hypothesis (train/val and test not same).')
    else:
        print(f'Since p-value ({p_value}) > alpha ({alpha}), '
              'not rejecting null hypothesis.')

    # compare the two test sets
    t_value, p_value = stats.ttest_1samp(div_test_test,
                                         div_train_val.mean(),
                                         alternative='two-sided')
    print(f'Test statistic is {t_value}')
    print(f'p-value for two-sided test is {p_value}')
    alpha = 0.05
    if p_value <= alpha:
        print(f'Since p-value ({p_value}) < alpha ({alpha}),'
              ' reject null hypothesis (the test sets are not the same).')
    else:
        print(f'Since p-value ({p_value}) > alpha ({alpha}), '
              'not rejecting null hypothesis.')
    print('*'*40)


if __name__ == "__main__":
    base_path = Path(args.body_loc_path)
    train_path = base_path / 'strong_labels_train'
    test_path = base_path / 'strong_labels_test'
    test2_path = base_path / 'strong_labels_test_balanced510'

    # get device
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print("Running on:", device)

    # transformation for dataset
    transform = transforms.Compose([
        transforms.Resize(256, interpolation=3),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
    ])

    # Train / Val set
    body_loc_dataset = EncryptedImageFolder(
        train_path,
        enc_keys=[str(base_path / 'key.key')],
        transform=transform)
    body_loc_train, body_loc_val = get_train_validation_data_loaders(
        body_loc_dataset, 32, num_workers=10, val_size=0.2)
    # Test set
    body_loc_test = EncryptedImageFolder(
        test_path,
        enc_keys=[str(base_path / 'key.key')],
        transform=transform)
    body_loc_test = DataLoader(
        body_loc_test,
        batch_size=32,
        drop_last=False,
        shuffle=False)
    body_loc_test2 = EncryptedImageFolder(
        test2_path,
        enc_keys=[str(base_path / 'key.key')],
        transform=transform)
    body_loc_test2 = DataLoader(
        body_loc_test2,
        batch_size=32,
        drop_last=False,
        shuffle=False)

    # load a dummy model
    model = models.resnet50(pretrained=False)
    # ResNet Model without last layer
    model = torch.nn.Sequential(*list(model.children())[:-1])
    model = model.to(device)
    model.eval()

    # test assumption
    check_dataset_shift_assumption(model, body_loc_train, body_loc_val,
                                   body_loc_test, body_loc_test2, device)
