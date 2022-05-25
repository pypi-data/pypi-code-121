# -*- coding: utf-8 -*-
MNAME=""
"""# 
Doc::
 Time Series Anomaly Detection using LSTM Autoencoders with PyTorch in Python
pip install -qq arff2pandas watermark

# %reload_ext watermark
# %watermark -v -p numpy,pandas,torch,arff2pandas


  https://prod.liveshare.vsengsaas.visualstudio.com/join?B79A51FE5D82309D32D1283340E14D9C411C


Join Zoom Meeting
https://us05web.zoom.us/j/2933746463?pwd=WUhRWkx0NWNZRVBFVjZ4enV6Y1R2QT09

Meeting ID: 293 374 6463
Passcode: J50Muh





"""
import os, glob, sys, math, time, json, functools, random, yaml, gc, copy
from datetime import datetime
import seaborn as sns, pandas as pd, numpy as np
from box import Box
from pylab import rcParams
import matplotlib.pyplot as plt
from matplotlib import rc
from sklearn.model_selection import train_test_split


from torch import nn, optim
import torch
import torch.nn.functional as F


#############################################################################################
from utilmy import log, log2

def help():
    """function help        """
    from utilmy import help_create
    print( help_create(MNAME) )



#############################################################################################
def test_all() -> None:
    """function test_all   to be used in test.py         """
    log(MNAME)
    test1()



def test1():
  """ lSTM Auto-encoder
  Example
  -------
    In this tutorial, you learned how to create an LSTM Autoencoder with PyTorch and use it to detect heartbeat anomalies in ECG data.
  
    - [Read  tutorial](https://www.curiousily.com/posts/time-series-anomaly-detection-using-lstm-autoencoder-with-pytorch-in-python/)
    - [Run  notebook in your browser (Google Colab)](https://colab.research.google.com/drive/1_J2MrBSvsJfOcVmYAN2-WSp36BtsFZCa)
    - [Read  Getting Things Done with Pytorch book](https://github.com/curiousily/Getting-Things-Done-with-Pytorch)
  
    You learned how to:
  
    - Prepare a dataset for Anomaly Detection from Time Series Data
    - Build an LSTM Autoencoder with PyTorch
    - Train and evaluate your model
    - Choose a cc.THRESHOLD for anomaly detection
    - Classify unseen examples as normal or anomaly
  
    While our Time Series data is univariate (have only 1 feature),  code should work for multivariate datasets (multiple features) with little or no modification. Feel free to try it!
  
    ## References
    - [Sequitur - Recurrent Autoencoder (RAE)](https://github.com/shobrook/sequitur)
    - [Towards Never-Ending Learning from Time Series Streams](https://www.cs.ucr.edu/~eamonn/neverending.pdf)
    - [LSTM Autoencoder for Anomaly Detection](https://towardsdatascience.com/lstm-autoencoder-for-anomaly-detection-e1f4f2ee7ccf)
  """

  sns.set(style='whitegrid', palette='muted', font_scale=1.2)
  HAPPY_COLORS_PALETTE = ["#01BEFE", "#FFDD00", "#FF7D00", "#FF006D", "#ADFF02", "#8F00FF"]
  sns.set_palette(sns.color_palette(HAPPY_COLORS_PALETTE))
  rcParams['figure.figsize'] = 12, 8

  #### params
  cc             = Box({})
  cc.epochs      = 1
  cc.device      = 'cpu'  ### 'gpu'
  cc.RANDOM_SEED = 42
  cc.MODEL_PATH  = 'model.pth'
  cc.THRESHOLD   = 26


  np.random.seed(cc.RANDOM_SEED)
  torch.manual_seed(cc.RANDOM_SEED)
  device = torch.device( cc.device)


  #######  Input data  ###########################################################################
  df = dataset_ECG5000_fetch_pandas(nrows=100)


  """have 5,000 examples. Each row represents a single heartbeat record. possible classes:"""
  CLASS_NORMAL = 1
  df = dataset_ECG5000_prep(df)
  classes = df.target.unique()



  """ normal class has a distinctly different pattern than all or classes. 
  Maybe our model will be able to detect anomalies?
  ### Data Preprocessing
  """


  """######## Data prep: Each Time Series will be converted to a 
     2D Tensor in  shape *sequence length* x *number of features* (140x1 in our case).
  """
  normal_df = df[df.target == str(CLASS_NORMAL)].drop(labels='target', axis=1)

  train_df, val_df = train_test_split(normal_df, test_size=0.15, random_state=cc.RANDOM_SEED)
  val_df, test_df  = train_test_split(val_df, test_size=0.33, random_state=cc.RANDOM_SEED)
  train_dataset, seq_len, n_features = dataset_create(train_df)
  val_dataset, _, _          = dataset_create(val_df)
  test_normal_dataset, _, _  = dataset_create(test_df)



  """######## Data prep: merge all or classes and mark as anomalies:"""
  anomaly_df = df[df.target != str(CLASS_NORMAL)].drop(labels='target', axis=1)
  test_anomaly_dataset, _, _ = dataset_create(anomaly_df)



  log("###### LSTM Autoencoder  ")
  model = modelRecurrentAutoencoder(seq_len, n_features, 128)
  model = model.to(device)


  """using a batch size of 1 (our model sees only 1 sequence at a time). 
  which measures  MAE (mean absolute error). Why?  reconstructions seem to be better than with MSE (mean squared error).
  ## Anomaly Detection in ECG Data
  use normal heartbeats as training data for our model and record  *reconstruction loss*.     
  """
  model, history = model_train(model, train_dataset, val_dataset, n_epochs= cc.epochs)

  model_plotLoss(history)

  model_save(model, cc.MODEL_PATH)



  ############################################################################
  #  if you want to download and load  pre-trained model:"""
  # !gdown --id 1jEYx5wGsb7Ix8cZAw3l5p5pOwHs3_I9A
  # model = torch.load('model.pth')
  # model = model.to(device)

  """## Choosing a cc.THRESHOLD
     reconstruction error on  training set.
  """

  """Our function goes through each example in  dataset and records  predictions and losses."""
  _, losses = model_predict(model, train_dataset)
  sns.distplot(losses, bins=50, kde=True);



  """## Evaluation
  Using  cc.THRESHOLD, can turn  problem into a simple binary classification task:
  - If  reconstruction loss for an example is below  cc.THRESHOLD, classify it as a *normal* heartbeat
  - Alternatively, if  loss is higher than  cc.THRESHOLD, classify it as an anomaly
  """


  ### Normal hearbeats
  ### Let's check how well our model does on normal heartbeats. use  normal heartbeats from  test set (our model haven't seen those):
  predictions, pred_losses = model_predict(model, test_normal_dataset)
  sns.distplot(pred_losses, bins=50, kde=True)

  # """count  correct predictions:"""
  correct = sum(l <= cc.THRESHOLD for l in pred_losses)
  print(f'Correct normal predictions: {correct}/{len(test_normal_dataset)}')



  """### Anomalies: do  same with  anomaly examples, but ir number is much higher. 
  get a subset that has  same size as  normal heartbeats:
  """
  anomaly_dataset = test_anomaly_dataset[:len(test_normal_dataset)]


  """Eval: predictions of our model for  subset of anomalies:"""
  predictions, pred_losses = model_predict(model, anomaly_dataset)
  sns.distplot(pred_losses, bins=50, kde=True);


  """Accuracy number of examples above  cc.THRESHOLD (considered as anomalies):"""
  correct = sum(l > cc.THRESHOLD for l in pred_losses)
  print(f'Correct anomaly predictions: {correct}/{len(anomaly_dataset)}')


  """have very good results. 
  In  real world, you can tweak  cc.THRESHOLD depending on what kind of errors you want to tolerate. 
  In this case, you might want to have more false positives (normal heartbeats considered as anomalies) 
  than false negatives (anomalies considered as normal).
  #### Looking at Examples  
  can overlay  real and reconstructed Time Series values to see how close y are. 
  do it for some normal and anomaly cases:
  """
  fig, axs = plt.subplots(nrows=len(classes) // 3 + 1, ncols=3, sharey=True, figsize=(14, 8))

  for i, data in enumerate(test_normal_dataset[:6]):
    plot_prediction(data, model, title='Normal', ax=axs[0, i])

  for i, data in enumerate(test_anomaly_dataset[:2]):
    plot_prediction(data, model, title='Anomaly', ax=axs[1, i])

  fig.tight_layout()




def dataset_ECG5000_fetch_pandas(nrows=100, dirout="./ztmp/"):
  """combine  training and test data into a single data frame.
     This will give us more data to train our Autoencoder. also shuffle it:"""
  from arff2pandas import a2p

  if not os.path.isfile(dirout + '/ECG5000_TRAIN.arff' ):
     from utilmy.util_download import google_download
     google_download( "16MIleqoIr1vYxlGk4GKnGmrsCPuWkkpT", dirout=dirout, unzip=True)
     #os.makedirs(dirout, exist_ok=True)
     #os.system(f"cd {dirout} && gdown --id  ")
     #os.system(f"unzip -qq  {dirout}/ECG5000.zip")

  with open( dirout + '/ECG5000_TRAIN.arff') as f:
    train = a2p.load(f)

  with open(dirout + '/ECG5000_TEST.arff') as f:
    test = a2p.load(f)

  df = train.append(test)
  df = df.sample(frac=1.0)
  df = df.sample(n=nrows)
  return df


def dataset_ECG5000_prep(df):
  """have 5,000 examples. Each row represents a single heartbeat record. Let's name  possible classes:"""
  CLASS_NORMAL = 1
  class_names = ['Normal','R on T','PVC','SP','UB']

  new_columns = list(df.columns)
  new_columns[-1] = 'target'
  df.columns = new_columns


  """## Exploratory Data Analysis"""
  df.target.value_counts()
  ax = sns.countplot(df.target)
  ax.set_xticklabels(class_names);


  """ normal class, has by far,  most examples. This is great because use it to train our model.
  Let's have a look at an averaged (smood out with one standard deviation on top and bottom of it) Time Series for each class:
  """
  classes = df.target.unique()

  fig, axs = plt.subplots(nrows=len(classes) // 3 + 1, ncols=3, sharey=True, figsize=(14, 8))
  for i, cls in enumerate(classes):
    ax = axs.flat[i]
    data = df[df.target == cls] \
      .drop(labels='target', axis=1) \
      .mean(axis=0) \
      .to_numpy()
    plot_time_series_class(data, class_names[i], ax)

  fig.delaxes(axs.flat[-1])
  fig.tight_layout()

  return df


#############################################################################################################
def dataset_create(df):

  sequences = df.astype(np.float32).to_numpy().tolist()
  dataset   = [torch.tensor(s).unsqueeze(1).float() for s in sequences]
  n_seq, seq_len, n_features = torch.stack(dataset).shape

  return dataset, seq_len, n_features



#############################################################################################################
class modelEncoder(nn.Module):
  """ *Encoder* uses two LSTM layers to compress  Time Series data input.

  Next, decode  compressed representation using a *Decoder*:
  """
  def __init__(self, seq_len, n_features, embedding_dim=64):
    super(modelEncoder, self).__init__()

    self.seq_len, self.n_features = seq_len, n_features
    self.embedding_dim, self.hidden_dim = embedding_dim, 2 * embedding_dim

    self.rnn1 = nn.LSTM(
      input_size=n_features,
      hidden_size=self.hidden_dim,
      num_layers=1,
      batch_first=True
    )

    self.rnn2 = nn.LSTM(
      input_size=self.hidden_dim,
      hidden_size=embedding_dim,
      num_layers=1,
      batch_first=True
    )

  def forward(self, x):
    x = x.reshape((1, self.seq_len, self.n_features))

    x, (_, _)        = self.rnn1(x)
    x, (hidden_n, _) = self.rnn2(x)

    return hidden_n.reshape((self.n_features, self.embedding_dim))



class modelDecoder(nn.Module):
  """Our Decoder contains two LSTM layers and an output layer that gives  final reconstruction.
  #
  # Time to wrap everything into an easy to use module:
  """
  def __init__(self, seq_len, input_dim=64, n_features=1):
    super(modelDecoder, self).__init__()

    self.seq_len, self.input_dim = seq_len, input_dim
    self.hidden_dim, self.n_features = 2 * input_dim, n_features

    self.rnn1 = nn.LSTM(
      input_size=input_dim,
      hidden_size=input_dim,
      num_layers=1,
      batch_first=True
    )

    self.rnn2 = nn.LSTM(
      input_size=input_dim,
      hidden_size=self.hidden_dim,
      num_layers=1,
      batch_first=True
    )

    self.output_layer = nn.Linear(self.hidden_dim, n_features)

  def forward(self, x):
    x = x.repeat(self.seq_len, self.n_features)
    x = x.reshape((self.n_features, self.seq_len, self.input_dim))

    x, (hidden_n, cell_n) = self.rnn1(x)
    x, (hidden_n, cell_n) = self.rnn2(x)
    x = x.reshape((self.seq_len, self.hidden_dim))

    return self.output_layer(x)



class modelRecurrentAutoencoder(nn.Module):
  """### LSTM Autoencoder
   [Autoencoder's](https://en.wikipedia.org/wiki/Autoencoder) job is to get some input data, pass it through  model, and obtain a reconstruction of  input.  reconstruction should match  input as much as possible.  trick is to use a small number of parameters, so your model learns a compressed representation of  data.
  In a sense, Autoencoders try to learn only  most important features (compressed version) of  data. Here, have a look at how to feed Time Series data to an Autoencoder. use a couple of LSTM layers (hence  LSTM Autoencoder) to capture  temporal dependencies of  data.
  To classify a sequence as normal or an anomaly, pick a cc.THRESHOLD above which a heartbeat is considered abnormal.


  ### Reconstruction Loss
  When training an Autoencoder,  objective is to reconstruct  input as best as possible.
  This is done by minimizing a loss function (just like in supervised learning).
  This function is known as *reconstruction loss*. Cross-entropy loss and Mean squared error are common examples.


  ![Autoencoder](https://lilianweng.github.io/lil-log/assets/images/autoencoder-architecture.png)
  *Sample Autoencoder Architecture [Image Source](https://lilianweng.github.io/lil-log/2018/08/12/from-autoencoder-to-beta-vae.html)*

   general Autoencoder architecture consists of two components.
       An *Encoder* that compresses  input and a *Decoder* that tries to reconstruct it.

  use  LSTM Autoencoder from this [GitHub repo](https://github.com/shobrook/sequitur)
  with some small tweaks. Our model's job is to reconstruct Time Series data.
  """
  def __init__(self, seq_len, n_features, embedding_dim=64, device='cpu'):
    super(modelRecurrentAutoencoder, self).__init__()

    self.encoder = modelEncoder(seq_len, n_features, embedding_dim).to(device)
    self.decoder = modelDecoder(seq_len, embedding_dim, n_features).to(device)

  def forward(self, x):
    x = self.encoder(x)
    x = self.decoder(x)

    return x



#############################################################################################################
def model_train(model, train_dataset, val_dataset, n_epochs, device='cpu'):
  """
  using a batch size of 1 (our model sees only 1 sequence at a time).
  minimizing  [L1Loss](https://pytorch.org/docs/stable/nn.html#l1loss),
  which measures  MAE (mean absolute error). Why?  reconstructions seem to be better than with MSE (mean squared error).

  n_epochs = cc.epochs

  """
  optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
  loss_calc = nn.L1Loss(reduction='sum').to(device)
  history   = dict(train=[], val=[])

  best_model_wts = copy.deepcopy(model.state_dict())
  best_loss = 10000.0

  for epoch in range(1, n_epochs + 1):
    break
    model = model.train()

    train_losses = []
    for seq_true in train_dataset:  ###  in  torch.Size([140, 1])
      break
      optimizer.zero_grad()

      seq_true = seq_true.to(device)
      seq_pred = model(seq_true)   ### out torch.Size([140, 1])

      loss = loss_calc(seq_pred, seq_true)   ####  tensor(97.8360, grad_fn=<L1LossBackward>)
      loss.backward()    ### grad is calc
      optimizer.step()   ### update weights
      train_losses.append(loss.item())


    val_losses = []
    model      = model.eval()
    with torch.no_grad():
      for seq_true in val_dataset:
        seq_true = seq_true.to(device)
        seq_pred = model(seq_true)
        loss     = loss_calc(seq_pred, seq_true)
        val_losses.append(loss.item())

    train_loss = np.mean(train_losses)
    val_loss   = np.mean(val_losses)

    history['train'].append(train_loss)
    history['val'].append(val_loss)

    if val_loss < best_loss:
      best_loss = val_loss
      best_model_wts = copy.deepcopy(model.state_dict())

    print(f'Epoch {epoch}: train loss {train_loss} val loss {val_loss}')

  model.load_state_dict(best_model_wts)
  return model.eval(), history



def model_predict(model, dataset, device='cpu'):
  predictions, losses = [], []
  loss_calc = nn.L1Loss(reduction='sum').to(device)
  with torch.no_grad():
    model = model.eval()
    for seq_true in dataset:
      seq_true = seq_true.to(device)
      seq_pred = model(seq_true)

      loss = loss_calc(seq_pred, seq_true)

      predictions.append(seq_pred.cpu().numpy().flatten())
      losses.append(loss.item())
  return predictions, losses



def model_evaluate(model, test_normal_dataset, device='cpu', THRESHOLD=0.2):
  predictions, pred_losses = model_predict(model, test_normal_dataset)
  sns.distplot(pred_losses, bins=50, kde=True)

  # """count  correct predictions:"""
  correct = sum(l <= THRESHOLD for l in pred_losses)
  print(f'Correct normal predictions: {correct}/{len(test_normal_dataset)}')



def model_plotLoss(history:dict):
  ax = plt.figure().gca()
  ax.plot(history['train'])
  ax.plot(history['val'])
  plt.ylabel('Loss')
  plt.xlabel('Epoch')
  plt.legend(['train', 'test'])
  plt.title('Loss over training epochs')
  plt.show()




def model_save(model, path):
  torch.save(model, path)  
  
  

if 'utils':
  def plot_time_series_class(data, class_name, ax, n_steps=10):
    time_series_df = pd.DataFrame(data)

    smooth_path = time_series_df.rolling(n_steps).mean()
    path_deviation = 2 * time_series_df.rolling(n_steps).std()

    under_line = (smooth_path - path_deviation)[0]
    over_line = (smooth_path + path_deviation)[0]

    ax.plot(smooth_path, linewidth=2)
    ax.fill_between(
      path_deviation.index,
      under_line,
      over_line,
      alpha=.125
    )
    ax.set_title(class_name)


  def plot_prediction(data, model, title, ax):
    predictions, pred_losses = model_predict(model, [data])

    ax.plot(data, label='true')
    ax.plot(predictions[0], label='reconstructed')
    ax.set_title(f'{title} (loss: {np.around(pred_losses[0], 2)})')
    ax.legend()
    fig, axs = plt.subplots(
      nrows=2,
      ncols=6,
      sharey=True,
      sharex=True,
      figsize=(22, 8)
    )




#############################################################################################################
########  New Model Explanation #############################################################################
class modelEncoder2(nn.Module):
  """ *Encoder* uses two LSTM layers to compress  Time Series data input.
    Args:
        input_size : The number of expected features in the input `x`
        hidden_size: The number of features in the hidden state `h`
        num_layers : Number of recurrent layers. E.g., setting ``num_layers=2``
            would mean stacking two LSTMs together to form a `stacked LSTM`,
            with the second LSTM taking in outputs of the first LSTM and
            computing the final results. Default: 1

        bias:        If ``False``, then the layer does not use bias weights `b_ih` and `b_hh`. Default: ``True``
        batch_first: If ``True``, then the input and output tensors are provided as (batch, seq, feature). Default: ``False``
        dropout    : If non-zero, introduces a `Dropout` layer on the outputs of each
            LSTM layer except the last layer, with dropout probability equal to :attr:`dropout`. Default: 0
        bidirectional: If ``True``, becomes a bidirectional LSTM. Default: ``False``

    Inpu Dimmension :
        embedding_dim= 64
        hidden_dim =  2 * 64

   encoder is 2 LSTM stacked as below:

   Let's continiue on the input like this :
      Xinput dim :    torch.Size([140, 1])   
      Ypred_dim  :    torch.Size([140, 1])   
   
    self.rnn1 = nn.LSTM(
      input_size=n_features,
      hidden_size=self.hidden_dim,
      num_layers=1,
    )

    self.rnn2 = nn.LSTM(
      input_size=self.hidden_dim,
      hidden_size=embedding_dim,
      num_layers=1,
    )


   what does it mean the n_features ???

    seq_len : lenght of the sequence (time series ??)

    Example : multi-variate time seeries , stacked together ?
       time sereis 1
       time series 2
       time series 3 
    =  n_features = 3  ????
    
    ok,   What about the stakced LSTM parts ??/

      x, (_, _)        = self.rnn1(x)
      x, (hidden_n, _) = self.rnn2(x)

     Sure, why using
         self.rnn1 = nn.LSTM(
            ...
          num_layers=  2 
    
     because the hidden layer is not passed 

     How to find dimension of the hidden layer ?
      ok, we reshape 1 embedding per channel (time series)  ??
         return hidden_n.reshape((self.n_features, self.embedding_dim))

     Other question, the forward pass only return the hidden layer...
     Thhough it will return the x too ???
         
    I would do it with 2 layers in one module    
    that is for 2 layers
    allows more representation power for the model

    
  correct
      seq_len - is obvi ous
      n_features is number of channels in input  (==nb of time series)

  """
  def __init__(self, seq_len, n_features, embedding_dim=64, dropout=0.3):
    super(modelEncoder, self).__init__()

    self.seq_len, self.n_features = seq_len, n_features
    self.embedding_dim, self.hidden_dim = embedding_dim, 2 * embedding_dim

    self.rnn1 = nn.LSTM(
      input_size=n_features,
      hidden_size=self.hidden_dim,
      dropout=dropout,
      num_layers=1,
      batch_first=True,
      bidirectional=False
    )

    self.rnn2 = nn.LSTM(
      input_size=self.hidden_dim,
      hidden_size=embedding_dim,
      dropout=dropout,
      num_layers=1,
      batch_first=True,
      bidirectional=False
    )

  def forward(self, x):
    # x = x.reshape((1, self.seq_len, self.n_features))
    assert x.shape[1] == self.seq_len and x.shape[2] == self.n_features

    x, (_, _)        = self.rnn1(x)
    x, (hidden_n, _) = self.rnn2(x)

    #### Last value of sequence  == hidden layer 
    return hidden_n.reshape((self.n_features, self.embedding_dim))



################################################################
####### another class  
class DynamicLSTM(nn.Module):
    """
    Dynamic LSTM module, which can handle variable length input sequence.

    Parameters
    ----------
    input_size : input size
    hidden_size : hidden size
    num_layers : number of hidden layers. Default: 1
    dropout : dropout rate. Default: 0.5
    bidirectional : If True, becomes a bidirectional RNN. Default: False.

    Inputs
    ------
    input: tensor, shaped [batch, max_step, input_size]
    seq_lens: tensor, shaped [batch], sequence lengths of batch

    Outputs
    -------
    output: tensor, shaped [batch, max_step, num_directions * hidden_size],
         tensor containing the output features (h_t) from the last layer
         of the LSTM, for each t.
    """

    def __init__(self, input_size, hidden_size=100,
                 num_layers=1, dropout=0., bidirectional=False):
        super(DynamicLSTM, self).__init__()

        self.lstm = nn.LSTM(
            input_size, hidden_size, num_layers, bias=True,
            batch_first=True, dropout=dropout, bidirectional=bidirectional)

    def forward(self, x, seq_lens):
        # sort input by descending length
        _, idx_sort = torch.sort(seq_lens, dim=0, descending=True)
        _, idx_unsort = torch.sort(idx_sort, dim=0)
        x_sort = torch.index_select(x, dim=0, index=idx_sort)
        seq_lens_sort = torch.index_select(seq_lens, dim=0, index=idx_sort)

        # pack input
        x_packed = pack_padded_sequence(
            x_sort, seq_lens_sort, batch_first=True)

        # pass through rnn
        y_packed, _ = self.lstm(x_packed)

        # unpack output
        y_sort, length = pad_packed_sequence(y_packed, batch_first=True)

        # unsort output to original order
        y = torch.index_select(y_sort, dim=0, index=idx_unsort)

        return y


class QuoraModel(nn.Module):
    """Model for quora insincere question classification.
    """

    def __init__(self, args):
        super(QuoraModel, self).__init__()

        vocab_size = args["vocab_size"]
        pretrained_embed = args["pretrained_embed"]
        padding_idx = args["padding_idx"]
        embed_dim = 300
        num_classes = 1
        num_layers = 2
        hidden_dim = 50
        dropout = 0.5

        if pretrained_embed is None:
            self.embed = nn.Embedding(vocab_size, embed_dim)
        else:
            self.embed = nn.Embedding.from_pretrained(
                pretrained_embed, freeze=False)
        self.embed.padding_idx = padding_idx

        self.rnn = DynamicLSTM(
            embed_dim, hidden_dim, num_layers=num_layers,
            dropout=dropout, bidirectional=True)

        self.fc = nn.Linear(hidden_dim * 4, hidden_dim)
        self.act = nn.ReLU()
        self.drop = nn.Dropout(dropout)
        self.out = nn.Linear(hidden_dim, num_classes)

        self.loss = nn.BCEWithLogitsLoss()

    def forward(self, word_seq, seq_len):
        # mask
        max_seq_len = torch.max(seq_len)
        mask = seq_mask(seq_len, max_seq_len)  # [b,msl]

        # embed
        e = self.drop(self.embed(word_seq))  # [b,msl]->[b,msl,e]

        # bi-rnn
        r = self.rnn(e, seq_len)  # [b,msl,e]->[b,msl,h*2]

        # pooling
        r_avg = mask_mean(r, mask)  # [b,h*2]
        r_max = mask_max(r, mask)  # [b,h*2]
        r = torch.cat([r_avg, r_max], dim=-1)  # [b,h*4]

        # feed-forward
        f = self.drop(self.act(self.fc(r)))  # [b,h*4]->[b,h]
        logits = self.out(f).squeeze(-1)  # [b,h]->[b]

        return logits


################################################################
#####  Transformer encoder
""""
https://pytorch.org/docs/stable/generated/torch.nn.TransformerEncoder.html#torch.nn.TransformerEncoder


https://discuss.pytorch.org/t/multiheadattention-after-lstm-returns-the-same-output-for-all-input/122035/2

"""


#############################################################################################################
class modelEncoder3(nn.Module):
  """ *Encoder* uses two LSTM layers to compress  Time Series data input.

  Next, decode  compressed representation using a *Decoder*:
  """
  def __init__(self, seq_len, n_features, embedding_dim=64):
    super(modelEncoder, self).__init__()

    self.seq_len, self.n_features = seq_len, n_features
    self.embedding_dim, self.hidden_dim = embedding_dim, 2 * embedding_dim

    """
      its more an EXERCICE to try to plug in the Transformer Encoder
      and match the dimensions.
      (  therey are many transformer things (ie sentence tranfsormer... ), next time
      we can try another one more adapted. )
      
        https://github.com/lucidrains/linear-attention-transformer


        TransformerEncoderLayer(d_model, 
        nhead, dim_feedforward=2048,
         dropout=0.1, 

          layer_norm_eps=1e-05,
          batch_first=False,
           norm_first=False, 
           device=None, dtype=None)



    
    bs = 5  ### 5 odd number for easy debug...
    seq_len =  10   ## seq lenth, nb of tokens. 
    d_in = 32   #####  In features size   //    d_in = 16 -> Linear(16, 32) -> d_model 32 tor march


    #### LSTM       batch,      seq_len,      n_features           
    x = torch.randn(bs, seq_len, d_in)
    d_h = 32   ### 32 of features.... for ONE token   ===  d_model ===  self.hidden_dim
    
    ### dim_feedforward=2048   ### Internal MLP
    Linear(d_model, d_ff) Linear(d_ff, d_model)
    enc = nn.TransformerEncoderLayer(d_h, 4, dim_feedforward=128, 
             batch_first=True   #### Ordering the input (batch size,  ....  )
          )

      Xencode = enc(X)

      ### torch.Size([5, 10, 32])  ####   out = enc(x)  print(out.shape)
      #### same dimension, in float ???  
      # ###  cannot use as "embedding" ...   


      TimSeries= bs, seq_len n_features ->ConveLayer--> (bs new_seq_len d_model)

      (bs new_seq_len d_model)   ---> TFLayer  --->  (bs new_seq_len d_model)    

                                    TLayerEncoder -->   (bs, seq_len_v2 d_model)  
                                    Pooling --> (bs, 0, d_model)    ### Role of middle "compressor""

        (bs, seq_len_v3 d_model), (bs, 0, d_model)--> TFLayerDecode -->  (bs, seq_len_v3 d_model)


      ### this is what they are using:  Pooling in the middle: here this one below:
      https://github.com/UKPLab/sentence-transformers/tree/master/examples/unsupervised_learning/TSDAE

  idea: timse series into "text token"

##Text Version:      bs, seq_len            [int] -> EmbeddingLayer                 -->  bs sl d_model [float]
## Time version :    bs, seq_len, n_feat [float]  -> 1D Conv (to create token-like) -->  bs sl2 d_model [float]


    #### Implementation 
      (Conv, TFEnc-decode, DeConv)   --> get back time series.

      We only have interest in the pooling "embedding"
         timeseries -->   Can we have Embedding Vector  --> we compare vectors...

         Embedding Vector ==  Output of the pooling  (which is here: 1st item , special token):

         Dimension of Output of the Pooling (for example):  bs, 1, d_model

         Pooling = Compression/Flattening of the list of TFEncode vectors  into  1D vector.


         Suppose you have used the output of the pooling for debugging/ check/ actual neighbor search ?
         by Cos. similarity,  "Easy Check if we have access to the pooling output".

         #####

         ConV/ Deconv        : TSeries --> Token...
         Poooling in the middle:   for  

         and Plug into TFLayer (Contentn Encoder, Content Decoder)
         TFLayer parameters NAMES, they are normalizd : d_in, d_h
             d_model (both input and output) num_heads (d_model//num_heads == 0)
             d_ff = 4* d_model
             growth like exponential with seq_len - but there linear attention models 

         ++ cost of training ++ longer.  3X-10X longer than LSTM ???
         In the end, LSTM is a good baselines (cost/perf/debugging ) 
             https://medium.com/ai%C2%B3-theory-practice-business/awd-lstm-6b2744e809c5
             FastAI, default one.
             standard one, 
             Dropout.

         Sure, Are you faimilait with Image model like EfficienttNet ?   
         Big model.... no worries,




               
       AWD-LSTM by Merity
       SHA-RNN by Merity 

from linear_attention_transformer import LinearAttentionTransformerLM, LinformerContextSettings
settings = LinformerContextSettings(  seq_len = 2048,  k = 256)

dec = LinearAttentionTransformerLM(
    num_tokens = 20000,
    dim = 512,
    heads = 8,
    depth = 6,
    
    max_seq_len = 4096,
    causal = True,
    context_linformer_settings = settings,
    receives_context = True
).cuda()


     Cannot use Pre-trained model (== hard to get results fast....).
      Google Mutlti horizon transformer time series.
      TSAI
      https://github.com/timeseriesAI/tsai    nice API

      DeepAR  by Amaazon ,  RNN + Auto-rerefressive ,.... It 
      https://ts.gluon.ai/
      https://ts.gluon.ai/api/gluonts/gluonts.model.deepar.html
       Business focus API
         Yes and NO :  it takes time to train....   
         ( simpler model == les time to train and perf woithin reasonable )

         TiemSeries :  we need more 4-5  years before anything liek NLP onees./.
         Deep Learning is NOT YET enough flexible to include business rules/ many Context things...

         BUT, for Outlier its ok, because of embedding.
           very easy after/standard.
         70% of DL application to get the embedding in some ways.

    ts-gluon  is good, generic, different models.... more simple ones too.
    torch-forecast :        
        https://pytorch-forecasting.readthedocs.io/en/stable/

     into the embedding part  ---> we can combine with Text, .... more easily.  
       we can store somewhere, forever....  
       Some input.

       DeepCTRL by Google ?
          To encore rules + data
          https://ai.googleblog.com/2022/01/controlling-neural-networks-with-rule.html


          ### Some clean re-implementation here too: 
          utilmy/deeplearning/ttorch/rule_encoder4.py  (not perfect...)

          Idea :
            modelA to encode "MANUAL RULES"  (ex:   if weight > 70% --> Always ypred=1, HARD constraints )

            modelB to encode  "data"  (ie auto-encoder, MLP, ...)

            modelMerge(modelA, modelB)  --> Prediction.


          
          Their code is very "hard-coded everywhere"....  




          Encode Data (encoder)




     library - api for time-series    

#### from SentenceEmb Code,
class Pooling(nn.Module):
    Performs pooling (max or mean) on the token embeddings.
    Using pooling, it generates from a variable sized sentence a fixed sized sentence embedding. This layer also allows to use the CLS token if it is returned by the underlying word embedding model.
    You can concatenate multiple poolings together.
    word_embedding_dimension: Dimensions for the word embeddings
    pooling_mode: Can be a string: mean/max/cls. If set, overwrites the other pooling_mode_* settings

    pooling_mode_cls_token: Use the first token (CLS token) as text representations

    pooling_mode_max_tokens: Use max in each dimension over all tokens.
    
    pooling_mode_mean_tokens: Perform mean-pooling
    pooling_mode_mean_sqrt_len_tokens: Perform mean-pooling, but devide by sqrt(input_length).



# Defining our sentence transformer model
word_embedding_model = models.Transformer(model_name, max_seq_length=max_seq_length)
pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension(), 'cls')
model = SentenceTransformer(modules=[word_embedding_model, pooling_model



    ### 
        self_attn.in_proj_weight     torch.Size([96, 32])
        self_attn.in_proj_bias       torch.Size([96])
        self_attn.out_proj.weight    torch.Size([32, 32])
        self_attn.out_proj.bias      torch.Size([32])

        ##### Position wise feedforward. <> MLP
        ### mini-compression  32 --> 128 --> 32   (mutiplication is done....)bs, sq 32 -> bs sq 128 -> bs sl 32
                                                 Input / outpit
        linear1.weight               torch.Size([128, 32])  +  linear1.bias                torch.Size([128])
        linear2.weight               torch.Size([32, 128])

        linear2.bias                 torch.Size([32])
        norm1.weight                 torch.Size([32])
        norm1.bias                   torch.Size([32])
        norm2.weight                 torch.Size([32])
        norm2.bias                   torch.Size([32])

    """



    self.rnn1 = nn.LSTM(
      input_size=n_features,
      hidden_size=self.hidden_dim,
      num_layers=1,
      batch_first=True
    )

    self.rnn2 = nn.LSTM(
      input_size=self.hidden_dim,
      hidden_size=embedding_dim,
      num_layers=1,
      batch_first=True
    )

  def forward(self, x):
    x = x.reshape((1, self.seq_len, self.n_features))

    x, (_, _)        = self.rnn1(x)
    x, (hidden_n, _) = self.rnn2(x)

    return hidden_n.reshape((self.n_features, self.embedding_dim))



class modelDecoder3(nn.Module):
  """Our Decoder contains two LSTM layers and an output layer that gives  final reconstruction.
  #
  # Time to wrap everything into an easy to use module:
  """
  def __init__(self, seq_len, input_dim=64, n_features=1):
    super(modelDecoder, self).__init__()

    self.seq_len, self.input_dim = seq_len, input_dim
    self.hidden_dim, self.n_features = 2 * input_dim, n_features

    self.rnn1 = nn.LSTM(
      input_size=input_dim,
      hidden_size=input_dim,
      num_layers=1,
      batch_first=True
    )

    self.rnn2 = nn.LSTM(
      input_size=input_dim,
      hidden_size=self.hidden_dim,
      num_layers=1,
      batch_first=True
    )

    self.output_layer = nn.Linear(self.hidden_dim, n_features)

  def forward(self, x):
    x = x.repeat(self.seq_len, self.n_features)
    x = x.reshape((self.n_features, self.seq_len, self.input_dim))

    x, (hidden_n, cell_n) = self.rnn1(x)
    x, (hidden_n, cell_n) = self.rnn2(x)
    x = x.reshape((self.seq_len, self.hidden_dim))

    return self.output_layer(x)



class modelRecurrentAutoencoder3(nn.Module):
  """### LSTM Autoencoder
   [Autoencoder's](https://en.wikipedia.org/wiki/Autoencoder) job is to get some input data, pass it through  model, and obtain a reconstruction of  input.  reconstruction should match  input as much as possible.  trick is to use a small number of parameters, so your model learns a compressed representation of  data.
  In a sense, Autoencoders try to learn only  most important features (compressed version) of  data. Here, have a look at how to feed Time Series data to an Autoencoder. use a couple of LSTM layers (hence  LSTM Autoencoder) to capture  temporal dependencies of  data.
  To classify a sequence as normal or an anomaly, pick a cc.THRESHOLD above which a heartbeat is considered abnormal.


  ### Reconstruction Loss
  When training an Autoencoder,  objective is to reconstruct  input as best as possible.
  This is done by minimizing a loss function (just like in supervised learning).
  This function is known as *reconstruction loss*. Cross-entropy loss and Mean squared error are common examples.


  ![Autoencoder](https://lilianweng.github.io/lil-log/assets/images/autoencoder-architecture.png)
  *Sample Autoencoder Architecture [Image Source](https://lilianweng.github.io/lil-log/2018/08/12/from-autoencoder-to-beta-vae.html)*

   general Autoencoder architecture consists of two components.
       An *Encoder* that compresses  input and a *Decoder* that tries to reconstruct it.

  use  LSTM Autoencoder from this [GitHub repo](https://github.com/shobrook/sequitur)
  with some small tweaks. Our model's job is to reconstruct Time Series data.
  """
  def __init__(self, seq_len, n_features, embedding_dim=64, device='cpu'):
    super(modelRecurrentAutoencoder, self).__init__()

    self.encoder = modelEncoder(seq_len, n_features, embedding_dim).to(device)
    self.decoder = modelDecoder(seq_len, embedding_dim, n_features).to(device)

  def forward(self, x):
    x = self.encoder(x)
    x = self.decoder(x)

    return x




def test_trans():
    """ are you here ?
     

    """
    import torch
    from torch import nn
    import torch.nn.functional as F

    from fastai.callback.hook import Hooks

    bs, seq_len, d_in = 5, 10, 32
    x = torch.randn(bs, seq_len, d_in)
    d_h = 32

    attn = nn.MultiheadAttention(d_h, 4, bias=False, batch_first=True)

    for n, p in attn.named_parameters():
        print(f"{n:<12} {p.shape}")

    out, attn_weights = attn(x, x, x, average_attn_weights=False)

    out.shape, attn_weights.shape

    enc = nn.TransformerEncoderLayer(d_h, 4, 128, batch_first=True)

    for n, p in enc.named_parameters():
        print(f"{n:<28} {p.shape}")

    out = enc(x)
    print(out.shape)

    dec = nn.TransformerDecoderLayer(d_h, 4, batch_first=True)
    for n, p in dec.named_parameters():
        print(f"{n:<32} {p.shape}")

    dec

    y = torch.randn(bs, seq_len-1, d_h)
    out = dec(x, y)
    print(out.shape)

    enc = nn.TransformerEncoder(
        nn.TransformerEncoderLayer(d_h, 4, batch_first=True),
        2
    )

    out = enc(x)
    print(out.shape)

    enc





   
 
    
###############################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire(test_all)


    
