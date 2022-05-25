"""
example
python interolog ppi seqs

#mechanism
protein A` is the homolog of protein A
protein B` is the homolog of protein B
if A`-B` have interation then we inference A-B also have interation.

#
1. protein sequences db in which protein also have ppi.
2. seach homolog of input protein pair
3. if any interaction of A`-B` then A-B interaction. vice versa.


python -test test_ppis.txt -train train_ppis.txt  -seqs fasta_seq
python -test test_ppis.txt

"""
import sys
import os
import numpy as np
import pandas as pd
from Bio import SeqIO
#import torch.nn as nn


#1 load input ppi and interolog_ppi_db
def enviroment_init():
    """
    download ppidb and ppiblastdb.
    you need install ncbi-blastp program first and add the blastp path to $PATH.
    """
    if not os.path.exists(f"{os.environ['HOME']}/.local/interolog/ppis_db.txt"):
        os.system("mkdir -p $HOME/.local/interolog/blastdb")
        os.system("wget https://github.com/miderxi/zzd_lib/raw/main/zzd/lib/blastdb.tar.gz \
                    -O $HOME/.local/interolog/blastdb/blastdb.tar.gz")
        os.system("tar -xvf $HOME/.local/interolog/blastdb/blastdb.tar.gz \
                    -C $HOME/.local/interolog/blastdb/")
        os.system("makeblastdb \
                    -in $HOME/.local/interolog/blastdb/blastdb.fasta \
                    -out $HOME/.local/interolog/blastdb/blastdb  -dbtype prot")
        os.system("wget https://github.com/miderxi/zzd_lib/raw/main/zzd/lib/ppis_db.tar.gz\
                    -O $HOME/.local/interolog/ppis_db.tar.gz")
        os.system("tar -xvf $HOME/.local/interolog/ppis_db.tar.gz \
                    -C $HOME/.local/interolog/")
 
def fetch_ppis_db(train_file=None,seqs_file=None):
    ppis_db  = set([tuple(i) for i in  
            pd.read_table(f"{os.environ['HOME']}/.local/interolog/ppis_db.txt",header=None).to_numpy()])
    if train_file:
        temp = np.genfromtxt(train_file,str,delimiter="\t")
        if temp.shape[1] == 3:
            temp = temp[temp[:,2] == "1"]
        for i in temp:
            ppis_db.add(tuple(i))
        if not os.path.existst("/tmp/interolog"):
            os.system("mkdir /tmp/interolog/")
        os.system(f"makeblastdb -in {seqs_file} -out /tmp/interolog/seqs -dbtype prot")
    return ppis_db


def fetch_homo(query_ppis,seqs_file,train_file,threshold=40,runblast=True,n_works=8):
    ids_query =set([j for i in  query_ppis for j in i])
    query_seqs = {i.id:str(i.seq) for i in SeqIO.parse(seqs_file,"fasta") if i.id in ids_query}
    with open("/tmp/interolog/query_seqs.fasta","w") as f :
        for k,v in query_seqs.items():
            f.write(f">{k}\n{v}\n")
    
    cmd1 = f"blastp -query /tmp/interolog/query_seqs.fasta \
                -db {os.environ['HOME']}/.local/interolog/blastdb/blastdb\
                -out /tmp/interolog/query_seqs.blastp \
                -evalue 1e-2 \
                -outfmt 6 \
                -num_threads {n_works}"
    cmd2 = f"blastp -query /tmp/interolog/query_seqs.fasta \
                -db /tmp/interolog/seqs\
                -out /tmp/interolog/query_seqs2.blastp \
                -evalue 1e-2 \
                -outfmt 6 \
                -num_threads {n_works}"
    if runblast:
        os.system(cmd1)
        if train_file:
            os.system(cmd2)
    
    homo = {}
    for line in pd.read_table("/tmp/interolog/query_seqs.blastp",header=None).to_numpy():
        if line[2] > threshold:
            if line[0] not in homo.keys():
                homo[line[0]] = set([line[1]])
            else:
                homo[line[0]].add(line[1])
    
    if train_file:
         for line in pd.read_table(f"/tmp/interolog/query_seqs2.blastp",header=None).to_numpy():
            if line[2] > threshold:
                if line[0] not in homo.keys():
                    homo[line[0]] = set([line[1]])
                else:
                    homo[line[0]].add(line[1])
    return homo



def prediction(query_ppis, ppis_db, homo,detail=True):
    ppis_pred = []
    for a,b in query_ppis[:,:2].reshape(-1,2):
        if detail:
            pred = [a,b,0,None]
        else:
            pred = 0

        if a in homo.keys() and b in homo.keys():
            candicate = set([(i,j) for i in  homo[a] for j in homo[b]] +
                        [(j,i) for i in  homo[a] for j in homo[b]])
            if candicate & ppis_db:
                if detail:
                    pred[2] = 1
                    pred[3] = candicate & ppis_db
                else:
                    pred = 1    
        ppis_pred.append(pred)
    return ppis_pred


def interolog(test_file, seqs_file=None,train_file=None, threshold=40,runblast=True,detail=False,n_works=8):
    """
    test_file:'protein_a\tprotein_b'  pair per line for predict.
    train_file:'protein_a\t protein_b' per line to infer from.   
    seqs_file:fasta format file
    """
    enviroment_init()
    query_ppis = np.genfromtxt(test_file,str,delimiter="\t")
    ppis_db = fetch_ppis_db(train_file=train_file,seqs_file=seqs_file)
    homo = fetch_homo(query_ppis,seqs_file,train_file,threshold,runblast,n_works=8)
    pred = prediction(query_ppis,ppis_db,homo,detail=detail)
    return pred


	
if __name__ == "__main__":
    from zzd import scores
    test_file = "../../../atppi/B2_train_and_test/p1n10_10folds/test_0.txt"
    train_file = "../../../atppi/B2_train_and_test/p1n10_10folds/train_0.txt"
    seqs_file = "../../../atppi/B1_ppis_and_seqs/ppis_ara_and_eff.fasta"

    #pred = interolog(test_file,seqs_file,train_file,runblast=False,detail=True)
    #[print(i) for i in pred]
    pred = interolog(test_file,seqs_file,train_file,runblast=False,detail=False,threshold=10,n_works=8)	
    scores(pd.read_table(test_file,header=None).to_numpy()[:,2],pred,show=True)

