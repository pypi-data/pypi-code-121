from abc import ABC, abstractmethod

import numpy as np


class DataLoader(ABC):
    """The DataLoader module is for user to map arbitrary data source to form that the environment can recognize.
    """    
    _features: list
    _idx: int
    _transaction_fee: np.array = None
    _transaction_fee_type: str = None

    @abstractmethod
    def __init__(self, start_idx, end_idx):
        """__init__

        Args:
            start_idx (int): Start index
            end_idx (int): End index
        """        
        super(DataLoader, self).__init__()
        self._start_idx = start_idx,
        self._end_idx = end_idx

    def __iter__(self):
        """This object is iterable. See https://www.w3schools.com/python/python_iterators.asp for more details.
        """        
        return self

    def get_transaction_fee_type(self):
        """Return the name of transaction fee type

        Returns:
            str
        """        
        return self._transaction_fee_type

    def get_transaction_fee(self, idx=None):
        """Return the transaction fee list

        Args:
            idx (int, optional): Number of transaction fee to return. Defaults to None.

        Returns:
            list
        """        
        if idx is None:
            return self._transaction_fee[self._idx]
        return self._transaction_fee[idx]

    def load_transaction_fee(self, values, fee_type='percentage'):
        """Load the transaction fee list

        Args:
            values (list): Transaction fee list
            fee_type (str, optional): 'percentage' or 'fix'. Defaults to 'percentage'.
        """        
        if not (fee_type == 'percentage' or fee_type == 'fix'):
            raise ValueError("fee_type should be 'fix' or 'percentage'.")

        record_length = len(self)
        values = np.array(values, dtype=np.float32)
        # sanity check
        values_len = values.shape[0]
        if values_len != record_length:
            raise ValueError(f"The length of input should be "
                             f"identical to the length of record. Got {values_len}, "
                             f"but the length of record is {record_length}.")
        self._transaction_fee = values
        self._transaction_fee_type = fee_type

    @abstractmethod
    def __next__(self):
        """See https://www.w3schools.com/python/python_iterators.asp for more details
        """        
        raise NotImplementedError()

    @abstractmethod
    def __len__(self):
        """Return the length of the iterable

        Raises:
            NotImplementedError
        """        
        raise NotImplementedError()

    @abstractmethod
    def reset(self):
        """Reset the dataloader

        Raises:
            NotImplementedError
        """        
        raise NotImplementedError()
    
    def get_idx(self):
        """Get current index

        Raises:
            NotImplementedError
        """        
        raise NotImplementedError()

    @abstractmethod
    def get_feature(self, feature_name):
        """Get input variables (features)

        Args:
            feature_name (str): name of the feature

        Raises:
            NotImplementedError
        """        
        raise NotImplementedError()

    @abstractmethod
    def get_duration(self):
        """Get length of the data source.

        Raises:
            NotImplementedError
        """        
        raise NotImplementedError()

    @property
    def idx(self):
        return self._idx
