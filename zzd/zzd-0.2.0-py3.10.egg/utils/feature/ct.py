import numpy as np

def ct(seq):
    aminos = "AGVCDEFILPHNQWKRMSTY"
    ct_category = {
                'A':'0','G':'0','V':'0',
                'C':'1',
                'D':'2','E':'2',
                'F':'3','I':'3','L':'3','P':'3',
                'H':'4','N':'4','Q':'4','W':'4',
                'K':'5','R':'5',
                'M':'6','S':'6','T':'6','Y':'6' } 
    ct_count = {i+j+k:0  for i in '0123456' for j in  '0123456' for k in  '0123456'}
    seq = "".join([ct_category[i] for i in seq if i in aminos])

    for i in range(len(seq)-2):
        ct_count[seq[i:i+3]] +=1
    values = np.array(list(ct_count.values())) / (len(seq)-2)
    return values


if __name__ == "__main__":
    seq = "AAAAAAAAAAAAAAAAAACCCCCCCCCCCCCCCCCCCCCCC"
    print(ct(seq), ct(seq).shape)

