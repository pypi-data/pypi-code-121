# -*- coding: utf-8 -*-
MNAME = "utilmy.deeplearning.torch.rule_encoder"
""" utils for model explanation

### pip install fire

python rule_encoder3.py test1


"""
import os,sys, collections, random, numpy as np,  glob, pandas as pd, matplotlib.pyplot as plt ;from box import Box
from copy import deepcopy
import copy
from abc import abstractmethod

from sklearn.preprocessing import OneHotEncoder, Normalizer, StandardScaler, Binarizer
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.utils import shuffle
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from turtle import forward
from sklearn.utils import shuffle
from tqdm import tqdm



#### Types


#############################################################################################
from utilmy import log, log2

def help():
    from utilmy import help_create
    ss = help_create(MNAME)
    log(ss)


#############################################################################################
def test_all():
    log(MNAME)
    test1()
    test2_new()



def test1():    
    """
    load and process data from default dataset
    if you want to training with custom datase.
    Do following step:
    def load_DataFrame(path) -> pandas.DataFrame:
        ...
        ...
        return df
    def prepro_dataset(df) -> tuple:
        ...
        ...
        return TrainX,trainY,...
    
    """    
    from box import Box ; from copy import deepcopy


    if 'ARG':
        BATCH_SIZE = None

        ARG = Box({
            'DATASET': {},
            'MODEL_INFO' : {},
        })

        MODEL_ZOO = {
            'dataonly': {'rule': 0.0},
            'ours-beta1.0': {'beta': [1.0], 'scale': 1.0, 'lr': 0.001},
            'ours-beta0.1': {'beta': [0.1], 'scale': 1.0, 'lr': 0.001},
            'ours-beta0.1-scale0.1': {'beta': [0.1], 'scale': 0.1},
            'ours-beta0.1-scale0.01': {'beta': [0.1], 'scale': 0.01},
            'ours-beta0.1-scale0.05': {'beta': [0.1], 'scale': 0.05},
            'ours-beta0.1-pert0.001': {'beta': [0.1], 'pert': 0.001},
            'ours-beta0.1-pert0.01': {'beta': [0.1], 'pert': 0.01},
            'ours-beta0.1-pert0.1': {'beta': [0.1], 'pert': 0.1},
            'ours-beta0.1-pert1.0': {'beta': [0.1], 'pert': 1.0},
                        
        }


        ### ARG.DATASET
        # ARG.seed = 42
        # ARG.DATASET.PATH =  './cardio_train.csv'
        # ARG.DATASET.URL = 'https://github.com/caravanuden/cardio/raw/master/cardio_train.csv'



        #ARG.TRAINING_CONFIG
        TRAINING_CONFIG = Box()
        TRAINING_CONFIG.SEED = 42
        TRAINING_CONFIG.DEVICE = 'cpu'
        TRAINING_CONFIG.BATCH_SIZE = 32
        TRAINING_CONFIG.EPOCHS = 1
        TRAINING_CONFIG.EARLY_STOPPING_THLD = 10
        TRAINING_CONFIG.VALID_FREQ = 1
        TRAINING_CONFIG.SAVE_FILENAME = './model.pt'
        TRAINING_CONFIG.TRAIN_RATIO = 0.7
        TRAINING_CONFIG.VAL_RATIO = 0.2
        TRAINING_CONFIG.TEST_RATIO = 0.1
        TRAINING_CONFIG.EPOCHS = 2

        ### ARG.MODEL_INFO

        ARG.MODEL_INFO.TYPE = 'dataonly' 
        PARAMS = MODEL_ZOO[ARG.MODEL_INFO.TYPE]
        ARG.MODEL_INFO.LR = PARAMS.get('lr',None)




        ### ARG.MODEL_RULE
        ARG.rule_encoder = Box()   #MODEL_RULE
        ARG.rule_encoder.seed = 42
        ARG.rule_encoder.RULE = PARAMS.get('rule',None)
        ARG.rule_encoder.SCALE = PARAMS.get('scale',1.0)
        ARG.rule_encoder.PERT = PARAMS.get('pert',0.1)
        ARG.rule_encoder.BETA = PARAMS.get('beta',[1.0])
        beta_param = ARG.rule_encoder.BETA

        from torch.distributions.beta import Beta
        if   len(beta_param) == 1:  ARG.rule_encoder.ALPHA_DIST = Beta(float(beta_param[0]), float(beta_param[0]))
        elif len(beta_param) == 2:  ARG.rule_encoder.ALPHA_DIST = Beta(float(beta_param[0]), float(beta_param[1]))

        ARG.rule_encoder.NAME = ''
        ARG.rule_encoder.RULE_IND = 2
        ARG.rule_encoder.RULE_THRESHOLD = 129.5
        ARG.rule_encoder.SRC_OK_RATIO = 0.3
        ARG.rule_encoder.SRC_UNOK_RATIO = 0.7
        ARG.rule_encoder.TARGET_RULE_RATIO = 0.7
        ARG.rule_encoder.ARCHITECT = [
            20,
            100,
            16
        ]


        ### ARG.MODEL_TASK
        
        ARG.data_encoder = Box()   #MODEL_TASK
        ARG.data_encoder.seed = 42
        ARG.data_encoder.NAME = ''
        ARG.data_encoder.ARCHITECT = [
            20,
            100,
            16
        ]

        ARG.merge_model = Box()
        ARG.merge_model.NAME = ''
        ARG.merge_model.seed = 42
        ARG.merge_model.SKIP = False
        ARG.merge_model.MERGE = 'cat'
        ARG.merge_model.ARCHITECT = {
            'decoder': [
            32,  
            100,
            1
        ]
        }
        ARG.merge_model.TRAINING_CONFIG = Box()
        ARG.merge_model.TRAINING_CONFIG = TRAINING_CONFIG

    """
    load and process data from default dataset
    if you want to training with custom datase.
    Do following step:
    def load_DataFrame(path) -> pandas.DataFrame:
        ...
        ...
        return df

    def prepro_dataset(df) -> tuple:
        ...
        ...
        return TrainX,trainY,...
    
    """


    




    ARG_copy = deepcopy(ARG)
    ARG_copy.rule_encoder.ARCHITECT = [9,100,16]
    ARG_copy.data_encoder.ARCHITECT = [9,100,16]
    ARG_copy.merge_model.TRAINING_CONFIG.SAVE_FILENAME = './model_x9.pt'
    load_DataFrame = RuleEncoder_Create.load_DataFrame   
    prepro_dataset = RuleEncoder_Create.prepro_dataset
    model = MergeEncoder_Create(ARG_copy)
    model.build()        
    model.training(load_DataFrame,prepro_dataset) 

    model.save_weight('ztmp/model_x9.pt') 
    model.load_weights('ztmp/model_x9.pt')
    inputs = torch.randn((1,9)).to(model.device)
    outputs = model.predict(inputs)



def test2_new():    
    """
    load and process data from default dataset
    if you want to training with custom datase.
    Do following step:
    def load_DataFrame(path) -> pandas.DataFrame:
        ...
        ...
        return df
    def prepro_dataset(df) -> tuple:
        ...
        ...
        return TrainX,trainY,...
    
    """    
    from box import Box ; from copy import deepcopy
    ARG = Box({
        'DATASET': {},
        'MODEL_INFO' : {},
    })


    PARAMS = Box()

    if 'ARG':
        BATCH_SIZE = None

        MODEL_ZOO = {
            'dataonly': {'rule': 0.0},
            'ours-beta1.0': {'beta': [1.0], 'scale': 1.0, 'lr': 0.001},
            'ours-beta0.1': {'beta': [0.1], 'scale': 1.0, 'lr': 0.001},
            'ours-beta0.1-scale0.1': {'beta': [0.1], 'scale': 0.1},
            'ours-beta0.1-scale0.01': {'beta': [0.1], 'scale': 0.01},
            'ours-beta0.1-scale0.05': {'beta': [0.1], 'scale': 0.05},
            'ours-beta0.1-pert0.001': {'beta': [0.1], 'pert': 0.001},
            'ours-beta0.1-pert0.01': {'beta': [0.1], 'pert': 0.01},
            'ours-beta0.1-pert0.1': {'beta': [0.1], 'pert': 0.1},
            'ours-beta0.1-pert1.0': {'beta': [0.1], 'pert': 1.0},
                        
        }


        ### ARG.DATASET
        # ARG.seed = 42
        # ARG.DATASET.PATH =  './cardio_train.csv'
        # ARG.DATASET.URL = 'https://github.com/caravanuden/cardio/raw/master/cardio_train.csv'


        ### ARG.MODEL_INFO
        ARG.MODEL_INFO.TYPE = 'dataonly' 
        PARAMS = MODEL_ZOO[ARG.MODEL_INFO.TYPE]


        #TRAINING_CONFIG
        TRAINING_CONFIG = Box()
        TRAINING_CONFIG.LR = PARAMS.get('lr',None)
        TRAINING_CONFIG.SEED = 42
        TRAINING_CONFIG.DEVICE = 'cpu'
        TRAINING_CONFIG.BATCH_SIZE = 32
        TRAINING_CONFIG.EPOCHS = 1
        TRAINING_CONFIG.EARLY_STOPPING_THLD = 10
        TRAINING_CONFIG.VALID_FREQ = 1
        TRAINING_CONFIG.SAVE_FILENAME = './model.pt'
        TRAINING_CONFIG.TRAIN_RATIO = 0.7
        TRAINING_CONFIG.VAL_RATIO = 0.2
        TRAINING_CONFIG.TEST_RATIO = 0.1
        TRAINING_CONFIG.EPOCHS = 2

    

    # load_DataFrame = RuleEncoder_Create.load_DataFrame   
    prepro_dataset = RuleEncoder_Create.prepro_dataset




    #### SEPARATE the models completetly, and create duplicate

    ### data_encoder  #################################
    ARG.data_encoder = Box()   #MODEL_TASK
    ARG.data_encoder.NAME = ''
    ARG.data_encoder.ARCHITECT = [ 9, 100, 16 ]
    ARG.data_encoder.dataset = Box()
    ARG.data_encoder.dataset.dirin = "/"
    ARG.data_encoder.dataset.colsy =  'solvey'
    ARG.data_encoder.seed = 42
    data_encoder = DataEncoder_Create(ARG.data_encoder)

    ### rule_encoder  #################################
    ARG.rule_encoder = Box()   #MODEL_RULE

    ARG.rule_encoder.dataset = Box()
    ARG.rule_encoder.dataset.dirin = "/"
    ARG.rule_encoder.dataset.colsy =  'solvey'


    ARG.rule_encoder.RULE = PARAMS.get('rule',None)
    ARG.rule_encoder.SCALE = PARAMS.get('scale',1.0)
    ARG.rule_encoder.PERT = PARAMS.get('pert',0.1)
    ARG.rule_encoder.BETA = PARAMS.get('beta',[1.0])
    beta_param = ARG.rule_encoder.BETA

    from torch.distributions.beta import Beta
    if   len(beta_param) == 1:  ARG.rule_encoder.ALPHA_DIST = Beta(float(beta_param[0]), float(beta_param[0]))
    elif len(beta_param) == 2:  ARG.rule_encoder.ALPHA_DIST = Beta(float(beta_param[0]), float(beta_param[1]))



    ARG.rule_encoder.NAME = ''
    ARG.rule_encoder.RULE_IND = 2
    ARG.rule_encoder.RULE_THRESHOLD = 129.5
    ARG.rule_encoder.SRC_OK_RATIO = 0.3
    ARG.rule_encoder.SRC_UNOK_RATIO = 0.7
    ARG.rule_encoder.TARGET_RULE_RATIO = 0.7
    ARG.rule_encoder.ARCHITECT = [9,100,16]
    ARG.rule_encoder.seed = 42
    rule_encoder = RuleEncoder_Create(ARG.rule_encoder )

    



    ### merge_model  #################################
    ARG.merge_model = Box()
    ARG.merge_model.NAME = ''
    ARG.merge_model.seed = 42
    ARG.merge_model.SKIP = False
    ARG.merge_model.MERGE = 'cat'
    ARG.merge_model.ARCHITECT = { 'decoder': [ 32, 100, 1 ] }

    ARG.merge_model.dataset = Box()
    ARG.merge_model.dataset.dirin = "/"
    ARG.merge_model.dataset.colsy =  'solvey'
    ARG.merge_model.TRAINING_CONFIG = Box()
    ARG.merge_model.TRAINING_CONFIG = TRAINING_CONFIG
    model = MergeEncoder_Create(ARG, rule_encoder=rule_encoder, data_encoder=data_encoder)


    #### Run Model   ###################################################
    load_DataFrame = RuleEncoder_Create.load_DataFrame   
    prepro_dataset = RuleEncoder_Create.prepro_dataset
    model.build()        
    model.training(load_DataFrame,prepro_dataset) 


    model.save_weight('ztmp/model_x9.pt') 
    model.load_weights('ztmp/model_x9.pt')
    inputs = torch.randn((1,9)).to(model.device)
    outputs = model.predict(inputs)
    print(outputs)



#############################################################################################
####  Common Prepro #########################################################################

def dataset_load() -> pd.DataFrame:
    from sklearn.datasets import fetch_covtype
    df = fetch_covtype(return_X_y=False, as_frame=True)
    df =df.data
    #   log(df)
    #   log(df.columns)
    df = df.iloc[:500, :10]
    #   log(df)
    return df


def dataset_load_prepro(arg):
    if hasattr(self.arg,'training_config'):
        train_ratio = self.arg.TRAINING_CONFIG.TRAIN_RATIO
        test_ratio = self.arg.TRAINING_CONFIG.TEST_RATIO
        val_ratio =   self.arg.TRAINING_CONFIG.TEST_RATIO
    else: 
        train_ratio = self.arg.merge_model.TRAINING_CONFIG.TRAIN_RATIO
        test_ratio = self.arg.merge_model.TRAINING_CONFIG.TEST_RATIO
        val_ratio =   self.arg.merge_model.TRAINING_CONFIG.TEST_RATIO


    ##########################################################
    df = dataset_load()
    coly  = 'Slope'  # df.columns[-1]
    y_raw = df[coly]
    X_raw = df.drop([coly], axis=1)

    X_column_trans = ColumnTransformer(
            [(col, StandardScaler() if not col.startswith('Soil_Type') else Binarizer(), [col]) for col in X_raw.columns],
            remainder='passthrough')

    y_trans = StandardScaler()

    X = X_column_trans.fit_transform(X_raw)
    # y = y_trans.fit_transform(y_raw.array.reshape(1, -1))
    y = y_trans.fit_transform(y_raw.values.reshape(-1, 1))

    ### Binarize
    y = np.array([  1 if yi >0.5 else 0 for yi in y])

    seed= 42
    train_X, test_X, train_y, test_y = train_test_split(X,  y,  test_size=1 - train_ratio, random_state=seed)
    valid_X, test_X, valid_y, test_y = train_test_split(test_X, test_y, test_size= test_ratio / (test_ratio + val_ratio), random_state=seed)
    return (np.float32(train_X), np.float32(train_y), np.float32(valid_X), np.float32(valid_y), np.float32(test_X), np.float32(test_y) )







#############################################################################################
class BaseModel(object):
    """
    This is BaseClass for model create

    Method:
        create_model : Initialize Model (torch.nn.Module)
        evaluate: 
        prepro_dataset:  (conver pandas.DataFrame to appropriate format)
        create_loss :   Initialize Loss Function 
        training:   starting training
        build: create model, loss, optimizer (call before training)
        train: equavilent to model.train() in pytorch (auto enable dropout,vv..vv..)
        eval: equavilent to model.eval() in pytorch (auto disable dropout,vv..vv..)
        device_setup: 
        load_DataFrame: read pandas
        load_weight: 
        save_weight: 
        predict : 
    """
    
    def __init__(self,arg):
        self.arg = Box(arg)
        self._device = self.device_setup(arg)
        self.losser = None
        self.is_train = False
        
    @abstractmethod
    def create_model(self,) -> torch.nn.Module:
    #   raise NotImplementedError
        log("       model is building")
    @abstractmethod
    def evaluate(self):
        raise NotImplementedError

    @abstractmethod
    def prepro_dataset(self,csv) -> pd.DataFrame:
        raise NotImplementedError
    
    @abstractmethod
    def create_loss(self,) -> torch.nn.Module:
        log("       loss is building")
        # raise NotImplementedError

    @abstractmethod
    def training(self,):
        raise NotImplementedError

    @property
    def device(self,):
        return self._device
    
    @device.setter
    def device(self,value):
        if isinstance(value,torch.device):
          self._device = value
        elif isinstance(value,str):
          self._device = torch.device(value)
        else:
          raise TypeError("device must be str or torch.device")

    def build(self,):
        self.net = self.create_model().to(self.device)
        self.loss_calc= self.create_loss().to(self.device)
        # self.loss_calc= 
        self.is_train = False
    
    def train(self): # equivalent model.train() in pytorch
        self.is_train = True
        self.net.train()

    def eval(self):     # equivalent model.eval() in pytorch
        self.is_train = False
        self.net.eval()

    def device_setup(self,arg):
        device = getattr(arg,'device','cpu')
        seed   = arg.seed if hasattr(arg,'seed') else 42
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)

        if 'gpu' in device :
            try :
                torch.cuda.manual_seed(seed)
                torch.cuda.manual_seed_all(seed)
                torch.backends.cudnn.deterministic = True
                torch.backends.cudnn.benchmark = False
            except Exception as e:
                log(e)
                device = 'cpu'
        return device

    def load_DataFrame(self,path=None)-> pd.DataFrame:
        if path:
            log(f"reading csv from {path}")
            self.df = pd.read_csv(path,delimiter=';')
            return self.df
        if os.path.isfile(self.arg.dataset.path):
            log(f"reading csv from arg.DATASET.PATH :{self.arg.dataset.path}")
            self.df = pd.read_csv(self.arg.dataset.path,delimiter=';')
            return self.df
        else:
            import requests
            import io
            r = requests.get(self.arg.dataset.url)
            log(f"Reading csv from arg.DATASET.URL")
            if r.status_code ==200:
                self.df = pd.read_csv(io.BytesIO(r.content),delimiter=';')
            else:
                raise Exception("Can't read data, status_code: {r.status_code}")
            
            return self.df


    def load_weights(self, path):
        assert os.path.isfile(path),f"{path} does not exist"
        try:
          ckp = torch.load(path,map_location=self.device)
        except Exception as e:
          log(e)
          log(f"can't load the checkpoint from {path}")  
        if isinstance(ckp,collections.OrderedDict):
          self.net.load_state_dict(ckp)
        else:
          self.net.load_state_dict(ckp['state_dict'])
    
    def save_weight(self,path,meta_data=None):
      os.makedirs(os.path.dirname(path),exist_ok=True)
      ckp = {
          'state_dict':self.net.state_dict(),
      }
      if meta_data:
        if isinstance(meta_data,dict):
            ckp.update(meta_data)
        else:
            ckp.update({'meta_data':meta_data,})
            
        
      torch.save(ckp,path)

    def predict(self,x,**kwargs):
        # raise NotImplementedError
        output = self.net(x,**kwargs)
        return output 


##############################################################################################
class MergeEncoder_Create(BaseModel):
    """
    """
    def __init__(self,arg, data_encoder=None, rule_encoder=None):
        """_summary_

        Args:
            arg (_type_): _description_
            data_encoder (_type_, optional): _description_. Defaults to None.
            rule_encoder (_type_, optional): _description_. Defaults to None.
            rule_encoder and data_encoder should got following attributes:

                attributes:
                    self.net : torch.nn.Module
                method:
                    self.build():
                    self.create_model() :  return net
                    


                
        
        """
        super(MergeEncoder_Create,self).__init__(arg)
        if data_encoder is None:
            self.data_encoder = DataEncoder_Create(arg.data_encoder)
        else:
            self.data_encoder = (data_encoder)
        if rule_encoder is None:
            self.rule_encoder = RuleEncoder_Create(arg.rule_encoder)
        else:
            self.rule_encoder = (rule_encoder)

        

    def create_model(self,):
        super(MergeEncoder_Create,self).create_model()
        # merge = self.arg.merge
        merge = getattr(self.arg.merge_model,'MERGE','add')
        skip = getattr(self.arg.merge_model,'SKIP',False)
        
        dims = self.arg.merge_model.ARCHITECT.decoder
        class Modelmerge(torch.nn.Module):
            def __init__(self,rule_encoder,data_encoder,dims,merge,skip):
                super(Modelmerge, self).__init__()

                #### rule encoder
                self.rule_encoder_net = copy.copy(rule_encoder.net)
                self.rule_encoder_net.load_state_dict(rule_encoder.net.state_dict())

                ###3 data encoder
                self.data_encoder_net = copy.copy(data_encoder.net)
                self.data_encoder_net.load_state_dict(data_encoder.net.state_dict())

                ##### Merge
                self.merge = merge
                self.skip = skip
                self.input_type = 'seq'
                if merge == 'cat':
                    self.input_dim_decision_block = self.rule_encoder_net.output_dim * 2
                elif merge == 'add':
                    self.input_dim_decision_block = self.data_encoder_net.output_dim

                # self.net = nn.Sequential()
                self.net = []
                input_dim = dims[0]
                for layer_dim in dims[1:-1]:
                    self.net.append(nn.Linear(input_dim, layer_dim))
                    self.net.append(nn.ReLU())
                    input_dim = layer_dim
                self.net.append(nn.Linear(input_dim, dims[-1]))
                self.net.append(nn.Sigmoid())

                self.net = nn.Sequential(*self.net)

            def forward(self, x,**kwargs):
            # merge: cat or add
                alpha = kwargs.get('alpha',0) # default only use rule_z
                # scale = kwargs.get('scale',1)
                rule_z = self.rule_encoder_net(x)
                
                data_z = self.data_encoder_net(x)

                if self.merge == 'add':
                    z = alpha*rule_z + (1-alpha)*data_z
                elif self.merge == 'cat':
                    z = torch.cat((alpha*rule_z, (1-alpha)*data_z), dim=-1)
                elif self.merge == 'equal_cat':
                    z = torch.cat((rule_z, data_z), dim=-1)

                if self.skip:
                    if self.input_type == 'seq':
                        return self.net(z) + x[:, -1, :]
                    else:
                        return self.net(z) + x    # predict delta values
                else:
                    return self.net(z)    # predict absolute values
        return Modelmerge(self.rule_encoder,self.data_encoder,dims,merge,skip)

    def build(self):
        # super(MergeEncoder_Create,self).build()
        log("rule_encoder:")
        self.rule_encoder.build()
        log("data_encoder:")
        self.data_encoder.build()
        log("MergeModel:")
        self.net = self.create_model().to(self.device)
        self.loss_calc= self.create_loss()#.to(self.device)
        self.optimizer = torch.optim.Adam(self.net.parameters())
        
    def create_loss(self,):
        super(MergeEncoder_Create,self).create_loss()
        rule_loss_calc= self.rule_encoder.loss_calc
        data_loss_calc= self.data_encoder.loss_calc

        class MergeLoss(torch.nn.Module):

            def __init__(self,rule_loss_calc,data_loss_calc):
                super(MergeLoss,self).__init__()
                self.rule_loss_calc= rule_loss_calc
                self.data_loss_calc= data_loss_calc

            def forward(self,output,target,alpha=0,scale=1):
                
                rule_loss = self.rule_loss_calc(output,target.reshape(output.shape))
                data_loss = self.data_loss_calc(output,target.reshape(output.shape))                
                result = rule_loss * alpha * scale + data_loss * (1-alpha)
                # result = rule_loss + data_loss
                return result
        return MergeLoss(rule_loss_calc,data_loss_calc)

    def prepro_dataset(self,df=None):
        if df is None:              
            df = self.df     # if there is no dataframe feeded , get df from model itself

        coly = 'cardio'
        y     = df[coly]
        X_raw = df.drop([coly], axis=1)

        # log("Target class ratio:")
        # log("# of y=1: {}/{} ({:.2f}%)".format(np.sum(y==1), len(y), 100*np.sum(y==1)/len(y)))
        # log("# of y=0: {}/{} ({:.2f}%)\n".format(np.sum(y==0), len(y), 100*np.sum(y==0)/len(y)))

        column_trans = ColumnTransformer(
            [('age_norm', StandardScaler(), ['age']),
            ('height_norm', StandardScaler(), ['height']),
            ('weight_norm', StandardScaler(), ['weight']),
            ('gender_cat', OneHotEncoder(), ['gender']),
            ('ap_hi_norm', StandardScaler(), ['ap_hi']),
            ('ap_lo_norm', StandardScaler(), ['ap_lo']),
            ('cholesterol_cat', OneHotEncoder(), ['cholesterol']),
            ('gluc_cat', OneHotEncoder(), ['gluc']),
            ('smoke_cat', OneHotEncoder(), ['smoke']),
            ('alco_cat', OneHotEncoder(), ['alco']),
            ('active_cat', OneHotEncoder(), ['active']),
            ], remainder='passthrough'
        )

        X = column_trans.fit_transform(X_raw)
        nsamples = X.shape[0]
        X_np = X.copy()


        ######## Rule : higher ap -> higher risk   #####################################
        """  Identify Class y=0 /1 from rule 1

        """
        if 'rule1':
            rule_threshold = self.arg.rule_encoder.RULE_THRESHOLD
            rule_ind       = self.arg.rule_encoder.RULE_IND
            rule_feature   = 'ap_hi'
            src_unok_ratio = self.arg.rule_encoder.SRC_OK_RATIO
            src_ok_ratio   = self.arg.rule_encoder.SRC_UNOK_RATIO

            #### Ok cases: nornal
            low_ap_negative  = (df[rule_feature] <= rule_threshold) & (df[coly] == 0)    # ok
            high_ap_positive = (df[rule_feature] > rule_threshold)  & (df[coly] == 1)    # ok

            ### Outlier cases (from rule)
            low_ap_positive  = (df[rule_feature] <= rule_threshold) & (df[coly] == 1)    # unok
            high_ap_negative = (df[rule_feature] > rule_threshold)  & (df[coly] == 0)    # unok




        #### Merge rules ##############################################
        # Samples in ok group
        idx_ok = low_ap_negative | high_ap_positive


        # Samples in Unok group
        idx_unok = low_ap_negative | high_ap_positive



        ##############################################################################
        # Samples in ok group
        X_ok = X[ idx_ok ]
        y_ok = y[ idx_ok ]
        y_ok = y_ok.to_numpy()
        X_ok, y_ok = shuffle(X_ok, y_ok, random_state=0)
        num_ok_samples = X_ok.shape[0]


        # Samples in Unok group
        X_unok = X[ idx_unok ]
        y_unok = y[ idx_unok ]
        y_unok = y_unok.to_numpy()
        X_unok, y_unok = shuffle(X_unok, y_unok, random_state=0)
        num_unok_samples = X_unok.shape[0]


        ######### Build a source dataset
        n_from_unok = int(src_unok_ratio * num_unok_samples)
        n_from_ok   = int(n_from_unok * src_ok_ratio / (1- src_ok_ratio))

        X_src = np.concatenate((X_ok[:n_from_ok], X_unok[:n_from_unok]), axis=0)
        y_src = np.concatenate((y_ok[:n_from_ok], y_unok[:n_from_unok]), axis=0)

        # log("Source dataset statistics:")
        # log("# of samples in ok group: {}".format(n_from_ok))
        # log("# of samples in Unok group: {}".format(n_from_unok))
        # log("ok ratio: {:.2f}%".format(100 * n_from_ok / (X_src.shape[0])))


        ##### Split   #########################################################################
        seed= 42
        if hasattr(self.arg,'training_config'):
            train_ratio = self.arg.TRAINING_CONFIG.TRAIN_RATIO
            test_ratio = self.arg.TRAINING_CONFIG.TEST_RATIO
            val_ratio =   self.arg.TRAINING_CONFIG.TEST_RATIO
        else: 
            train_ratio = self.arg.merge_model.TRAINING_CONFIG.TRAIN_RATIO
            test_ratio = self.arg.merge_model.TRAINING_CONFIG.TEST_RATIO
            val_ratio =   self.arg.merge_model.TRAINING_CONFIG.TEST_RATIO
        train_X, test_X, train_y, test_y = train_test_split(X_src,  y_src,  test_size=1 - train_ratio, random_state=seed)
        valid_X, test_X, valid_y, test_y = train_test_split(test_X, test_y, test_size= test_ratio / (test_ratio + val_ratio), random_state=seed)
        return (train_X, train_y, valid_X,  valid_y, test_X,  test_y, )
        


    def training(self,load_DataFrame=None,prepro_dataset=None):

        # training with load_DataFrame and prepro_data function or default funtion in self.method

        if load_DataFrame:
            df = load_DataFrame(self)
        else:
            df = self.load_DataFrame()
        if prepro_dataset:
           train_X, train_y, valid_X,  valid_y, test_X,  test_y = prepro_dataset(self,df)
        else:
            train_X, train_y, valid_X,  valid_y, test_X,  test_y = self.prepro_dataset(df)  
        if hasattr(self.arg,'TRINING_CONFIG'):
            batch_size = self.arg.TRAINING_CONFIG.BATCH_SIZE
        else:
            batch_size = self.arg.merge_model.TRAINING_CONFIG.BATCH_SIZE
        train_loader, valid_loader, test_loader =  dataloader_create(train_X, train_y, 
                                                                    valid_X,  valid_y,
                                                                    test_X,  test_y,
                                                                    device=self.device,
                                                                    batch_size=batch_size)
        if hasattr(self.arg,'TRAINING_CONFIG'):
            EPOCHS = self.arg.TRAINING_CONFIG.EPOCHS
        else:
            EPOCHS = self.arg.merge_model.TRAINING_CONFIG.EPOCHS
        n_train = len(train_loader)
        n_val = len(valid_loader)
        
        for epoch in tqdm(range(1,EPOCHS+1)):
            self.train()
            loss_train = 0
            with torch.autograd.set_detect_anomaly(True): 
                for inputs,targets in tqdm(train_loader,total=n_train, desc='training'):
                    if   self.arg.MODEL_INFO.TYPE.startswith('dataonly'):  alpha = 0.0
                    elif self.arg.MODEL_INFO.TYPE.startswith('ruleonly'):  alpha = 1.0
                    elif self.arg.MODEL_INFO.TYPE.startswith('ours'):      alpha = self.arg.rule_encoder.ALPHA_DIST.sample().item()
                    
                    predict = self.net(inputs,alpha=alpha)
                    self.optimizer.zero_grad()
                    # self.optimizer.step()
                    scale =1
                    loss = self.loss_calc(predict,targets,alpha=alpha,scale=scale)
                    # loss.grad
                    loss.backward()
                    self.optimizer.step()
                    loss_train += loss * inputs.size(0)
                loss_train /= len(train_loader.dataset) # mean on dataset

            loss_val = 0
            self.eval()
            with torch.no_grad():
                for inputs,targets in tqdm(valid_loader, total=n_val, desc='validating'):
                    predict = self.predict(inputs)
                    self.optimizer.zero_grad()
                    scale=1
                    loss = self.loss_calc(predict,targets,alpha=alpha,scale=scale)
                    
                    loss_val += loss * inputs.size(0)
            loss_val /= len(valid_loader.dataset) # mean on dataset
            if hasattr(self.arg,'TRAINING_CONFIG'):
                path_save = self.arg.TRAINING_CONFIG.SAVE_FILENAME
            else:
                path_save = self.arg.merge_model.TRAINING_CONFIG.SAVE_FILENAME
            self.save_weight(
                path = path_save,
                meta_data = {
                    'epoch' : epoch,
                    'loss_train': loss_train,
                    'loss_val': loss_val,
                }
            )






##############################################################################################
class RuleEncoder_Create(BaseModel):
    """

    Args:
        BaseModel (_type_): _description_
    """
    def __init__(self, arg:dict):
        super(RuleEncoder_Create,self).__init__(arg)
        # self.rule_ind = arg.rule_encoder.RULE_IND
        # self.pert_coeff = arg.rule_encoder.PERT
        self.rule_ind = arg.RULE_IND
        self.pert_coeff = arg.PERT
    def create_model(self):
        super(RuleEncoder_Create,self).create_model()
        # dims = self.arg.rule_encoder.ARCHITECT
        dims = self.arg.ARCHITECT
        rule_ind = self.rule_ind
        pert_coeff = self.pert_coeff
        def get_perturbed_input(input_tensor, pert_coeff):
            '''
            X = X + pert_coeff*rand*X
            return input_tensor + input_tensor*pert_coeff*torch.rand()
            '''
            device = input_tensor.device
            result =  input_tensor + torch.abs(input_tensor)*pert_coeff*torch.rand(input_tensor.shape, device=device)
            return result

        class RuleEncoder(torch.nn.Module):
            def __init__(self,arg,dims=[20,100,16]):
                super(RuleEncoder, self).__init__()
                self.dims = dims 
                self.output_dim = dims[-1]
                # self.net = nn.Sequential()
                self.net = []
                input_dim = dims[0]
                for layer_dim in dims[1:-1]:

                    self.net.append(torch.nn.Linear(input_dim, layer_dim))

                    self.net.append(torch.nn.ReLU())
                    input_dim = layer_dim
                self.net.append(torch.nn.Linear(input_dim, dims[-1]))
                self.net = torch.nn.Sequential(*self.net)

            def forward(self, x,**kwargs):

                x[:,rule_ind] = get_perturbed_input(x[:,rule_ind], pert_coeff)

                return self.net(x)
            
            # def __call__(self,x,**kwargs):
            #     return forward(self,x,**kwargs)

        return RuleEncoder(self.arg,dims)   

    def create_loss(self,) -> torch.nn.Module:
        super(RuleEncoder_Create,self).create_loss()
        class LossRule(torch.nn.Module):
            
            def __init__(self):
                super(LossRule,self).__init__()
                # self.relu = torch.nn.ReLU()

            def forward(self,output,target):
                # return torch.mean(self.relu(output-target))
                return torch.mean(torch.nn.functional.relu(output-target))

        return LossRule()

    def load_DataFrame(self,) -> pd.DataFrame:
        from sklearn.datasets import fetch_covtype
        df = fetch_covtype(return_X_y=False, as_frame=True)
        df =df.data
        df = df.iloc[:500, :10]
        return df

    def prepro_dataset(self,df):
        if df is None:
            df = self.df
        coly  = 'Slope'  # df.columns[-1]
        y_raw = df[coly]
        X_raw = df.drop([coly], axis=1)

        X_column_trans = ColumnTransformer(
                [(col, StandardScaler() if not col.startswith('Soil_Type') else Binarizer(), [col]) for col in X_raw.columns],
                remainder='passthrough')

        y_trans = StandardScaler()

        X = X_column_trans.fit_transform(X_raw)
        # y = y_trans.fit_transform(y_raw.array.reshape(1, -1))
        y = y_trans.fit_transform(y_raw.values.reshape(-1, 1))

        ### Binarize
        y = np.array([  1 if yi >0.5 else 0 for yi in y])
        if hasattr(self.arg,'training_config'):
            train_ratio = self.arg.TRAINING_CONFIG.TRAIN_RATIO
            test_ratio = self.arg.TRAINING_CONFIG.TEST_RATIO
            val_ratio =   self.arg.TRAINING_CONFIG.TEST_RATIO
        else: 
            train_ratio = self.arg.merge_model.TRAINING_CONFIG.TRAIN_RATIO
            test_ratio = self.arg.merge_model.TRAINING_CONFIG.TEST_RATIO
            val_ratio =   self.arg.merge_model.TRAINING_CONFIG.TEST_RATIO
        seed= 42
        train_X, test_X, train_y, test_y = train_test_split(X,  y,  test_size=1 - train_ratio, random_state=seed)
        valid_X, test_X, valid_y, test_y = train_test_split(test_X, test_y, test_size= test_ratio / (test_ratio + val_ratio), random_state=seed)
        return (np.float32(train_X), np.float32(train_y), np.float32(valid_X), np.float32(valid_y), np.float32(test_X), np.float32(test_y) )




##############################################################################################
class DataEncoder_Create(BaseModel):
    """
    DataEncoder

    Method:
        create_model : 
        create_loss : 
    """
    def __init__(self,arg):
        super(DataEncoder_Create,self).__init__(arg)

    def create_model(self):
        super(DataEncoder_Create,self).create_model()
        # dims = self.arg.data_encoder.ARCHITECT
        dims = self.arg.ARCHITECT
        class DataEncoder(torch.nn.Module):
            def __init__(self,dims=[20,100,16]):
                super(DataEncoder, self).__init__()
                self.dims = dims 
                self.output_dim = dims[-1]
                # self.net = nn.Sequential()
                self.net = []
                input_dim = dims[0]
                for layer_dim in dims[:-1]:
                    self.net.append(nn.Linear(input_dim, layer_dim))
                    self.net.append(nn.ReLU())
                    input_dim = layer_dim
                self.net.append(nn.Linear(input_dim, dims[-1]))
                self.net = nn.Sequential(*self.net)

            def forward(self, x,**kwargs):
                return self.net(x)

        return DataEncoder(dims)

    def create_loss(self) -> torch.nn.Module:
        super(DataEncoder_Create,self).create_loss()
        return torch.nn.BCELoss()






##############################################################################################
def dataloader_create(train_X=None, train_y=None, valid_X=None, valid_y=None, test_X=None, test_y=None,device=None,batch_size=None):
    # batch_size = batch_size
    train_loader, valid_loader, test_loader = None, None, None

    if train_X is not None :
        train_X, train_y = torch.tensor(train_X, dtype=torch.float32, device=device), torch.tensor(train_y, dtype=torch.float32, device=device)
        train_loader = DataLoader(TensorDataset(train_X, train_y), batch_size=batch_size, shuffle=True)
        # log("data size", len(train_X) )

    if valid_X is not None :
        valid_X, valid_y = torch.tensor(valid_X, dtype=torch.float32, device=device), torch.tensor(valid_y, dtype=torch.float32, device=device)
        valid_loader = DataLoader(TensorDataset(valid_X, valid_y), batch_size=batch_size)
        # log("data size", len(valid_X)  )

    if test_X  is not None :
        test_X, test_y   = torch.tensor(test_X,  dtype=torch.float32, device=device), torch.tensor(test_y, dtype=torch.float32, device=device)
        test_loader  = DataLoader(TensorDataset(test_X, test_y), batch_size=batch_size)
        # log("data size:", len(test_X) )

    return train_loader, valid_loader, test_loader



##############################################################################################



 




###################################################################################################
if __name__ == "__main__":
    import fire 
    fire.Fire()
    test_all()
