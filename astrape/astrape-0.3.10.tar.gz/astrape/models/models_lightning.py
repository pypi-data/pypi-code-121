from pickle import BINBYTES
from random import sample
import torch
import torch.nn as nn
from astrape.utilities.utils_lightning import set_default_parameters
from astrape.base.model_base import BaseNet, ConvNet
from typing import Union, List, Dict, Any, Optional, cast, Tuple
from astrape.exceptions.exceptions import *
from astrape.models.model_buildingblocks import Down, DoubleConv, Up
import math
import numpy as np


# *****************************************************************  Classes  ***************************************************************** 
########################################################## _MLP & MLP (Begins) ##########################################################
"""
_MLP and MLP defines an MLP with all hidden layers having a same number of hidden units.
Therefore, the hyperparameters that are additionally defined in MLP are n_layers and n_hidden_units.

_MLP and MLP are basically identical in structure. The only difference is that _MLP is an offspring
of nn.Module and MLP is an offspring of BaseNet.

Arguments:
    - dims (Union[int, Tuple[int]]): The dimension of the data. e.g., 4, (8,8,1)

    - n_classes (Optional[int]) : Number of classes (labels) in the classification task.
                                    Do not specify this argument (set is as None) when you 
                                    are performing regression tasks.
    
    - n_layers (int) : Number of layers. If 1, it would be an old-school perceptron i.e., logistic regression.
                       Default : 2

    - n_hidden_units (int) : Number of hidden units for all hidden layers. Default : 10 

    - batch_size (int) : Batch size. Default : 64 (see utils_lightning.py)

    - optimizer_type (str) : Type of the optimizer. ("adam" or "sgd") Default : "adam" (see utils_lightning.py) 
                            #TODO : implement other optimizers.(in model_base.py)

    - dropout_p (0<= float < 1) : Dropout probability Default : 0 (see utils_lightning.py)

    - bn (bool) : Whether to use batch normalization or not. Default : True (see utils_lightning.py)

    - weight_decay (0<= float) : coefficient for L2-regularization. Default : 0 (see utils_lightning.py)

    - lr ( 0 < float) : Learning rate. Default: 1e-4 (see utils_lightning.py)
"""
class _MLP(nn.Module):
    def __init__(
        self,
        dims : Union[int, Tuple[int]],
        n_classes : int, 
        n_layers : int,
        n_hidden_units : int,
        batch_size : int,
        optimizer_type : str,
        dropout_p : float,
        bn : bool,
        lr : float,
        weight_decay : float,
        l1_strength : float,
        activation_type : str = "relu", # "relu" or "leaky_relu"
        negative_slope : Optional[float] = None, # negative slope for leaky relu   
        sample_weight : Optional[Union["np.ndarray", "torch.Tensor"]] = None
    ) -> None:

        super(_MLP, self).__init__()
        layers = []
        
        if isinstance(dims, tuple):
            flattened = 1
            for dim in dims:
                flattened *= dim
            dims = flattened 

        self.dims = dims
        self.n_classes = n_classes
        self.n_layers = n_layers
        self.n_hidden_units = n_hidden_units
        self.optimizer_type = optimizer_type
        self.batch_size = batch_size
        self.dropout_p = dropout_p
        self.bn = bn
        self.lr = lr
        self.weight_decay = weight_decay 
        self.sample_weight = sample_weight
        self.l1_strength = l1_strength
        self.activation_type = activation_type
        self.negative_slope = negative_slope
        if self.n_layers == 1:
            if self.n_classes > 2:
                layers.append(nn.Linear(self.dims, self.n_classes))
            else:
                layers.append(nn.Linear(self.dims, 1))

        else : #Deep  Neural Network
            fc1 = nn.Linear(self.dims, self.n_hidden_units)
            layers.append(fc1)
            if self.bn:
                layers.append(nn.BatchNorm1d(num_features=self.n_hidden_units))
            
            if activation_type == "tanh":
                layers.append(nn.Tanh())
            elif activation_type == "relu":
                layers.append(nn.ReLU())
            elif activation_type == "leaky_relu":
                if not negative_slope:
                    negative_slope = 1e-2
                layers.append(nn.LeakyReLU(negative_slope=negative_slope))
            else:
                raise ValueError("Wrong name {} for activation function.".format(activation_type))
            layers.append(nn.Dropout(self.dropout_p))
            
            for i in range(self.n_layers-2):
                fc2 = nn.Linear(self.n_hidden_units, self.n_hidden_units)
                layers.append(fc2)
                if self.bn:
                    layers.append(nn.BatchNorm1d(num_features=self.n_hidden_units))
                
                if activation_type == "tanh":
                    layers.append(nn.Tanh())
                elif activation_type == "relu":
                    layers.append(nn.ReLU())
                elif activation_type == "leaky_relu":
                    if not negative_slope:
                        negative_slope = 1e-2
                    layers.append(nn.LeakyReLU(negative_slope=negative_slope))
                else:
                    raise ValueError("Wrong name {} for activation function.".format(activation_type))
                layers.append(nn.Dropout(self.dropout_p))

            
            if self.n_classes > 2:
                fc3 = nn.Linear(self.n_hidden_units, self.n_classes)
                layers.append(fc3)
            else: # including the case when self.n_classes is None
                fc3 = nn.Linear(self.n_hidden_units, 1)
                layers.append(fc3)
        
        if self.n_classes is None:
            pass
        elif self.n_classes> 2:
            layers.append(nn.Softmax(dim=1))
        else:
            layers.append(nn.Sigmoid())

    
        self.layers = nn.Sequential(*layers)
    
    def forward(self, X):
        return self.layers(X)


class MLP(BaseNet):
    def __init__(
        self,
        dims : Union[int, Tuple[int]],
        n_classes : int,
        sample_weight : Optional[Union["torch.Tensor", "np.ndarray"]] = None,
        **hparams : Any
    ) -> None:
        
        
        entire_keys = [
            'dims', 
            'n_classes', 
            'n_layers',
            'n_hidden_units', 
            'optimizer_type', 
            'batch_size',
            'dropout_p',
            'bn',
            'sample_weight',
            'lr',
            'weight_decay',
            'l1_strength',
            'activation_type',
            'negative_slope'
            ]
        default_parameter_dict = {
            'n_layers' : 2,
            'n_hidden_units' : 10
        }
        
        self.dims = dims
        self.n_classes = n_classes
        self.sample_weight = sample_weight
        
        # set default for model-specific hyperparameters
        for argument, default in default_parameter_dict.items():
            if argument not in hparams.keys(): 
                hparams.update({argument : default})
        # set default for model-agnostic hyperparameters (read utils_lightning.py)
        set_default_parameters(hparams)
        # save information of **hparams to self.hparams.
        self.save_hyperparameters(*hparams)
        # validate contraction_ratio
        
        super(MLP, self).__init__(
            dims=dims, 
            n_classes=n_classes, 
            sample_weight=sample_weight,
            **hparams
        )
        # sanity check. Check if right arguments are declared.
        for key in hparams.keys():
            if key not in entire_keys:
                raise ValueError('Wrong argument {} is passed to the model.'.format(key))
        self.model = _MLP(dims=self.dims, n_classes=self.n_classes, sample_weight=self.sample_weight, **hparams)

    def forward(self, X):
        return self.model.forward(X)

    def help(self) -> None :
        whoami = "Multi-Layer Perceptron\n\n"
        helptext = "Parameters ------------------------------------------------------------------------------------------------------- \n"
        helptext += "dims:\t Dimension of the data. Normally X.shape[1].\n"
        helptext += "n_classes:\t Number of classes in the classification task. If it is binary classification, 'n_classes' = 2\n"
        helptext += "In defining hyperparameters and optimizer_type, we recommend you to define a dictionary.\n"
        helptext += "Define a dictionary containing :\n\t-'optimizer_type': str (default='adam')\n\t-'n_layers' : int (default=2)\n\t-'n_hidden_units' : int (default=10)\n\t-'dropout_p' : 0 <= float < 1 (default=0)\n\t-'weight_decay' : 0<= float < 1(default=0)\n\t-'lr' : float(default=1e-4)."
        
        text= whoami + helptext
        print(text)
########################################################## _MLP & MLP (Ends) ##########################################################


########################################################## _ContractingMLP & ContractingMLP (Begins) ##########################################################
"""
_ContractingMLP and ContractingMLP defines an MLP with number of hidden units decreasing with a factor
of contraction_ratio.
Therefore, the hyperparameter that is additionally defined in ContractingMLP is contraction_ratio.

_ContractingMLP and ContractingMLP are basically identical in structure. The only difference is that
_ContractingMLP is an offspring of nn.Module and ContractingMLP is an offspring of BaseNet.

Arguments:
    - dims (Union[int, Tuple[int]]): The dimension of the data. e.g., 4, (8,8,1)

    - n_classes (Optional[int]) : Number of classes (labels) in the classification task.
                                    Do not specify this argument (set is as None) when you 
                                    are performing regression tasks.
    
    - contraction_ratio (0 < float < 1) : The contraction ratio for n_hidden_units. Default : 0.5

    - batch_size (int) : Batch size. Default : 64 (see utils_lightning.py)

    - optimizer_type (str) : Type of the optimizer. ("adam" or "sgd") Default : "adam" (see utils_lightning.py) 
                            #TODO : implement other optimizers.(in model_base.py)

    - dropout_p (0<= float < 1) : Dropout probability Default : 0 (see utils_lightning.py)

    - bn (bool) : Whether to use batch normalization or not. Default : True (see utils_lightning.py)

    - weight_decay (0<= float) : coefficient for L2-regularization. Default : 0 (see utils_lightning.py)

    - lr ( 0 < float) : Learning rate. Default: 1e-4 (see utils_lightning.py)


"""
class _ContractingMLP(nn.Module):
    def __init__(
        self,
        dims : Union[int, Tuple[int]],
        n_classes : int,
        contraction_ratio : float, 
        optimizer_type : str, 
        batch_size : int ,
        dropout_p : float,
        bn : bool,
        lr : float,
        weight_decay : float,
        l1_strength : float,
        activation_type : str = "relu",
        negative_slope : Optional[float] = None,
        sample_weight : Optional[Union["torch.Tensor", "np.ndarray"]] = None
    ) -> None:
        super(_ContractingMLP, self).__init__()

        if isinstance(dims, tuple):
            flattened = 1
            for dim in dims:
                flattened *= dim
            dims = flattened 

        self.dims = dims
        self.n_classes = n_classes
        self.contraction_ratio = contraction_ratio
        self.optimizer_type = optimizer_type
        self.batch_size = batch_size
        self.dropout_p = dropout_p
        self.bn = bn
        self.lr = lr
        self.weight_decay = weight_decay  
        self.sample_weight = sample_weight
        self.l1_strength = l1_strength
        self.current_units = self.dims
        self.activation_type = activation_type
        self.negative_slope = negative_slope
        
        
        layers = []

        if int(self.current_units * self.contraction_ratio) <= self.n_classes:
            if self.n_classes > 2:
                layers.append(nn.Linear(self.dims, self.n_classes))
            else:
                layers.append(nn.Linear(self.dims, 1))

        else : #Deep  Neural Network
            self.current_units = int(self.current_units * self.contraction_ratio)
            fc1 = nn.Linear(self.dims, self.current_units)
            layers.append(fc1)
            if self.bn:
                layers.append(nn.BatchNorm1d(num_features=self.current_units))
            if activation_type == "tanh":
                layers.append(nn.Tanh())
            elif activation_type == "relu":
                layers.append(nn.ReLU())
            elif activation_type == "leaky_relu":
                if not negative_slope:
                    negative_slope = 1e-2
                layers.append(nn.LeakyReLU(negative_slope=negative_slope))
            else:
                raise ValueError("Wrong name {} for activation function.".format(activation_type))
            
            layers.append(nn.Dropout(self.dropout_p))

            
            while int(self.current_units * self.contraction_ratio) >= self.n_classes:

                
                fc2 = nn.Linear(self.current_units,  int(self.current_units * self.contraction_ratio))
                self.current_units = int(self.current_units * self.contraction_ratio)
                layers.append(fc2)
                if self.bn:
                    layers.append(nn.BatchNorm1d(num_features=self.current_units))

                if activation_type == "tanh":
                    layers.append(nn.Tanh())
                elif activation_type == "relu":
                    layers.append(nn.ReLU())
                elif activation_type == "leaky_relu":
                    if not negative_slope:
                        negative_slope = 1e-2
                    layers.append(nn.LeakyReLU(negative_slope=negative_slope))
                else:
                    raise ValueError("Wrong name {} for activation function.".format(activation_type))
                
                layers.append(nn.Dropout(self.dropout_p))
                
            if self.n_classes > 2:
        
                fc3 = nn.Linear(self.current_units, self.n_classes)
                layers.append(fc3)
            else:
                fc3 = nn.Linear(self.current_units, 1)
                layers.append(fc3)
        
        if self.n_classes> 2:
            layers.append(nn.Softmax(dim=1))
        else:
            layers.append(nn.Sigmoid())


        self.layers = nn.Sequential(*layers)


    def forward(self, X):
        return self.layers(X)

class ContractingMLP(BaseNet):
    def __init__(
        self,
        dims : Union[int, Tuple[int]],
        n_classes : int,
        sample_weight : Optional[Union["torch.Tensor", "np.ndarray"]] = None,
        **hparams : Any
    ) -> None:
        
        entire_keys = [
            'dims', 
            'n_classes', 
            'sample_weight',
            'contraction_ratio', 
            'optimizer_type', 
            'batch_size',
            'dropout_p',
            'bn',
            'lr',
            'weight_decay',
            'l1_strength',
            'activation_type',
            'negative_slope'
            ]
        default_parameter_dict = {
            'contraction_ratio' : 0.5
        }
        
        # set default for model-specific hyperparameters
        for argument, default in default_parameter_dict.items():
            if argument not in hparams.keys(): 
                hparams.update({argument : default})
        #set default for model-agnostic hyperparameters
        set_default_parameters(hparams)
        # save information of **hparams to self.hparams.
        self.save_hyperparameters(*hparams)
        # validate contraction_ratio
        if not self.hparams.contraction_ratio < 1 and not self.hparams.contraction_ratio >0 :
            raise ValueError("'contraction_ratio' must be values between 0 and 1") 

        super(ContractingMLP, self).__init__(
            dims=dims,
            n_classes=n_classes,
            sample_weight=sample_weight,
            **hparams
        )

        # sanity check. Check if right arguments are declared.
        for key in hparams.keys():
            if key not in entire_keys:
                raise ValueError('Wrong argument is passed to the model.')
        self.model = _ContractingMLP(dims=dims, n_classes=n_classes, sample_weight=sample_weight, **hparams)

    def forward(self, X):
        return self.model.forward(X)

########################################################## _ContractingMLP & ContractingMLP (Ends) ##########################################################

########################################################## _CustomMLP & CustomMLP (Begins) ##########################################################
"""
_CustomMLP and CustomMLP defines an MLP with number of hidden units for hidden layers 
customized for all layers. 

We can define n_hidden_units for all hidden layers with a list of integers.

The hyperparameters that are only in CustomMLP are 'layer_{n}_dim's (for all hidden layers). 


_CustomMLP and CustomMLP are basically identical in structure. The only difference is that
_CustomMLP is an offspring of nn.Module and CustomMLP is an offspring of BaseNet.

Arguments:
    - dims (Union[int, Tuple[int]]): The dimension of the data. e.g., 4, (8,8,1)

    - n_classes (Optional[int]) : Number of classes (labels) in the classification task.
                                    Do not specify this argument (set is as None) when you 
                                re performing regression tasks.
    
    - n_hidden_units_list : Optional[List[int]] : List of all n_hidden_units for all hidden layers.
                                                  If not specified, it would be an old-school perceptron.

    - batch_size (int) : Batch size. Default : 64 (see utils_lightning.py)

    - optimizer_type (str) : Type of the optimizer. ("adam" or "sgd") Default : "adam" (see utils_lightning.py) 
                            #TODO : implement other optimizers.(in model_base.py)

    - dropout_p (0<= float < 1) : Dropout probability Default : 0 (see utils_lightning.py)

    - bn (bool) : Whether to use batch normalization or not. Default : True (see utils_lightning.py)

    - weight_decay (0<= float) : coefficient for L2-regularization. Default : 0 (see utils_lightning.py)

    - lr ( 0 < float) : Learning rate. Default: 1e-4 (see utils_lightning.py)
"""
class _CustomMLP(nn.Module):
    def __init__(
        self,
        dims : Union[int, Tuple[int]],
        n_classes : int, 
        optimizer_type : str, 
        batch_size : int ,
        dropout_p : float,
        bn : bool,
        lr : float,
        weight_decay : float,
        l1_strength : float,
        activation_type : str = "relu",
        negative_slope : Optional[float] = None,
        n_hidden_units_list : Optional[List[int]] = None,
        sample_weight : Optional[Union["torch.Tensor", "np.ndarray"]] = None
    ) -> None:
        super(_CustomMLP, self).__init__()
        if isinstance(dims, tuple):
            flattened = 1
            for dim in dims:
                flattened *= dim
            dims = flattened 
        self.dims = dims
        self.n_classes = n_classes
        self.n_hidden_units_list = n_hidden_units_list
        self.optimizer_type = optimizer_type
        self.batch_size = batch_size
        self.dropout_p = dropout_p
        self.bn = bn
        self.lr = lr
        self.weight_decay = weight_decay  
        self.sample_weight = sample_weight
        self.l1_strength = l1_strength
        self.activation_type = activation_type
        self.negative_slope = negative_slope

        for n_hidden_units in self.n_hidden_units_list:
            if n_hidden_units <=0:
                raise ValueError("Number of hidden units can't be less than or equal to 0.")
        
        layers = []

        if self.n_hidden_units_list is None:
            if self.n_classes > 2:
                layers.append(nn.Linear(self.dims, self.n_classes))
            else:
                layers.append(nn.Linear(self.dims, 1))
        
        else:
            layers.append(nn.Linear(self.dims, self.n_hidden_units_list[0]))
            if self.bn:
                layers.append(nn.BatchNorm1d(num_features=self.n_hidden_units_list[0]))
            if activation_type == "tanh":
                layers.append(nn.Tanh())
            elif activation_type == "relu":
                layers.append(nn.ReLU())
            elif activation_type == "leaky_relu":
                if not negative_slope:
                    negative_slope = 1e-2
                layers.append(nn.LeakyReLU(negative_slope=negative_slope))
            else:
                raise ValueError("Wrong name {} for activation function.".format(activation_type))
            layers.append(nn.Dropout(self.dropout_p))
            the_rest = self.n_hidden_units_list[1:]
            for idx in range(len(the_rest-1)):
                layers.append(nn.Linear(the_rest[idx], the_rest[idx+1]))
                if self.bn:
                    layers.append(nn.BatchNorm1d(num_features=self.the_rest[idx+1]))
                if activation_type == "tanh":
                    layers.append(nn.Tanh())
                elif activation_type == "relu":
                    layers.append(nn.ReLU())
                elif activation_type == "leaky_relu":
                    if not negative_slope:
                        negative_slope = 1e-2
                    layers.append(nn.LeakyReLU(negative_slope=negative_slope))
                else:
                    raise ValueError("Wrong name {} for activation function.".format(activation_type))
                layers.append(nn.Dropout(self.dropout_p))
            
            if self.n_classes > 2:
                layers.append(nn.Linear(the_rest[-1], self.n_classes))
            else:
                layers.append(nn.Linear(the_rest[-1], 1))
        
        if self.n_classes> 2:
            layers.append(nn.Softmax(dim=1))
        else:
            layers.append(nn.Sigmoid())


        self.layers = nn.Sequential(*layers)

    def forward(self, X):
        return self.layers(X)

class CustomMLP(BaseNet):
    def __init__(
        self,
        dims : Union[int, Tuple[int]],
        n_classes : int,
        sample_weight : Optional[Union["torch.Tensor", "np.ndarray"]] = None,
        **hparams : Any
    ) -> None:
        
        entire_keys = [
            'dims', 
            'n_classes', 
            'n_hidden_units_list', 
            'optimizer_type', 
            'batch_size',
            'dropout_p',
            'bn',
            'lr',
            'weight_decay',
            'sample_weight',
            'l1_strength'
            ]
        default_parameter_dict = {
            'n_hidden_units_list' : None
        }
        
        # set default for model-specific hyperparameters
        for argument, default in default_parameter_dict.items():
            if argument not in hparams.keys(): 
                hparams.update({argument : default})
        #set default for model-agnostic hyperparameters
        set_default_parameters(hparams)
        # add hparams : layer_n_dim
        for idx in range(1, len(self.n_hidden_units_list)+1):
            key_str = 'layer_' + str(idx) +'_dim'
            hparams.update({key_str : self.n_hidden_units_list[idx-1]}) 
        # save information of **hparams to self.hparams.
        self.save_hyperparameters(*hparams)
        # n_hidden_units_list
        for n_hidden_units in self.n_hidden_units_list:
            if n_hidden_units <=0:
                raise ValueError("Number of hidden units can't be less than or equal to 0.")

        super(CustomMLP, self).__init__(
            dims=dims,
            n_classes=n_classes,
            sample_weight=sample_weight,
            **hparams
        )

        # sanity check. Check if right arguments are declared.
        for key in hparams.keys():
            if key not in entire_keys:
                raise ValueError('Wrong argument is passed to the model.')
        self.model = _CustomMLP(dims=dims, n_classes=n_classes, sample_weight=sample_weight, **hparams)

    def forward(self, X):
        return self.model.forward(X)

########################################################## _CustomMLP & CustomMLP (Ends) ##########################################################

########################################################## _VGG & VGG (Begins) ##########################################################
class _VGG(nn.Module):
    def __init__(
        self,
        dims : Union[Tuple[int], int],
        n_classes : int, 
        cfg : str,
        batch_size : int,
        optimizer_type : str,
        dropout_p : float,
        bn : bool,
        lr : float,
        weight_decay : float,
        l1_strength : float,
        activation_type : str = "relu",
        negative_slope : Optional[float] = None, 
        sample_weight : Optional[Union["torch.Tensor", "np.ndarray"]] = None
    ) -> None: 
        
        super(_VGG, self).__init__()
        if isinstance(dims, int):
            height = width = math.sqrt(dims)
            if (height != int(height)):
                raise ValueError("Wrong dimension in input.")
            dims = (1, height, width)
        if len(dims) == 2:
            height = dims[0]
            width = dims[1]
            dims = (1, height, width)
        if len(dims) == 4:
            dims = dims[1:]
        if len(dims) > 4:
            raise ValueError("dimension of the input can't be higher than 4.")
        self.dims = dims # (in_channels, height, width)
        self.n_classes = n_classes
        self.cfg = cfg
        self.batch_size = batch_size
        self.optimizer_type = optimizer_type
        self.dropout_p = dropout_p
        self.bn = bn
        self.lr = lr
        self.weight_decay = weight_decay
        self.sample_weight = sample_weight
        self.l1_strength = l1_strength
        self.activation_type = activation_type
        self.negative_slope = negative_slope
    
        self.avgpool = nn.AdaptiveAvgPool2d((7, 7))
        layers = []
        layers.append(nn.Linear(512 * 7 * 7, 4096))
        if activation_type == "tanh":
            layers.append(nn.Tanh())
        elif activation_type == "relu":
            layers.append(nn.ReLU())
        elif activation_type == "leaky_relu":
            if not negative_slope:
                negative_slope = 1e-2
            layers.append(nn.LeakyReLU(negative_slope=negative_slope))
        else:
            raise ValueError("Wrong name {} for activation function.".format(activation_type))

        layers.append(nn.Dropout(p=self.dropout_p))
        layers.append(nn.Linear(4096, 4096))
        if activation_type == "tanh":
            layers.append(nn.Tanh())
        elif activation_type == "relu":
            layers.append(nn.ReLU())
        elif activation_type == "leaky_relu":
            if not negative_slope:
                negative_slope = 1e-2
            layers.append(nn.LeakyReLU(negative_slope=negative_slope))
        else:
            raise ValueError("Wrong name {} for activation function.".format(activation_type))
        layers.append(nn.Dropout(p=self.dropout_p))
        layers.append(nn.Linear(4096, n_classes))
        
        self.classifier = nn.Sequential(*layers)

        self.cfgs: Dict[str, List[Union[str, int]]] = {
        "NoMaxPool" :[64,  128, 256, 256,  512, 512,  512, 512], #only for debugging.
        "VGG11": [64, "M", 128, "M", 256, 256, "M", 512, 512, "M", 512, 512, "M"],
        "VGG13": [64, 64, "M", 128, 128, "M", 256, 256, "M", 512, 512, "M", 512, 512, "M"],
        "VGG16": [64, 64, "M", 128, 128, "M", 256, 256, 256, "M", 512, 512, 512, "M", 512, 512, 512, "M"],
        "VGG19": [64, 64, "M", 128, 128, "M", 256, 256, 256, 256, "M", 512, 512, 512, 512, "M", 512, 512, 512, 512, "M"],
        }
        
    
    def make_layers(
        self,
        cfg : List[Union[str,int]],
        bn : bool=True
    ) -> nn.Sequential:
        layers = []
        in_channels = (self.dims)[0]
        for v in cfg:
            if v=="M":
                layers.append(nn.MaxPool2d(kernel_size=2, stride=2))
            else:
                v = cast(int, v)
                layers.append(nn.Conv2d(in_channels, v, kernel_size=3, padding=1))
                if bn:
                    layers.append(nn.BatchNorm2d(v))
                    
                if self.activation_type == "tanh":
                    layers.append(nn.Tanh())
                elif self.activation_type == "relu":
                    layers.append(nn.ReLU())
                elif self.activation_type == "leaky_relu":
                    if not negative_slope:
                        negative_slope = 1e-2
                    layers.append(nn.LeakyReLU(negative_slope=self.negative_slope))
                else:
                    raise ValueError("Wrong name {} for activation function.".format(self.activation_type))
                in_channels = v

        return nn.Sequential(*layers)    


    def forward(self, X) -> torch.Tensor:
        out = self.make_layers(self.cfgs[self.cfg], self.bn)(X)
        out = self.avgpool(out)
        out = torch.flatten(out, 1)
        out = self.classifier(out) 
        return out

class VGG(ConvNet):

    def __init__(
        self,
        dims : Union[int, Tuple[int]],
        n_classes : int,
        sample_weight : Optional[Union["torch.Tensor", "np.ndarray"]] = None,
        cfg : str ="VGG11",
        **hparams
    ) -> None:
        

        entire_keys = [ 
            'dims',
            'n_classes', 
            'cfg', 
            'optimizer_type', 
            'batch_size',
            'dropout_p',
            'bn',
            'lr',
            'weight_decay',
            'sample_weight',
            'l1_strength',
            'activation_type',
            'negative_slope'
            ]

        default_parameter_dict = {}
    
        # set default for model-specific hyperparameters
        for argument, default in default_parameter_dict.items():
            if argument not in hparams.keys(): 
                hparams.update({argument : default})
        #set default for model-agnostic hyperparameters
        set_default_parameters(hparams)
        # save information of **hparams to self.hparams.
        self.save_hyperparameters(*hparams)

        super(VGG, self).__init__(
            dims=dims,
            n_classes=n_classes,
            sample_weight=sample_weight,
            model_type="VGG",
            cfg=cfg,
            **hparams
        )
        # sanity check. Check if right arguments are declared.
        for key in hparams.keys():
            if key not in entire_keys:
                raise ValueError('Wrong argument is passed to the model.')
        self.model = _VGG(
            dims=dims,
            n_classes=n_classes,
            sample_weight=sample_weight,
            cfg=cfg,
            **hparams
        )

    def forward(self, X):
        return self.model.forward(X)

    def help(self) -> None :
        whoami = "VGG Network\n\n"
        helptext = "Parameters ------------------------------------------------------------------------------------------------------- \n"
        helptext += "n_classes: int \t Number of classes in the classification task. If it is binary classification, n_classes=2\n"
        helptext += "cfg: str\t The configuration of VGG. 'VGG11', 'VGG13', 'VGG16', and 'VGG19' are available.\n"
        helptext += "In defining hyperparameters and optimizer_type, we recommend you to define a dictionary.\n"
        helptext += "Define a dictionary containing :\n\t-'optimizer_type': str (default='adam')\n\t-'dropout_p' : 0 <= float < 1(default : 0)\n\t-'weight_decay' : 0<= float < 1(default=0)\n\t-'lr' : float(default=1e-4)."
        
        text= whoami + helptext
        print(text)
        
class _UNet(nn.Module):
    """
    Paper: `U-Net: Convolutional Networks for Biomedical Image Segmentation
    <https://arxiv.org/abs/1505.04597>`
    Args:
        n_classes: Number of output classes required
        dims : Dimension of the input
        num_layers: Number of layers in each side of U-net (default 5)
        features_start: Number of features in first layer (default 64)
        bilinear: Whether to use bilinear interpolation or transposed convolutions (default) for upsampling.
    """

    def __init__(
        self,
        n_classes : int, 
        dims : Union[int, Tuple[int]],
        batch_size : int,
        optimizer_type : str,
        lr : float,
        weight_decay : float,
        n_layers : int, 
        bn : bool,
        features_start : int, 
        bilinear : bool,
        l1_strength : float,
        activation_type : str = "relu",
        negative_slope : Optional[float] = None,
        model_type : str = "UNet", # don't change this ,
        sample_weight : Optional[Union["torch.Tensor", "np.ndarray"]] = None
    ):
        self.n_classes = n_classes
        self.batch_size = batch_size
        self.optimizer_type = optimizer_type
        self.bn = bn
        self.lr = lr
        self.weight_decay = weight_decay
        self.l1_strength = l1_strength
        self.n_layers = n_layers
        self.features_start = features_start
        self.bilinear = bilinear
        self.model_type = model_type
        self.sample_weight = sample_weight
        self.activation_type = activation_type 
        self.negative_slope = negative_slope

        if self.n_layers < 1:
            raise ValueError(f"n_layers = {self.n_layers}, expected: n_layers > 0")

        if isinstance(dims, int):
            height = width = math.sqrt(dims)
            if (height != int(height)):
                raise ValueError("Wrong dimension in input.")
            dims = (1, height, width)
        if len(dims) == 2:
            height = dims[0]
            width = dims[1]
            dims = (1, height, width)
        if len(dims) == 4:
            dims = dims[1:]
        if len(dims) > 4:
            raise ValueError("dimension of the input can't be higher than 4.")
        self.dims = dims # (in_channels, height, width)
        self.input_channels = self.dims[0]
        super().__init__()

        layers = [DoubleConv(self.input_channels, self.features_start, 
                             bn=self.bn, activation_type=activation_type, negative_slope=negative_slope)]

        feats = self.features_start
        for _ in range(self.n_layers - 1):
            layers.append(Down(feats, feats * 2))
            feats *= 2

        for _ in range(self.n_layers - 1):
            layers.append(Up(feats, feats // 2, self.bilinear))
            feats //= 2

        layers.append(nn.Conv2d(feats, n_classes, kernel_size=1))

        self.layers = nn.ModuleList(layers)

    def forward(self, x):
        xi = [self.layers[0](x)]
        # Down path
        for layer in self.layers[1 : self.n_layers]:
            xi.append(layer(xi[-1]))
        # Up path
        for i, layer in enumerate(self.layers[self.n_layers : -1]):
            xi[-1] = layer(xi[-1], xi[-2 - i])
        return self.layers[-1](xi[-1])


class UNet(ConvNet):
    def __init__(
        self,
        dims : Union[int, Tuple[int]],
        n_classes: int,
        model_type : str = "UNet", # don't change this
        sample_weight : Optional[Union["torch.Tensor", "np.ndarray"]] = None,
        **hparams : Any
    ):

        entire_keys = [
            'n_classes', 
            'model_type',
            'dims', 
            'n_layers', 
            'bn',
            'features_start', 
            'bilinear',
            'batch_size' ,
            'optimizer_type' ,
            'lr' ,
            'weight_decay',
            'sample_weight',
            'l1_strength',
            'activation_type',
            'negative_slope'
        ]

        default_parameter_dict = {
            'n_layers' : 3,
            'features_start' : 64,
            'bilinear' : False
        }
        
        
        
        
        # set default for model-specific hyperparameters
        for argument, default in default_parameter_dict.items():
            if argument not in hparams.keys(): 
                hparams.update({argument : default})
        #set default for model-agnostic hyperparameters
        set_default_parameters(hparams)
        # for some reason, we don't use dropout here
        hparams.pop('dropout_p')
        # save information of **hparams to self.hparams.
        self.save_hyperparameters(*hparams)

        super(UNet, self).__init__(
            n_classes=n_classes, 
            dims=dims, 
            sample_weight=sample_weight,
            model_type="UNet",
            **hparams
        )
        # sanity check. Check if right arguments are declared.
        for key in hparams.keys():
            if key not in entire_keys:
                raise ValueError('Wrong argument is passed to the model.')
        self.model = _UNet(
            n_classes=n_classes, 
            dims=dims, 
            sample_weight=sample_weight,
            **hparams
        )

    def forward(self, X):
        return self.model.forward(X)
    
    
    
    def help(self) -> None :
        whoami = "U-Net. \n\n"
        helptext = "Parameters ------------------------------------------------------------------------------------------------------- \n"
        helptext += "n_classes: int \t Number of classes in the classification task. If it is binary classification, n_classes=2\n"
        helptext += "In defining hyperparameters and optimizer_type, we recommend you to define a dictionary.\n"
        helptext += "Define a dictionary containing :\n\t"
        helptext += "-'optimizer_type': str (default='adam')\n\t" 
        helptext += "-'n_hidden_units': int (default=10)\n\t"
        helptext += "-'weight_decay' : 0< float < 1\n\t"
        helptext += "-'depth' : int (default=5)\n\t"
        helptext += "-'bilinear': bool (default=True)\n\t"
        helptext += "-'lr' : float (default=1e-4)."
        
        text= whoami + helptext
        print(text)
    
    
"""

TODO : Implement GoogleNet
TODO : Implement ResNet
TODO : Implement YOLO

"""