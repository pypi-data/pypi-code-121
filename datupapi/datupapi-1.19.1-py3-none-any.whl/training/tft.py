import os
import warnings
import pandas as pd
import featurewiz as FW
import numpy as np
import copy
from pathlib import Path
import warnings
import pytorch_lightning as pl
from pytorch_lightning.callbacks import EarlyStopping, LearningRateMonitor
from pytorch_lightning.loggers import TensorBoardLogger
import torch
import gc
from tensorflow.keras import backend as K
from dateutil.relativedelta import relativedelta
from datetime import datetime
import time
from sklearn.preprocessing import MinMaxScaler
from datupapi.extract.io import IO
from datupapi.configure.config import Config
from datupapi.predict.forecast import Forecast
from pytorch_forecasting import Baseline, TemporalFusionTransformer, TimeSeriesDataSet, DeepAR, NBeats
from pytorch_forecasting.data import GroupNormalizer, EncoderNormalizer, TorchNormalizer
from pytorch_forecasting.metrics import SMAPE, PoissonLoss, QuantileLoss, RMSE, MASE, MAPE, MAE, NormalDistributionLoss
from pytorch_forecasting.models.temporal_fusion_transformer.tuning import optimize_hyperparameters
import re

class Tft(Config):

    def __init__(self, config_file, logfile, log_path, *args, **kwargs):
        Config.__init__(self, config_file=config_file, logfile=logfile)
        self.log_path = log_path

    def min_max_scaler(self, data_train):
        """
        Scales the data with a Min Max scaler.
        
        :param data: Input dataframe used to train the models predictions.
 
        :return scalers: Array with the scalers for each feature.
        :return data_train: Normalized input dataframe.

        """
        scalers={}
        for j in data_train.columns:
                scaler = MinMaxScaler(feature_range=(-1,1))
                s_s = scaler.fit_transform(data_train[j].values.reshape(-1,1))
                s_s=np.reshape(s_s,len(s_s))
                scalers['scaler_'+ str(j)] = scaler
                data_train[j]=s_s
        return scalers, data_train

    def rescale(self,scalers, p0, backtest):
        p1=pd.DataFrame()
        if self.use_location:
            p0["item_id"]=p0.apply(lambda row: (str(row["item_id"])+"*-+"+str(row["location"])),axis=1)
        p0["item_id"]=p0["item_id"].astype(str)
        print("string")
        for key in scalers.keys():
            aux=pd.DataFrame()
            scaler=scalers[key]
            l_columns=["p5",	"p20",	"p40",	"p50",	"p60",	"p80",	"p95", "demand"] if backtest != 0 else ["p5",	"p20",	"p40",	"p50",	"p60",	"p80",	"p95"]
            aux=pd.DataFrame(scaler.inverse_transform(p0[p0.item_id==key.replace("scaler_", "")][l_columns]), columns=l_columns)
            p1=p1.append(aux, ignore_index=True)
        p1["item_id"]=p0.apply(lambda row: row["item_id"].split("*-+")[0], axis=1) if self.use_location else p0["item_id"]
        p1["time_idx"]=p0["time_idx"]
        if self.use_location:
            p1["location"]=p0["location"]
        return p1

    def transform_to_matrix(self, df, value=None, method=None):
        """
        Returns a dataframe in matrix form in order to be trained by the attention model

        :param df: Dataframe with columns: timestamp, item_id and demand
        :return df_out: Output dataframe with each item as a column
        >>> df =
                Date        item_id  Demand
                2021-16-05     sku1      23
                2021-16-05     sku2     543
                2021-16-05     sku3     123
        >>> df = transform_to_matrix(df)
        >>> df =
                      Date           sku1    sku2     sku3 ......... skuN
                idx1  2021-16-05      23      543      123 ......... 234
        """
        df_out = df.sort_values(by='timestamp')
        df_out = df_out.reset_index()
        df_out = df_out.iloc[:, 1:]
        df_out = df_out.pivot(index='timestamp', columns='item_id', values='demand').reset_index()
        df_out = df_out.fillna(value=value, method=method)
        df_out = df_out.rename(columns={'timestamp': 'Date'})
        df_out=df_out.set_index("Date")
        df_out =df_out.reindex(sorted(df_out.columns), axis=1)
        df_out=df_out.reset_index()
        for_loc = []
        return df_out, for_loc

    def date_index_generator(self, date_data, data_range):
        for index, date in enumerate(data_range):
            if date_data==date:
                return index

    def clean_negatives(self, df):
        """
        Replace negative values with zeros.

        :param noneg (df): Dataframe with the negative values to be replaces.
        :param n_backtests (int): Number of backtests. 5 by default.

        :return noneg (df): Dataframe without negative values.
        """
        inter = ["p95", "p5", "p60", "p40", "p80", "p20", "p50"]
        for i in range(1, self.backtests + 1):
            df[i]['target_value'] = df[i]['target_value'].map(lambda x: 0 if x < 0 else x)

        for i in inter:
            for j in range(self.backtests + 1):
                df[j][i] = df[j][i].map(lambda x: 0 if x < 0 else x)

        return df
    
    def prepare_data(self, value=0):
        DOCKER_CONFIG_PATH = os.path.join('/opt/ml/processing/input', 'config.yml')
        io = IO(config_file=DOCKER_CONFIG_PATH, logfile='data_training', log_path='output/logs')

        data1 = io.download_object_csv(datalake_path=self.dataset_import_path[0])
        data1["timestamp"]=pd.to_datetime(data1["timestamp"])
    
        #Filling dates and scaling if normalization==True    
        scalers,data1 = self.fill_dates(data1, value=value, method=None)

        #Detect frequency for resample---------------------------------------------
        frequency=self.dataset_frequency
        if frequency== "M" or (frequency=="Q") or frequency== "2M":
            suffix= "S" if pd.to_datetime(data1.timestamp.min()).day==1 else ""
            if ("Q" in frequency):
                month=pd.to_datetime(data1.timestamp.max()).month
                months={1:"-JAN", 2:"-FEB", 3:"-MAR", 4:"-APR", 5:"-MAY",6:"-JUN",7:"-JUL",8:"-AUG",9:"-SEP",10:"-OCT",11:"-NOV",12:"-DIC"}
                suffix= suffix+months[month]
        elif frequency=="W":
            day=data1["timestamp"].min().day_name()
            days={"Monday":"-MON", "Tuesday":"-TUE", "Wednesday":"-WED", "Thursday":"-THU", "Friday":"-FRI","Saturday":"-SAT","Sunday":"-SUN"}
            suffix=days[day]
    
        #Add time idx----------------------------------------------------------------------------------------
        if frequency=='2M':
            data_range=pd.date_range(start=data1.timestamp.min(), end=data1.timestamp.max(), freq=frequency)
            data_range= data_range+pd.offsets.MonthEnd(n=data1.timestamp.max().month%2)if suffix=='' else data_range+pd.offsets.MonthBegin(n=data1.timestamp.max().month%2)
        else:
            data_range=pd.date_range(start=data1.timestamp.min(), end=data1.timestamp.max(), freq=frequency+suffix)
        data_range_df=pd.DataFrame(data_range, columns=["timestamp"]).reset_index().rename(columns={"index":"time_idx"})
        warnings.filterwarnings("ignore")  # avoid printing out absolute paths
        data1=data1.sort_values(by=["timestamp","item_id"])
        #if frequency=="M":
        #    data1["time_idx"] = data1["timestamp"].dt.year * 12 + data1["timestamp"].dt.month
        #    data1["time_idx"] -= data1["time_idx"].min()
        #elif frequency=="Q":    
        #    data1["time_idx"]=data1.apply(lambda row: self.date_index_generator(row["timestamp"], data_range), axis=1)
        #elif frequency=="2M":
        #    data1["time_idx"]=data1.apply(lambda row: self.date_index_generator(row["timestamp"], data_range), axis=1)
        #elif frequency=="W":
        #    data1["time_idx"]=data1.apply(lambda row: self.date_index_generator(row["timestamp"], data_range), axis=1)
        data1=data1.merge(data_range_df, how="left", on=["timestamp"])

        n_features=len(data1.groupby(["item_id","location"]).size()) if self.use_location else data1.item_id.nunique()
        max_prediction_length = self.forecast_horizon
        max_encoder_length = self.input_window  

        #Create test_data
        item_location=[]
        test_data=pd.DataFrame(np.tile(pd.date_range(start=data1.timestamp.max(), periods=max_prediction_length+1, freq=frequency+suffix)[1:], n_features), columns=["timestamp"])
        test_data.insert(0, "time_idx", np.tile(np.arange(data1.time_idx.max()+1,data1.time_idx.max()+1+max_prediction_length), n_features))
        if self.use_location:
            item_location=data1.groupby(["item_id","location"]).size().reset_index()
            test_data.insert(2, "item_id", np.repeat(item_location.item_id.values ,max_prediction_length ))  
            test_data.insert(3, "location", np.repeat(item_location.location.values ,max_prediction_length ))  
        else:
            test_data.insert(2, "item_id", np.repeat(data1.item_id.unique() ,max_prediction_length ))

        ts_column = 'timestamp'
        test_data["timestamp"]=pd.to_datetime(test_data["timestamp"])
        test_data=test_data.assign(demand=0)
        data1=pd.concat([data1,test_data], axis=0)   

        #add holidays
        io.datalake="unimilitar-datalake"
        holidays = io.download_object_csv(datalake_path="as-is/opendata/Holidays.csv").loc[:, :"holidays_Colombia"]
        holidays.Date=pd.to_datetime(holidays.Date)
        holidays= holidays.set_index("Date").resample(frequency+suffix).sum().reset_index()
        holidays=holidays.rename(columns={"Date":"timestamp", "holidays_Colombia":"holidays_col"})
        data1=data1.merge(holidays, on="timestamp")
        io = IO(config_file=DOCKER_CONFIG_PATH, logfile='data_training', log_path='output/logs')

        #Add time related features
        timestamp=data1[["timestamp"]]
        ts_column = 'timestamp'
        data1["Mes"]=pd.to_datetime(data1[ts_column]).dt.month
        data1["timestamp_weekofyear"]=data1[ts_column].dt.weekofyear
        data1["timestamp_dayofyear"]=data1[ts_column].dt.dayofyear
        data1["timestamp_year"]=data1[ts_column].dt.year
        data1["timestamp_quarter"]=data1[ts_column].dt.quarter
        #data1, ts_adds_in = FW.FE_create_time_series_features(data1, ts_column, ts_adds_in=[])
        #data1=data1.drop(columns=["timestamp_month_typeofday_cross","timestamp_typeofday","timestamp_age_in_years","timestamp_month_dayofweek_cross","timestamp_is_warm","timestamp_is_cold","timestamp_is_festive","timestamp_month","timestamp_dayofweek_hour_cross","timestamp_dayofweek"])
        #data1["timestamp"]=timestamp

        #Merge exo data
        n_columns=0
        categorical=[]
        unknown=["demand"]
        if len(self.dataset_import_path)==2:
                Qdisc = io.download_object_csv(datalake_path=self.dataset_import_path[1])
                Qdisc.item_id=Qdisc.item_id.astype("string")
                Qdisc["timestamp"]=pd.to_datetime(Qdisc["timestamp"])
                if self.use_location:
                  Qdisc.location=Qdisc.location.astype("string")
                  for column in Qdisc.columns[3:]:
                      if Qdisc[column].dtype=='O':
                        categorical.append(column)
                      else:
                        unknown.append(column)
                  data1=pd.merge_ordered(data1, Qdisc, on=["timestamp","item_id", "location"], suffixes=["","-disc"], fill_method=0, how="left" )
                else:
                  for column in Qdisc.columns[2:]:
                      if Qdisc[column].dtype=='O':
                        categorical.append(column)
                      else:
                        unknown.append(column)
                  data1=pd.merge_ordered(data1,Qdisc, on=["timestamp","item_id"], suffixes=["","-disc"], fill_method=0, how="left")

        if len(self.dataset_import_path)==3:
                if self.dataset_import_path[1] !="":
                    Qdisc = io.download_object_csv(datalake_path=self.dataset_import_path[1])
                    Qdisc.item_id=Qdisc.item_id.astype("string")
                    Qdisc["timestamp"]=pd.to_datetime(Qdisc["timestamp"])
                    if self.use_location:
                      Qdisc.location=Qdisc.location.astype("string")
                      for column in Qdisc.columns[3:]:
                          if Qdisc[column].dtype=='O':
                            categorical.append(column)
                          else:
                            unknown.append(column)
                      data1=pd.merge_ordered(data1, Qdisc, on=["timestamp","item_id", "location"], suffixes=["","-disc"], fill_method=0, how="left")
                    else:
                      for column in Qdisc.columns[2:]:
                          if Qdisc[column].dtype=='O':
                            categorical.append(column)
                          else:
                            unknown.append(column)
                      data1=pd.merge_ordered(data1,Qdisc, on=["timestamp","item_id"], suffixes=["","-disc"], fill_method=0, how="left")
                if self.dataset_import_path[2] !="":

                  Qexo = io.download_object_csv(datalake_path=self.dataset_import_path[2])
                  n_columns=n_columns+len(Qexo.columns)-1
                  Qexo["timestamp"]=pd.to_datetime(Qexo["timestamp"])
                  data1=pd.merge_ordered(data1, Qexo, on=["timestamp"], fill_method=0, how="outer")

        data1=data1.fillna(0)
        data1["item_id"]=data1["item_id"].astype(str)
        test_data=data1[data1.time_idx> (data1.time_idx.max()-max_prediction_length-max_encoder_length)]
        data1=data1[data1.time_idx<= (data1.time_idx.max()-max_prediction_length)]

        #define variables
        group_ids=["item_id","location"] if self.use_location else ["item_id"] 

        if n_columns != 0:
            for index in data1.columns[-n_columns:]:
                unknown.append(index)
        known=['time_idx', 'Mes','holidays_col', 'timestamp_quarter',
            'timestamp_year',
            'timestamp_dayofyear', 'timestamp_weekofyear'] 
        #if frequency=="M" or frequency=="Q" or frequency=="2M":
        #    known.remove('timestamp_dayofmonth')   

        return data1, scalers, suffix, known, unknown, group_ids, test_data, n_features, item_location, categorical

    def add_dates(self, data1, predict, suffix, scalers):
        data_range=pd.date_range(start=data1.timestamp.min(), periods=data1.timestamp.nunique()+self.forecast_horizon, freq=self.dataset_frequency+suffix) if self.dataset_frequency=="M" or self.dataset_frequency=="Q" or self.dataset_frequency=="2M" else pd.date_range(start=data1.timestamp.min(), end=data1.timestamp.max().date()+relativedelta(weeks=self.forecast_horizon), freq=self.dataset_frequency+suffix)
        predict[0]["date"]=predict[0].apply(lambda row: data_range[int(row["time_idx"])], axis=1)
        column_names=["item_id","location", "date","p5","p20","p40","p50","p60","p80","p95"] if self.use_location else ["item_id","date","p5","p20","p40","p50","p60","p80","p95"]
        predict[0] = predict[0].reindex(columns=column_names)
        data1.item_id=data1.item_id.astype("string")
        for i in range(1, self.backtests+1):
            if self.use_location:
                predict[i].location=predict[i].location.astype("string")
                data1.location=data1.location.astype("string")
            predict[i].item_id=predict[i].item_id.astype("string")

            predict[i]=predict[i].merge(data1[["time_idx", "item_id","location", "demand"]], on=["time_idx", "item_id", "location"]) if self.use_location else predict[i].merge(data1[["time_idx", "item_id","demand"]], on=["time_idx", "item_id"])
            if self.normalization:
              predict[i]=self.rescale(scalers,predict[i], i)
            
            predict[i]["timestamp"]=predict[i].apply(lambda row: data_range[row["time_idx"]], axis=1)
            predict[i]=predict[i].assign(backtestwindow_start_time=data_range[predict[i].time_idx.min()])
            predict[i]=predict[i].assign(backtestwindow_end_time=data_range[predict[i].time_idx.max()])
            predict[i]=predict[i].rename(columns={"demand":"target_value"})
            column_names=["item_id","location", "timestamp","target_value","backtestwindow_start_time","backtestwindow_end_time","p5","p20", "p40","p50","p60","p80","p95"] if self.use_location else ["item_id","timestamp","target_value","backtestwindow_start_time","backtestwindow_end_time","p5","p20", "p40","p50","p60","p80","p95"]
            predict[i] = predict[i].reindex(columns=column_names)
        return predict
    
    def create_training_dataset(self, data1, training_cutoff, group_ids, max_encoder_length, max_prediction_length, unknown, known, categorical):
        target_normalizer=EncoderNormalizer()
    
        training = TimeSeriesDataSet(
            data1[data1.time_idx <= training_cutoff],
            time_idx="time_idx",
            target="demand",
            group_ids=group_ids,
            min_encoder_length=max_encoder_length ,  # keep encoder length long (as it is in the validation set)
            max_encoder_length=max_encoder_length,
            min_prediction_length=max_prediction_length,
            max_prediction_length=max_prediction_length,
            time_varying_unknown_reals=unknown,
            time_varying_known_reals=known,
            static_categoricals=categorical,
            target_normalizer=target_normalizer,
            add_relative_time_idx=True,
            add_target_scales=True,
            add_encoder_length=True,

        )
        return training


    def create_trainer(self, callbacks,
                      logger,
                     gpus=0,
                    limit_train_batches=100,
                   devices=None,
                  accelerator="auto",
                 strategy=None, num_nodes=1,
                num_processes=1,
                sync_batchnorm=False,
               enable_progress_bar=False,
              enable_checkpointing=True):
        trainer = pl.Trainer(
            enable_checkpointing=enable_checkpointing,
            max_epochs=self.epochs_tft,
            gpus=gpus,
            auto_scale_batch_size="binsearch",
            auto_lr_find=True,
            accelerator=accelerator,
            strategy=strategy,
            num_nodes=num_nodes, 
            num_processes=num_processes,
            devices=devices,
            weights_summary="top",
            gradient_clip_val=self.gradient_clip_val,
            #limit_train_batches=0.5,  # coment in for training, running valiation every 30 batches
            limit_train_batches=limit_train_batches,  # coment in for training, running valiation every 30 batches
            # fast_dev_run=True,  # comment in to check that networkor dataset has no serious bugs
            enable_progress_bar = enable_progress_bar,
            sync_batchnorm=sync_batchnorm,
            callbacks=callbacks,
            logger=logger
            )
        return trainer  

    def create_tft(self, training):
        tft = TemporalFusionTransformer.from_dataset(
            training,
            learning_rate=self.lr_tft,
            lstm_layers=self.lstm_layers,
            hidden_size=self.hidden_size,
            attention_head_size=self.attention_head_size,
            dropout=self.dropout_train,
            hidden_continuous_size=self.hidden_continuous_size,
            output_size=7,  # 7 quantiles by default
            loss=QuantileLoss(quantiles=[0.05, 0.2, 0.4, 0.5,0.6, 0.8, 0.95 ]),
            log_interval=10,  # uncomment for learning rate finder and otherwise, e.g. to 10 for logging every 10 batches
            reduce_on_plateau_patience=10,
        )
        return tft


    def fill_dates(self, data1, value=0, method=None):
        if self.use_location:
            data1["item_id"]=data1["item_id"].astype(str)+"*-+"+data1["location"].astype(str)
            #data1["item_id"]=data1.apply(lambda row: (str(row["item_id"])+"*-+"+str(row["location"])),axis=1)
            data1=data1[["timestamp","item_id","demand"]]

        data_train,_=self.transform_to_matrix(data1, value=value, method=method)
        if value!=0:
            data_train.iloc[-(self.forecast_horizon*self.backtests+self.input_window):]=data_train.iloc[-(self.forecast_horizon*self.backtests+self.input_window):].where(data_train.ffill().notna(), data_train.median().values.tolist())
            data_train=data_train.fillna(0)
        scalers=[]
        if self.normalization:
            scalers,data_train=self.min_max_scaler(data_train.set_index("Date"))
            data_train=data_train.reset_index()
    
        data1= data_train.set_index('Date')\
                 .stack()\
                 .reset_index(drop=False)\
                 .rename(columns={'level_1': 'item_id', 0: 'demand'})\
                 .sort_values(by='Date',ascending=True)
        data1.columns=["timestamp","item_id","demand"]
        if self.use_location:
            data1[["item_id", "location"]]=data1["item_id"].str.split(re.escape("*-+"),  expand=True)
            #data1["location"]=data1.apply(lambda row: row["item_id"].split("*-+")[1], axis=1)
            #data1["item_id"]=data1.apply(lambda row: row["item_id"].split("*-+")[0], axis=1)
        return scalers, data1
