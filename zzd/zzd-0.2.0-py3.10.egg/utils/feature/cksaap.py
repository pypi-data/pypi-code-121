import numpy as np

def cksaap(seq,k=3):
    aminos = "AGVCDEFILPHNQWKRMSTY"
    ckdpc =  {str(idx)+i+j:0 for idx in range(k) for i in aminos for j in aminos}

    for idx in range(k):
        for i in range(len(seq)-idx-1):
            ckdpc[str(idx)+seq[i]+seq[i+idx+1]]+=1
    
    values = np.array(list(ckdpc.values()))/ (len(seq)-k)
    return values


if __name__ == "__main__":
    seq = "AGVAGV"
    print(cksaap(seq),cksaap(seq).shape)
