import os

PROBLEMS_FOLDER = os.path.join('problems')

def rename(path, _old, _new, recursive=False):
    for f in os.listdir(path):        
        if os.path.isdir(os.path.join(path, f)):
            if recursive:
                rename(os.path.join(path, f), _old, _new, recursive)
        
        if _old in f:
            os.rename(
                os.path.join(path, f), 
                os.path.join(path, f.replace(_old,_new))
            )