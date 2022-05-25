import torch
import torch.nn as nn
import pytorch_lightning as pl
from astrape.utilities.utils import *
from astrape.exceptions.exceptions import *
from astrape.constants.astrape_constants import *
from typing import Union, List, Dict, Any, Optional, cast, Tuple
import math 
import torchmetrics
applicable_val_metric_list = APPLICABLE_VAL_METRIC_LIST
applicable_optimizer_type_list = APPLICABLE_OPTIMIZER_TYPE_LIST

"""
Below are classes of which foundate Pytorch-Lightning Models defined in "models_lightning.py".
i.e., they are the parent classes of the classes in "models_lightning.py".

The classes below specifies the i) training/validation/prediction/test step operations
                                ii) optimizer configurations
                                iii) methods for resetting/initializing model weights


    


"""
# *****************************************************************  Classes  ***************************************************************** 

########################################################## BaseNet (Begins) ##########################################################

"""
BaseNet (offspring of pl.LightningModule): 

    BaseNet is the parent class for MLPs(MLP, ContractingMLP, CustomMLP). It is also
    compatible with other MLPs that are written in pytorch_lightning.

    When inheriting BaseNet, you only need to specify the structure of your MLP because 
    other magics are defined in BaseNet.  

    BaseNet can perform both classification and regression tasks. If you specify n_classes, 
    BaseNet will recognize the task as a classification problem. If n_classes is not passed
    as a parameter for BaseNet, it will understand that the task is a regression problem.

    Arguments: 
        - dims (Union[int, tuple[int]]): The dimension of the data. e.g., 4, (8,8,1)

        - n_classes (Optional[int]) : Number of classes (labels) in the classification task.
                                      Do not specify this argument (set is as None) when you 
                                      are performing regression tasks.

        - **config (Any) : Hyperparameters that can be shared among different models. 
                           e.g., optimizer_type, lr, weight_decay, batch_size, bn, dropout_p, etc.
                
"""
class BaseNet(pl.LightningModule):

    def __init__(
        self,
        dims : Union[int, Tuple[int]],
        n_classes : Optional[int],
        l1_strength : float = 0.0,
        sample_weight : Optional[Union["np.ndarray", "torch.Tensor"]] = None,
        **config : Any
    ) -> None:

        super(BaseNet, self).__init__()
        if isinstance(dims, tuple):
            flattened = 1
            for dim in dims:
                flattened *= dim
            dims = flattened 

        self.dims = dims
        self.n_classes = n_classes if n_classes is not None else None 
        self.config = config
        self.sample_weight = sample_weight

        config.update({'l1_strength' : l1_strength})
            
        self.save_hyperparameters(*config)
        #optimizer_type_check(applicable_optimizer_type_list, self.hparams.optimizer_type)


    def on_after_batch_transfer(self, batch, dataloader_idx=0):
        
        # Modify this part if you want to perform reweighting.
        
        self.sample_weight = torch.ones_like(batch[1]).type_as(batch[1])
        

        return batch

    @property
    def criterion(self):
        if self.n_classes is None:
            if 'regression_metric' in self.config.keys():
                if self.config['regression_metric'] == "mse":
                    criterion = MSELoss()
                elif self.config['regression_metric'] == "r2":
                    criterion = R2Score()
                elif self.config['regression_metric'] == "rmse":
                    criterion = RMSELoss()
                else:
                    raise NotImplementedError("Only MSE loss, R2 score, and RMSE are supported in expytorch_lightning v 0.0.0.")
            else:
                criterion = MSELoss()
        else:
            criterion = CELossAccuracy() if self.n_classes > 2 else BCELossAccuracy()
        return criterion

    def training_step(self, train_batch, batch_idx):

        x_batch, y_batch = train_batch
        Yhat = self.forward(x_batch)
        y_batch = self.sample_weight * y_batch
        

        if self.n_classes is None: # regression
            loss = self.criterion(Yhat.squeeze(), y_batch)
            # L1 regularizer
            if self.hparams.l1_strength > 0:
                l1_reg = self.linear.weight.abs().sum()
                loss += self.hparams.l1_strength * l1_reg
            self.log('train/loss', loss)
            return {'loss' : loss}
        else: # classification
            loss, acc, auc = self.criterion(Yhat.squeeze(), y_batch.long())

            self.log('train/loss', loss)
            self.log('train/acc', acc)
            self.log('train/auc', auc)
            return {'loss' : loss, 'acc' : acc, 'auc' : auc}
    
    def validation_step(self, val_batch, batch_idx):
        x_batch, y_batch = val_batch
        
        Yhat = self.forward(x_batch)
        if self.n_classes is None:
            loss = self.criterion(Yhat.squeeze(), y_batch)
            # L1 regularizer
            if self.hparams.l1_strength > 0:
                l1_reg = self.linear.weight.abs().sum()
                loss += self.hparams.l1_strength * l1_reg

            
            self.log('val/loss', loss)
            return {'loss' : loss}
        else:    
            loss, acc, auc = self.criterion(Yhat.squeeze().type_as(y_batch), y_batch)

            self.log('val/loss', loss)
            self.log('val/acc', acc)
            self.log('val/auc', auc)
            return {'loss' : loss, 'acc' : acc, 'auc' : auc}
        
        
        
    def predict_step(self, pred_batch, batch_idx, dataloader_idx=0):
        x_batch, y_batch = pred_batch
        
        Yhat = self.forward(x_batch)
        if self.n_classes is None:
            loss = self.criterion(Yhat.squeeze(), y_batch)
            # L1 regularizer
            if self.hparams.l1_strength > 0:
                l1_reg = self.linear.weight.abs().sum()
                loss += self.hparams.l1_strength * l1_reg

            
            self.log('predict/loss', loss)
            return {'loss' : loss}
        else:    
            loss, acc, auc = self.criterion(Yhat.squeeze(), y_batch.type(torch.LongTensor))

            self.log('predict/loss', loss)
            self.log('predict/acc', acc)
            self.log('predict/auc', auc)
            return {'loss' : loss, 'acc' : acc, 'auc' : auc}

    def test_step(self, test_batch, batch_idx, data_loader_idx=0):
        x_batch, y_batch = test_batch
        
        Yhat = self.forward(x_batch)
        if self.n_classes is None:
            loss = self.criterion(Yhat.squeeze(), y_batch)
            # L1 regularizer
            if self.hparams.l1_strength > 0:
                l1_reg = self.linear.weight.abs().sum()
                loss += self.hparams.l1_strength * l1_reg

            
            self.log('test/loss', loss)
            return {'loss' : loss}
        else:    
            loss, acc, auc = self.criterion(Yhat.squeeze(), y_batch.type(torch.LongTensor))

            self.log('test/loss', loss)
            self.log('test/acc', acc)
            self.log('test/auc', auc)
            return {'loss' : loss, 'acc' : acc, 'auc' : auc}


    def reset_weights(self, module):
        if isinstance(module, nn.Linear):
            module.reset_parameters()
            
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.kaiming_normal_(module.weight)
        elif isinstance(module, nn.BatchNorm1d):
            nn.init.constant_(module.weight, 1)
            nn.init.constant_(module.bias, 0)

    def configure_optimizers(self):

        #optimizer_type_check(applicable_optimizer_type_list, self.config.optimizer_type)
        if self.hparams.optimizer_type == "adam":
            optimizer = torch.optim.Adam(self.parameters(),
                                     lr=self.hparams.lr,
                                     weight_decay=self.hparams.weight_decay)
        elif self.hparams.optimizer_type == "sgd":
            optimizer = torch.optim.SGD(self.parameters(),
                                        lr=self.hparams.lr)
        
        return optimizer
        
########################################################## BaseNet (Ends) ##########################################################


########################################################## ConvNet (Begins) ##########################################################
"""
ConvNet (offspring of pl.LightningModule): 


    II. ConvNet (offspring of pl.LightningModule):
    ConvNet is the parent class for CNNs(VGG, UNet). It is also compatible with other CNNs
    that are written in pytorch_lightning. 

    When inheriting ConvNet, you only need to specify the structure of your MLP because 
    other magics are defined in ConvNet. 

    Currently in expytorch_lightning v. 0.0.0, ConvNet only supports basic classification
    tasks such as classification using CE loss or dice loss. Other operations will be 
    updated soon(Be tuned!).


    Arguments: 

        - model_type (pl.LightningModule) : The class of the model that you will use.

        - n_classes (Optional[int]) : Number of classes (labels) in the classification task.
                                    
        - **config (Any) : Hyperparameters that can be shared among different models. 
                           e.g., optimizer_type, lr, weight_decay, batch_size, bn, dropout_p, etc.
                
"""
class ConvNet(pl.LightningModule):
    def __init__(
        self,
        model_type : "pl.LightningModule",
        n_classes : Optional[int] = None,
        sample_weight : Optional[Union["np.ndarray", "torch.Tensor"]] = None,
        **config : Any
    ) -> None:
        super(ConvNet, self).__init__()

        if 'optimizer_type' not in config.keys():
            config.update({'optimizer_type' : 'adam'})
        
        self.model_type = model_type
        self.n_classes = n_classes
        self.sample_weight = sample_weight
        self.save_hyperparameters(*config)
        

    @property
    def criterion(self):   
        if self.n_classes is None:
            if 'regression_metric' in self.config.keys():
                if self.config['regression_metric'] == "mse":
                    criterion = MSELoss()
                elif self.config['regression_metric'] == "r2":
                    criterion = R2Score()
                elif self.config['regression_metric'] == "rmse":
                    criterion = RMSELoss()
                else:
                    raise NotImplementedError("Only MSE loss, R2 score, and RMSE are supported in expytorch_lightning v 0.0.0.")
            else:
                criterion = MSELoss()
        else:
            if self.model_type == "UNet":
                criterion = CEDiceLossAccuracy(self.n_classes)
            else:
                criterion = CELossAccuracy() if self.n_classes > 2 else BCELossAccuracy()
        return criterion

    @staticmethod
    def reshape_x(x_batch):
        dims = x_batch.shape[1:]
        
        if len(dims) == 1:
            width = height = math.sqrt(dims[0])
            if (height != int(height)):
                raise ValueError("Wrong dimension for the input.")
            x_batch = x_batch.reshape(-1, 1, int(height), int(width))
        elif len(dims) == 2:
            height = dims[0]
            width = dims[1]
            x_batch = x_batch.reshape(-1, 1, int(height), int(width))
        elif len(dims) == 3:
            x_batch = x_batch.reshape(-1, int(dims[0]), int(dims[1]), int(dims[2]))
        else:
            raise ValueError("Wrong dimension for the input.")

        return x_batch

    def on_before_batch_transfer(self, batch: Any, dataloader_idx=0):
        batch[0] = self.reshape_x(batch[0])
        return batch
    
    def on_after_batch_transfer(self, batch, dataloader_idx=0):
        # modify this part if you want to perform model reweigthing.
        self.sample_weight = torch.ones_like(batch[1]).type_as(batch[1])
        return batch
    
    def training_step(self, train_batch, batch_idx):
        x_batch, y_batch = train_batch
        x_batch = self.reshape_x(x_batch)
            
        y_batch = self.sample_weight * y_batch

        Yhat = self.forward(x_batch)
        if self.n_classes is None:
            loss = self.criterion(Yhat.squeeze(), y_batch)
            self.log('train/loss', loss)
            return {'loss' : loss}
        else:    
            loss, acc, auc = self.criterion(Yhat.squeeze(), y_batch.type(torch.LongTensor))

            self.log('train/loss', loss)
            self.log('train/acc', acc)
            self.log('train/auc', auc)
            return {'loss' : loss, 'acc' : acc, 'auc' : auc}

        
    def validation_step(self, val_batch, batch_idx):
        x_batch, y_batch = val_batch
        x_batch = self.reshape_x(x_batch)
        Yhat = self.forward(x_batch)
        if self.n_classes is None:
            loss = self.criterion(Yhat.squeeze(), y_batch)
            self.log('val/loss', loss)
            return {'loss' : loss}
        else:    
            loss, acc, auc = self.criterion(Yhat.squeeze(), y_batch.type(torch.LongTensor))

            self.log('val/loss', loss)
            self.log('val/acc', acc)
            self.log('val/auc', auc)
            return {'loss' : loss, 'acc' : acc, 'auc' : auc}

    def predict_step(self, pred_batch, batch_idx, dataloader_idx=0):
        x_batch, y_batch = pred_batch
        x_batch = self.reshape_x(x_batch)
        Yhat = self.forward(x_batch)
        if self.n_classes is None:
            loss = self.criterion(Yhat.squeeze(), y_batch)
            self.log('pred/loss', loss)
            return {'loss' : loss}
        else:    
            loss, acc, auc = self.criterion(Yhat.squeeze(), y_batch.type(torch.LongTensor))

            self.log('pred/loss', loss)
            self.log('pred/acc', acc)
            self.log('pred/auc', auc)
            return {'loss' : loss, 'acc' : acc, 'auc' : auc}

    def test_step(self, test_batch, batch_idx):
        x_batch, y_batch = test_batch
        x_batch = self.reshape_x(x_batch)
        Yhat = self.forward(x_batch)
        if self.n_classes is None:
            loss = self.criterion(Yhat.squeeze(), y_batch)
            self.log('test/loss', loss)
            return {'loss' : loss}
        else:    
            loss, acc, auc = self.criterion(Yhat.squeeze(), y_batch.type(torch.LongTensor))

            self.log('test/loss', loss)
            self.log('test/acc', acc)
            self.log('test/auc', auc)
            return {'loss' : loss, 'acc' : acc, 'auc' : auc}

    def reset_weights(self, module):
        if isinstance(module, nn.Linear):
            module.reset_parameters()
            
    def _init_weights(self, module) -> None:
        if isinstance(module, nn.Linear):
            nn.init.kaiming_normal_(module.weight)
        elif isinstance(module, nn.BatchNorm1d):
            nn.init.constant_(module.weight, 1)
            nn.init.constant_(module.bias, 0)
        elif isinstance(module, nn.Conv2d):
            nn.init.kaiming_normal_(module.weight, mode="fan_out", nonlinearity="relu")
            if module.bias is not None:
                nn.init.constant_(module.bias, 0)

    def configure_optimizers(self):

        #optimizer_type_check(applicable_optimizer_type_list, self.hparams.optimizer_type)

        if self.hparams.optimizer_type == "adam":
            optimizer = torch.optim.Adam(self.parameters(),
                                     lr=self.hparams.lr,
                                     weight_decay=self.hparams.weight_decay)
        elif self.hparams.optimizer_type == "sgd":
            optimizer = torch.optim.SGD(self.parameters(),
                                        lr=self.hparams.lr)

        return optimizer

########################################################## ConvNet (Ends) ##########################################################