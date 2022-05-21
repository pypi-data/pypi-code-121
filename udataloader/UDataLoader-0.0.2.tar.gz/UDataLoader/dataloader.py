import torch
import jieba
import os
import torch.utils.data as Data
import torch
from collections import Counter
pdir=os.path.dirname(os.path.abspath(__file__))
class UDataloader():
    def __init__(self, datapath,batch_size=16,tasktype='cls',public_vocab=False,custom_index=None,fix_length=-1,dynamic_input={},dynamic_label={}):
        self.datapath=datapath
        self.tasktype=tasktype
        self.input_field=None
        self.label_field=None
        self.train_dataset=None
        self.valid_dataset=None
        self.test_dataset=None
        self.train_DataLoader=None
        self.valid_DataLoader=None
        self.test_DataLoader=None
        self.raw_data_list=None
        self.data_list=None
        self.custom_index=custom_index
        self.public_vocab=public_vocab
        self.batch_size=batch_size
        self.dynamic_input=dynamic_input
        self.dynamic_label=dynamic_label
        self.fix_length=fix_length
        self.init()
    def init(self):
        self.raw_data_list=self.get_data()
        self.data_list=self.build_corpus(self.raw_data_list)
        self.train_dataset,self.valid_dataset,self.test_dataset=self.MakeCorpus()
        self.get_dataFeild()
        self.input_field.build_vocab(self.train_dataset,self.valid_dataset)
        self.label_field.build_vocab(self.train_dataset,self.valid_dataset)
        self.train_DataLoader=Data.DataLoader(dataset=self.train_dataset,collate_fn=self.collate_batch,batch_size=self.batch_size,shuffle=True)
        self.valid_DataLoader=Data.DataLoader(dataset=self.valid_dataset,collate_fn=self.collate_batch,batch_size=self.batch_size, shuffle=True)
        self.test_DataLoader=Data.DataLoader(dataset=self.valid_dataset,collate_fn=self.collate_batch,batch_size=self.batch_size, shuffle=False)
    def tokenizer(self,x):
        """
        "The quick fox jumped over a lazy dog."   -> (tokenization)
        ["The", "quick", "fox", "jumped", "over", "a", "lazy", "dog", "."]
        """
        def is_all_chinese(strs):
            for _char in strs:
                if not '\u4e00' <= _char <= '\u9fa5':
                    return False
            return True
        x=jieba.lcut(x)
        xx=[]
        for w in x:
            if is_all_chinese(w):
                xx+=[wi for wi in w if w]
            else:
                xx+=[w]
        return xx
    def cleanHighfreqencyWordsAndLow(self,corpus):
        print('cleanHighfreqencyWords.........')
        tokens=[]
        for sent,_ in corpus:
            tokens+=jieba.lcut(sent)
        ctokens=Counter(tokens)
        result=ctokens.most_common()
        # print(result)
        for i in range(len(corpus)):
#             for key,fre in result[:5]:
#                 corpus[i][0]=corpus[i][0].replace(key,'')
            for key,fre in result[-200:]:
                corpus[i][0]=corpus[i][0].replace(key,'')
        return corpus
    def toPredict(self,data,isFile=False):
        lines=None
        if isFile:
            with open(data,'r',encoding='utf8') as f:
                    lines=[line.strip() for line in  f.readlines()]
        else:
            lines=data
        dataset=self.build_corpus(lines)
        DataLoader=Data.DataLoader(dataset=dataset,collate_fn=self.collate_batch_test,batch_size=self.batch_size, shuffle=False)
        return DataLoader
    def get_data(self):
        lines=None
        with open(self.datapath,'r',encoding='utf8') as f:
                lines=[line.strip() for line in  f.readlines()]
        return lines
    def build_corpus(self,lines,buildtype='normal'):
        nlines=[]
        print('build_corpus......,lines size %s'%(len(lines)))
        def get_dynamic(lines):
            nlines=[]
            for line in lines:
                line=line.strip().split('\t')
                if len(line)>0:
#                     text,label=line[0],line[1:]
                    nlines.append(line)
            return nlines
        def splitTextLabel(lines):
            nlines=[]
            for line in lines:
                line=line.strip().split('\t')
                if len(line)>=2:
                    text,label=line[0],line[1]
                    nlines.append([text,label])
            return nlines
        def mult_aspect_splitTextLabel(lines):
            nlines=[]
            for line in lines:
                line=line.strip().split('\t')
                if len(line)>=2:
                    text,label=line[0],line[1:]
                    nlines.append([text,label])
            return self.cleanHighfreqencyWordsAndLow(nlines)
        def splitImageLabel(lines):
            nlines=[]
            img_transfomer=self.train_transformer
            for line in lines:
                line=line.strip().split('\t')
                if len(line)>=2:
                    text,label=line[0],line[1]
                    if buildtype=='test':
                        img_transfomer=self.test_transformer
                    nlines.append([text,label])
            return nlines
        def charTolist(lines):
            nlines=[]
            text = []
            labels = []
            for line in lines:
                line=line.strip()
                if line:
                    line=line.split('\t') if '\t' in line else line.split()
                    if len(line)>=2:
                        word, label =line[0],line[1]
                        text.append(word)
                        labels.append(label)
                else:
                    if text and labels:
                        nlines.append([text,labels])
                        text = []
                        labels = []
            if text and labels:
                nlines.append([text,labels])
                text = []
                labels = []
            return nlines
        def get_triple(lines):
            nlines=[]
            for line in lines:
                line=line.strip().split('\t')
                if len(line)>=3:
                    nlines.append([line[0],line[1],line[2]])
            nlines=generateNegSamples(nlines)
            return nlines
        if self.tasktype=='cls':
            nlines=splitTextLabel(lines)
        elif self.tasktype=='ascls': #multi aspect
            nlines=mult_aspect_splitTextLabel(lines)
        elif self.tasktype=='img_cls':
            nlines=splitImageLabel(lines)
        elif self.tasktype=='seq_tagging':
            nlines=charTolist(lines)
        elif self.tasktype=='seq2seq':
            nlines=splitTextLabel(lines)
        elif self.tasktype=='kge':
            nlines=get_triple(lines)
        elif self.tasktype=='dynamic':
            nlines=get_dynamic(lines)
        return nlines
    def MakeCorpus(self,isRegen=False):
        test_size = int(0.01 * len(self.data_list))
        valid_size=int(0.18 * len(self.data_list))
        train_size = len(self.data_list) - test_size-valid_size
        def datasplit(_corpus,dsizes):
            newdata=[]
            for i,ds in enumerate(dsizes):
                newdata.append(_corpus[sum(dsizes[:i]):sum(dsizes[:i])+dsizes[i]])
            return newdata
        train_dataset,valid_dataset,test_dataset=datasplit(self.data_list,[train_size,valid_size,test_size])
        print('train_dataset,valid_dataset,test_dataset:',train_size,valid_size, test_size)
        files=['train.tsv','valid.tsv','test.tsv']
        dtt=[train_dataset,valid_dataset,test_dataset]
        datapath='data'
        if not os.path.exists(datapath):
            os.mkdir(datapath)
        for file,dt in zip(files,dtt):
            if isRegen or not os.path.exists(os.path.join(datapath,file)):
                with open(os.path.join(datapath,file),'w',encoding='utf8') as f:
                    for d in dt:
                        f.write('%s'%(d))
        return train_dataset,valid_dataset,test_dataset
    def get_dataFeild(self):
        if self.tasktype=='cls':
            input_field=DataFeilds(index=self.custom_index[0] if self.custom_index else [0],sequential=True,isText=True,fix_length=self.fix_length,tokenize=self.tokenizer,public_vocab=self.public_vocab,pads=['[PAD]','[UNK]'])
            label_field=DataFeilds(index=self.custom_index[1] if self.custom_index else [1],sequential=False,isText=False,pads=['[UNK]'])
        elif self.tasktype=='ascls':
            input_field=DataFeilds(index=self.custom_index[0] if self.custom_index else [0],sequential=True,isText=True,fix_length=self.fix_length,tokenize=self.tokenizer,public_vocab=self.public_vocab,pads=['[PAD]','[UNK]'])
            label_field=DataFeilds(index=self.custom_index[1] if self.custom_index else [1],sequential=False,isText=False,pads=['[UNK]'])
        elif self.tasktype=='img_cls':
            input_field=DataFeilds(index=self.custom_index[0] if self.custom_index else [0],isImage=True)
            label_field=DataFeilds(index=self.custom_index[1] if self.custom_index else [1],sequential=False,isText=False,pads=['[UNK]'])
        elif self.tasktype=='seq_tagging':
            input_field=DataFeilds(index=self.custom_index[0] if self.custom_index else [0],sequential=True,isText=True,fix_length=self.fix_length,public_vocab=self.public_vocab,pads=['[PAD]','[UNK]'])
            label_field=DataFeilds(index=self.custom_index[1] if self.custom_index else [1],sequential=True,isText=False,fix_length=self.fix_length,pads=['[PAD]','[UNK]'])
        elif self.tasktype=='seq2seq': 
            input_field=DataFeilds(index=self.custom_index[0] if self.custom_index else [0],sequential=True,isText=True,fix_length=self.fix_length,tokenize=self.tokenizer,pads=['[PAD]','[UNK]'])
            label_field=DataFeilds(index=self.custom_index[1] if self.custom_index else [1],sequential=True,isText=True,fix_length=self.fix_length,tokenize=self.tokenizer,pads=['[PAD]','[UNK]'])
        elif self.tasktype=='kge':
            input_field=DataFeilds(index=self.custom_index[0] if self.custom_index else [0,1,3,4],sequential=False,isText=False,pads=['[PAD]','[UNK]'])
            label_field=DataFeilds(index=self.custom_index[1] if self.custom_index else [2,5],sequential=False,isText=False,pads=['[PAD]','[UNK]'])
        elif self.tasktype=='dynamic':
            input_field=DataFeilds(index=self.custom_index[0],**self.dynamic_input,pads=['[PAD]','[UNK]'])
            label_field=DataFeilds(index=self.custom_index[1],**self.dynamic_label,pads=['[PAD]','[UNK]'])
        else:
            raise Exception('please set task') 
        self.input_field,self.label_field=input_field,label_field
    def collate_batch_test(self,batch):
        data_org=[]
        data_ix=[]
        tags_ix=[]
        inputs=self.input_field.tokenize2id(batch)
        data_ix.append(inputs)
        data_org=batch
        data_ixs=torch.cat(data_ix,1)
        return [data_ixs,data_org]
    def collate_batch(self,batch):
        data_org=[]
        data_ix=[]
        tags_ix=[]
        inputs=self.input_field.tokenize2id(batch)
        data_ix.append(inputs)
        inputs=self.label_field.tokenize2id(batch)
        tags_ix.append(inputs)
        data_org=batch
        data_ixs=torch.cat(data_ix,1)
        tags_ixs=torch.cat(tags_ix,1)
        return [data_ixs,tags_ixs,data_org]
class DataFeilds():
    def __init__(self,index,sequential=False,isImage=False,isText=False,fix_length=-1,tokenize=None,public_vocab=False,pads=[]):
        self.index=index
        self.data_list=[]
        self.sequential=sequential
        self.isText=isText
        self.isImage=isImage
        self.fix_length=fix_length
        self.tokenize=tokenize
        self.pads=pads
        self.size=[] # for image width,height
        self.public_vocab=public_vocab
        self.vocab=None
        self.data2id={}
        self.id2data={}
        if public_vocab:
            self.data2id=torch.load(os.path.join(pdir,'word2id'))
            self.id2data={self.data2id[k]:k for k in self.data2id }
    def set_data2id(self,data2id):
        self.data2id=data2id
        self.id2data={self.data2id[k]:k for k in self.data2id }
    def add_data(self,data_list):
        try:
            for _index in self.index:
                for data in data_list:
    #                 print(data,_index)
                    if type(data[_index]) is list:
                        for ddt in data[_index]:
                            self.data_list.append(ddt)
                    else:
                        self.data_list.append(data[_index])
        except:
            pass
    def build_vocab(self,*datas):
        if self.isImage:
            if datas:
                for data in datas:
                    self.add_data(data)
                    break
                Img=torch.load(self.data_list[0])
                self.size=Img.size
        else:
            if not self.public_vocab:
                if datas:
                    for data in datas:
                        self.add_data(data)
                self.data_list=self.data_list[0] if len(self.data_list)==1 else self.data_list
                print(len(self.data_list))
                if self.tokenize:
                    self.data_list=[w for sent in self.data_list for w in self.tokenize(sent)]
                self.vocab=self.pads+sorted(list(set(self.data_list)))
                self.data2id={w:i for i,w in enumerate(self.vocab)}
                self.id2data={i:w for i,w in enumerate(self.data2id)}
#             else:
#                 self.data2id=torch.load(os.path.join(pdir,'word2id'))
#                 self.id2data={self.data2id[k]:k for k in self.data2id }
    def tokenize2id(self,data_list,Imgtransformer=None): 
        if type(self.index) is not list:
            self.index=[self.index]
        data2ix_list = []
        sen_len=self.fix_length if self.fix_length>0 else 800
        if self.sequential:
            sen_len=self.fix_length if self.fix_length>0 else max([len(se[self.index[0]]) for se in data_list])
        def padding(dlist,sen_len):
            if sen_len>510:
                sen_len=510 
            if len(dlist)>sen_len:
                return dlist[:sen_len]
            return dlist+[self.data2id['[PAD]'] for i in range(sen_len-len(dlist)) ]
        img_size=None    
        if self.isImage:
                for i,data_one in enumerate(data_list):
                    tmp=[]
                    for _index in self.index:
                        if Imgtransformer:
                            Img=torch.load(data_one[_index]).convert('1')
                            if img_size is None:
                                img_size=Img.size
                            newsize=transforms.Resize([img_size])
                            imgEnc=Imgtransformer(newsize(Img))
                            # print(imgEnc.shape)
                            tmp.append(imgEnc)
                        else:
                            tmp.append(data_one[_index])
                    if len(tmp)==1:
                        tmp=tmp[0]
                    data2ix_list.append(tmp)
        else:
            for i,data_one in enumerate(data_list):
                if self.sequential:
                    tmp=[]
                    for _index in self.index:
                        if self.tokenize and not self.public_vocab:
                            data_one[_index]=self.tokenize(''.join(data_one[_index]))
                        tmp.append(padding([self.data2id.get(w,self.data2id['[UNK]']) for w in data_one[_index]],sen_len))
#                         tmp.append(padding([ord(w) for w in data_one[_index]],sen_len))
                    if len(tmp)==1:
                        tmp=tmp[0]
                    data2ix_list.append(tmp) 
                else:
                    tmp=[]
                    for _index in self.index:
                        if type(data_one[_index]) is not list:
                            data_one[_index]=[data_one[_index]]
                        tmp.append([self.data2id.get(w,self.data2id['[UNK]']) for w in data_one[_index]])
                    if len(tmp)==1:
                        tmp=tmp[0]
                    data2ix_list.append(tmp)
        out_data=torch.tensor(data2ix_list)
        return  out_data
