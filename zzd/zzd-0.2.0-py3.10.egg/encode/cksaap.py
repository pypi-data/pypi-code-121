import numpy as np
from multiprocessing import Pool

class cksaap:
    def __init__(self,seqs=None):
        self.aminos = "AGVCDEFILPHNQWKRMSTY"
        self.keys = [i+j for i in self.aminos for j in self.aminos]
        self.dpc = { k:0 for k in self.keys}
        self.seqs = seqs
    
    def CKSAAP(self,seq):
        seq = ''.join([_ for _ in seq if _ in self.aminos])
        dpc0 = self.dpc.copy()
        dpc1 = self.dpc.copy()
        dpc2 = self.dpc.copy()
        dpc3 = self.dpc.copy()
        for i in range(len(seq)-1):
            dpc0[seq[i]+seq[i+1]]+=1

        for i in range(len(seq)-2):
            dpc1[seq[i]+seq[i+2]]+=1

        for i in range(len(seq)-3):
            dpc2[seq[i]+seq[i+3]]+=1

        for i in range(len(seq)-4):
            dpc3[seq[i]+seq[i+4]]+=1

        values = np.array([[dpc0[k],dpc1[k],dpc2[k],dpc3[k]] 
            for k in self.keys]).ravel()/ (len(seq)-1)
        return values

    def ppi2cksaap(self,a_seq,b_seq):
        return np.hstack((self.CKSAAP(a_seq),self.CKSAAP(b_seq)))

    def ppis2cksaaps(self,ppis,works=1): 
        def seq_pair(ppis):
            for a,b in ppis:
                yield self.seqs[a],self.seqs[b]

        if works >1:
            p = Pool(works)
            re_ppis = p.starmap(self.ppi2cksaap ,seq_pair(ppis))
            p.close()
        else:
            re_ppis = [self.ppi2cksaap(a,b) for (a,b) in seq_pair(ppis)]
        return re_ppis


if __name__ == "__main__":
    a= cksaap().CKSAAP("AGVAGV")
    print(a,a.shape)
