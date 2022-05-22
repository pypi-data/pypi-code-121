import numpy as np
from ..helper import seed_once


def remove_const_features(x):
    """
    Remove constant features from a numpy array.
    """
    assert len(x.shape) == 2, "remove_const_features only works on 2D arrays"
    return x[:, np.where(np.std(x, axis=0) > 0)[0]]

@seed_once
def train_test_split(x,y,max_test_size=0.3):
    """
    Split data into training and test sets.
    """
    assert len(x.shape) == 2, "train_test_split only works on 2D arrays"
    norm=np.array([xx for xx,yy in zip(x,y) if yy==0])
    anom=np.array([xx for xx,yy in zip(x,y) if yy!=0])
    
    np.random.shuffle(norm)
    np.random.shuffle(anom)

    n_ano=int(anom.shape[0])
    n_ano=min([int(max_test_size*norm.shape[0]),n_ano])

    train=norm[:-n_ano]
    testn=norm[-n_ano:]
    testa=anom[:n_ano]
    test=np.concatenate((testn,testa),axis=0)
    testy=np.array([0]*n_ano+[1]*n_ano)

    return train,test,testy

@seed_once
def shuffle(x,y=None):
    """
    Shuffle the data. Keeps the connection between the data and the labels if provided
    """
    if y is not None:
        seed = np.random.randint(0, 2**32 - 1)
        np.random.seed(seed)
        np.random.shuffle(x)
        np.random.seed(seed)
        np.random.shuffle(y)
        return x,y
    else:
        np.random.shuffle(x)
        return x


@seed_once
def crossassign(n_samples,n_folds):
    """
    Randomly assigns samples to folds.
    """
    n_samples = int(n_samples)
    n_folds = int(n_folds)
    if n_samples < n_folds:
        raise ValueError("n_samples must be greater than n_folds")
    if n_folds < 2:
        raise ValueError("n_folds must be greater than 1")
    assigns=[i%n_folds for i in range(n_samples)]
    np.random.shuffle(assigns)
    return assigns

@seed_once
def crossvalidate(x,y,n_folds=5):
    """
    Splits the data into crossvalidation folds. Return n_folds versions of train, test and testy
    """
    x0=np.array([xx for xx,yy in zip(x,y) if yy==0])
    x1=np.array([xx for xx,yy in zip(x,y) if yy!=0])

    assigns=crossassign(len(x0),n_folds)

    def fold(x,y,i):    
        train=np.array([xx for ass,xx in zip(assigns,x0) if ass!=i])#training folds
        test_n=np.array([xx for ass,xx in zip(assigns,x0) if ass==i])#test fold
        if len(test_n)>=len(x1):#more normal data than abnormal one in the testing data. 
            test_n=test_n[:len(test_n)]#So cut the normal one
            x1m=x1#but keep the abnormal one
        elif len(test_n)<len(x1):#more abnormal data than normal one in the testing data.
            #folding so other abnormal samples are used sometime
            border=int((i/n_folds)*len(x1))
            a,b=x1[:border],x1[border:]
            x1m=np.concatenate((a,b),axis=0)
            x1m=x1m[:len(test_n)]
            #keep the testing one
        test=np.concatenate([test_n,x1m],axis=0)
        test_y=np.array([0]*len(test_n)+[1]*len(x1m))
        return train,test,test_y

    trains,tests,test_ys=[],[],[]
    for i in range(n_folds):
        train,test,test_y=fold(x,y,i)
        yield train,test,test_y

def normalize(x,sec=None,method="zscore"):
    """
    Normalize the data by the given method.
    if sec is provided, it is also normalized using the same method and statistics from the first one
    """

    if method=="zscore":
        xm=np.mean(x,axis=0)
        xs=np.std(x,axis=0)
        xs=np.where(xs==0,1,xs)
    elif method=="minmax":
        xm=np.min(x,axis=0)
        xs=np.max(x,axis=0)-xm
        xs=np.where(xs==0,1,xs)
    else:
        raise ValueError("Unknown normalization method: "+method)
    x=(x-xm)/xs
    if sec is not None:
        sec=(sec-xm)/xs
        return x,sec
    return x

def asfloat(x):
    return np.array(x).astype(np.float32)

def asint(x):
    return np.array(x).astype(np.int32)



