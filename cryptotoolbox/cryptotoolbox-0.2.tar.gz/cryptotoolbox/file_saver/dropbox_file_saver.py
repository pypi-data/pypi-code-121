"""Upload the contents of your Downloads folder to Dropbox.
This is an example app for API v2.
"""

from __future__ import print_function

import contextlib
import datetime
import os
import time
import pandas as pd
import numpy as np
import dropbox
from pathlib import Path
from io import StringIO

import pickle

@contextlib.contextmanager
def stopwatch(message):
    """Context manager to print how long a block of code took."""
    t0 = time.time()
    try:
        yield
    finally:
        t1 = time.time()
        print('Total elapsed time for %s: %.3f' % (message, t1 - t0))

class NaPoleonDropboxConnector(object):
    def __init__(self, drop_token='',overwrite = True, dropbox_backup = True):
        self.drop_token = drop_token
        self.dbx = dropbox.Dropbox(self.drop_token)
        self.overwrite = overwrite
        self.dropbox_backup = dropbox_backup

    def download_pkl(self,pkl_file_name = ''):
        bytes_data_pkl = self.download('', '', pkl_file_name)
        #string_data_csv = StringIO(str(bytes_data_csv, 'utf-8'))
        deserialized = pickle.loads(bytes_data_pkl)
        #pickle.load(bytes_data_pkl, encoding='latin-1')
        return deserialized

    def download_pkl5(self,pkl_file_name = ''):
        bytes_data_pkl = self.download('', '', pkl_file_name)
        #string_data_csv = StringIO(str(bytes_data_csv, 'utf-8'))
        import pickle5 as pickle5
        deserialized = pickle5.loads(bytes_data_pkl)
        return pickle5

    def download_csv(self, csv_file_name = '', sep = ',', index_date = False):
        bytes_data_csv = self.download('', '', csv_file_name)
        string_data_csv = StringIO(str(bytes_data_csv, 'utf-8'))
        dataframe = pd.read_csv(string_data_csv, sep=sep)
        if index_date:
            if not 'date' in list(dataframe.columns):
                try:
                    dataframe = dataframe.rename(columns={"Unnamed: 0": "date"}, errors="raise")
                except:
                    dataframe = dataframe.rename(columns={"datetime": "date"}, errors="raise")
            dataframe['date'] = pd.to_datetime(dataframe['date'])
            dataframe = dataframe.sort_values(by=['date'])
            dataframe = dataframe.set_index(dataframe['date'])
            dataframe = dataframe.drop(columns=['date'])
        return dataframe

    def uploadFileToDropbox(self, filename='', dropbox_subfolder = '', fullpath=''):
        self.upload(fullname=fullpath, folder='', subfolder=dropbox_subfolder, name=filename, overwrite=self.overwrite)

    def local_sqlite_overwrite_from_db(self,folder='', subfolder='', sqlite_file_name='',local_root_directory=''):
        res = self.download(folder=folder, subfolder=subfolder, name=sqlite_file_name)
        local_root_directory=Path(local_root_directory)
        local_sqlite_path = local_root_directory/subfolder/sqlite_file_name
        print('overwriting local file ' + str(local_sqlite_path) + ' with dropbox file ', sqlite_file_name)
        f = open(local_sqlite_path, 'wb')
        f.write(res)
        f.close()

    def local_overwrite_and_load_pickle(self, folder='', subfolder='', returns_pkl_file_name='', local_root_directory = ''):
        local_root_directory = Path(local_root_directory)
        local_returns_pkl_path = local_root_directory/subfolder/returns_pkl_file_name
        print('overwriting local file ' + str(local_returns_pkl_path) + ' with dropbox file')
        if self.dropbox_backup:
            res = self.download(folder = folder,subfolder= subfolder, name = returns_pkl_file_name)
            f = open(local_returns_pkl_path, 'wb')
            f.write(res)
            f.close()
        print('loading overwritting local returns pickle file reading ' + str(local_returns_pkl_path))
        df = pd.read_pickle(local_returns_pkl_path)
        return df

    def local_features_npy_ovverwrite_and_load_array(self, starting_date = None, ending_date = None, feature_type=None,
                                           n_past_features=None, local_root_directory='', user='',
                                           features_saving_suffix='', features_names_saving_suffix='',shortcut_features_saving_suffix = '',shortcut_features_names_saving_suffix=''):
        features_file_name = starting_date.strftime('%d_%b_%Y')+'_'+ending_date.strftime('%d_%b_%Y') +'_'+user + '_' + feature_type.name + '_' + str(n_past_features) + features_saving_suffix
        local_root_directory = Path(local_root_directory)
        features_full_path = local_root_directory/features_file_name

        if self.dropbox_backup:
            res_feat = self.download(folder='', subfolder='', name=features_file_name)
            f = open(features_full_path, 'wb')
            f.write(res_feat)
            f.close()
        features = np.load(features_full_path)
        features_names_file_names = user + '_' + feature_type.name + '_' + str(
            n_past_features) + features_names_saving_suffix
        features_names_full_path = local_root_directory/features_names_file_names
        if self.dropbox_backup:
            res_feat_names = self.download(folder='', subfolder='', name=features_names_file_names)
            f = open(features_names_full_path, 'wb')
            f.write(res_feat_names)
            f.close()
        features_names = np.load(features_names_full_path)

        shortcut_features_pkl_file_name = starting_date.strftime('%d_%b_%Y') + '_' + ending_date.strftime(
            '%d_%b_%Y') + '_' + user + shortcut_features_saving_suffix


        shortcut_features_file_full_path = local_root_directory/shortcut_features_pkl_file_name
        if self.dropbox_backup:
            res_feat = self.download(folder='', subfolder='', name=shortcut_features_pkl_file_name)
            f = open(shortcut_features_file_full_path, 'wb')
            f.write(res_feat)
            f.close()

        shortcut_features = np.load(shortcut_features_file_full_path)


        shortcut_features_names_file_names = user+shortcut_features_names_saving_suffix
        shortcut_features_names_full_path = local_root_directory/shortcut_features_names_file_names
        if self.dropbox_backup:
            res_feat_names = self.download(folder='', subfolder='', name=shortcut_features_names_file_names)
            f = open(features_names_full_path, 'wb')
            f.write(res_feat_names)
            f.close()
        shortcut_features_names = np.load(shortcut_features_names_full_path)

        return features, features_names, shortcut_features, shortcut_features_names

    def local_supervision_npy_overwrite_and_load_array(self, starting_date = None, ending_date = None,  rebal=None,  lower_bound=0.02, upper_bound=0.4, local_root_directory='', user='',supervision_npy_file_suffix=''):
        supervision_file_name = starting_date.strftime('%d_%b_%Y')+'_'+ending_date.strftime('%d_%b_%Y')+'_'+user + '_' + str(rebal)  + '_' + str(lower_bound)+ '_' + str(upper_bound) +  supervision_npy_file_suffix
        local_root_directory = Path(local_root_directory)
        local_supervision_npy_path = local_root_directory/supervision_file_name
        if self.dropbox_backup:
            res_sup = self.download(folder='', subfolder='', name=supervision_file_name)
            f = open(local_supervision_npy_path, 'wb')
            f.write(res_sup)
            f.close()
        results = np.load(local_supervision_npy_path)
        return results

    def local_features_npy_save_and_upload(self, starting_date = None, ending_date = None, shortcut_features=None, features=None, features_names=None, shortcut_features_names = None, feature_type=None, n_past_features = None, local_root_directory='', user='', shortcut_features_saving_suffix='',features_saving_suffix='', features_names_saving_suffix='', shortcut_features_names_saving_suffix=''):
        features_file_name = starting_date.strftime('%d_%b_%Y')+'_'+ending_date.strftime('%d_%b_%Y')+'_'+user +'_' + feature_type.name + '_' + str(n_past_features) + features_saving_suffix
        local_root_directory = Path(local_root_directory)
        features_full_path = local_root_directory/features_file_name
        print('saving local file '+str(features_full_path))
        np.save(features_full_path, features)
        if self.dropbox_backup:
            self.upload(fullname=features_full_path, folder='', subfolder='', name = features_file_name, overwrite=self.overwrite)
        features_names_file_names = user + '_' + feature_type.name + '_' + str(n_past_features) + features_names_saving_suffix
        features_names_full_path = local_root_directory/features_names_file_names
        np.save(features_names_full_path, features_names)
        if self.dropbox_backup:
            self.upload(fullname=features_names_full_path, folder='', subfolder='', name = features_names_file_names, overwrite=self.overwrite)

        shortcut_features_file_name = starting_date.strftime('%d_%b_%Y')+'_'+ending_date.strftime('%d_%b_%Y')+'_'+user+ shortcut_features_saving_suffix
        local_root_directory = Path(local_root_directory)
        shortcut_features_full_path = local_root_directory/shortcut_features_file_name
        print('saving local file '+str(shortcut_features_full_path))
        np.save(shortcut_features_full_path, shortcut_features)
        if self.dropbox_backup:
            self.upload(fullname=shortcut_features_full_path, folder='', subfolder='', name = shortcut_features_file_name, overwrite=self.overwrite)

        shortcut_features_names_file_names = user + shortcut_features_names_saving_suffix
        shortcut_features_names_full_path = local_root_directory/shortcut_features_names_file_names
        np.save(shortcut_features_names_full_path, shortcut_features_names)
        if self.dropbox_backup:
            self.upload(fullname=shortcut_features_names_full_path, folder='', subfolder='', name = shortcut_features_names_file_names, overwrite=self.overwrite)





    def local_supervision_npy_save_and_upload(self, starting_date = None, ending_date = None, data=None, rebal = None, lower_bound=0.02, upper_bound=0.4, local_root_directory='', user='', supervision_npy_file_suffix=''):
        supervision_file_name = starting_date.strftime('%d_%b_%Y') + '_' +ending_date.strftime('%d_%b_%Y') + '_'+ user + '_' + str(rebal) + '_' + str(lower_bound)+ '_' + str(upper_bound) + supervision_npy_file_suffix
        local_root_directory = Path(local_root_directory)
        local_supervision_npy_path = local_root_directory/supervision_file_name
        print('saving local file '+str(local_supervision_npy_path))
        np.save(local_supervision_npy_path, data)
        if self.dropbox_backup:
            self.upload(fullname=local_supervision_npy_path, folder='', subfolder='', name = supervision_file_name, overwrite=self.overwrite)


    def list_folder(self, folder, subfolder):
        """List a folder.
        Return a dict mapping unicode filenames to
        FileMetadata|FolderMetadata entries.
        """
        path = '/%s/%s' % (folder, subfolder.replace(os.path.sep, '/'))
        while '//' in path:
            path = path.replace('//', '/')
        path = path.rstrip('/')
        try:
            with stopwatch('list_folder'):
                res = self.dbx.files_list_folder(path)
        except dropbox.exceptions.ApiError as err:
            print('Folder listing failed for', path, '-- assumed empty:', err)
            return {}
        else:
            rv = {}
            for entry in res.entries:
                rv[entry.name] = entry
            return rv



    def upload(self, fullname, folder, subfolder, name, overwrite=False):
        """Upload a file.
        Return the request response, or None in case of error.
        """
        path = '/%s/%s/%s' % (folder, subfolder.replace(os.path.sep, '/'), name)
        while '//' in path:
            path = path.replace('//', '/')
        mode = (dropbox.files.WriteMode.overwrite
                if overwrite
                else dropbox.files.WriteMode.add)
        mtime = os.path.getmtime(fullname)
        with open(fullname, 'rb') as f:
            data = f.read()
        with stopwatch('upload %d bytes' % len(data)):
            try:
                res = self.dbx.files_upload(
                    data, path, mode,
                    client_modified=datetime.datetime(*time.gmtime(mtime)[:6]),
                    mute=True)
            except dropbox.exceptions.ApiError as err:
                print('*** API error', err)
                return None
        print('uploaded as', res.name.encode('utf8'))
        return res

    def download(self, folder, subfolder, name):
        """Download a file.
        Return the bytes of the file, or None if it doesn't exist.
        """
        path = '/%s/%s/%s' % (folder, subfolder.replace(os.path.sep, '/'), name)
        while '//' in path:
            path = path.replace('//', '/')
        with stopwatch('download'):
            try:
                md, res = self.dbx.files_download(path)
            except dropbox.exceptions.HttpError as err:
                print('*** HTTP error', err)
                return None
        data = res.content
        print(len(data), 'bytes; md:', md)
        return data


