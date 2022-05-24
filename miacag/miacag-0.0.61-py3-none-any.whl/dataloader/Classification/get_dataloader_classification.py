from torch.utils.data import DataLoader
import torch
from monai.data import (
    list_data_collate, pad_list_data_collate,
    ThreadDataLoader)
from torchvision import datasets
import psycopg2
import pandas as pd
import os
from monai.data import DistributedWeightedRandomSampler, DistributedSampler
from miacag.utils.sql_utils import getDataFromDatabase
import numpy as np

class ClassificationLoader():
    def __init__(self, config) -> None:
        self.config = config
        self.df, self.connection = getDataFromDatabase(self.config)
        self.df = self.df.dropna(subset=config["labels_names"], how='any')
        if self.config['loaders']['mode'] == 'testing':
            self.val_df = self.df
        else:
            self.train_df = self.df[self.df['phase'] == 'train']
            self.val_df = self.df[self.df['phase'] == 'val']

 
    def get_classification_loader_train(self, config):
        if config['loaders']['format'] in ['dicom']:
            from miacag.dataloader.Classification._3D.dataloader_monai_classification_3D import \
                train_monai_classification_loader
            if config['loaders']['val_method']['type'] == 'patches':
                from miacag.dataloader.Classification._3D.dataloader_monai_classification_3D import \
                    val_monai_classification_loader
            elif config['loaders']['val_method']['type'] == 'sliding_window':
                from miacag.dataloader.Classification._3D.dataloader_monai_classification_3D import \
                    val_monai_classification_loader_SW as val_monai_classification_loader
            else:
                raise ValueError("Invalid validation moode %s" % repr(
                    config['loaders']['val_method']['type']))
        elif config['loaders']['format'] in ['db']:
            from \
                miacag.dataloader.Classification.tabular.dataloader_monai_classification_tabular import \
                train_monai_classification_loader, val_monai_classification_loader
        elif config['loaders']['format'] in ['dicom_db']:
            print('NOT implemented')
        else:
            raise ValueError("Invalid validation moode %s" % repr(
                    config['loaders']['val_method']['type']))
        train_ds = train_monai_classification_loader(
            self.train_df,
            config)

        if config['weighted_sampler'] == 'True':
            weights = train_ds.weights
            train_ds = train_ds()
            sampler = DistributedWeightedRandomSampler(
                dataset=train_ds,
                weights=weights,
                even_divisible=True,
                shuffle=True)
        else:
            train_ds = train_ds()
            sampler = DistributedSampler(
                dataset=train_ds,
                even_divisible=True,
                shuffle=True)
            
        val_ds = val_monai_classification_loader(
                self.val_df,
                config)
        val_ds = val_ds()
    
        train_loader = ThreadDataLoader(
            train_ds,
            sampler=sampler,
            batch_size=config['loaders']['batchSize'],
            shuffle=False,
            num_workers=0, #config['num_workers'],
            collate_fn=pad_list_data_collate,
            pin_memory=False,) #True if config['cpu'] == "False" else False,)
        with torch.no_grad():
            val_loader = ThreadDataLoader(
                val_ds,
                batch_size=config['loaders']['batchSize'],
                shuffle=False,
                num_workers=0,
                collate_fn=pad_list_data_collate,#pad_list_data_collate if config['loaders']['val_method']['type'] == 'sliding_window' else list_data_collate,
                pin_memory=False,)
        return train_loader, val_loader, train_ds, val_ds

    def get_classificationloader_patch_lvl_test(self, config):
        if config['loaders']['format'] == 'dicom':
            if config['loaders']['val_method']['type'] == 'patches':
                from miacag.dataloader.Classification._3D. \
                    dataloader_monai_classification_3D import \
                    val_monai_classification_loader
                # nr_repeat = config['loaders']['val_method']['patches']
                # self.val_df = pd.DataFrame(np.repeat(
                #     self.val_df.values, nr_repeat,
                #     axis=0), columns=self.val_df.columns)
                self.val_ds = val_monai_classification_loader(
                    self.val_df,
                    config)
            elif config['loaders']['val_method']['type'] == 'sliding_window':
                from miacag.dataloader.Classification._3D. \
                    dataloader_monai_classification_3D import \
                    val_monai_classification_loader_SW
                self.val_ds = val_monai_classification_loader_SW(
                    self.val_df,
                    config)
        elif config['loaders']['format'] == 'db':
            if config['loaders']['val_method']['type'] == 'full':
                from miacag.dataloader.Classification.tabular. \
                    dataloader_monai_classification_tabular import \
                    val_monai_classification_loader
                self.val_ds = val_monai_classification_loader(
                    self.val_df,
                    config)
            else:

                raise ValueError("Invalid validation moode %s" % repr(
                    config['loaders']['val_method']['type']))
        else:
            raise ValueError("Invalid data format %s" % repr(
                    config['loaders']['format']))
        self.val_ds = self.val_ds()
        with torch.no_grad():
            self.val_loader = DataLoader(
                self.val_ds,
                batch_size=config['loaders']['batchSize'],
                shuffle=False,
                num_workers=0,
                collate_fn=list_data_collate if
                        config['loaders']['val_method']['type'] != 'sliding_window' else pad_list_data_collate,
                pin_memory=False if config['cpu'] == "False" else True,)

            # self.val_loader = ThreadDataLoader(
            #                 self.val_ds,
            #                 batch_size=config['loaders']['batchSize'],
            #                 shuffle=False,
            #                 num_workers=0,
            #                 collate_fn=pad_list_data_collate,#pad_list_data_collate if config['loaders']['val_method']['type'] == 'sliding_window' else list_data_collate,
            #                 pin_memory=False,)
