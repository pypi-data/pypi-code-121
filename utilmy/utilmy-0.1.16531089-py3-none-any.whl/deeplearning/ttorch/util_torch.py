# -*- coding: utf-8 -*-
"""#
Doc::

    Utils for torch training
    TVM optimizer
    https://spell.ml/blog/optimizing-pytorch-models-using-tvm-YI7pvREAACMAwYYz

    https://github.com/szymonmaszke/torchlayers

    https://github.com/Riccorl/transformers-embedder

    https://github.com/szymonmaszke/torchfunc


"""
import os, random, numpy as np, glob, pandas as pd, matplotlib.pyplot as plt ;from box import Box
from copy import deepcopy
from typing import List,Dict,Union

from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from sklearn.metrics import mean_squared_error, accuracy_score, roc_curve, auc, roc_auc_score, precision_score, recall_score, precision_recall_curve, accuracy_score


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
    ss = help_create(MNAME)
    log(ss)


#############################################################################################
def test_all():
    """function test_all
    Args:
    Returns:
        
    """
    log(MNAME)
    test1()
    # test2()


def test1():
    """function test2
    Args:
    Returns:
        
    """
    arg = Box({
      "dataurl":  "https://github.com/caravanuden/cardio/raw/master/cardio_train.csv",
      "datapath": './cardio_train.csv',

      ##### Rules
      "rules" : {},

      #####
      "train_ratio": 0.7,
      "validation_ratio": 0.1,
      "test_ratio": 0.2,

      "model_type": 'dataonly',
      "input_dim_encoder": 16,
      "output_dim_encoder": 16,
      "hidden_dim_encoder": 100,
      "hidden_dim_db": 16,
      "n_layers": 1,


      ##### Training
      "seed": 42,
      "device": 'cpu',  ### 'cuda:0',
      "batch_size": 32,
      "epochs": 1,
      "early_stopping_thld": 10,
      "valid_freq": 1,
      'saved_filename' :'./model.pt',

    })



###############################################################################################
def device_setup( device='cpu', seed=42, arg:dict=None):
    """Setup 'cpu' or 'gpu' for device and seed for torch
        
    """
    device = arg.device if arg is not None else device
    seed   = arg.seed   if arg is not None else seed
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


def dataloader_create(train_X=None, train_y=None, valid_X=None, valid_y=None, test_X=None, test_y=None,  
                     batch_size=64, shuffle=True, device='cpu', batch_size_val=None, batch_size_test=None):
    """dataloader_create
    Doc::

         Example

        
    """
    train_loader, valid_loader, test_loader = None, None, None

    batch_size_val  = valid_X.shape[0] if batch_size_val is None else batch_size_val
    batch_size_test = valid_X.shape[0] if batch_size_test is None else batch_size_test

    if train_X is not None :
        train_X, train_y = torch.tensor(train_X, dtype=torch.float32, device=device), torch.tensor(train_y, dtype=torch.float32, device=device)
        train_loader = DataLoader(TensorDataset(train_X, train_y), batch_size=batch_size, shuffle=shuffle)
        log("train size", len(train_X) )

    if valid_X is not None :
        valid_X, valid_y = torch.tensor(valid_X, dtype=torch.float32, device=device), torch.tensor(valid_y, dtype=torch.float32, device=device)
        valid_loader = DataLoader(TensorDataset(valid_X, valid_y), batch_size= batch_size_val)
        log("val size", len(valid_X)  )

    if test_X  is not None :
        test_X, test_y   = torch.tensor(test_X,  dtype=torch.float32, device=device), torch.tensor(test_y, dtype=torch.float32, device=device)
        test_loader  = DataLoader(TensorDataset(test_X, test_y), batch_size=test_X.shape[0])
        log("test size:", len(test_X) )

    return train_loader, valid_loader, test_loader




###############################################################################################
def model_load(dir_checkpoint:str, torch_model=None, doeval=True, dotrain=False, device='cpu', input_shape=None, **kw):
    """function model_load from checkpoint
    Doc::

        dir_checkpoint = "./check/mycheck.pt"
        torch_model    = "./mymodel:NNClass.py"   ### or Torch Object
        model_load(dir_checkpoint, torch_model=None, doeval=True, dotrain=False, device='cpu')
    """

    if isinstance( torch_model, str) : ### "path/mymodule.py:myModel"
        torch_class_name = load_function_uri(uri_name= torch_model)
        torch_model      = torch_class_name() #### Class Instance  Buggy
        log('loaded from file ', torch_model)

    if 'http' in dir_checkpoint :
       #torch.cuda.is_available():
       map_location = torch.device('gpu') if 'gpu' in device else  torch.device('cpu')
       import torch.utils.model_zoo as model_zoo
       model_state = model_zoo.load_url(dir_checkpoint, map_location=map_location)
    else :   
       checkpoint = torch.load( dir_checkpoint)
       model_state = checkpoint['model_state_dict']
       log( f"loss: {checkpoint.get('loss')}\t at epoch: {checkpoint.get('epoch')}" )
       
    torch_model.load_state_dict(state_dict=model_state)

    if doeval:
      ## Evaluate
      torch_model.eval()
      # x   = torch.rand(1, *input_shape, requires_grad=True)
      # out = torch_model(x)

    if dotrain:
      torch_model.train()  

    return torch_model 
    

def model_save(torch_model=None, dir_checkpoint:str="./checkpoint/check.pt", optimizer=None, cc:dict=None,
               epoch=-1, loss_val=0.0, show=1, **kw):
    """function model_save
    Doc::

        dir_checkpoint = "./check/mycheck.pt"
        model_save(model, dir_checkpoint, epoch=1,)
    """
    from copy import deepcopy
    dd = {}
    dd['model_state_dict'] = deepcopy(torch_model.state_dict())
    dd['epoch'] = cc.get('epoch',   epoch)
    dd['loss']  = cc.get('loss_val', loss_val)
    dd['optimizer_state_dict']  = optimizer.state_dict()  if optimizer is not None else {}

    torch.save(dd, dir_checkpoint)
    if show>0: log(dir_checkpoint)
    return dir_checkpoint



def model_load_state_dict_with_low_memory(model: nn.Module, state_dict: Dict[str, torch.Tensor]):
    """  using 1x RAM for large model
    Doc::

        model = MyModel()
        model_load_state_dict_with_low_memory(model, torch.load("checkpoint.pt"))

        # free up memory by placing the model in the `meta` device
        https://github.com/FrancescoSaverioZuppichini/Loading-huge-PyTorch-models-with-linear-memory-consumption


    """
    from typing import Dict

    def get_keys_to_submodule(model: nn.Module) -> Dict[str, nn.Module]:
        keys_to_submodule = {}
        # iterate all submodules
        for submodule_name, submodule in model.named_modules():
            # iterate all paramters in each submobule
            for param_name, param in submodule.named_parameters():
                # param_name is organized as <name>.<subname>.<subsubname> ...
                # the more we go deep in the model, the less "subname"s we have
                splitted_param_name = param_name.split('.')
                # if we have only one subname, then it means that we reach a "leaf" submodule, 
                # we cannot go inside it anymore. This is the actual parameter
                is_leaf_param = len(splitted_param_name) == 1
                if is_leaf_param:
                    # we recreate the correct key
                    key = f"{submodule_name}.{param_name}"
                    # we associate this key with this submodule
                    keys_to_submodule[key] = submodule
                    
        return keys_to_submodule

    # free up memory by placing the model in the `meta` device
    model.to(torch.device("meta"))
    keys_to_submodule = get_keys_to_submodule(model)
    for key, submodule in keys_to_submodule.items():
        # get the valye from the state_dict
        val = state_dict[key]
        # we need to substitute the parameter inside submodule, 
        # remember key is composed of <name>.<subname>.<subsubname>
        # the actual submodule's parameter is stored inside the 
        # last subname. If key is `in_proj.weight`, the correct field if `weight`
        param_name = key.split('.')[-1]
        param_dtype = getattr(submodule, param_name).dtype
        val = val.to(param_dtype)
        # create a new parameter
        new_val = torch.nn.Parameter(val)
        setattr(submodule, param_name, new_val)




###############################################################################################
def model_train(model, loss_calc, optimizer=None, train_loader=None, valid_loader=None, arg:dict=None ):
    """One liner for training a pytorch model.
    Doc::

       import utilmy.deepelearning.ttorch.util_torch as ut
       cc= Box({})
       cc=0

       model= ut.test_model_dummy2()
       log(model)

       ut.model_train(model,
            loss_calc=
            optimizer= torch.optim.Adam(model.parameters(), lr= cc.lr)


    """
    arg   = Box(arg)  ### Params
    histo = Box({})  ### results


    arg.lr     = arg.get('lr', 0.001)
    arg.epochs = arg.get('epochs', 1)
    arg.early_stopping_thld    = arg.get('early_stopping_thld' ,2)
    arg.seed   = arg.get('seed', 42)
    model_params   = arg.model_info[ arg.model_type]

    metric_list = arg.get('metric_list',  ['mean_squared_error'] )


    #### Optimizer model params
    if optimizer is None:
       optimizer      = torch.optim.Adam(model.parameters(), lr= arg.lr)


    #### Train params
    counter_early_stopping = 1
    log('saved_filename: {}\n'.format( arg.dir_modelsave))
    best_val_loss = float('inf')


    for epoch in range(1, arg.epochs+1):
      model.train()
      for batch_train_x, batch_train_y in train_loader:
        batch_train_y = batch_train_y.unsqueeze(-1)
        optimizer.zero_grad()

        ###### Base output #########################################
        output    = model(batch_train_x).view(batch_train_y.size())


        ###### Loss Rule perturbed input and its output
        loss = loss_calc()


        ###### Total Losses
        loss.backward()
        optimizer.step()


      # Evaluate on validation set
      if epoch % arg.valid_freq == 0:
        model.eval()
        with torch.no_grad():
          for val_x, val_y in valid_loader:
            val_y = val_y.unsqueeze(-1)

            output = model(val_x).reshape(val_y.size())
            val_loss_task = loss_calc(output, val_y).item()

            val_loss = val_loss_task
            y_true = val_y.cpu().numpy()
            y_score = output.cpu().numpy()
            y_pred = np.round(y_score)

            y_true = y_pred.reshape(y_true.shape[:-1])
            y_pred = y_pred.reshape(y_pred.shape[:-1])
            val_acc = metrics_eval(y_pred, ytrue=y_true, metric_list= metric_list)


          if val_loss < best_val_loss:
            counter_early_stopping = 1
            best_val_loss = val_loss
            best_model_state_dict = deepcopy(model.state_dict())
            torch.save({
                'epoch': epoch,
                'model_state_dict': best_model_state_dict,
                'optimizer_state_dict': optimizer.state_dict(),
                'loss': best_val_loss
            }, arg.dir_modelsave)
          else:
            log( f'[Valid] Epoch: {epoch} Loss: {val_loss} ')
            if counter_early_stopping >= arg.early_stopping_thld:
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
    for alpha in alphas:
      model_eval.eval()
      with torch.no_grad():
        for te_x, te_y in test_loader:
          te_y = te_y.unsqueeze(-1)


        test_loss_task = loss_task_func(output, te_y.view(output.size())).item()


        y_true = te_y.cpu().numpy()
        y_score = output.cpu().numpy()
        y_pred = np.round(y_score)

        test_acc = mean_squared_error(y_true.squeeze(), y_pred.squeeze())

      log('[Test] Average loss: {:.8f} (alpha:{})'.format(test_loss_task, alpha))
      log('[Test] Accuracy: {:.4f} (alpha:{})'.format(test_acc, alpha))
      log("[Test] Ratio of verified predictions: {:.6f} (alpha:{})".format(test_ratio, alpha))
      log()



def model_summary(model, **kw):
    """   PyTorch model to summarize.
    Doc::

        https://pypi.org/project/torch-summary/
        #######################
        import torchvision
        model = torchvision.models.resnet50()
        summary(model, (3, 224, 224), depth=3)
        #######################
        model (nn.Module):
                PyTorch model to summarize.

        input_data (Sequence of Sizes or Tensors):
                Example input tensor of the model (dtypes inferred from model input).
                - OR -
                Shape of input data as a List/Tuple/torch.Size
                (dtypes must match model input, default is FloatTensors).
                You should NOT include batch size in the tuple.
                - OR -
                If input_data is not provided, no forward pass through the network is
                performed, and the provided model information is limited to layer names.
                Default: None

        batch_dim (int):
                Batch_dimension of input data. If batch_dim is None, the input data
                is assumed to contain the batch dimension.
                WARNING: in a future version, the default will change to None.
                Default: 0

        branching (bool):
                Whether to use the branching layout for the printed output.
                Default: True

        col_names (Iterable[str]):
                Specify which columns to show in the output. Currently supported:
                ("input_size", "output_size", "num_params", "kernel_size", "mult_adds")
                If input_data is not provided, only "num_params" is used.
                Default: ("output_size", "num_params")

        col_width (int):
                Width of each column.
                Default: 25

        depth (int):
                Number of nested layers to traverse (e.g. Sequentials).
                Default: 3

        device (torch.Device):
                Uses this torch device for model and input_data.
                If not specified, uses result of torch.cuda.is_available().
                Default: None

        dtypes (List[torch.dtype]):
                For multiple inputs, specify the size of both inputs, and
                also specify the types of each parameter here.
                Default: None

        verbose (int):
                0 (quiet): No output
                1 (default): Print model summary
                2 (verbose): Show weight and bias layers in full detail
                Default: 1

        *args, **kwargs:
                Other arguments used in `model.forward` function.

    Return:
        ModelStatistics object
                See torchsummary/model_statistics.py for more information.
    """
    try :
       from torchsummary import summary
    except:
        os.system('pip install torch-summary')
        from torchsummary import summary

    return summary(model, **kw)


###############################################################################################
########### Custom layer ######################################################################
class SmeLU(nn.Module):
    """
    This class implements the Smooth ReLU (SmeLU) activation function proposed in:
    https://arxiv.org/pdf/2202.06499.pdf


    Example :
        def main() -> None:
            # Init figures
            fig, ax = plt.subplots(1, 1)
            fig_grad, ax_grad = plt.subplots(1, 1)
            # Iterate over some beta values
            for beta in [0.5, 1., 2., 3., 4.]:
                # Init SemLU
                smelu: SmeLU = SmeLU(beta=beta)
                # Make input
                input: torch.Tensor = torch.linspace(-6, 6, 1000, requires_grad=True)
                # Get activations
                output: torch.Tensor = smelu(input)
                # Compute gradients
                output.sum().backward()
                # Plot activation and gradients
                ax.plot(input.detach(), output.detach(), label=str(beta))
                ax_grad.plot(input.detach(), input.grad.detach(), label=str(beta))
            # Show legend, title and grid
            ax.legend()
            ax_grad.legend()
            ax.set_title("SemLU")
            ax_grad.set_title("SemLU gradient")
            ax.grid()
            ax_grad.grid()
            # Show plots
            plt.show()

    """

    def __init__(self, beta: float = 2.) -> None:
        """
        Constructor method.
        beta (float): Beta value if the SmeLU activation function. Default 2.
        """
        # Call super constructor
        super(SmeLU, self).__init__()
        # Check beta
        assert beta >= 0., f"Beta must be equal or larger than zero. beta={beta} given."
        # Save parameter
        self.beta: float = beta

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        input (torch.Tensor): Tensor of any shape
        :return (torch.Tensor): Output activation tensor of the same shape as the input tensor
        """
        output: torch.Tensor = torch.where(input >= self.beta, input,
                                           torch.tensor([0.], device=input.device, dtype=input.dtype))
        output: torch.Tensor = torch.where(torch.abs(input) <= self.beta,
                                           ((input + self.beta) ** 2) / (4. * self.beta), output)
        return output



###############################################################################################
########### Metrics  ##########################################################################
from utilmy.deeplearning.util_dl import metrics_eval, metrics_plot




#############################################################################################
#############################################################################################
class test_model_dummy(nn.Module):
  def __init__(self, input_dim, output_dim, hidden_dim=4):
    super(DataEncoder, self).__init__()
    self.input_dim = input_dim
    self.output_dim = output_dim
    self.net = nn.Sequential(nn.Linear(input_dim, hidden_dim),
                             nn.ReLU(),
                             nn.Linear(hidden_dim, output_dim))

  def forward(self, x):
    return self.net(x)


class test_model_dummy2(nn.Sequential):
    def __init__(self):
        super().__init__()
        self.in_proj = nn.Linear(2, 10)
        self.stages = nn.Sequential(
             nn.Linear(10, 10),
             nn.Linear(10, 10)
        )
        self.out_proj = nn.Linear(10, 2)



if 'utils':
    def to_numpy(tensor):
        return tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()

    from utilmy.utilmy import load_function_uri

    def test_load_function_uri():
        uri_name = "./testdata/ttorch/models.py:SuperResolutionNet"
        myclass = load_function_uri(uri_name)
        log(myclass)


    def test_create_model_pytorch(dirsave=None, model_name=""):
        """   Create model classfor testing purpose

        
        """    
        ss = """import torch ;  import torch.nn as nn; import torch.nn.functional as F
        class SuperResolutionNet(nn.Module):
            def __init__(self, upscale_factor, inplace=False):
                super(SuperResolutionNet, self).__init__()

                self.relu = nn.ReLU(inplace=inplace)
                self.conv1 = nn.Conv2d(1, 64, (5, 5), (1, 1), (2, 2))
                self.conv2 = nn.Conv2d(64, 64, (3, 3), (1, 1), (1, 1))
                self.conv3 = nn.Conv2d(64, 32, (3, 3), (1, 1), (1, 1))
                self.conv4 = nn.Conv2d(32, upscale_factor ** 2, (3, 3), (1, 1), (1, 1))
                self.pixel_shuffle = nn.PixelShuffle(upscale_factor)

                self._initialize_weights()

            def forward(self, x):
                x = self.relu(self.conv1(x))
                x = self.relu(self.conv2(x))
                x = self.relu(self.conv3(x))
                x = self.pixel_shuffle(self.conv4(x))
                return x

            def _initialize_weights(self):
                init.orthogonal_(self.conv1.weight, init.calculate_gain('relu'))
                init.orthogonal_(self.conv2.weight, init.calculate_gain('relu'))
                init.orthogonal_(self.conv3.weight, init.calculate_gain('relu'))
                init.orthogonal_(self.conv4.weight)    

        """
        ss = ss.replace("    ", "")  ### for indentation

        if dirsave  is not None :
            with open(dirsave, mode='w') as fp:
                fp.write(ss)
            return dirsave    
        else :
            SuperResolutionNet =  None
            eval(ss)        ## trick
            return SuperResolutionNet  ## return the class




def test_dataset_classification_fake(nrows=500):
    """function test_dataset_classification_fake
    Args:
        nrows:   
    Returns:
        
    """
    from sklearn import datasets as sklearn_datasets
    ndim    =11
    coly    = 'y'
    colnum  = ["colnum_" +str(i) for i in range(0, ndim) ]
    colcat  = ['colcat_1']
    X, y    = sklearn_datasets.make_classification(n_samples=nrows, n_features=ndim, n_classes=1,
                                                   n_informative=ndim-2)
    df         = pd.DataFrame(X,  columns= colnum)
    df[coly]   = y.reshape(-1, 1)

    for ci in colcat :
      df[ci] = np.random.randint(0,1, len(df))

    pars = { 'colnum': colnum, 'colcat': colcat, "coly": coly }
    return df, pars



###################################################################################################
def load_partially_compatible(model,device='cpu'):
    current_model=model.state_dict()
    keys_vin=torch.load('',map_location=device)

    new_state_dict={k:v if v.size()==current_model[k].size()  else  current_model[k] for k,v in zip(current_model.keys(), keys_vin['model_state_dict'].values()) 
                    }    
    current_model.load_state_dict(new_state_dict)
    return current_model



###################################################################################################
def gradwalk(x, _depth=0):
    if hasattr(x, 'grad_fn'):
        x = x.grad_fn
    if hasattr(x, 'next_functions'):
        for fn in x.next_functions:
            print(' ' * _depth + str(fn))
            gradwalk(fn[0], _depth+1)

def gradwalk_run(graph):
    for name, param in graph.named_parameters():
        gradwalk(param)



if __name__ == "__main__":
    import fire 
    fire.Fire() 
    # test_all()


