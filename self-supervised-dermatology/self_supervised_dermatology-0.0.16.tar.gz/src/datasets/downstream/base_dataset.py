import os
import sklearn
import sklearn.preprocessing
import pickle
from torch.utils.data import Dataset


class BaseDataset(Dataset):
    """Base class for datasets."""
    IMG_COL = 'image'
    LBL_COL = 'label'

    def __init__(self,
                 transform=None,
                 val_transform=None):
        """
        Initializes the dataset.

        Sets the correct path for the needed arguments.

        Parameters
        ----------
        transform : Union[callable, optional]
            Optional transform to be applied to the images.
        """
        self.training = True
        self.transform = transform
        self.val_transform = val_transform
        self.labelencoder = sklearn.preprocessing.LabelEncoder()

    def save_label_encoder(self, path: str):
        if self.labelencoder is not None:
            le_file_name = os.path.join(path, 'label_encoder.pickle')
            le_file = open(le_file_name, 'wb')
            pickle.dump(self.labelencoder, le_file)
            le_file.close()
