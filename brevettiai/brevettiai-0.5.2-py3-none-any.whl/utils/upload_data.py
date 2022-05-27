#!/usr/bin/env python
"""
Functionality and script to upload data to the [Brevetti AI Platform](https://platform.brevetti.ai)

"""
import argparse
import os.path
import time
import concurrent
from tqdm import tqdm
import os
from brevettiai.platform.models.dataset import Dataset
from brevettiai.platform import PlatformAPI


def recursive_relative_paths(path, reverse=False):
    for root, dirs, files in os.walk(path):
        if reverse:
            dirs[:] = dirs[::-1]
        for file in files:
            file_path = os.path.join(root, file)
            dataset_path = os.path.relpath(file_path, path)
            yield (file_path, dataset_path.replace("\\", "/"))

def filtered_generator(path, filter_files, reverse=False):
    for (disk_path, dataset_path) in recursive_relative_paths(path):
        ix = filter_files.searchsorted(dataset_path)
        if ix >= len(filter_files) or filter_files[ix] != dataset_path:
            yield disk_path, dataset_path

def copy_recursive(dataset, generator):
    def upload_to_ds(ds, src, ds_target):
        pth = ds.get_location(ds_target)

        status = ds.io.copy(src, pth)
        return pth

    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        futures = []
        for (disk_path, dataset_path) in generator:
            future = executor.submit(upload_to_ds,
                                    dataset, disk_path, dataset_path)
            futures.append(future)
    for f in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
        pass


"""
Example usage:

python -m brevettiai.utils.upload_data my_local_folder --dataset_name "My new dataset name" --username my_name@my_domain.com --password *****
"""
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_folder', help='Absolute path to the folder containing the Dataset')
    parser.add_argument('--dataset_name', help='Name of the dataset as it will appear on the platform')
    parser.add_argument('--reference', help='Reference Field for the dataset')
    parser.add_argument('--username', help='Brevetti-AI platform username (https://platform.brevetti.ai)')
    parser.add_argument('--password', help='Brevetti-AI platform password (https://platform.brevetti.ai)')
    parser.add_argument('--dataset_id', help="Id of existing dataset to upload to")
    parser.add_argument('--overwrite', help="Overwrite data in existing dataset (only used if uploading to an existing dataset)", type=bool, default=False)
    parser.add_argument('--reverse', help="Reverse order of upload", type=bool, default=False)

    args = parser.parse_args()

    credentials = {}
    if "username" in args:
        credentials["username"] = args.username
    if "password" in args:
        credentials["password"] = args.password

    platform = PlatformAPI(**credentials, cache_remote_files=False, remember_me=True)

    if args.dataset_id:
        dataset = platform.get_dataset(args.dataset_id, write_access=True)
    else:
        ds_name = args.dataset_name if args.dataset_name else os.path.basename(args.input_folder)
        dataset = Dataset(name=ds_name, reference=args.reference)
        print(f'Creating dataset {ds_name} on platform')
        dataset = platform.create(dataset, write_access=True)

    if not args.overwrite and args.dataset_id:
        import numpy as np
        remote_files = np.array([f"{x[0]}/{y}"[len(dataset.bucket)+1:] for x in dataset.io.walk(dataset.bucket) for y in x[2]])
        remote_files.sort()
        generator = filtered_generator(args.input_folder, remote_files, reverse=args.reverse)
        print(f'Copying files to s3...')
    else:
        generator = recursive_relative_paths(args.input_folder, reverse=args.reverse)
        print('Copy entire dataset to s3...')

    start_procedure = time.time()

    copy_recursive(dataset, generator)

    print('End copy...')
    print(f'Dataset Created-Posted in {time.time() - start_procedure}s...')
