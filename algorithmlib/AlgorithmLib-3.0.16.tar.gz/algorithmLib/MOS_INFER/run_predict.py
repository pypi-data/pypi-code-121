# -*- coding: utf-8 -*-
import sys

sys.path.append('../')
"""
@author: Gabriel Mittag, TU-Berlin
"""
from MOS_INFER.NISQA_model import nisqaModel
import os
import warnings

os.environ['CUDA_VISIBLE_DEVICES'] = '0'
warnings.filterwarnings('ignore')

def cal_mos_infer(testFile=None):
    """
    Parameters
    ----------
    testFile

    Returns
    -------

    """
    args = {'mode': 'predict_file', 'pretrained_model': 'SC_res_retrain_220316_185754125621__ep_007.tar',
     'deg': '', 'data_dir': 'test', 'output_dir': None, 'csv_file': 'test-Copy1.csv',
     'csv_deg': 'filename', 'num_workers': 0, 'bs': 1, 'ms_channel': None, 'tr_bs_val': 1, 'tr_num_workers': 0,
     'task_type': 1}
    args['deg'] = testFile
    nisqa = nisqaModel(args)
    df = nisqa.predict()
    try:
        npyfile = testFile[:-4] + '_mel48.npy'
        os.remove(npyfile)
    except:
        print('AI MOS file delete err!')
    return df['mos_pred'].values[0]


if __name__ == "__main__":
    test = 'mixDstFile_minus_6.wav'
    df = cal_mos_infer(test)
    print(df)


































