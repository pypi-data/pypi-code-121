import argparse 
import pandas as pd
import os
import numpy as np
from sklearn.metrics import accuracy_score
import pandas as pd
import nibabel as nib
import SimpleITK as sitk
import concurrent.futures
from pathlib import PurePath


parser = argparse.ArgumentParser(
    description='Define data inputs')
parser.add_argument(
    "--train_csv_files", nargs="+",
    help="The paths for train csv files")
parser.add_argument(
    "--val_csv_files", nargs="+",
    help="The paths for val csv files")
parser.add_argument(
    '--output_train_csv', type=str,
    help="The out path for train csv file")
parser.add_argument(
    "--output_val_csv", type=str,
    help="The out path for train csv file")
parser.add_argument(
    "--minc_file_path", type=str,
    help="The out path for minc files")
parser.add_argument(
    "--num_workers", type=int,
    help="number of workers")
parser.add_argument(
    "--output_data_root", type=str,
    help="output data root path")
parser.add_argument(
    '--unlabeled_folder', type=str,
    help="The out path for train csv file")


def mkFolder(dir):
    os.makedirs(dir, exist_ok=True)


def appendDataframes(csv_dcm_files):
    li = []
    for filename in csv_dcm_files:
        df = pd.read_csv(
            filename, index_col=None,
            header=0, dtype=str)
        li.append(df)
    return pd.concat(li, axis=0, ignore_index=True)


def write_nifty(input_path, output_path):
    mkFolder(os.path.dirname(output_path))
    try:
        sitk_image = sitk.ReadImage(input_path)
        spacing = sitk_image.GetSpacing()
        size = sitk_image.GetSize()
        sitk_array = sitk.GetArrayFromImage(sitk_image)
        sitk_array = np.transpose(sitk_array, (1, 2, 0))
        sitk_array = np.rot90(sitk_array, k=3, axes=(0, 1))
        spacing = (spacing[0], spacing[1], 1/spacing[2])
        img = nib.Nifti1Image(sitk_array, np.eye(4))
        img = nib.as_closest_canonical(img)
        img.header['pixdim'][1:4] = spacing
        nib.save(img, output_path)
    except RuntimeError:
        print('WARNING: the following data cannot be converted',
              input_path)
    return spacing, size


def remove_leakage(df1, df2, patient_col):
    """
    Return True if there any patients are in both df1 and df2.

    Args:
        df1 (dataframe): dataframe describing first dataset
        df2 (dataframe): dataframe describing second dataset
        patient_col (str): string name of column with patient IDs
    Returns:
        leakage (bool): True if there is leakage, otherwise False
    """

    df1_patients_unique = set(df1[patient_col].values)
    df2_patients_unique = set(df2[patient_col].values)
    patients_in_both_groups = df1_patients_unique.intersection(
        df2_patients_unique)

    df1 = df1[~df1[patient_col].isin(list(patients_in_both_groups))]     
    return df1


def maybeConcatDf(df_train, df_folder):
    if df_folder is not None:
        df_files = [os.path.join(df_folder, i) for i in os.listdir(df_folder)]
        df_unlabel = appendDataframes(df_files)
        df_train = pd.concat([df_train, df_unlabel], axis=0, ignore_index=True)
        # df_train = pd.concat([df_train df_unlabel], axis=1)

    return df_train


def main():
    args = parser.parse_args()
    op = args.output_data_root
    df_train = appendDataframes(args.train_csv_files)
    df_val = appendDataframes(args.val_csv_files)
    #df_train = maybeConcatDf(df_train, args.unlabeled_folder)
    df_train = remove_leakage(df_train, df_val, 'bth_pid')

    df_train['labels_ori'] = df_train[config['labels_names']]
    df_val['labels_ori'] = df_val[config['labels_names']]
    di = {'0': '0',
          '1': '1',
          '2': '2',
          '3': '4',
          '4': '5',
          '6': '6',
          '7': '6',
          '8': '6',
          '9': '6',
          '10': '6',
          '11': '6',
          '12': '6',
          '13': '6',
          '14': '6',
          '15': '6',
          '16': '6',
          '17': '6',
          '18': '6',
          '19': '6',
          '20': '6'}
    df_train = df_train.replace({config['labels_names']: di})
    df_val = df_val.replace({config['labels_names']: di})
    df_val = df_val[df_val[config['labels_names']] != 'stop']
    df_val = df_val[df_val[config['labels_names']] != 'slut']
    df_train = df_train[df_train[config['labels_names']] != 'stop']
    df_train = df_train[df_train[config['labels_names']] != 'slut']

    df_val['image1'] = df_val['RecursiveFilePath'].apply(
            lambda x: os.path.splitext(
                os.path.join(
                    *PurePath(x).parts[-4:]))[0]) + '.nii.gz'
    input_path_val = df_val['RecursiveFilePath'].to_list()
    df_train['image1'] = df_train['RecursiveFilePath'].apply(
            lambda x: os.path.splitext(
                os.path.join(
                    *PurePath(x).parts[-4:]))[0]) + '.nii.gz'
    input_path_train = df_train['RecursiveFilePath'].to_list()

    mkFolder(op)

    output_path_val = [
        os.path.join(op, i)for i in df_val['image1'].to_list()]
    output_path_train = [
        os.path.join(op, i) for i in df_train['image1'].to_list()]

   # write_nifty(input_path_train[0], df_train['image1'].iloc[0])
   #### Train
    with concurrent.futures.ProcessPoolExecutor(
            max_workers=args.num_workers) as executor:
        result = executor.map(
            write_nifty, input_path_train, output_path_train)
        space_size = []
        for value in result:
            space_size.append([str(value[0])] + [str(value[1])])

    df_train = pd.concat([
        df_train,
        pd.DataFrame(space_size, columns=['spacings', 'sizes'])], axis=1)
    df_train.to_csv(
        args.output_train_csv, index=False)
    #### Val
    with concurrent.futures.ProcessPoolExecutor(
            max_workers=args.num_workers) as executor:
        result = executor.map(
            write_nifty, input_path_val, output_path_val)
        space_size = []
        for value in result:
            space_size.append([str(value[0])] + [str(value[1])])

    df_val = pd.concat([
        df_val,
        pd.DataFrame(space_size, columns=['spacings', 'sizes'])], axis=1)
    
    if 'predictions' in df_val.columns:
        df_val = df_val.drop(columns=['predictions'])
    if 'confidences' in df_val.columns:
        df_val = df_val.drop(columns=['confidences'])
    df_val.to_csv(
        args.output_val_csv, index=False)


    # do baseline 
    labels_train = df_train[config['labels_names']].dropna().astype(int).to_numpy()
    labels_val = df_val[config['labels_names']].dropna().astype(int).to_numpy()
    preds_train = np.zeros(len(labels_train)).astype(int)
    preds_val = np.zeros(len(labels_val)).astype(int)
    print(
        'print zero performance train: ',
        accuracy_score(labels_train, preds_train))

    print(
        "print zero performance val:",
        accuracy_score(labels_val, preds_val))
    print('done preparing data')
    # os.system('chmod -R o-rwx {}'.format(op))
    # print('done changing permission')


if __name__ == '__main__':
    main()
