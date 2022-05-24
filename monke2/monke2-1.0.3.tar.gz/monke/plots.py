import matplotlib.pyplot as plt

def errorbar(x_val,y_val,y_err,x_err=[0],marker='o',markersize=7,color='tab:red',line='',label='Daten',caps=5,eline=1.5,markerwidth=1.5):
    if x_err == [0]:
        x_err = [0]*len(x_val)
    plt.errorbar(x_val, y_val,color=color,marker=marker,markersize=markersize,linestyle=line,
    yerr=y_err, xerr=x_err,label=label,capsize=caps, elinewidth=eline, markeredgewidth=markerwidth)
