import torch
from platform import python_version, uname

def get_info():
    '''complete sys info'''
    
    print(f'---------- Sys Info ----------')
    print(f'Python Version: {python_version()}')
    print(uname())
       
    print(f'\n---------- PyTorch Info ----------')
    print(f'torch version: {torch.__version__}')
    if torch.cuda.is_available():
        print(f'CUDA Version: {torch.version.cuda}')
    else:
        print(f'CUDA Unavailable!')
        
        
if __name__ == '__main__':
    get_info()