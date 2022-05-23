import os

import numpy as np

from kolibri.data.text.base_stream import BaseStream
from kolibri.data.text.format import read_csv, read_conll

class FileStream(BaseStream):
    """ FileStream
    A stream generated from the entries of a file.
    """
    _CLASSIFICATION = 'classification'
    _REGRESSION = 'regression'

    def __init__(self, filepath, content_col, target_idx=-1, target_cols=None, filetype='csv'):
        super().__init__()
        self.filename = ''
        self.X = None
        self.y = None
        self.content_column = content_col
        if not isinstance(target_cols, list):
            target_cols = [target_cols]
        self.target_columns = target_cols
        self.task_type = None
        self.n_classes = 0
        self.target_idx = target_idx
        self.filepath = filepath
        self.filename = ''
        self.basename = ''
        self.filetype = filetype
        if target_cols:
            self.n_targets = len(target_cols)
        # Automatically infer target_idx if not passed in multi-output problems
        if self.n_targets > 1 and self.target_idx == -1:
            self.target_idx = -self.n_targets

        self.min_class_count = 0

        self.__configure()

    def __configure(self):
        self.basename = os.path.basename(self.filepath)
        filename, extension = os.path.splitext(self.basename)
        if self.filetype == 'csv':
            self.read_function = read_csv
        elif self.filetype == 'conll':
            self.read_function = read_conll
        else:
            raise ValueError('Unsupported format: ', extension)
        self.filename = filename

    @property
    def target_idx(self):
        """
        Get the number of the column where Y begins.
        Returns
        -------
        int:
            The number of the column where Y begins.
        """
        return self._target_idx

    @target_idx.setter
    def target_idx(self, target_idx):
        """
        Sets the number of the column where Y begins.
        Parameters
        ----------
        target_idx: int
        """

        self._target_idx = target_idx

    @property
    def n_targets(self):
        """
         Get the number of targets.
        Returns
        -------
        int:
            The number of targets.
        """
        return self._n_targets

    @n_targets.setter
    def n_targets(self, n_targets):
        """
        Sets the number of targets.
        Parameters
        ----------
        n_targets: int
        """

        self._n_targets = n_targets

    @property
    def cat_features_idx(self):
        """
        Get the list of the categorical features index.
        Returns
        -------
        list:
            List of categorical features index.
        """
        return self._cat_features_idx

    @cat_features_idx.setter
    def cat_features_idx(self, cat_features_idx):
        """
        Sets the list of the categorical features index.
        Parameters
        ----------
        cat_features_idx:
            List of categorical features index.
        """

        self._cat_features_idx = cat_features_idx

    def prepare(self, min_class_count=0, **kwargs):
        """ prepare_for_use
        Prepares the stream for use. This functions should always be
        called after the stream initialization.
        """

        if min_class_count >0:
            if isinstance(min_class_count, int):
                self.min_class_count = min_class_count
            else:
                print("'min_class_count', should be an integer. It will not be taken into account.")
        self._load_data(**kwargs)
        self.sample_idx = 0
        self.current_sample_x = None
        self.current_sample_y = None

    def _load_data(self, **kwargs):
        try:
            if kwargs is None:
                kwargs={'file_type': self.filetype}
            else:
                kwargs['file_type']=self.filetype

            raw_data = self.read_function(self.filepath, **kwargs)
            self.n_samples = 0
            for line in raw_data:
                if self.content_column is None:
                    self.content_column=[k for k in line if k not in self.target_columns]
                self.n_samples += 1
                if self.filetype == 'conll':
                    for token in line:
                        if self.n_targets == 1:
                            self.target_values.append(token[self.target_columns[0]])
                        else:
                            self.target_values.append([token[self.target_columns[i]] for i in range(self.n_targets)])

                else:
                    if self.n_targets == 1:
                        self.target_values.append(line[self.target_columns[0]])
                    else:
                        self.target_values.append([line[self.target_columns[i]] for i in range(self.n_targets)])

            targets, counts = np.unique(self.target_values, return_counts=True)
            self.target_values_statistics = dict(zip(targets, counts))
            self.target_values = [k for k, v in self.target_values_statistics.items() if v >= self.min_class_count]
            skipped_classes= [k for k, v in self.target_values_statistics.items() if v < self.min_class_count]

            if skipped_classes:
                print("The following classe will be excluded")
                for c in skipped_classes:
                    print(c)

            if np.issubdtype(np.array(self.target_values).dtype, np.integer) or np.issubdtype(
                    np.array(self.target_values).dtype, np.object):
                self.task_type = self._CLASSIFICATION
                self.n_classes = len(self.target_values)
            else:
                self.task_type = self._REGRESSION

            self.raw_data = self.read_function(self.filepath, **kwargs)

        except FileNotFoundError:
            raise FileNotFoundError("File {} does not exist.".format(self.filepath))
        pass

    def restart(self):
        """ restart
        Restarts the stream's sample feeding, while keeping all of its
        parameters.
        It basically server the purpose of reinitializing the stream to
        its initial state.
        """
        self.sample_idx = 0
        self.raw_data = self.read_function(self.filepath)
        self.current_sample_x = None
        self.current_sample_y = None

    def get_data(self, nb_samples=None):
        X = []
        Y = []
        if nb_samples:
            current_size = 0
            for x, y in self:
                X.append(x)
                Y.append(y)
                if current_size >= nb_samples:
                    break
                current_size += 1

        else:
            for x, y in self:
                if y[0] in self.target_values:
                    X.append(x)
                    Y.append(y)

        return X, Y

    def get_next_documents(self, batch_size=1):

        self.current_documents = []
        self.sample_idx += batch_size
        for i, d in enumerate(self):
            if (i % batch_size == 0 and i > 0):
                return self.current_documents
            self.current_documents.append(Document(text=d[0], target=d[1]))

        return self.current_documents

    def get_all_documents(self):
        return [Document(text=x, target=y) for x, y in self]

    def next(self, batch_size=1):
        """ next_sample
        If there is enough instances to supply at least batch_size samples, those
        are returned. If there aren't a tuple of (None, None) is returned.
        Parameters
        ----------
        batch_size: int
            The number of instances to return.
        Returns
        -------
        tuple or tuple list
            Returns the next batch_size instances.
            For general purposes the return can be treated as a numpy.ndarray.
        """
        self.current_sample_x = []
        self.current_sample_y = []
        self.sample_idx += batch_size
        for i, d in enumerate(self):
            if (i % batch_size == 0 and i > 0):
                return self.current_sample_x, self.current_sample_y
            self.current_sample_x.append(d[0])
            self.current_sample_y.append(d[1])

        return self.current_sample_x, self.current_sample_y

    def __iter__(self):

        for d in self.raw_data:
            if self.n_targets == 1:
                if d[self.target_columns[0]] not in self.target_values:
                    continue
                if isinstance(self.content_column, list):
                    yield [d[k] for k in self.content_column], d[self.target_columns[0]]
                else:
                    yield d[self.content_column], d[self.target_columns[0]]

            elif self.n_targets > 1:
                if isinstance(self.content_column, list):
                    yield  [d[k] for k in self.content_column], [d[self.target_columns[i]] for i in range(self.n_targets)]

                else:
                    yield d[self.content_column], [d[self.target_columns[i]] for i in range(self.n_targets)]

    def has_more_samples(self):
        """ Checks if stream has more samples.
        Returns
        -------
        Boolean
            True if stream has more samples.
        """
        return (self.n_samples - self.sample_idx) > 0

    def n_remaining_samples(self):
        """ Returns the estimated number of remaining samples.
        Returns
        -------
        int
            Remaining number of samples.
        """
        return self.n_samples - self.sample_idx

    def print_df(self):
        """
        Prints all the samples in the stream.
        """
        print(self.X)
        print(self.y)

    def get_data_info(self):
        if self.task_type == self._CLASSIFICATION:
            return "{} - {} label(s), {} classes".format(self.basename, self.n_targets, self.n_classes)
        elif self.task_type == self._REGRESSION:
            return "{} - {} label(s)".format(self.basename, self.n_targets)

    def get_info(self):
        return 'File Stream: filename: ' + str(self.basename) + \
               '  -  n_targets: ' + str(self.n_targets)

    def save_to_directory(self, dir):

        file_name = os.path.join(dir, 'consumers-catgories.txt')
        with open(file_name, 'w') as f:
            for l in self.target_values:
                f.write(l + '\n')
