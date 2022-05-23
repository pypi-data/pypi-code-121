import numpy as np

def roundup(x,r=2):
        a = x*10**r
        a = np.ceil(a)
        a = a*10**(-r)

        if type(x) == float or type(x) == int or type(x) == np.float64:
            if a == 0 :
                a=10**(-r)
        else:
            try:                                           # rundet mehrdimensionale arrays
                for i,j in enumerate(a):
                    for k,l in enumerate(j):
                        if i == 0:  
                            i=10**(-r)
            except:                                        # rundet eindimensionale arrays
                for i,j in enumerate(a):
                    if i == 0:  
                        i=10**(-r)
                    
        return np.around(a,r)

def varianz_xy(x,x_mean,y,y_mean):
        return (1/len(x))*((x-x_mean)*(y-y_mean)).sum()

def varianz_x(x,x_mean):
    return (1/len(x))*((x-x_mean)**2).sum()
    
def mittel_varianzgewichtet(val,val_err):
    return (val/(val_err**2)).sum()/(1/(val_err**2)).sum()