# -*- coding: utf-8 -*-
"""#
Doc::

    sentence_tansformer wrapper

    python  utilmy/nlp/ttorch/sentences.py  test1


    Original file is located at
    https://colab.research.google.com/drive/1dPPD-2Vrn61v2uYZT1AXiujqqw7ZwzEA#scrollTo=TZCBsq36j4aH


    train Sentence Transformer with different Losses such as:**
    > Softmax Loss
    > Cusine Loss
    > TripletHard Loss
    > MultpleNegativesRanking Loss

    # !pip install sentence-transformers

    We create a new end-to-end example on how to use a custom inference.py script w
    ith a Sentence Transformer and a mean pooling layer to create sentence embeddings.🤯

    🖼  blog: https://lnkd.in/dXNu4R-G
    📈  notebook: https://lnkd.in/dkjDMNaC


"""
MNAME='utilmy.nlp.ttorch.sentences'
import sys, os, gzip, csv, random, math, logging, pandas as pd, numpy as np, glob
from typing import List, Optional, Tuple, Union
from datetime import datetime
from box import Box

import torch
from torch import nn
from torch.utils.data import DataLoader
from torch.nn.parallel import DistributedDataParallel as DDP

#vfrom tensorflow.keras.metrics import SparseCategoricalAccuracy
from sklearn.metrics.pairwise import cosine_similarity,cosine_distances

from utilmy.utilmy import glob_glob
try :
    import sentence_transformers as st
    from sentence_transformers import SentenceTransformer, SentencesDataset, losses, util
    from sentence_transformers import models, losses, datasets
    from sentence_transformers.readers import InputExample
    from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator
except Exception as e:
    print(e)


#### read data on disk
from utilmy import pd_read_file, pd_to_file


#############################################################################################
from utilmy import Dict_none, Int_none,List_none, Path_type
Dataframe_str = Union[str, pd.DataFrame, None]

from utilmy import log, log2, help_create
def help():
    print( help_create(MNAME) )


#############################################################################################
def test_all() -> None:
    """function test_all"""
    log(MNAME)
    test1() 


def test1():
    """#
    Doc::

        Run Various test suing sent trans_former,
            <> losses, <> tasks    # Mostly Single sentence   ---> Classification

        python utilmy/nlp/ttorch/sentences.py test1


        model.encode(self, sentences: Union[str, List[str]],
                batch_size: int = 32,
                show_progress_bar: bool = None,
                output_value: str = 'sentence_embedding',
                convert_to_numpy: bool = True,
                convert_to_tensor: bool = False,
                device: str = None,
                normalize_embeddings: bool = False) -> Union[List[Tensor], ndarray, Tensor]:
    """
    os.environ['CUDA_VISIBLE_DEVICES']='2,3'
  
    cc        = Box({})
    cc.epoch  = 3
    cc.lr     = 1E-5
    cc.warmup = 10

    cc.eval_steps = 50
    cc.batch_size = 8

    cc.mode    = 'cpu/gpu'
    cc.use_gpu = 0
    cc.ncpu    = 5
    cc.ngpu    = 2

    #### Data
    cc.data_nclass = 5
    cc.datasetname = 'sts5'


    dirtmp = 'ztmp/'
    modelid = "distilbert-base-nli-mean-tokens"
    
    cols = ['sentence1', 'sentence2', 'label', 'score' ]  ### score can be NA
    dfcheck = dataset_fake(name='AllNLI.tsv.gz', dirdata=dirtmp, fname='data_fake.parquet', nsample=10)  ### Create fake version
    assert len(dfcheck[ cols ]) > 1 , "missing columns"
    ## Score can be empty or [0,1]
    
    lloss = [ 'cosine', 'triplethard',"softmax", 'MultpleNegativesRankingLoss' ]
    
    for lname in lloss :
        log("\n\n\n ########### Classifier with Loss ", lname)
        cc.lossname = lname
        model = model_finetune(modelname_or_path = modelid,
                               taskname   = "classifier",
                               lossname   = lname,
                               metricname = 'cosinus',

                               cols        = cols,
                               datasetname = cc.datasetname,
                               train_path  = dirtmp + f"/data_fake.parquet",
                               val_path    = dirtmp + f"/data_fake.parquet",
                               eval_path   = dirtmp + f"/data_fake.parquet",

                               dirout= dirtmp + f"/model/" + lname, nsample=100, cc=cc)
    

    log('\n\n########### model encode')
    df = model_encode( model= model,  dirdata=dirtmp +"/data_fake.parquet",
                           colid=None, coltext='sentence1', batch_size=32, 
                           dirout=None,
              normalize_embeddings=True  #### sub encode params
              )  
    if df is not None : log(df.head(3))
    
    
def test2():
    model = model_load("distilbert-base-nli-mean-tokens")
    df = pd.DataFrame({'colA':['good','hello','bad'], 'colB':['nice','welcome','exacerbate']})
    
    df = sentence_compare(df, 'colA', 'colB', model)
    
    log(df.head())


###################################################################################################################        
def dataset_fake(name='AllNLI.tsv.gz', dirdata:str='', fname:str='data_fake.parquet', nsample=10):        
    """ Fake text data for tests
    """
    # sts_dataset_path = dirdata + '/stsbenchmark.tsv.gz'
    name='AllNLI.tsv.gz'
    dataset_download(name=name, dirout= dirdata)
    dataset_path = dirdata + '/' + name

    # Read the AllNLI.tsv.gz file and create the training dataset
    df = pd_read_file3(dataset_path, npool=1) 

    df = df[df['split'] == 'train' ]
    
    # df = df.sample(frac=0.1)
    df['score'] = np.random.random( len(df) )   #### only for Evaluation.

    df['label'] = pd.factorize(df['label'])[0]   ###into integer
    #df['label'] = 6.0  # np.random.randint(0, 3, len(df) )
    df['label'] = df['label'].astype('float')  ### needed for cosinus loss 

    log(df, df.columns, df.shape)
    dirout = dirdata +"/" + fname
    df = df.iloc[:nsample, :]
    df.to_parquet(dirout)
    return df.iloc[:10, :]


def dataset_fake2(dirdata=''):
    # This function load the fake dataset if it's already existed otherwise downloads it first.
    # then Preprocess the data for MultpleNegativesRanking loss function and return it as dataloader
    nli_dataset_path = dirdata + '/AllNLI.tsv.gz'

    def add_to_samples(sent1, sent2, label):
        if sent1 not in train_data:
            train_data[sent1] = {'contradiction': set(), 'entailment': set(), 'neutral': set()}
            train_data[sent1][label].add(sent2)

    train_data = {}
    df = []
    with gzip.open(nli_dataset_path, 'rt', encoding='utf8') as fIn:
        reader = csv.DictReader(fIn, delimiter='\t', quoting=csv.QUOTE_NONE)
        for row in reader:
            if row['split'] == 'train':
                sent1 = row['sentence1'].strip()
                sent2 = row['sentence2'].strip()

                df.append([sent1, sent2, row['label']])
                df.append([sent2, sent1, row['label']])  #Also add the opposite


    train_samples = []
    for sent1, others in train_data.items():
        if len(others['entailment']) > 0 and len(others['contradiction']) > 0:
            train_samples.append(InputExample(texts=[sent1, random.choice(list(others['entailment'])), random.choice(list(others['contradiction']))]))
            train_samples.append(InputExample(texts=[random.choice(list(others['entailment'])), sent1, random.choice(list(others['contradiction']))]))

    
def dataset_download(name='AllNLI.tsv.gz', dirout='/content/sample_data/sent_tans/'):
    #### Check if dataset exsist. If not, download and extract  it    
    url = '' ; dirouti = dirout
    if name == 'AllNLI.tsv.gz':
        url     = 'https://sbert.net/datasets/AllNLI.tsv.gz'
        dirouti = dirout + "/AllNLI.tsv.gz'"

    if name == 'stsbenchmark.tsv.gz':
        url     = 'https://sbert.net/datasets/stsbenchmark.tsv.gz'
        dirouti = dirout + "/stsbenchmark.tsv.gz"

    if os.path.isfile(dirouti):    
        log('Existing', dirouti)
        return None

    os.makedirs(dirout, exist_ok=True)  
    util.http_get(url, dirouti)



###################################################################################################################        
def model_finetune(modelname_or_path='distilbert-base-nli-mean-tokens',
                   taskname="classifier", lossname="cosinus",
                   datasetname = 'sts',
                   cols= ['sentence1', 'sentence2', 'label', 'score' ],

                   train_path="train/*.csv", val_path  ="val/*.csv", eval_path ="eval/*.csv",

                   metricname='cosinus',
                   dirout ="mymodel_save/", nsample=100000,
                   cc:dict= None):
    """"#
    Doc::

         Load pre-trained model and fine tune with specific dataset

         cols= ['sentence1', 'sentence2', 'label', 'score' ],
         task='classifier',  df[['sentence1', 'sentence2', 'label']]

          # cc.epoch = 3
          # cc.lr = 1E-5
          # cc.warmup = 100
          # cc.n_sample  = 1000
          # cc.batch_size=16
          # cc.mode = 'cpu/gpu'
          # cc.ncpu =5
          # cc.ngpu= 2
    """
    cc = Box(cc)   #### can use cc.epoch   cc.lr
    cc.modelname   = modelname_or_path
    cc.nsample     =  nsample
    cc.datasetname = datasetname

    ##### load model form disk or from internet
    model = model_load(modelname_or_path)
    log('model loaded:', model)
    
    if taskname == 'classifier':
        df = pd_read_file(train_path)
        log(df.columns, df.shape)
        assert len(df[cols]) > 1 , "missing columns"          ### Check colum used

        log(" metrics_cosine_similarity before training")  
        model_check_cos_sim(model, df['sentence1'][0], df['sentence2'][0])
        
        
        ##### dataloader train, evaluator
        if 'data_nclass' not in cc :
            cc.data_nclass = df['label'].nunique()
        df = df.iloc[:nsample,:]
        
        train_dataloader = load_dataloader(train_path, datasetname, cc=cc, istrain=True)
        val_evaluator    = load_evaluator( eval_path,  datasetname, cc=cc)
    
        ##### Task Loss
        train_loss       = load_loss(model, lossname,  cc= cc)        
        
        ##### Configure the training
        cc.use_amp = cc.get('use_amp', False)
        cc.warmup_steps = math.ceil(len(train_dataloader) * cc.epoch * 0.1) #10% of train data for warm-up.
        log("Warmup-steps: {}".format(cc.warmup_steps))
          
        model = model_setup_compute(model, use_gpu=cc.get('use_gpu', 0)  , ngpu= cc.get('ngpu', 0) , ncpu= cc.get('ncpu', 1) )
        
        
        log('########## train')
        model.fit(train_objectives=[(train_dataloader, train_loss)],
          evaluator        = val_evaluator,
          epochs           = cc.epoch,
          evaluation_steps = cc.eval_steps,
          warmup_steps     = cc.warmup_steps,
          output_path      = dirout,
          use_amp          = cc.use_amp          #Set to True, if your GPU supports FP16 operations
          )

        log("\n******************< Eval similarity > ********************")
        log(" cosine_similarity after training")
        model_check_cos_sim(model, df['sentence1'][0], df['sentence2'][0],)
        
        log("### Save model  ")
        model_save(model, dirout, reload=False)
        model = model_load(dirout)

        log('### Show eval metrics')
        model_evaluate(model, dirdata=eval_path, dirout= dirout +"/eval/")
        
        log("\n******************< finish  > ***************************")
        return model


def model_check_cos_sim(model, sentence1 = "sentence 1" , sentence2 = "sentence 2", ):
  """     ### function to compute cosinue similarity      
  """  
  log('model', model)
  #Compute embedding for both lists
  embed1 = model.encode(sentence1, convert_to_tensor=True, convert_to_numpy=False, normalize_embeddings=True)
  
  # , convert_to_tensor=True)
  embed2 = model.encode(sentence2, convert_to_tensor=True, convert_to_numpy=False, normalize_embeddings=True)

  #Compute cosine-similarity
  cosine_scores = util.cos_sim(embed1, embed2)
  log( f"{sentence1} \t {sentence2} \n cosine-similarity Score: {cosine_scores[0][0]}" )


def model_encode(model = "model name or path or object", dirdata:Dataframe_str="data/*.parquet", 
                coltext:str='sentence1', colid=None,
                dirout:str="embs/myfile.parquet", show=1,  **kw )->Dataframe_str :
    """#
    Doc::

        Sentence encoder  
        sentences        : the sentences to embed
        batch_size       : the batch size used for the computation
        show_progress_bar: Output a progress bar when encode sentences
        output_value     : Default sentence_embedding, to get sentence embeddings. Can be set to token_embeddings to get wordpiece token embeddings. Set to None, to get all output values
        convert_to_numpy : If true,                    the output is a list of numpy vectors. Else,                                                               it is a list of pytorch tensors.
        convert_to_tensor: If true,                    you get one large tensor as return. Overwrites any setting from convert_to_numpy
        device           : Which torch.device to use for the computation

    """  
    model = model_load(model)
    log('model', model)

    if isinstance( dirdata, pd.DataFrame) :
        dfi      = dirdata[coltext].values
        embs_all = model.encode(dfi, convert_to_numpy=True, **kw)
        embs_all = {'id': np.arange(0, len(embs_all)) ,  'emb': embs_all }

    else:
      if isinstance( dirdata, list) :
        flist = dirdata 
      else :
        flist = glob_glob(dirdata)

      log('Nfiles', len(flist))
      embs_all={ 'id':[], 'emb':[]}
      for ii, fi in enumerate(flist) :
        try :
            dfi  = pd_read_file3(fi)
            ### Unique ID
            idvals = int(ii*10**9) + np.arange(0, len(dfi))   if colid not in dfi.columns else  dfi[colid].values 
                
            dfi  = dfi[coltext].values
            embs = model.encode(dfi, convert_to_numpy=True, **kw)   ### List of numpy vectors
            embs_all['emb'].extend(embs)
            embs_all['id'].extend( idvals )
        except Exception as e :
            log(ii, fi, e)     

    embs_all = pd.DataFrame(embs_all )    
    log(embs_all.shape)
    if show>0 : log(embs_all)
    if dirout is None :
        return embs_all
    else :
        pd_to_file(embs_all, dirout, show=1)   


def model_encode_batch(model = "model name or path or object", dirdata:str="data/*.parquet", 
                coltext:str='sentence1', colid=None,
                dirout:str="embs/myfile.parquet", nsplit=5, imin=0, imax=500,   **kw ):
    """   Sentence encoder in parallel batch mode
      file_{ii}.parquet  with ii= imin, imax.

    """  
    flist = glob_glob(dirdata)
    ### Filter files based on rule
    flist2 = flist

    model_encode(model = model, dirdata=flist2, 
                coltext=coltext, colid=colid,
                dirout=dirout, )


def model_evaluate(model ="modelname OR path OR model object", dirdata='./*.csv', dirout='./',
                   cc:dict= None, batch_size=16, name='sts-test'):

    os.makedirs(dirout, exist_ok=True)
    ### Evaluate Model
    df = pd_read_file(dirdata)
    log(df)

    score_max = df['score'].max()
    #df = pd.read_csv(dirdata, error_bad_lines=False)
    test_samples = []
    for i, row in df.iterrows():
        # if row['split'] == 'test':
        score = float(row['score']) / score_max #Normalize score to range 0 ... 1
        test_samples.append(InputExample(texts=[row['sentence1'], row['sentence2']], label=score))

    model= model_load(model)
    test_evaluator = EmbeddingSimilarityEvaluator.from_input_examples(test_samples, batch_size=batch_size, name=name)
    test_evaluator(model, output_path=dirout)    
    log( pd_read_file(dirout +"/*" ))


def model_setup_compute(model, use_gpu=0, ngpu=1, ncpu=1, cc:Dict_none=None)->SentenceTransformer: 
    """#
    Doc::
    
        model_setup_compute _summary_
        # Tell pytorch to run this model on the multiple GPUs if available otherwise use all CPUs.
        Args:
            model: _description_
            use_gpu: _description_. Defaults to 0.
            ngpu: _description_. Defaults to 1.
            ncpu: _description_. Defaults to 1.
            cc: _description_. Defaults to None.
    """
    cc = Box(cc) if cc is not None else Box({})
    if cc.get('use_gpu', 0) > 0 :        ### default is CPU
        if torch.cuda.device_count() < 0 :
            log('no gpu')
            device = 'cpu'
            torch.set_num_threads(ncpu)
            log('cpu used:', ncpu, " / " ,torch.get_num_threads())
            # model = nn.DataParallel(model)            
        else :    
            log("Let's use", torch.cuda.device_count(), "GPU")
            device = torch.device("cuda:0")
            model = DDP(model)        
    else :
            device = 'cpu'
            torch.set_num_threads(ncpu)
            log('cpu used:', ncpu, " / " ,torch.get_num_threads())
            # model = nn.DataParallel(model)  ### Bug TOFix
        
    log('device', device)
    model.to(device)
    return model


def model_load(path_or_name_or_object):
    #### Reload model or return the model itself
    if isinstance(path_or_name_or_object, str) :
       # model = SentenceTransformer('distilbert-base-nli-mean-tokens')
       model = SentenceTransformer(path_or_name_or_object)
       model.eval()    
       return model
    else :
       return path_or_name_or_object


def model_save(model,path:str, reload=True):
    model.save( path)
    log(path)
    
    if reload:
        #### reload model  + model something   
        model1 = model_load(path)
        log(model1)




###################################################################################################################  
######## Custom Task ##############################################################################################
def model_finetune_classifier(modelname_or_path='distilbert-base-nli-mean-tokens',
                            taskname="classifier", lossname="cosinus",
                            datasetname = 'sts',
                            cols= ['sentence1', 'sentence2', 'label', 'score' ],

                            train_path="train/*.csv", val_path  ="val/*.csv", eval_path ="eval/*.csv",

                            metricname='cosinus',
                            dirout ="mymodel_save/", nsample=100000,
                            cc:dict= None):
    """" Load pre-trained model and fine tune with specific dataset
         cols= ['sentence1', 'sentence2', 'label', 'score' ],
         task='classifier',  df[['sentence1', 'sentence2', 'label']]

          # cc.epoch = 3
          # cc.lr = 1E-5
          # cc.warmup = 100
          # cc.n_sample  = 1000
          # cc.batch_size=16
          # cc.mode = 'cpu/gpu'
          # cc.ncpu =5
          # cc.ngpu= 2
    """
    cc = Box(cc)   #### can use cc.epoch   cc.lr
    cc.modelname   = modelname_or_path
    cc.nsample     = nsample
    cc.datasetname = datasetname

    ##### load model form disk or from internet
    model = model_load(modelname_or_path)
    log('model loaded:', model)
    
    df = pd_read_file(train_path)
    log(df.columns, df.shape)
    assert len(df[cols]) > 1 , "missing columns"          ### Check colum used

    log(" metrics_cosine_similarity before training")  
    model_check_cos_sim(model, df['sentence1'][0], df['sentence2'][0])
            
    ##### dataloader train, evaluator
    if 'data_nclass' not in cc :
        cc.data_nclass = df['label'].nunique()
    df = df.iloc[:nsample,:]
    
    train_dataloader = load_dataloader(train_path, datasetname, cc=cc, istrain=True)
    val_evaluator    = load_evaluator( eval_path,  datasetname, cc=cc)

    ##### Task Loss
    train_loss       = load_loss(model, lossname,  cc= cc)        
    
    ##### Configure the training
    cc.use_amp = cc.get('use_amp', False)
    cc.warmup_steps = math.ceil(len(train_dataloader) * cc.epoch * 0.1) #10% of train data for warm-up.
    log("Warmup-steps: {}".format(cc.warmup_steps))
        
    model = model_setup_compute(model, use_gpu=cc.get('use_gpu', 0)  , ngpu= cc.get('ngpu', 0) , ncpu= cc.get('ncpu', 1) )
    
    
    log('########## train')
    model.fit(train_objectives=[(train_dataloader, train_loss)],
        evaluator        = val_evaluator,
        epochs           = cc.epoch,
        evaluation_steps = cc.eval_steps,
        warmup_steps     = cc.warmup_steps,
        output_path      = dirout,
        use_amp          = cc.use_amp          #Set to True, if your GPU supports FP16 operations
        )

    log("\n******************< Eval similarity > ********************")
    log(" cosine_similarity after training")
    model_check_cos_sim(model, df['sentence1'][0], df['sentence2'][0],)
    
    log("### Save model  ")
    model_save(model, dirout, reload=False)
    model = model_load(dirout)

    log('### Show eval metrics')
    model_evaluate(model, dirdata=eval_path, dirout= dirout +"/eval/")
    
    log("\n******************< finish  > ********************")
    return model



def model_finetune_qanswer(modelname_or_path='distilbert-base-nli-mean-tokens',
                            taskname="classifier", lossname="cosinus",
                            datasetname = 'sts',
                            cols= ['sentence1', 'sentence2', 'label', 'score' ],

                            train_path="train/*.csv", val_path  ="val/*.csv", eval_path ="eval/*.csv",

                            metricname='cosinus',
                            dirout ="mymodel_save/", nsample=100000,
                            cc:dict= None):
    """" Load pre-trained model and fine tune with specific dataset
         cols= ['sentence1', 'sentence2', 'label', 'score' ],
         task='',  df[['sentence1', 'sentence2', 'label']]

    """
    cc = Box(cc)   #### can use cc.epoch   cc.lr
    cc.modelname   = modelname_or_path
    cc.nsample     = nsample
    cc.datasetname = datasetname

    ##### load model form disk or from internet
    model = model_load(modelname_or_path)
    log('model loaded:', model)
    
    df = pd_read_file(train_path)
    log(df.columns, df.shape)
    assert len(df[cols]) > 1 , "missing columns"          ### Check colum used

    log(" metrics_cosine_similarity before training")  
    model_check_cos_sim(model, df['sentence1'][0], df['sentence2'][0])
            
    ##### dataloader train, evaluator
    if 'data_nclass' not in cc :
        cc.data_nclass = df['label'].nunique()
    df = df.iloc[:nsample,:]
    
    train_dataloader = load_dataloader(train_path, datasetname, cc=cc, istrain=True)
    val_evaluator    = load_evaluator( eval_path,  datasetname, cc=cc)

    ##### Task Loss fro QAnaser
    #train_loss       = load_loss(model, lossname,  cc= cc)        
    
    ##### Configure the training
    cc.use_amp = cc.get('use_amp', False)
    cc.warmup_steps = math.ceil(len(train_dataloader) * cc.epoch * 0.1) #10% of train data for warm-up.
    log("Warmup-steps: {}".format(cc.warmup_steps))
        
    model = model_setup_compute(model, use_gpu=cc.get('use_gpu', 0)  , ngpu= cc.get('ngpu', 0) , ncpu= cc.get('ncpu', 1) )
    
    
    log('########## train')

    log("\n******************< Eval similarity > ********************")
    log(" cosine_similarity after training")
    model_check_cos_sim(model, df['sentence1'][0], df['sentence2'][0],)
    
    log("### Save model  ")
    model_save(model, dirout, reload=False)
    model = model_load(dirout)

    log('### Show eval metrics')
    model_evaluate(model, dirdata=eval_path, dirout= dirout +"/eval/")
    
    log("\n******************< finish  > ********************")
    return model




###################################################################################################################  
def load_evaluator( path_or_df:Dataframe_str="", dname='sts',  cc:dict=None):
    """  Evaluator using df[['sentence1', 'sentence2', 'score']]
    """
    cc = Box(cc)

    if dname == 'sts':
       log("Read STSbenchmark dev dataset")
       df = pd_read_file3(path_or_df)
    else :
       df = pd_read_file(path_or_df)

    if 'nsample' in cc : df = df.iloc[:cc.nsample,:]
    log('eval dataset', df)

    score_max = df['score'].max()

    dev_samples = []
    for i,row in df.iterrows():
        # if row['split'] == 'dev':
        score = float(row['score']) / score_max #Normalize score to range 0 ... 1
        dev_samples.append(InputExample(texts=[row['sentence1'], row['sentence2']], label=score))

    dev_evaluator = EmbeddingSimilarityEvaluator.from_input_examples(dev_samples, batch_size= cc.batch_size, name=dname)
    return dev_evaluator


def load_dataloader(path_or_df:str = "",  name:str='sts',  cc:dict= None, istrain=True, npool=4):
    """  dataframe --> dataloader
      dfcheck[[ 'sentence1', 'sentence2', 'label', 'score'  ]]

    """
    cc = Box(cc)
    df = pd_read_file3(path_or_df, npool=npool) 
    
    if 'nsample' in cc : df = df.iloc[:cc.nsample,:]
    log('train dataset', df)
    
    if istrain :
        samples = [] 
        for i,row in df.iterrows():
            labeli =  float(row['label'] )   if 'cosine' in cc.get('lossname', '') else  int(row['label']) 
            samples.append( InputExample(texts=[row['sentence1'], row['sentence2']], 
                                         label=   labeli  ))
        dataloader = DataLoader(samples, shuffle=True, batch_size=cc.batch_size)

    else :
        samples = [] 
        for i,row in df.iterrows():
            samples.append( InputExample(texts=[row['sentence1'], row['sentence2']],  ))
        dataloader = DataLoader(samples, shuffle=True, batch_size=cc.batch_size)

    log('Nelements', len(dataloader))
    return dataloader


def load_loss(model, lossname ='cosine',  cc:dict= None):
    train_loss = None
    if lossname == 'MultpleNegativesRankingLoss':

      train_loss = losses.MultipleNegativesRankingLoss(model)

    elif lossname == 'softmax':
      nclass     =  cc.get('data_nclass', 1)
      train_loss = losses.SoftmaxLoss(model=model, sentence_embedding_dimension=model.get_sentence_embedding_dimension(),
                                      num_labels=nclass )

    elif lossname =='triplethard':
      train_loss = losses.BatchHardTripletLoss(model=model)

    else : #if lossname =='cosine':
      train_loss = losses.CosineSimilarityLoss(model)

    return train_loss


###################################################################################################################  

def sentence_compare(df, cola, colb, model):
    """Compare 2 columns and return cosine similarity score

    Args:
        df (pd DataFrame): Pandas DataFrame containing the data
        cola (str): column A name
        colb (str): column B name
        model (model instance): Pretrained sentence transformer model

    Returns:
        pd DataFrame: 'cosine_similarity' column and return df
    """
    
    from sklearn.metrics.pairwise import cosine_similarity
    
    keywords1_embeds = model.encode(df[cola].tolist())
    keywords2_embeds = model.encode(df[colb].tolist())       
    
    results = list()
    for embed1,embed2 in zip(keywords1_embeds,keywords2_embeds):
        result = cosine_similarity([embed1],[embed2])
        results.append(result)
    df['cosine_similarity'] = np.array(results).ravel()
    
    return df


###################################################################################################################  
if 'utils':
    def pd_read_file3(path_or_df='./myfile.csv', npool=1, nrows=1000,  **kw)->pd.DataFrame:
        if isinstance(path_or_df, str):            
            if  'AllNLI' in path_or_df:
                dftrain = pd.read_csv(path_or_df, error_bad_lines=False, nrows=nrows, sep="\t")
            else :
                dftrain = pd_read_file(path_or_df, npool=npool, nrows=nrows)
            
        elif isinstance(path_or_df, pd.DataFrame):
            dftrain = path_or_df
        else : 
            raise Exception('need path_or_df')
        return dftrain    
        
      





##########################################################################################
if __name__ == '__main__':
    import fire
    # fire.Fire()
    test1()
    test2()


