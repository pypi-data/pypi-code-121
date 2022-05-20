# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""The main module responsible for reading and loading the datasets."""

import sys
import random
import json
import warnings
import logging
import pandas as pd

from learner.validator.input_validator import remove_subset_list


class DataLoader:
    def __init__(self, conf=None):
        """The conf is an instance of the Configuration class. The df attribute can either hold a panda's dataframe
        once it's being loaded in memory or it can be a TextFileReader object."""

        self._conf = conf
        self.df = None
        self.meta_data = None
        self.train_nrows = self._conf.data.train_nrows
        self.validation_nrows = self._conf.data.validation_nrows
        self.skiprows = None

    @property
    def conf(self):
        return self._conf

    def connect_file(self, data_source, nrows=None, chunksize=None, dtype=None, usecols=None, sep=",", header=0, call_num=0, format="csv"):
        """Load data through a file location. The df attribute gets populated here. This method accepts a file format and
        then calls the relevant methods to load the data.

        :param data_source: the path to the data file
        :param nrows: number of rows of the file to read
        :param chunksize: the chunksize when iterating through the file, setting it will return a TextFileReader object
        :param dtype: a dictionary containing the dtypes
        :param usecols: a list of columns that should be used when loading the data
        :param call_num: call number for the attempts to load the data. This is used to avoid infinite recursion
        :param format: the format of the file - the supported formats are: csv, parquet, and feather
        :return: None
        """
        if format == "csv":
            self.connect_csv(data_source, nrows, chunksize, dtype, usecols, sep, header, call_num)
        elif format == "parquet":
            self.connect_parquet(data_source, usecols)
        elif format == "feather":
            self.connect_feather(data_source, usecols)
        # we should never get here as long as configuration file is validated
        else:
            logging.critical("Unknown file format. Exiting...")
            sys.exit(1)

    def connect_csv(self, data_source, nrows=None, chunksize=None, dtype=None, usecols=None, sep=",", header=0, call_num=0):
        """Load data from a csv file. If the dtype is populated, we'll try to load the data using those dtypes. If we
        fail to lead the data, we'll ignore the dtype and make a second attempt.

        :param data_source: the path to the data file
        :param nrows: number of rows of the file to read
        :param chunksize: the chunksize when iterating through the file, setting it will return a TextFileReader object
        :param dtype: a dictionary containing the dtypes
        :param usecols: a list of columns that should be used when loading the data
        :param call_num: call number for the attempts to load the data. This is used to avoid infinite recursion
        :return: None
        """
        try:
            # try to load with dtypes if it's being asked
            self.df = pd.read_csv(data_source
                                  , sep=sep
                                  , names=self._conf.column.all_cols
                                  , nrows=nrows
                                  , header=header
                                  , usecols=usecols
                                  , skiprows=self.skiprows
                                  , chunksize=chunksize
                                  , dtype=dtype)

            logging.info("Successfully loaded the data")
        except Exception as e:
            if call_num > 0:
                logging.critical("The second attempt for loading data was unsuccessful. Exiting...")
                sys.exit(1)
            logging.error("Loading the data failed, trying to load the data with updated parameters. The error is: '%s'",
                          str(e))
            # increment call_num to avoid infinite recursion (call_num+1)
            self.connect_csv(data_source, nrows=nrows, usecols=usecols, sep=sep, header=header, call_num=call_num + 1)

    def connect_parquet(self, data_source, usecols=None, engine="pyarrow", call_num=0):
        """Load the data from a parquet file.

        :param data_source: the path to the data file
        :param usecols: a list of columns that should be used when loading the data
        :return: None
        """
        try:
            self.df = pd.read_parquet(data_source,
                                      columns=usecols,
                                      engine=engine)

            logging.info("Successfully loaded the data")
        except Exception as e:
            if call_num > 0:
                logging.critical("The second attempt for loading data was unsuccessful. Exiting...")
                sys.exit(1)
            logging.error(f"Loading the data failed, trying to load the data with updated parameters. The error is: {str(e)}")
            self.connect_parquet(data_source, usecols=usecols, engine="fastparquet", call_num=call_num + 1)  # we change the engine if we fail

    def connect_feather(self, data_source, usecols=None):
        """Load the data from a feather file.

        :param data_source: the path to the data file
        :param usecols: a list of columns that should be used when loading the data
        :return: None
        """
        try:
            self.df = pd.read_feather(data_source,
                                      columns=usecols)

            logging.info("Successfully loaded the data")
        except Exception as e:
            logging.error(f"Loading the data failed. The error is: {str(e)}")
            sys.exit(1)

    def connect_presto(self, query, chunksize=None):
        """Execute a query and load the results into a pandas dataframe from a presto/hive table

        :param query: a string of query to be executed.
        :param chunksize: if specified, return an iterator where chunksize is the number of rows to include in each chunk
        :return: a pandas dataframe or a generator
        """
        try:
            with self.conf.connection.presto_client.connect() as con:
                self.df = pd.read_sql(query, con=con, chunksize=chunksize)
        except Exception as e:
            logging.critical(f"Loading the data from presto failed. The error is: {str(e)}")
            sys.exit(1)

    def connect_postgres(self, query, chunksize=None):
        """Execute a query and load the results into a pandas dataframe from a postgres table

        :param query: a string of query to be executed.
        :param chunksize: if specified, return an iterator where chunksize is the number of rows to include in each chunk
        :return: a pandas dataframe or a generator
        """
        try:
            with self.conf.connection.postgres_client.connect() as con:
                self.df = pd.read_sql(query, con=con, chunksize=chunksize)
        except Exception as e:
            logging.critical(f"Loading the data from postgres failed. The error is: {str(e)}")
            sys.exit(1)

    def connect_mysql(self, query, chunksize=None):
        """Execute a query and load the results into a pandas dataframe from a mysql table

        :param query: a string of query to be executed.
        :param chunksize: if specified, return an iterator where chunksize is the number of rows to include in each chunk
        :return: a pandas dataframe or a generator
        """
        try:
            with self.conf.connection.mysql_client.connect() as con:
                self.df = pd.read_sql(query, con=con, chunksize=chunksize)
        except Exception as e:
            logging.critical(f"Loading the data from mysql failed. The error is: {str(e)}")
            sys.exit(1)

    def connect_snowflake(self, query, chunksize=None):
        """Execute a query and load the results into a pandas dataframe from a snowflake table

        :param query: a string of query to be executed.
        :param chunksize: if specified, return an iterator where chunksize is the number of rows to include in each chunk
        :return: a pandas dataframe or a generator
        """
        try:
            with self.conf.connection.snowflake_client.connect() as con:
                self.df = pd.read_sql(query, con=con, chunksize=chunksize)
        except Exception as e:
            logging.critical(f"Loading the data from snowflake failed. The error is: {str(e)}")
            sys.exit(1)

    def load_train_data(self):
        """Load the training data by calling the appropriate methods.

        :return: pandas dataframe
        """
        logging.info("Loading the training data...")
        if self._conf.data.train_location:
            return self.load_train_from_file()
        elif self._conf.data.train_query_activate:
            return self.load_train_from_db()

    def load_validation_data(self):
        """Load the validation data by calling the appropriate methods.

        :return: pandas dataframe
        """
        logging.info("Loading the validation data...")
        if self._conf.data.validation_location:
            return self.load_validation_from_file()
        elif self._conf.data.validation_query_activate:
            return self.load_validation_from_db()

    def load_test_data(self):
        """Get a pointer to the test data so that we can iterate through the chunks.

        :return: a generator
        """
        logging.info("Loading the test data...")
        if self._conf.data.test_location:
            return self.load_test_from_file()
        elif self._conf.data.test_query_activate:
            return self.load_test_from_db(chunksize=self._conf.data.test_chunksize)

    def load_train_from_file(self):
        """If we need to load training data from a file, decide how to load the data and call connect_file to get them.

        :return: a pandas dataframe containing the training data
        """
        if self._conf.column.dtype_activate:
            logging.info("Loading the data using dtypes...")
            # update the dtype dictionary by doing a trial run
            self._conf.column.dtype_dict = self.update_dtype_dict(self._conf.data.train_location,
                                                                  dtype_trial_nrows=self._conf.column.dtype_trial_nrows)

        if self._conf.data.train_sample_size and self._conf.data.train_format == "csv":
            logging.info("Sampling %i rows from the train dataset...", self._conf.data.train_sample_size)
            self.train_nrows = self.get_file_num_rows(self._conf.data.train_location)

            if self._conf.data.train_sample_size >= self.train_nrows:
                warnings.warn("The sample size is greater than the number of rows in the dataset. The entire "
                              "dataset will be used for training...", Warning)
            else:
                self.skiprows = self.get_skiprows(self.train_nrows)

        self.connect_file(self._conf.data.train_location,
                          nrows=self.train_nrows,
                          dtype=self._conf.column.dtype_dict,
                          usecols=self._conf.column.use_cols,
                          sep=self._conf.data.train_delimiter,
                          header=self._conf.data.train_header,
                          format=self._conf.data.train_format
                          )

        # reset indices if we've skipped rows
        if self.skiprows:
            self.df.reset_index(drop=True, inplace=True)

        if self._conf.data.train_sample_size and self._conf.data.train_format != "csv":
            logging.info("Sampling %i rows from the train dataset...", self._conf.data.train_sample_size)
            self.df = self.df.sample(n=self._conf.data.train_sample_size,
                                     replace=False,
                                     random_state=self._conf.data.train_sample_seed)
            # the newer version of pandas has the option "ignore_index", we can update when we use the newer versions
            self.df.reset_index(drop=True, inplace=True)

        return self.df

    def load_validation_from_file(self):
        """If we need to load validation data from a file, decide how to load the data and call connect_file to get them.

        :return: a pandas dataframe containing the validation data
        """
        if self._conf.column.dtype_activate:
            logging.info("Loading the data using dtypes...")
            # update the dtype dictionary by doing a trial run
            self._conf.column.dtype_dict = self.update_dtype_dict(self._conf.data.validation_location,
                                                                  dtype_trial_nrows=self._conf.column.dtype_trial_nrows)

        if self._conf.data.validation_sample_size and self._conf.data.validation_format == "csv":
            logging.info("Sampling %i rows from the validation dataset...", self._conf.data.validation_sample_size)
            self.validation_nrows = self.get_file_num_rows(self._conf.data.validation_location)

            if self._conf.data.validation_sample_size >= self.validation_nrows:
                warnings.warn("The sample size is greater than the number of rows in the dataset. The entire "
                              "dataset will be used for training...", Warning)
            else:
                self.skiprows = self.get_skiprows(self.validation_nrows)

        self.connect_file(self._conf.data.validation_location,
                          nrows=self.validation_nrows,
                          dtype=self._conf.column.dtype_dict,
                          usecols=self._conf.column.use_cols,
                          sep=self._conf.data.validation_delimiter,
                          header=self._conf.data.validation_header,
                          format=self._conf.data.validation_format
                          )

        # reset indices if we've skipped rows
        if self.skiprows:
            self.df.reset_index(drop=True, inplace=True)

        if self._conf.data.validation_sample_size and self._conf.data.validation_format != "csv":
            logging.info("Sampling %i rows from the validation dataset...", self._conf.data.validation_sample_size)
            self.df = self.df.sample(n=self._conf.data.validation_sample_size,
                                     replace=False,
                                     random_state=self._conf.data.validation_sample_seed)
            # the newer version of pandas has the option "ignore_index", we can update when we use the newer versions
            self.df.reset_index(drop=True, inplace=True)

        return self.df

    def load_test_from_file(self, **kwargs):
        """If we need to get the test data from a file, call connect_file with chunksize to get a TextFileReader object.

        :return: a TextFileReader object from pandas
        """
        self.connect_file(self._conf.data.test_location,
                          nrows=self._conf.data.test_nrows,
                          chunksize=kwargs["chunksize"] if "chunksize" in kwargs else self._conf.data.test_chunksize,
                          usecols=remove_subset_list(self._conf.column.use_cols, [self._conf.column.target_col]),
                          sep=self._conf.data.test_delimiter,
                          header=self._conf.data.test_header,
                          format=self._conf.data.test_format)

        return self.df

    def load_train_from_db(self):
        """If we need to load the training data from a table, check what type of db we need to connect to and then call
        the appropriate method to ge the data. Once we obtain the data, make sure we only keep the columns defined in use_cols.

        :return: a pandas dataframe
        """
        if self._conf.data.train_db_type == "presto":
            self.connect_presto(self._conf.data.train_query)
        elif self._conf.data.train_db_type == "postgres":
            self.connect_postgres(self._conf.data.train_query)
        elif self._conf.data.train_db_type == "mysql":
            self.connect_mysql(self._conf.data.train_query)
        elif self._conf.data.train_db_type == "snowflake":
            self.connect_snowflake(self._conf.data.train_query)

        if self._conf.column.use_cols:
            # only keep the columns in use columns
            self.df = self.df[self._conf.column.use_cols]

        return self.df

    def load_validation_from_db(self):
        """If we need to load the validation data from a table, check what type of db we need to connect to and then call
        the appropriate method to ge the data. Once we obtain the data, make sure we only keep the columns defined in use_cols.

        :return: a pandas dataframe
        """
        if self._conf.data.validation_db_type == "presto":
            self.connect_presto(self._conf.data.validation_query)
        elif self._conf.data.validation_db_type == "postgres":
            self.connect_postgres(self._conf.data.validation_query)
        elif self._conf.data.validation_db_type == "mysql":
            self.connect_mysql(self._conf.data.validation_query)
        elif self._conf.data.validation_db_type == "snowflake":
            self.connect_snowflake(self._conf.data.validation_query)

        if self._conf.column.use_cols:
            # only keep the columns in use columns
            self.df = self.df[self._conf.column.use_cols]

        return self.df

    def load_test_from_db(self, chunksize=None):
        """If we need to load the test data from a table, check what type of db we need to connect to and then call
        the appropriate method to ge the data. The chunksize can be passed as a parameter here. The reason is that, this
        method can be used to get a TextFileReader object or the actual data. We may need to get the actual data, if the
        user needs to save the query data or wants to use query along with segmentation.

        :param chunksize: the chunksize for getting the data
        :return: A TextFileReader object or the loaded pandas dataframe.
        """

        if self._conf.data.test_db_type == "presto":
            self.connect_presto(self._conf.data.test_query, chunksize=chunksize)
        elif self._conf.data.test_db_type == "postgres":
            self.connect_postgres(self._conf.data.test_query, chunksize=chunksize)
        elif self._conf.data.test_db_type == "mysql":
            self.connect_mysql(self._conf.data.test_query, chunksize=chunksize)
        elif self._conf.data.test_db_type == "snowflake":
            self.connect_snowflake(self._conf.data.test_query, chunksize=chunksize)

        return self.df

    def update_dtype_dict(self, data_source, dtype_trial_nrows=200000):
        """Update dtype_dict through a trial load.

        :param data_source: path to the data
        :param dtype_trial_nrows: the number of rows to be used for the trial run
        :return: an updated dtype_dict
        """
        # do trial loading of data to remove cols with incorrect dtypes
        logging.info("Checking if dtype_dict is valid. dtype_dict will be updated for invalid types...")
        for col in self._conf.column.use_cols:
            if col in self._conf.column.dtype_dict:
                try:
                    pd.read_csv(data_source,
                                sep=self._conf.data.delimiter,
                                names=self._conf.column.all_cols,
                                nrows=dtype_trial_nrows,
                                header=self._conf.data.header,
                                usecols=[col],
                                dtype=self._conf.column.dtype_dict[col])
                except Exception as e:
                    del self._conf.column.dtype_dict[col]
                    logging.info("Deleting %s from dtype_dict due to incorrect type. The error is: '%s'", col, str(e))

        return self._conf.column.dtype_dict

    def get_file_num_rows(self, location):
        """Get the number of rows in a dataset by reading one column from the file.

        :return: number of rows in a dataset
        """
        logging.info("Getting the total number of rows in the dataset...")
        file = pd.read_csv(location,
                           delimiter=self._conf.data.train_delimiter,
                           usecols=[0],
                           header=self._conf.data.train_header,
                           skip_blank_lines=False)

        # add 1 to file_num_rows if the dataset doesn't have a header row because we are assuming one of the rows does
        # not contain data
        if self._conf.data.manifest:
            file_num_rows = file.shape[0] + 1
        else:
            file_num_rows = file.shape[0]

        logging.info("The dataset has %i rows", file_num_rows)
        return file_num_rows

    def get_skiprows(self, file_num_rows):
        """Use the number of rows in a data set and the sample size to return the rows numbers that should be skipped
        when reading a data set. This value is then passed to the pandas reader.

        :return: a list of indices that should be skipped
        """
        # randomly select the row numbers that should NOT be loaded (we do this because panda provide the functionality
        # for it). We sample (file_num_rows - sample_size) numbers from the total number of rows in the file.
        # for example if there are 100 rows in the data set and we want to sample 30 rows. We randomly select 70 rows
        # that should be skipped
        random.seed(a=self._conf.data.train_sample_seed)
        return sorted(random.sample(range(self._conf.data.train_header + 1, file_num_rows),
                                    file_num_rows - self._conf.data.train_sample_size))


def get_data(data_source, manifest_file=None, format="csv", **kwargs):
    """Load a dataset and return a pandas dataframe. This function supports multiple file formats including csv, parquet,
    and feather.

    :param data_source: the path to the dataset
    :param manifest_file: the path to a manifest file if it exists
    :param format: the format of the file. The supported formats are: csv, parquet, and feather
    :param kwargs: the kwargs that should be passed to read_csv
    :return: a pandas dataframe
    """
    if manifest_file:
        idx, cols = get_index_cols_from_manifest(manifest_file, kwargs["usecols"])
        kwargs['names'] = cols
        kwargs['usecols'] = idx
        kwargs['header'] = None

    if format == "csv":
        data = pd.read_csv(data_source, **kwargs)
    elif format == "parquet":
        data = pd.read_parquet(data_source, columns=kwargs["usecols"])
        # if we have the manifest, we plugin the names here
        if "names" in kwargs:
            data.columns = kwargs["names"]
    elif format == "feather":
        data = pd.read_feather(data_source, columns=kwargs["usecols"])
        # if we have the manifest, we plugin the names here
        if "names" in kwargs:
            data.columns = kwargs["names"]
    else:
        logging.critical("Unknown data type. Exiting...")
        sys.exit(1)
    return data


def get_indices_for_value(data, col, value):
    """Get the indices of a dataframe corresponding to a value in a specific column.

    :param data: a pandas dataframe
    :param col: a column name to perform the filtering on. This should be a string
    :param value: the value to be used for filtering the data set
    :return: a numpy array that contains the indices corresponding to value
    :raises TypeError: if an incorrect type for col is passes, e.g, list instead of string
    """
    if isinstance(col, str) is False:
        logging.error("get_indices_for_value accept a string, not %s", type(col))
        raise TypeError()
    indices = data[data[col] == value].index.values
    return indices


def get_index_cols_from_manifest(manifest_file, usecols):
    """Get the indices and the corresponding column names using a manifest file. This function returns the correct order
    of column names if the usecols passed by user does not match the sequence of the column names in manifest.
    This function assumes the manifest file contain the correct sequence for the column names.

    :param manifest_file: a manifest file that contains column names. Each row in this file contains the name of a single column
    :param usecols: a list of column names, which should be used to get the indices
    :return: a list of indices and a list of column names in the right order
    """
    with open(manifest_file, 'r') as file:
        cols = [x.strip() for x in file.readlines()]
        if usecols:
            idx = [cols.index(c) for c in cols if c in usecols]
        else:
            idx = [cols.index(c) for c in cols]
    # loop through the indices and retrieve a list of column names
    selected_cols = [cols[i] for i in idx]
    return idx, selected_cols


def get_meta_data(meta_data_path):
    """Get the meta data loaded from the meta file listed in the config

    :param meta_data_path: path of json or csv file to the meta data file to open
    :return: a dictionary containing meta data
    """
    try:
        with open(meta_data_path) as f:
            meta_data = json.load(f)
        return meta_data
    except json.decoder.JSONDecodeError:
        logging.exception("Decoding meta data json file has failed. Check the formatting of the json file")
        raise


def get_file_num_rows(location, **kwargs):
    """Get the number of rows in a dataset by reading one column from the file.
    Note: this function only works for datasets that contain a header row. This function is typically used for
    validating the output files generated by Learner.

    :param location: location of file to retrieve number of rows
    :param kwargs: parameters used by pandas read_csv function
    :return: number of rows in a dataset
    """
    file = pd.read_csv(location,
                       usecols=[0],
                       skip_blank_lines=False,
                       **kwargs)

    file_num_rows = file.shape[0]

    return file_num_rows


def get_dtype_dict(meta_data, use_cols, col_dtypes):
    """Get column dtypes from either meta_data or configuration file (priority)

    :param meta_data: a meta_data file
    :param use_cols: the use_cols for loading the data
    :param col_dtypes: the col_dtype dictionary from the configuration file
    :return: the updated dtype_dict
    """
    # initialize dtype_dict from configuration file and meta data file
    dtype_dict = {}
    if meta_data:
        for col in meta_data['column']:
            if col in use_cols:
                try:
                    dtype_dict[col] = meta_data['column'][col]['dtype']
                except KeyError:
                    logging.info("The col %s exists in meta_data file but doesn't include dtype...", col)

    if col_dtypes:
        for col in col_dtypes:
            dtype_dict[col] = col_dtypes[col]
    return dtype_dict


def get_value(dictionary, default_value, *keys):
    """Get the value from a single- or multi-level (nested) dictionary using a series of keys. If the value does not
    exist, return the default_value.

    :param dictionary: a single- or multi-level dictionary
    :param default_value: return this value if no value exist
    :param keys: a chain of keys pointing towards the value needed
    """
    tmp = dictionary
    for key in keys:
        if isinstance(tmp, dict):
            try:
                tmp = tmp[key]
            except KeyError:
                return default_value
    return tmp
