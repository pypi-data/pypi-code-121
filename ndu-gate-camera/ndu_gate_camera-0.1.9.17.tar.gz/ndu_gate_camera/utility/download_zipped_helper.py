import time
import urllib.request
import os
from os import path
import zipfile


def download_runner_data(runner_type, runner_load_path, download_urls):
    name = runner_type

    runner_dir = runner_load_path
    if not runner_load_path:
        runner_dir = path.join(get_runner_dir(), name)

    if download_urls.get(runner_type) is None:
        return

    url = download_urls[name]

    data_folder = path.join(runner_dir, 'data')
    zip_file_path = os.path.join(runner_dir, 'data.zip')

    # if os.path.isfile(zip_file_path):
    #     old_zip_file_path = os.path.join(runner_dir, 'old_' + time.time() + '_data.zip')
    #     os.rename(zip_file_path, old_zip_file_path)

    try:
        if path.isdir(data_folder) is False:
            print('Data folder created')
            os.mkdir(data_folder)

        if not path.isfile(zip_file_path):
            print('Path to download is : ', data_folder)
            urllib.request.urlretrieve(url, zip_file_path)
        else:
            print('Data zip file exists, skipping download')

        if len(os.listdir(data_folder)) > 0:
            print("Data folder is not empty")
        else:
            unzip_to_data_folder(zip_file_path, runner_dir)

    except urllib.error.HTTPError as e:
        print(e.code)
    except PermissionError as e:
        print('PermissionError during extracting zip file')
    except Exception as e:
        print('Error during retrieving file')
        print(e)




def get_runner_dir():
    cur_dir = os.getcwd()
    parent_dir = os.path.abspath(os.path.join(cur_dir, os.pardir))
    runner_dir = os.path.join(parent_dir, 'runners')
    return runner_dir


def unzip_to_data_folder(zip_file_path, data_folder):
    zip_ref = zipfile.ZipFile(zip_file_path, 'r')
    zip_ref.extractall(data_folder)
    zip_ref.close()

# def unzip_and_delete(runner_dir, name):
#     # unzip
#     if path.isdir(os.path.join(runner_dir, name)) is False or path.isdir(
#             os.path.join(runner_dir, name, 'data')) is False:
#         zip_ref = zipfile.ZipFile(os.path.join(runner_dir, name + '.zip'), 'r')
#         zip_ref.extractall(os.path.join(runner_dir))
#         zip_ref.close()
#
#         # delete zip
#         os.remove(os.path.join(runner_dir, name + '.zip'))
