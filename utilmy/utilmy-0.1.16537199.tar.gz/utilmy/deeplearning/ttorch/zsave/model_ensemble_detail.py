# -*- coding: utf-8 -*-
""" utils for model merge
Doc::

        https://discuss.pytorch.org/t/combining-trained-models-in-pytorch/28383/45

        https://discuss.pytorch.org/t/merging-3-models/66230/3



"""
import os, random, numpy as np, glob, pandas as pd, matplotlib.pyplot as plt ;from box import Box
from copy import deepcopy
from abc import abstractmethod

from sklearn.preprocessing import OneHotEncoder, Normalizer, StandardScaler, Binarizer
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.utils import shuffle

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset

#############################################################################################
from utilmy import log, log2

def help():
    """function help        
    """
    from utilmy import help_create
    ss = HELP + help_create(MNAME)
    log(ss)


#############################################################################################
if 'comments':
    """
    class ModelA :
        input XA
        ...
        get_embedding_fromlayer(layer_id= 1)


    class modelB:
        input XB
        ...
        get_embedding_fromlayer(layer_id= 1)


    class mergeModel(BaseModel):
      def __init__(self, modelA, modelB, **kw) -> None:
          super().__init__()
          self.Xinput_dim  = XA_dim + Xb_dim
          self.modelHead = MLP([ Xinput_dim,100, 300, 500]) 

      def forward(self, X1, X2):
            XAout = modelA.get_embedding_fromlayer(X1)
            XBout = modelB.get_embedding_fromlayer(X2)

            Xmerge_input  = self.concat(XAout, XBout, method='stack') 

            Xmergeout = self.modelHead(Xmerge_input)
            return Xmergeout
        

        def loss_task_calc(self, model, batch_train_x, loss_task_func, output, arg:dict):
      

        def train():

        for (X1,X2), Y in train_laoder:

            optimizer.zero_grad()
            ypred = self.modelMerge(X1, X2)

          Merg 

    class BaseModel(object):
        This is BaseClass for model create
        Method:
            create_model : Initialize Model (torch.nn.Module)
            create_loss :   Initialize Loss Function 

            build_devicesetup: 
            build: create model, loss, optimizer (call before training)

            training:   starting training
            train: equavilent to model.train() in pytorch (auto enable dropout,vv..vv..)
            eval: equavilent to model.eval() in pytorch (auto disable dropout,vv..vv..)
            predict :
            encode :
            evaluate: 
            load: 
            save: 
    


MergeModel:
   merge embA, embB
   + Custom Head task (MLP, classfier)



for Image, tabular (ie like MLP type model)


here....

    mergeModel(modelA, modelB, **params)
      Xinput_dim  = XA_dim + Xb_dim
      modelMerge = MLP([ Xinput_dim,100, 300, 500]) 

      def forward(self,X)
            XAout = modelA.get_embedding_fromlayer(X)

            XBout = modelB.get_embedding_fromlayer(X)

            Xmege_input  = concat(XAout, XBout) 



            Xmergeout = modelMerge(Xmerge_input)
    class MergeModel_create(BaseModel):

        def __init__(self,arg, modelB=None, modelA=None, architecture:dict):

            architecture = Box(architecture)

            Args:
                arg (_type_): _description_
                modelB (_type_, optional): _description_. Defaults to None.
                modelA (_type_, optional): _description_. Defaults to None.
                modelA and modelB should got following attributes:

                modelMerge = MLP( architecture.mlp.layer_dim_list )   ### ok

                    attributes:
                        self.head_task : torch.nn.Module
                        self.modelA_is_train  
                        self.modelB_is_train

                    method:
                        self.__init__(modelA,modelB,**params)
                        self.create_loss()
                        self.create_model() :  return net
                        self.build():
                        
                        self.training()
                        self.evaluate()
                        self.encode  :  to output the embeddings after merge.YES< but more TRICKY PART, so a method is needed ## equavilant to __call__(self,X). ok
                        self.save
                        self.load
                        ### merge_input is implemented in __call__()

    mergmodel_C = MergeModel( ...)
    mergmodel_D = MergeModel( ...)

    mergmodel_E = MergeModel(  mergmodel_C, mergmodel_D )

    We can  re-merge the mergeModel with others...


    """




def test2_new():    
    """     
    """    
    from box import Box ; from copy import deepcopy
    ARG = Box({
        'MODE'   : 'mode1',
        'DATASET': {},
        'MODEL_INFO' : {},
    })
    PARAMS = Box()

    ### acces byt bot 

    from utilmy.adatasets import test_dataset_classifier_fake
    df, cols_dict = test_dataset_classifier_fake(100, normalized=True)

    def load_DataFrame():
        return df

    prepro_dataset = None 
    

    ##################################################################
    if ARG.MODE == 'mode1':
        ARG.MODEL_INFO.TYPE = 'dataonly' 
        #train_config
        train_config                     = Box({})
        train_config.LR                  = 0.001
        train_config.SEED                = 42
        train_config.DEVICE              = 'cpu'
        train_config.BATCH_SIZE          = 32
        train_config.EPOCHS              = 1
        train_config.EARLY_STOPPING_THLD = 10
        train_config.VALID_FREQ          = 1
        train_config.SAVE_FILENAME       = './model.pt'
        train_config.TRAIN_RATIO         = 0.7
        train_config.VAL_RATIO           = 0.2
        train_config.TEST_RATIO          = 0.1


    #### SEPARATE the models completetly, and create duplicate
    ### modelA  ########################################################
    ARG.modelA               = Box()   #MODEL_TASK
    ARG.modelA.name          = 'modelA1'
    ARG.modelA.architect     = [ 9, 100, 16 ]
    ARG.modelA.dataset       = Box()
    ARG.modelA.dataset.dirin = "/"
    ARG.modelA.dataset.coly  = 'ytarget'
    ARG.modelA.seed          = 42
    modelA = modelA_create(ARG.modelA)


    ### modelB  ########################################################
    ARG.modelB               = Box()   #MODEL_RULE
    ARG.modelB.name         = 'modelB1'
    ARG.modelB.architect     = [9,100,16]
    ARG.modelB.dataset       = Box()
    ARG.modelB.dataset.dirin = "/"
    ARG.modelB.dataset.coly  = 'ytarget'
    ARG.modelB.seed          = 42
    modelB = modelB_create(ARG.modelB )

    
    ### merge_model  ###################################################
    ARG.merge_model           = Box()
    ARG.merge_model.name      = 'modelmerge1'
    ARG.merge_model.seed      = 42
    ARG.merge_model.architect = { 'decoder': [ 32, 100, 1 ] }

    ARG.merge_model.MERGE = 'cat'

    ARG.merge_model.dataset       = Box()
    ARG.merge_model.dataset.dirin = "/"
    ARG.merge_model.dataset.coly = 'ytarget'
    ARG.merge_model.train_config  = train_config
    model = MergeModel_create(ARG, modelB=modelB, modelA=modelA)

    ##### lien was cut  , new zoom id
    #Join Zoom Meeting
    #https://us05web.zoom.us/j/2933746463?pwd=WUhRWkx0NWNZRVBFVjZ4enV6Y1R2QT09

    # ok
    #### Run Model   ###################################################
    # load_DataFrame = modelB_create.load_DataFrame   
    # prepro_dataset = modelB_create.prepro_dataset
    model.build()        
    model.training(load_DataFrame, prepro_dataset) 

    model.save_weight('ztmp/model_x9.pt') 
    model.load_weights('ztmp/model_x9.pt')
    inputs = torch.randn((1,9)).to(model.device)
    outputs = model.predict(inputs)
    print(outputs)



##############################################################################################
class BaseModel(object):
    """This is BaseClass for model create

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
        self.head_task = self.create_model().to(self.device)
        self.loss_calc= self.create_loss().to(self.device)
        # self.loss_calc= 
        self.is_train = False
    
    def train(self): # equivalent model.train() in pytorch
        self.is_train = True
        self.head_task.train()

    def eval(self):     # equivalent model.eval() in pytorch
        self.is_train = False
        self.head_task.eval()

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
          self.head_task.load_state_dict(ckp)
        else:
          self.head_task.load_state_dict(ckp['state_dict'])
    
    def save_weight(self,path,meta_data=None):
      os.makedirs(os.path.dirname(path),exist_ok=True)
      ckp = {
          'state_dict':self.head_task.state_dict(),
      }
      if meta_data:
        if isinstance(meta_data,dict):
            ckp.update(meta_data)
        else:
            ckp.update({'meta_data':meta_data,})
            
        
      torch.save(ckp,path)

    def predict(self,x,**kwargs):
        # raise NotImplementedError
        output = self.head_task(x,**kwargs)
        return output 




##############################################################################################
class MergeModel_create(BaseModel):
    """
    """
    def __init__(self,arg, modelA=None, modelB=None):
        """_summary_


        from box import Box   ####
                      
        """
        super(MergeModel_create,self).__init__(arg)
        if modelA is None:
            self.modelA = modelA_create(arg.modelA) 
        else:
            self.modelA = (modelA)
        if modelB is None:
            self.modelB = modelB_create(arg.modelB)
        else:
            self.modelB = (modelB)
    

    def freeze_all(self,):
        for param in self.modelA.model.parameters():
            param.requires_grad = False

        for param in self.modelB.model.parameters():
            param.requires_grad = False

    def unfreeze_all(self,):
        for param in self.modelA.model.parameters():
            param.requires_grad = True

        for param in self.modelB.model.parameters():
            param.requires_grad = True

    def create_model(self,):
        super(MergeModel_create,self).create_model()
        # merge = self.arg.merge
        merge = getattr(self.arg.merge_model,'MERGE','add')
        skip = getattr(self.arg.merge_model,'SKIP',False)
        
        dims = self.arg.merge_model.architect.decoder
        class Modelmerge(torch.nn.Module):
            def __init__(self,modelB,modelA, dims, merge,skip):
                super(Modelmerge, self).__init__()

                #### rule encoder
                self.modelB_net = copy.copy(modelB.net)
                self.modelB_net.load_state_dict(modelB.net.state_dict())

                ###3 data encoder
                self.modelA_net = copy.copy(modelA.net)
                self.modelA_net.load_state_dict(modelA.net.state_dict())

                ##### Merge
                self.merge = merge
                self.skip = skip
                self.input_type = 'seq'



                ##### Head Task   #####################
                # self.head_task = nn.Sequential()
                self.head_task = []
                input_dim = dims[0]
                for layer_dim in dims[1:-1]:
                    self.head_task.append(nn.Linear(input_dim, layer_dim))
                    self.head_task.append(nn.ReLU())
                    input_dim = layer_dim
                self.head_task.append(nn.Linear(input_dim, dims[-1]))

                ###### Not good in model, keep into Losss
                # self.head_task.append(nn.Sigmoid())  #### output layer

                ##### MLP Head task
                self.head_task = nn.Sequential(*self.head_task)


            def forward(self, x,**kw):
                # merge: cat or add
                alpha = kw.get('alpha',0) # default only use YpredA
                scale = kw.get('scale',1)
        
                ## with torch.no_grad():
                embB = self.modelB_net.get_embedding(x)                
                embA = self.modelA_net.get_embedding(x)

                ##### 
                normB = torch_norm_l2(embB)
                embA =  torch_norm_l2(embA)

                ###### Scale, 
                if self.merge == 'cat':
                    z = torch.cat((alpha*embB, (1-alpha)*embA), dim=-1)

                elif self.merge == 'cat_equal':
                    ### May need scale 
                    z = torch.cat((embB, embA), dim=-1)


                return self.head_task(z)    # predict absolute values

            def get_embedding(self, x,**kw):
                 return emb

        return Modelmerge(self.modelB,self.modelA,dims,merge,skip)


    def build(self):
        # super(MergeModel_create,self).build()
        log("modelB:")
        self.modelB.build()

        log("modelA:")
        self.modelA.build()
        
        log("MergeModel:")
        self.net_all   = self.create_model().to(self.device)
        self.loss_calc = self.create_loss()#.to(self.device)

        #### BE cacreful to include all the params if COmbine loss.
        self.optimizer = torch.optim.Adam(self.net_all.head_task.parameters())
        
        # self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(self.optimizer, mode='min', factor=0.5, patience=5, verbose=True, threshold=0.0001, threshold_mode='rel', cooldown=0, min_lr=0, eps=1e-08)
        #self.optimizer = torch.optim.Adam(self.head_task )


        #### Freeze modelA, modelB top the fraidnet
        self.freeze_all()


    def create_loss1(self,):
        """
            2 possibilites:
               1) Only Head task loss : Classfieri head  ### Baseline
                    Stop the gradient or not in modelA and modelB.
                    embA_d = embA.detach()  ### Stop the gradient

        """
        super(MergeModel_create,self).create_loss()
        loss =  torch.nn.BCEWithLogitsLoss()
        return loss
        


    def create_loss2(self,):
        """
            2 possibilites:
               2) Classifer head + other model loss.     ### tweaking ,

           One issue is : Image classifier, VCG, EfficientNet , 
              modelA : blackBox, not always access to label...
              modelB : blackBox, not always access to label...
               cannot combine easily,  dont have head for those models
              
           Last layer embedding.


           1) Only Head task loss : Classfieri head  ### Baseline
           Stop the gradient or not in modelA and modelB.
            embA_d = embA.detach()  ### Stop the gradient
            modelA_loss(x_a, embA)



        """
        super(MergeModel_create,self).create_loss()
        modelB_loss_calc= self.modelB.loss_calc
        modelA_loss_calc= self.modelA.loss_calc

        class MergeLoss(torch.nn.Module):
            def __init__(self,modelB_loss_calc,modelA_loss_calc):
                super(MergeLoss,self).__init__()
                self.modelB_loss_calc= modelB_loss_calc
                self.modelA_loss_calc= modelA_loss_calc

            def forward(self,output,target,alpha=0,scale=1):                
                #### All have SAME Head labels.
                modelB_loss = self.modelB_loss_calc(output,  target.reshape(output.shape))
                modelA_loss = self.modelA_loss_calc(output,  target.reshape(output.shape))                
                loss_combine = modelB_loss * alpha * scale + modelA_loss * (1-alpha)
                # result = modelB_loss + modelA_loss
                return loss_combine
        return MergeLoss(modelB_loss_calc,modelA_loss_calc)


    def prepro_dataset(self,df=None):
        if df is None:              
            df = self.df     # if there is no dataframe feeded , get df from model itself

        coly = 'cardio'
        y     = df[coly]
        X_raw = df.drop([coly], axis=1)

        # log("Target class ratio:")
        # log("# of y=1: {}/{} ({:.2f}%)".format(np.sum(y==1), len(y), 100*np.sum(y==1)/len(y)))

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


        ##### Split   #########################################################################
        seed= 42 
        train_ratio = self.arg.merge_model.train_config.TRAIN_RATIO
        test_ratio = self.arg.merge_model.train_config.TEST_RATIO
        val_ratio =   self.arg.merge_model.train_config.TEST_RATIO
        train_X, test_X, train_y, test_y = train_test_split(X_src,  y_src,  test_size=1 - train_ratio, random_state=seed)
        valid_X, test_X, valid_y, test_y = train_test_split(test_X, test_y, test_size= test_ratio / (test_ratio + val_ratio), random_state=seed)
        return (train_X, train_y, valid_X,  valid_y, test_X,  test_y, )
        

    def training(self,load_DataFrame=None,prepro_dataset=None):
        # training with load_DataFrame and prepro_data function or default funtion in self.method

      
        df = load_DataFrame(self) if load_DataFrame else self.load_DataFrame()
        if prepro_dataset:
           train_X, train_y, valid_X,  valid_y, test_X,  test_y = prepro_dataset(self,df)
        else:
            train_X, train_y, valid_X,  valid_y, test_X,  test_y = self.prepro_dataset(df)  

        batch_size = self.arg.merge_model.train_config.BATCH_SIZE
        train_loader, valid_loader, test_loader =  dataloader_create(train_X, train_y, 
                                                                    valid_X,  valid_y,
                                                                    test_X,  test_y,
                                                                    device=self.device,
                                                                    batch_size=batch_size)
        
        EPOCHS = self.arg.merge_model.train_config.EPOCHS
        n_train = len(train_loader)
        n_val = len(valid_loader)
        
        
        for epoch in range(1,EPOCHS+1):
            self.train()
            loss_train = 0
            with torch.autograd.set_detect_anomaly(True): 
                for inputs,targets in train_loader:
                    
                    predict = self.head_task(inputs)
                    self.optimizer.zero_grad()
                    # self.optimizer.step()
                    scale =1
                    loss = self.loss_calc(predict, targets)
                    # loss.grad
                    loss.backward()
                    self.optimizer.step()
                    loss_train += loss * inputs.size(0)
                loss_train /= len(train_loader.dataset) # mean on dataset


            ##### Eval
            loss_val = 0
            self.eval()
            with torch.no_grad():
                for inputs,targets in valid_loader:
                    predict = self.predict(inputs)
                    self.optimizer.zero_grad()
                    scale=1
                    loss = self.loss_calc(predict,targets)                    
                    loss_val += loss * inputs.size(0)
            loss_val /= len(valid_loader.dataset) # mean on dataset
            
            
            path_save = self.arg.merge_model.train_config.SAVE_FILENAME
            self.save_weight(  path = path_save, meta_data = { 'epoch' : epoch, 'loss_train': loss_train, 'loss_val': loss_val, } )



def torch_norm_l2(X):
  """
   normalize the torch  tensor X by L2 norm.
  """
  X_norm = torch.norm(X, p=2, dim=1, keepdim=True)
  X_norm = X / X_norm
  return X_norm


def mytrain(x1, x2):
    pass

###################################################################################################
if __name__ == "__main__":
    import fire 
    fire.Fire() 
    # test_all()
    ###   https://github.com/google/python-fire
    ### arg_parser
    ####  python myfile.py   myClass.method1  --x1  234223  --x2 2


sorry, the line was cut. 
thanks for today, and various comments




##############################################################################################
class modelB_create(BaseModel):
    """ modelB
    """
    def __init__(self,arg):
        super(modelA_create,self).__init__(arg)

    def create_model(self):
        super(modelA_create,self).create_model()
        dims = self.arg.architect
        
        class modelB(torch.nn.Module):
            def __init__(self,dims=[20,100,16]):
                super(modelA, self).__init__()
                self.dims = dims 
                self.output_dim = dims[-1]
                # self.head_task = nn.Sequential()
                self.head_task = []
                input_dim = dims[0]
                for layer_dim in dims[:-1]:
                    self.head_task.append(nn.Linear(input_dim, layer_dim))
                    self.head_task.append(nn.ReLU())
                    input_dim = layer_dim
                self.head_task.append(nn.Linear(input_dim, dims[-1]))   #####  Do not use Sigmoid 
                self.head_task = nn.Sequential(*self.head_task)

            def forward(self, x,**kwargs):
                return self.head_task(x)

            def get_embedding(self,x, **kwargs):
              """  call signature
                   get name of the layer to extract it
                       Custom by model, API.
                       manual extraction + 

                        https://pytorch.org/vision/main/feature_extraction.html

                        https://discuss.pytorch.org/t/how-to-delete-layer-in-pretrained-model/17648/6


                        https://github.com/Riccorl/transformers-embedder

                        poling --> embedding for trasnfoemer

                        TIM ?
                        https://github.com/rwightman/pytorch-image-models


                        Re-normlaize the model through embedidng.

                           Use this case:
                            new article 
                                Image model --->  embA   ---> MergeModel --> 
                                NLP model   --->  embB
                                .....
                                .....
                                ....

                                  https://github.com/ml-jku/cloob
                                CLIP :  CLOOB  
                                ConText should be same,



              """  
              self.taks_task(x) # bs x c x h x w
              
              self.net.


              

        return modelB(dims)

    def create_loss(self) -> torch.nn.Module:
        super(modelA_create,self).create_loss()
        return torch.nn.BCELoss()



class modelA_create(BaseModel):
    """ modelA
    """
    def __init__(self,arg):
        super(modelA_create,self).__init__(arg)

    def create_model(self):
        super(modelA_create,self).create_model()
        dims = self.arg.architect
        
        class modelA(torch.nn.Module):
            def __init__(self,dims=[20,100,16]):
                super(modelA, self).__init__()
                self.dims = dims 
                self.output_dim = dims[-1]
                # self.head_task = nn.Sequential()
                self.head_task = []
                input_dim = dims[0]
                for layer_dim in dims[:-1]:
                    self.head_task.append(nn.Linear(input_dim, layer_dim))
                    self.head_task.append(nn.ReLU())
                    input_dim = layer_dim
                self.head_task.append(nn.Linear(input_dim, dims[-1]))
                self.head_task = nn.Sequential(*self.head_task)

            def forward(self, x,**kwargs):
                return self.head_task(x)

            def get_embedding(self, x,**kwargs):
               return emb

        return modelA(dims)

    def create_loss(self) -> torch.nn.Module:
        super(modelA_create,self).create_loss()
        return torch.nn.BCELoss()




###############################################################################################
###############################################################################################
def device_setup(arg):
    """function device_setup
    Args:
        arg:   
    Returns:
        
    """
    device = arg.device
    seed   = arg.seed
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


def dataloader_create(train_X=None, train_y=None, valid_X=None, valid_y=None, test_X=None, test_y=None,  arg=None):
    """function dataloader_create
    Args:
        train_X:   
        train_y:   
        valid_X:   
        valid_y:   
        test_X:   
        test_y:   
        arg:   
    Returns:
        
    """
    batch_size = arg.batch_size
    train_loader, valid_loader, test_loader = None, None, None

    if train_X is not None :
        train_X, train_y = torch.tensor(train_X, dtype=torch.float32, device=arg.device), torch.tensor(train_y, dtype=torch.float32, device=arg.device)
        train_loader = DataLoader(TensorDataset(train_X, train_y), batch_size=batch_size, shuffle=True)
        log("data size", len(train_X) )

    if valid_X is not None :
        valid_X, valid_y = torch.tensor(valid_X, dtype=torch.float32, device=arg.device), torch.tensor(valid_y, dtype=torch.float32, device=arg.device)
        valid_loader = DataLoader(TensorDataset(valid_X, valid_y), batch_size=valid_X.shape[0])
        log("data size", len(valid_X)  )

    if test_X  is not None :
        test_X, test_y   = torch.tensor(test_X,  dtype=torch.float32, device=arg.device), torch.tensor(test_y, dtype=torch.float32, device=arg.device)
        test_loader  = DataLoader(TensorDataset(test_X, test_y), batch_size=test_X.shape[0])
        log("data size:", len(test_X) )

    return train_loader, valid_loader, test_loader


def model_load(arg):
    """function model_load
    Args:
        arg:   
    Returns:
        
    """
    model_eval = model_build(arg=arg, mode='test')

    checkpoint = torch.load( arg.saved_filename)
    model_eval.load_state_dict(checkpoint['model_state_dict'])
    log("best model loss: {:.6f}\t at epoch: {}".format(checkpoint['loss'], checkpoint['epoch']))


    ll = Box({})
    ll.loss_rule_func = lambda x,y: torch.mean(F.relu(x-y))
    ll.loss_task_func = nn.BCELoss()
    return model_eval, ll # (loss_task_func, loss_rule_func)
    # model_evaluation(model_eval, loss_task_func, arg=arg)


def model_build(arg:dict, mode='train'):
    """function model_build
    Args:
        arg ( dict ) :   
        mode:   
    Returns:
        
    """
    arg = Box(arg)

    if 'test' in mode :
        modelA = modelB(arg.input_dim, arg.output_dim_encoder, arg.hidden_dim_encoder)
        modelB = modelA(arg.input_dim, arg.output_dim_encoder, arg.hidden_dim_encoder)
        model_eval = Net(arg.input_dim, arg.output_dim, modelA, modelB, hidden_dim=arg.hidden_dim_db, n_layers=arg.n_layers, merge=arg.merge).to(arg.device)    # Not residual connection
        return model_eval

    ##### Params  ############################################################################
    model_params = arg.model_info.get( arg.model_type, {} )

    #### Training
    arg.lr      = model_params.get('lr', 0.001)  # if 'lr' in model_params else 0.001

    #### Rules encoding
    from torch.distributions.beta import Beta
    arg.rules.pert_coeff   = model_params.get('pert', 0.1)
    arg.rules.scale        = model_params.get('scale', 1.0)
    beta_param   = model_params.get('beta', [1.0])
    if   len(beta_param) == 1:  arg.rules.alpha_dist = Beta(float(beta_param[0]), float(beta_param[0]))
    elif len(beta_param) == 2:  arg.rules.alpha_dist = Beta(float(beta_param[0]), float(beta_param[1]))
    arg.rules.beta_param = beta_param


    #########################################################################################
    losses    = Box({})

    #### Rule model
    modelA          = modelB(arg.input_dim, arg.output_dim_encoder, arg.hidden_dim_encoder)
    losses.loss_rule_func = arg.rules.loss_rule_func #lambda x,y: torch.mean(F.relu(x-y))    # if x>y, penalize it.


    #### Data model
    modelB = modelA(arg.input_dim, arg.output_dim_encoder, arg.hidden_dim_encoder)
    losses.loss_task_func = nn.BCELoss()    # return scalar (reduction=mean)

    #### Merge Ensembling
    model        = Net(arg.input_dim, arg.output_dim, modelA, modelB, hidden_dim=arg.hidden_dim_db,
                        n_layers=arg.n_layers, merge= arg.merge).to(arg.device)    # Not residual connection

    ### Summary
    log('model_type: {}\tscale:\tBeta distribution: Beta()\tlr: \t \tpert_coeff: {}'.format(arg.model_type, arg.rules))
    return model, losses, arg



def loss_rule_calc(model, batch_train_x, loss_rule_func, output, arg:dict):
    """ Calculate loss for constraints rules

    """
    rule_ind   = arg.rules.rule_ind
    pert_coeff = arg.rules.pert_coeff
    alpha      = arg.alpha

    pert_batch_train_x             = batch_train_x.detach().clone()
    pert_batch_train_x[:,rule_ind] = get_perturbed_input(pert_batch_train_x[:,rule_ind], pert_coeff)
    pert_output = model(pert_batch_train_x, alpha= alpha)
    loss_rule   = loss_rule_func(output.reshape(pert_output.size()), pert_output)    # output should be less than pert_output
    return loss_rule



def model_train(model, losses, train_loader, valid_loader, arg:dict=None ):
    """function model_train
    Args:
        model:   
        losses:   
        train_loader:   
        valid_loader:   
        arg ( dict ) :   
    Returns:
        
    """
    arg      = Box(arg)  ### Params
    arghisto = Box({})  ### results


    #### Rules Loss, params  ##################################################
    rule_feature   = arg.rules.get( 'rule_feature',   'ap_hi' )
    loss_rule_func = arg.rules.loss_rule_func
    if 'loss_rule_calc' in arg.rules: loss_rule_calc = arg.rules.loss_rule_calc
    src_ok_ratio   = arg.rules.src_ok_ratio
    src_unok_ratio = arg.rules.src_unok_ratio
    rule_ind       = arg.rules.rule_ind
    pert_coeff     = arg.rules.pert_coeff


    #### Core model params
    model_params   = arg.model_info[ arg.model_type]
    lr             = model_params.get('lr',  0.001)
    optimizer      = torch.optim.Adam(model.parameters(), lr=lr)
    loss_task_func = losses.loss_task_func


    #### Train params
    model_type = arg.model_type
    # epochs     = arg.epochs
    early_stopping_thld    = arg.early_stopping_thld
    counter_early_stopping = 1
    # valid_freq     = arg.valid_freq
    seed=arg.seed
    log('saved_filename: {}\n'.format( arg.saved_filename))
    best_val_loss = float('inf')


    for epoch in range(1, arg.epochs+1):
      model.train()
      for batch_train_x, batch_train_y in train_loader:
        batch_train_y = batch_train_y.unsqueeze(-1)
        optimizer.zero_grad()

        if   model_type.startswith('dataonly'):  alpha = 0.0
        elif model_type.startswith('ruleonly'):  alpha = 1.0
        elif model_type.startswith('ours'):      alpha = arg.rules.alpha_dist.sample().item()
        arg.alpha = alpha

        ###### Base output #########################################
        output    = model(batch_train_x, alpha=alpha).view(batch_train_y.size())
        loss_task = loss_task_func(output, batch_train_y)


        ###### Loss Rule perturbed input and its output  #####################
        loss_rule = loss_rule_calc(model, batch_train_x, loss_rule_func, output, arg )


        #### Total Losses  ##################################################
        scale = 1
        loss  = alpha * loss_rule + scale * (1 - alpha) * loss_task
        loss.backward()
        optimizer.step()


      # Evaluate on validation set
      if epoch % arg.valid_freq == 0:
        model.eval()
        if  model_type.startswith('ruleonly'):  alpha = 1.0
        else:                                   alpha = 0.0

        with torch.no_grad():
          for val_x, val_y in valid_loader:
            val_y = val_y.unsqueeze(-1)

            output = model(val_x, alpha=alpha).reshape(val_y.size())
            val_loss_task = loss_task_func(output, val_y).item()

            # perturbed input and its output
            pert_val_x = val_x.detach().clone()
            pert_val_x[:,rule_ind] = get_perturbed_input(pert_val_x[:,rule_ind], pert_coeff)
            pert_output = model(pert_val_x, alpha=alpha)    # \hat{y}_{p}    predicted sales from perturbed input

            val_loss_rule = loss_rule_func(output.reshape(pert_output.size()), pert_output).item()
            val_ratio = verification(pert_output, output, threshold=0.0).item()

            val_loss = val_loss_task

            y_true = val_y.cpu().numpy()
            y_score = output.cpu().numpy()
            y_pred = np.round(y_score)

            y_true = y_pred.reshape(y_true.shape[:-1])
            y_pred = y_pred.reshape(y_pred.shape[:-1])

            val_acc = mean_squared_error(y_true, y_pred)

          if val_loss < best_val_loss:
            counter_early_stopping = 1
            best_val_loss = val_loss
            best_model_state_dict = deepcopy(model.state_dict())
            log('[Valid] Epoch: {} Loss: {:.6f} (alpha: {:.2f})\t Loss(Task): {:.6f} Acc: {:.2f}\t Loss(Rule): {:.6f}\t Ratio: {:.4f} best model is updated %%%%'
                  .format(epoch, best_val_loss, alpha, val_loss_task, val_acc, val_loss_rule, val_ratio))
            torch.save({
                'epoch': epoch,
                'model_state_dict': best_model_state_dict,
                'optimizer_state_dict': optimizer.state_dict(),
                'loss': best_val_loss
            }, arg.saved_filename)
          else:
            log('[Valid] Epoch: {} Loss: {:.6f} (alpha: {:.2f})\t Loss(Task): {:.6f} Acc: {:.2f}\t Loss(Rule): {:.6f}\t Ratio: {:.4f}({}/{})'
                  .format(epoch, val_loss, alpha, val_loss_task, val_acc, val_loss_rule, val_ratio, counter_early_stopping, early_stopping_thld))
            if counter_early_stopping >= early_stopping_thld:
              break
            else:
              counter_early_stopping += 1


def model_evaluation(model_eval, loss_task_func, arg, dataset_load1, dataset_preprocess1 ):
    """function model_evaluation
    Args:
        model_eval:   
        loss_task_func:   
        arg:   
        dataset_load1:   
        dataset_preprocess1:   
    Returns:
        
    """
    ### Create dataloader
    df = dataset_load1(arg)
    train_X, test_X, train_y, test_y, valid_X, valid_y = dataset_preprocess1(df, arg)



    ######
    train_loader, valid_loader, test_loader = dataloader_create( train_X, test_X, train_y, test_y, valid_X, valid_y, arg)
    model_eval.eval()
    with torch.no_grad():
      for te_x, te_y in test_loader:
        te_y = te_y.unsqueeze(-1)

      output         = model_eval(te_x, alpha=0.0)
      test_loss_task = loss_task_func(output, te_y.view(output.size())).item()

    log('\n[Test] Average loss: {:.8f}\n'.format(test_loss_task))

    ########## Pertfubation
    pert_coeff = arg.rules.pert_coeff
    rule_ind   = arg.rules.rule_ind
    model_type = arg.model_type
    alphas     = [0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]


    model_eval.eval()

    # perturbed input and its output
    pert_test_x = te_x.detach().clone()
    pert_test_x[:,rule_ind] = get_perturbed_input(pert_test_x[:,rule_ind], pert_coeff)
    for alpha in alphas:
      model_eval.eval()
      with torch.no_grad():
        for te_x, te_y in test_loader:
          te_y = te_y.unsqueeze(-1)

        if model_type.startswith('dataonly'):
          output = model_eval(te_x, alpha=0.0)
        elif model_type.startswith('ours'):
          output = model_eval(te_x, alpha=alpha)
        elif model_type.startswith('ruleonly'):
          output = model_eval(te_x, alpha=1.0)

        test_loss_task = loss_task_func(output, te_y.view(output.size())).item()

        if model_type.startswith('dataonly'):
          pert_output = model_eval(pert_test_x, alpha=0.0)
        elif model_type.startswith('ours'):
          pert_output = model_eval(pert_test_x, alpha=alpha)
        elif model_type.startswith('ruleonly'):
          pert_output = model_eval(pert_test_x, alpha=1.0)

        test_ratio = verification(pert_output, output, threshold=0.0).item()

        y_true = te_y.cpu().numpy()
        y_score = output.cpu().numpy()
        y_pred = np.round(y_score)

        test_acc = mean_squared_error(y_true.squeeze(), y_pred.squeeze())

      log('[Test] Average loss: {:.8f} (alpha:{})'.format(test_loss_task, alpha))
      log('[Test] Accuracy: {:.4f} (alpha:{})'.format(test_acc, alpha))
      log("[Test] Ratio of verified predictions: {:.6f} (alpha:{})".format(test_ratio, alpha))
      log()






###################################################################################################
if __name__ == "__main__":
    import fire 
    fire.Fire() 
    # test_all()

####################################################################################################
if '''not model.py ''' :
    class NaiveModel(nn.Module):
      def __init__(self):
        """ NaiveModel:__init__
        Args:
        Returns:
          
        """
        super(NaiveModel, self).__init__()
        self.head_task = nn.Identity()

      def forward(self, x, alpha=0.0):
        """ Net:forward
        Args:
            x:     
            alpha:     
        Returns:
          
        """
        """ NaiveModel:forward
        Args:
            x:     
            alpha:     
        Returns:
          
        """
        return self.head_task(x)


    class modelB(nn.Module):
      def __init__(self, input_dim, output_dim, hidden_dim=4):
        """ modelB:__init__
        Args:
            input_dim:     
            output_dim:     
            hidden_dim:     
        Returns:
          
        """
        """ modelA:__init__
        Args:
            input_dim:     
            output_dim:     
            hidden_dim:     
        Returns:
          
        """
        super(modelB, self).__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.head_task = nn.Sequential(nn.Linear(input_dim, hidden_dim),
                                nn.ReLU(),
                                nn.Linear(hidden_dim, output_dim))

      def forward(self, x):
        """ modelB:forward
        Args:
            x:     
        Returns:
          
        """
        """ modelA:forward
        Args:
            x:     
        Returns:
          
        """
        return self.head_task(x)


    class modelA(nn.Module):
      def __init__(self, input_dim, output_dim, hidden_dim=4):
        super(modelA, self).__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.head_task = nn.Sequential(nn.Linear(input_dim, hidden_dim),
                                nn.ReLU(),
                                nn.Linear(hidden_dim, output_dim))

      def forward(self, x):
        return self.head_task(x)


    class Net(nn.Module):
      def __init__(self, input_dim, output_dim, modelA, modelB, hidden_dim=4, n_layers=2, merge='cat', skip=False, input_type='state'):
        """ Net:__init__
        Args:
            input_dim:     
            output_dim:     
            modelA:     
            modelB:     
            hidden_dim:     
            n_layers:     
            merge:     
            skip:     
            input_type:     
        Returns:
          
        """
        super(Net, self).__init__()
        self.skip = skip
        self.input_type   = input_type
        self.modelA = modelA
        self.modelB = modelB
        self.n_layers =n_layers
        assert self.modelA.input_dim == self.modelB.input_dim
        assert self.modelA.output_dim == self.modelB.output_dim
        self.merge = merge
        if merge == 'cat':
          self.input_dim_decision_block = self.modelA.output_dim * 2
        elif merge == 'add':
          self.input_dim_decision_block = self.modelA.output_dim

        self.head_task = []
        for i in range(n_layers):
          if i == 0:
            in_dim = self.input_dim_decision_block
          else:
            in_dim = hidden_dim

          if i == n_layers-1:
            out_dim = output_dim
          else:
            out_dim = hidden_dim

          self.head_task.append(nn.Linear(in_dim, out_dim))
          if i != n_layers-1:
            self.head_task.append(nn.ReLU())

        self.head_task.append(nn.Sigmoid())

        self.head_task = nn.Sequential(*self.head_task)

      def get_z(self, x, alpha=0.0):
        """ Net:get_z
        Args:
            x:     
            alpha:     
        Returns:
          
        """
        YpredB = self.modelA(x)
        YpredA = self.modelB(x)

        if self.merge == 'add':
          z = alpha*YpredB + (1-alpha)*YpredA
        elif self.merge == 'cat':
          z = torch.cat((alpha*YpredB, (1-alpha)*YpredA), dim=-1)
        elif self.merge == 'equal_cat':
          z = torch.cat((YpredB, YpredA), dim=-1)

        return z

      def forward(self, x, alpha=0.0):
        # merge: cat or add

        YpredB = self.modelA(x)
        YpredA = self.modelB(x)

        if self.merge == 'add':
          z = alpha*YpredB + (1-alpha)*YpredA
        elif self.merge == 'cat':
          z = torch.cat((alpha*YpredB, (1-alpha)*YpredA), dim=-1)
        elif self.merge == 'equal_cat':
          z = torch.cat((YpredB, YpredA), dim=-1)

        if self.skip:
          if self.input_type == 'seq':
            return self.head_task(z) + x[:, -1, :]
          else:
            return self.head_task(z) + x    # predict delta values
        else:
          return self.head_task(z)    # predict absolute values


