from pystoi.stoi import stoi
import numpy as np

def cal_stoi(ref, est, sr=16000):
    return stoi(ref, est, sr, extended=False)


if __name__ == '__main__':
    with open('clean.pcm','rb') as ref:
        pcmdata = ref.read()
    with open('in.pcm','rb') as ref:
        indata = ref.read()
    ref = np.frombuffer(pcmdata,dtype=np.int16)
    ins = np.frombuffer(indata, dtype=np.int16)
    print(cal_stoi(ref,ins))