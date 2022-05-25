# -*- coding: utf-8 -*-
"""
@author: Gabriel Mittag, TU-Berlin
"""

import os
import datetime


import pandas as pd; pd.options.mode.chained_assignment=None
import torch
import torch.nn as nn
from MOS_INFER import NISQA_lib as NL
import sys

sys.path.append('../')
class nisqaModel(object):
    '''
    nisqaModel: Main class that loads the model and the datasets. Contains
    the training loop, prediction, and evaluation function.                                               
    '''      
    def __init__(self, args):
        self.args = args
        self.runinfos = {}       
        self._getDevice()
        self._loadModel()
        self._loadDatasets()
        self.args['now'] = datetime.datetime.today()

    def predict(self):
        print('---> Predicting ...')
        if self.args['tr_parallel']:
            self.model = nn.DataParallel(self.model)           
        
        if self.args['dim']==True:
            y_val_hat, y_val = NL.predict_dim(
                self.model, 
                self.ds_val, 
                self.args['tr_bs_val'],
                self.dev,
                num_workers=self.args['tr_num_workers'])
        else:
            if self.args['task_type'] == 0:
                y_val_hat, y_val = NL.predict_mos(
                    self.model, 
                    self.ds_val, 
                    self.args['tr_bs_val'],
                    self.dev,
                    num_workers=self.args['tr_num_workers']) 
            elif self.args['task_type'] == 1:
                y_val_hat, y_val = NL.predict_mos_multitask(
                    self.model, 
                    self.ds_val, 
                    self.args['tr_bs_val'],
                    self.dev,
                    num_workers=self.args['tr_num_workers']) 
            elif self.args['task_type'] == 2:
                y_val_hat, y_val = NL.predict_mos_multifeature(
                    self.model, 
                    self.ds_val, 
                    self.args['tr_bs_val'],
                    self.dev,
                    num_workers=self.args['tr_num_workers']) 
            elif self.args['task_type'] == 3:
                y_val_hat, y_val = NL.predict_mos_multiresolution(
                    self.model_1, 
                    self.model_2, 
                    self.model_3, 
                    self.ds_val, 
                    self.args['tr_bs_val'],
                    self.dev,
                    num_workers=self.args['tr_num_workers']) 
            elif self.args['task_type'] == 4:
                y_val_hat, y_val = NL.predict_mos_multiscale(
                    self.model_1, 
                    self.model_2, 
                    self.model_3, 
                    self.ds_val, 
                    self.args['tr_bs_val'],
                    self.dev,
                    num_workers=self.args['tr_num_workers']) 
            
        # import pdb; pdb.set_trace()        
        if self.args['output_dir']:
            self.ds_val.df['model'] = self.args['name']
            self.ds_val.df.to_csv(
                os.path.join(self.args['output_dir'], 'test.csv'),
                index=False)

            
        # print(self.ds_val.df.to_string(index=False))

        if self.args['task_type'] == 1:
            r_mos = NL.calc_eval_metrics(y_val[:,0].squeeze(), y_val_hat[:,0].squeeze())
            r_std = NL.calc_eval_metrics(y_val[:,1].squeeze(), y_val_hat[:,1].squeeze())
            print('mos')
            print(r_mos)
            print('std')
            print(r_std)
        else:
            r = NL.calc_eval_metrics(y_val.squeeze(), y_val_hat.squeeze())
            print(r)

        return self.ds_val.df


    
    def _loadDatasets(self):
        if self.args['mode']=='predict_file':
            self._loadDatasetsFile()
        elif self.args['mode']=='predict_dir':
            self._loadDatasetsFolder()  
        elif self.args['mode']=='predict_csv':
            self._loadDatasetsCSVpredict()
        elif self.args['mode']=='main':
            self._loadDatasetsCSV()
        else:
            raise NotImplementedError('mode not available')                        
            
    

    def _loadDatasetsFile(self):
        data_dir = os.path.dirname(self.args['deg'])
        file_name = os.path.basename(self.args['deg'])
        df_val = pd.DataFrame([file_name], columns=['deg'])

        # creating Datasets ---------------------------------------------------
        self.ds_val = NL.SpeechQualityDataset(
            df_val,
            df_con=None,
            data_dir = data_dir,
            filename_column = 'deg',
            mos_column = 'predict_only',
            seg_length = self.args['ms_seg_length'],
            max_length = self.args['ms_max_segments'],
            to_memory = None,
            to_memory_workers = None,
            seg_hop_length = self.args['ms_seg_hop_length'],
            transform = None,
            ms_n_fft = self.args['ms_n_fft'],
            ms_hop_length = self.args['ms_hop_length'],
            ms_win_length = self.args['ms_win_length'],
            ms_n_mels = self.args['ms_n_mels'],
            ms_sr = self.args['ms_sr'],
            ms_fmax = self.args['ms_fmax'],
            ms_channel = self.args['ms_channel'],
            double_ended = self.args['double_ended'],
            dim = self.args['dim'],
            filename_column_ref = None,
            mos_std_column = 'mos_std',
            votes_column = 'votes',
            task_type = self.args['task_type'],
        )


    def _loadModel(self):    
        '''
        Loads the Pytorch models with given input arguments.
        '''   
        # if True overwrite input arguments from pretrained model
        # import pdb; pdb.set_trace()
        if self.args['pretrained_model']:
            # if os.path.isabs(self.args['pretrained_model']):
            #     model_path = os.path.join(self.args['pretrained_model'])
            # else:
            #     model_path = os.path.join(os.getcwd(), self.args['pretrained_model'])
            #model_path = os.path.join(sys.prefix, self.args['pretrained_model'])
            model_path = sys.prefix + '//'+ self.args['pretrained_model']
            print(sys.prefix,model_path)
            if self.args['task_type'] == 3 or self.args['task_type'] == 4:
                checkpoint = torch.load(model_path[:-4] + '_1.tar', map_location=self.dev)
                checkpoint_2 = torch.load(model_path[:-4] + '_2.tar', map_location=self.dev)
                checkpoint_3 = torch.load(model_path[:-4] + '_3.tar', map_location=self.dev)
                
            else:
                checkpoint = torch.load(model_path, map_location=self.dev)
            
            # update checkpoint arguments with new arguments
            checkpoint['args'].update(self.args)
            self.args = checkpoint['args']
            
        if self.args['model']=='NISQA_DIM':
            self.args['dim'] = True
            self.args['csv_mos'] = None # column names hardcoded for dim models
        else:
            self.args['dim'] = False
            
        if self.args['model']=='NISQA_DE':
            self.args['double_ended'] = True
        else:
            self.args['double_ended'] = False     
            self.args['csv_ref'] = None

        # Load Model
        self.model_args = {
            
            'ms_seg_length': self.args['ms_seg_length'],
            'ms_n_mels': self.args['ms_n_mels'],
            
            'cnn_model': self.args['cnn_model'],
            'cnn_c_out_1': self.args['cnn_c_out_1'],
            'cnn_c_out_2': self.args['cnn_c_out_2'],
            'cnn_c_out_3': self.args['cnn_c_out_3'],
            'cnn_kernel_size': self.args['cnn_kernel_size'],
            'cnn_dropout': self.args['cnn_dropout'],
            'cnn_pool_1': self.args['cnn_pool_1'],
            'cnn_pool_2': self.args['cnn_pool_2'],
            'cnn_pool_3': self.args['cnn_pool_3'],
            'cnn_fc_out_h': self.args['cnn_fc_out_h'],
            
            'td': self.args['td'],
            'td_sa_d_model': self.args['td_sa_d_model'],
            'td_sa_nhead': self.args['td_sa_nhead'],
            'td_sa_pos_enc': self.args['td_sa_pos_enc'],
            'td_sa_num_layers': self.args['td_sa_num_layers'],
            'td_sa_h': self.args['td_sa_h'],
            'td_sa_dropout': self.args['td_sa_dropout'],
            'td_lstm_h': self.args['td_lstm_h'],
            'td_lstm_num_layers': self.args['td_lstm_num_layers'],
            'td_lstm_dropout': self.args['td_lstm_dropout'],
            'td_lstm_bidirectional': self.args['td_lstm_bidirectional'],
            
            'td_2': self.args['td_2'],
            'td_2_sa_d_model': self.args['td_2_sa_d_model'],
            'td_2_sa_nhead': self.args['td_2_sa_nhead'],
            'td_2_sa_pos_enc': self.args['td_2_sa_pos_enc'],
            'td_2_sa_num_layers': self.args['td_2_sa_num_layers'],
            'td_2_sa_h': self.args['td_2_sa_h'],
            'td_2_sa_dropout': self.args['td_2_sa_dropout'],
            'td_2_lstm_h': self.args['td_2_lstm_h'],
            'td_2_lstm_num_layers': self.args['td_2_lstm_num_layers'],
            'td_2_lstm_dropout': self.args['td_2_lstm_dropout'],
            'td_2_lstm_bidirectional': self.args['td_2_lstm_bidirectional'],                
            
            'pool': self.args['pool'],
            'pool_att_h': self.args['pool_att_h'],
            'pool_att_dropout': self.args['pool_att_dropout'],
            }
            
        if self.args['double_ended']:
            self.model_args.update({
                'de_align': self.args['de_align'],
                'de_align_apply': self.args['de_align_apply'],
                'de_fuse_dim': self.args['de_fuse_dim'],
                'de_fuse': self.args['de_fuse'],        
                })
                      
        print('Model architecture: ' + self.args['model'])
        if self.args['model']=='NISQA':
            if self.args['task_type'] == 0:
                self.model = NL.NISQA(**self.model_args)     
            elif self.args['task_type'] == 1:
                self.model = NL.NISQA_MULTITASK(**self.model_args)
            elif self.args['task_type'] == 2:
                self.model = NL.NISQA(**self.model_args) 
            elif self.args['task_type'] == 3:
                self.model_1 = NL.NISQA(**self.model_args)  
                self.model_2 = NL.NISQA(**self.model_args) 
                self.model_3 = NL.NISQA(**self.model_args)
            elif self.args['task_type'] == 4:
                self.model_1 = NL.NISQA(**self.model_args)  
                self.model_2 = NL.NISQA(**self.model_args) 
                self.model_3 = NL.NISQA(**self.model_args) 
                
        elif self.args['model']=='NISQA_DIM':
            self.model = NL.NISQA_DIM(**self.model_args)     
        elif self.args['model']=='NISQA_DE':
            self.model = NL.NISQA_DE(**self.model_args)     
        else:
            raise NotImplementedError('Model not available')                        
        
        
        # Load weights if pretrained model is used ------------------------------------
        if self.args['pretrained_model']:
            if self.args['task_type'] == 3 or self.args['task_type'] == 4:
                missing_keys, unexpected_keys = self.model_1.load_state_dict(checkpoint['model_state_dict'], strict=True)
                missing_keys, unexpected_keys = self.model_2.load_state_dict(checkpoint_2['model_state_dict'], strict=True)
                missing_keys, unexpected_keys = self.model_3.load_state_dict(checkpoint_3['model_state_dict'], strict=True)
            else:
                missing_keys, unexpected_keys = self.model.load_state_dict(checkpoint['model_state_dict'], strict=True)
            print('Loaded pretrained model from ' + self.args['pretrained_model'])
            if missing_keys:
                print('missing_keys:')
                print(missing_keys)
            if unexpected_keys:
                print('unexpected_keys:')
                print(unexpected_keys)  
                
        # para_num = sum([p.numel() for p in self.model.parameters()])
        # para_size = para_num * 4 / 1024
        # import pdb; pdb.set_trace()


    def _getDevice(self):
        '''
        Train on GPU if available.
        '''
        if torch.cuda.is_available():
            self.dev = torch.device("cuda")
        else:
            self.dev = torch.device("cpu")

        if "tr_device" in self.args:
            if self.args['tr_device']=='cpu':
                self.dev = torch.device("cpu")
            elif self.args['tr_device']=='cuda':
                self.dev = torch.device("cuda")
        print('Device: {}'.format(self.dev))

        if "tr_parallel" in self.args:
            if (self.dev==torch.device("cpu")) and self.args['tr_parallel']==True:
                self.args['tr_parallel']==False
                print('Using CPU -> tr_parallel set to False')


            
