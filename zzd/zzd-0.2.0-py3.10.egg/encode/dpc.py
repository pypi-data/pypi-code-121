import numpy as np
from multiprocessing import Pool

class dpc:
    def __init__(self,seqs=None):
        self.aminos = "AGVCDEFILPHNQWKRMSTY"
        self.keys = [i+j for i in self.aminos for j in self.aminos]
        self.dpc = { k:0 for k in self.keys}
        self.seqs = seqs

    def DPC(self,seq):
        seq = "".join([i for i in seq if i in self.aminos])
        dpc = self.dpc.copy()
        seq_len = len(seq)

        for i in range(seq_len-1):
            dpc[seq[i:i+2]] += 1

        values = np.array(list(dpc.values())) / (len(seq)-1)
        return values

    def ppi2dpc(self,a_seq,b_seq):
        return np.hstack((self.DPC(a_seq),self.DPC(b_seq)))

    def ppis2dpcs(self,ppis,works=1): 
        def seq_pair(ppis):
            for a,b in ppis:
                yield self.seqs[a],self.seqs[b]
        if works > 1:
            p = Pool()
            re_ppis = p.starmap(self.ppi2dpc ,seq_pair(ppis))
            p.close()
        else:
            re_ppis = [self.ppi2dpc(a,b) for (a,b) in seq_pair(ppis)]
        return re_ppis

if __name__ == "__main__":
    a="'MIRRISPGAVPPSLPSAPVASHHHADAPQAGVQPPADTAHHAPRLRPAPPRKRRRGMRSLDGMDDELDATELEEAEAARVSALRGRVSIAVAQPQGQGQRQDDQHGEGGNAQAGDPQAGTWPIAAPSQVDDSARASVQEVLDRYAATPAADQTIRRRALAVALVELRAIGVAHPAAAQLTTMVWRLMREHLHSGSAGAAAETLQALRKRLLDLVPAQPDTSPALRSFHLLLPLMLLNAEKPRKRLDRARAITRLNTLLIEHHDGTAQEIRA'"

    print(dpc().DPC(a).shape)
    print(dpc().DPC(a).max())
