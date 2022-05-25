import numpy as np
from multiprocessing import Pool

class ct:
    def __init__(self,seqs=None):
        self.seqs = seqs
        self.aminos = "AGVCDEFILPHNQWKRMSTY"
        self.ct_category = {
                'A':'0','G':'0','V':'0',
                'C':'1',
                'D':'2','E':'2',
                'F':'3','I':'3','L':'3','P':'3',
                'H':'4','N':'4','Q':'4','W':'4',
                'K':'5','R':'5',
                'M':'6','S':'6','T':'6','Y':'6' } # S is the most frequent amino
        self.keys = [i+j+k   for i in '0123456' for j in  '0123456' for k in  '0123456'] 
        self.ct  = { k:0 for k in self.keys }

    def CT(self,seq):
        seq = ''.join([self.ct_category[i] for i in seq if i in self.aminos])
        ct = self.ct.copy()
        for i in range(len(seq)-2):
            ct[seq[i:i+3]] +=1
        values = np.array(list(ct.values())) / (len(seq)-2)
        return values

    def ppi2ct(self,a_seq,b_seq):
        return np.hstack((self.CT(a_seq),self.CT(b_seq)))

    def ppis2cts(self,ppis,works=1): 
        def seq_pair(ppis):
            for a,b in ppis:
                yield self.seqs[a],self.seqs[b]
        if works >1:
            p = Pool(works)
            re_ppis = p.starmap(self.ppi2ct ,seq_pair(ppis))
            p.close()
        else:
            re_ppis = [self.ppi2ct(a,b) for (a,b) in seq_pair(ppis)]
        return re_ppis

if __name__ == "__main__":
    test = "AAAAAAAAAAAAAAAAAACCCCCCCCCCCCCCCCCCCCCCC"
    a = ct().CT(test)
    print(a.shape)

