import numpy as np
from torch.utils.data import Dataset
from torch.utils.data.sampler import SubsetRandomSampler
from torch.utils.data import DataLoader


def get_train_validation_data_loaders(ds: Dataset,
                                      batch_size: int,
                                      num_workers: int,
                                      val_size: float):
    # obtain training indices that will be used for validation
    num_train = len(ds)
    indices = list(range(num_train))
    np.random.shuffle(indices)

    split = int(np.floor(val_size * num_train))
    train_idx, valid_idx = indices[split:], indices[:split]

    # define samplers for obtaining training and validation batches
    train_sampler = SubsetRandomSampler(train_idx)
    valid_sampler = SubsetRandomSampler(valid_idx)

    # create the train and val loaders
    train_loader = DataLoader(ds,
                              batch_size=batch_size,
                              sampler=train_sampler,
                              num_workers=num_workers,
                              drop_last=True,
                              shuffle=False)

    valid_loader = DataLoader(ds,
                              batch_size=batch_size,
                              sampler=valid_sampler,
                              num_workers=num_workers,
                              drop_last=True,
                              shuffle=False)

    return train_loader, valid_loader
