#!/usr/bin/env python3
# coding: utf-8

#!/usr/bin/env python3
# coding: utf-8

from cryptotoolbox.features import features_type
from cryptotoolbox.file_saver import dropbox_file_saver
from cryptotoolbox.neural_net import lrs_type
from cryptotoolbox.neural_net import activations

class FeaturesLauncher():

    def __init__(self,drop_token='', dropbox_backup=True, local_root_directory='../data',user='napoleon',  db_path_suffix = '_run.sqlite', meta_features_types=[features_type.FeaturesType.STANDARD_ADVANCED], meta_layers=[[2048,1024,512,256,128,64,32]], convolutions=[0], activations=[activations.ActivationsType.LEAK_0SUB_0MAX0], meta_n=[126], meta_seeds=[0], epochss=[1], ss=[21], meta_n_past_features=[21], utilities=['f_drawdown'], meta_lrs_types = [lrs_type.LrType.CONSTANT],meta_lrs = [0.01],lower_bounds=[0.02],upper_bounds=[0.4]):
        # print('Epochs ' + str(epochss))
        # print('Seed ' + str(meta_seeds))
        # print('Training period size ' + str(meta_n))
        # print('Neural net layout ' + str(meta_layers))
        # print('Stationarize ' + str(meta_stationarize))
        # print('Normalize ' + str(meta_normalize))
        # print('Advanced ' + str(meta_advance_features))
        # print('Signals ' + str(meta_advance_signals))
        # print('History ' + str(meta_history))
        # print('Normalized ' + str(meta_normalize))
        # print('Rebalancing ' + str(ss))
        # print('Activation ' + str(activations))
        # print('Convolution' + str(convolutions))
        # print('Utility' + str(utilities))
        # print('n past features ' + str(meta_n_past_features))
        # print('Rebalancing ' + str(ss))
        self.args = []
        self.counter = 1
        for lrs_type in meta_lrs_types:
            for lr in meta_lrs:
                for utility in utilities:
                    for n_past_features in meta_n_past_features:
                        for convolution in convolutions:
                            for activation in activations:
                                for s in ss:
                                    for epochs in epochss:
                                        for feature_type in meta_features_types:
                                            for seed in meta_seeds:
                                                for layers in meta_layers:
                                                    for n in meta_n:
                                                        for low_bound in lower_bounds:
                                                            for up_bound in upper_bounds:
                                                                self.args.append((self,seed, utility, layers, epochs,
                                                                             n_past_features, n, s, feature_type,
                                                                             activation, convolution,lr, lrs_type, low_bound, up_bound))
                                                                self.counter = self.counter + 1
        self.local_root_directory = local_root_directory
        self.user = user
        self.db_path_suffix = db_path_suffix
        self.filename =  user + db_path_suffix
        self.db_path = self.local_root_directory + self.filename
        self.dbx = dropbox_file_saver.NaPoleonDropboxConnector(drop_token=drop_token,dropbox_backup=dropbox_backup)



    def launchExplainer(self, toRun):
        if len(self.args)>1:
            raise Exception('Features explanation for one run only')
        featuresDf = toRun(*self.args[0])
        return featuresDf



