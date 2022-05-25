import numpy as np
from multiprocessing import Pool

#def AC(seq):
#    aminos = "AGVCDEFILPHNQWKRMSTY"
#    ac_category = {
#                "A":[1,1,1,1,3,2,4],"C":[1,2,3,3,3,2,4],"D":[3,2,6,6,2,1,2],"E":[3,3,6,6,2,1,2],
#                "F":[1,5,2,7,3,1,4],"G":[2,1,1,11,3,2,4],"H":[2,3,5,5,1,1,3],"I":[1,4,1,1,3,2,4],
#                "K":[3,4,5,5,1,1,1],"L":[1,4,1,1,3,2,4],"M":[1,4,3,3,3,1,4],"N":[3,2,7,2,3,1,3],
#                "P":[2,2,1,10,3,1,4],"Q":[3,3,7,2,3,1,3],"R":[3,4,5,5,1,1,1],"S":[2,1,4,4,3,2,3],
#                "T":[2,2,4,4,3,2,3],"V":[1,3,1,1,3,1,4],"W":[1,5,2,8,3,1,1],"Y":[2,5,2,9,3,2,3]}
#    seq = np.array([self.ac_category[i] for i in  seq if i in aminos])
#    L=len(seq)
#    def S_ac(lag):
#        return np.mean(np.multiply(
#                seq[0:L - lag, :] - np.mean(seq, axis=0),
#                seq[lag:, :] - np.mean(seq, axis=0)), axis=0)
#
#    values = np.array(list(map(S_ac,range(1,31)))).ravel()
#    return values
#



class ac:
    def __init__(self,seqs=None):
        self.seqs = seqs
        self.aminos = "AGVCDEFILPHNQWKRMSTY"
        self.ac_category = {
                "A":[1,1,1,1,3,2,4],"C":[1,2,3,3,3,2,4],"D":[3,2,6,6,2,1,2],"E":[3,3,6,6,2,1,2],
                "F":[1,5,2,7,3,1,4],"G":[2,1,1,11,3,2,4],"H":[2,3,5,5,1,1,3],"I":[1,4,1,1,3,2,4],
                "K":[3,4,5,5,1,1,1],"L":[1,4,1,1,3,2,4],"M":[1,4,3,3,3,1,4],"N":[3,2,7,2,3,1,3],
                "P":[2,2,1,10,3,1,4],"Q":[3,3,7,2,3,1,3],"R":[3,4,5,5,1,1,1],"S":[2,1,4,4,3,2,3],
                "T":[2,2,4,4,3,2,3],"V":[1,3,1,1,3,1,4],"W":[1,5,2,8,3,1,1],"Y":[2,5,2,9,3,2,3]}
    
    def AC(self,seq):
        seq = np.array([self.ac_category[i] for i in  seq if i in self.aminos])
        L=len(seq)
        def S_ac(lag):
            return np.mean(np.multiply(
                seq[0:L - lag, :] - np.mean(seq, axis=0),
                seq[lag:, :] - np.mean(seq, axis=0)), axis=0)
        values = np.array(list(map(S_ac,range(1,31)))).ravel()
        return values

    def ppi2ac(self,a_seq,b_seq):
        return np.hstack((self.AC(a_seq),self.AC(b_seq)))

    def ppis2acs(self,ppis,works=1): 
        def seq_pair(ppis):
            for a,b in ppis:
                yield self.seqs[a],self.seqs[b]
        if works >1:
            p = Pool(works)
            re_ppis = p.starmap(self.ppi2ac ,seq_pair(ppis))
            p.close()
        else:
            re_ppis = [self.ppi2ac(a,b) for (a,b) in seq_pair(ppis)]
        return re_ppis

if __name__ == "__main__":
    test = "AAAAAAAAAAAAAAAAAACCCCCCCCCCCCCCCCCCCCCCC"
    a = ac().AC(test)
    print(a,"\nshape:",a.shape)

