import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np
from sklearn import metrics


def auprc_curve(y_true, y_pred,save_file=False,label="",title="",color=False,*argvs):
    """
    y_true: true label
    y_pred: pred probility
    
    output: auprc curve
        x-axil :recall  
        y-axil :precision
    """
    _, ax = plt.subplots(1, 1, figsize=(8, 6))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    #axises
    ax.xaxis.set_major_locator(MultipleLocator(0.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.tick_params(labelsize=26)

    #plot
    AUPRC = round(metrics.average_precision_score(y_true, y_pred), 5)
    precision, recall, threshold = metrics.precision_recall_curve(y_true, y_pred)
    print("x:",recall)
    print("y:",precision )
    print("threshold",threshold)
    if color:
        ax.plot(recall, precision, label=label , color=color, linewidth=2.0)
    else:
        ax.plot(recall, precision, label=label , linewidth=2.0)

    #title and label
    ax.set_xlabel("Recall=TP/(TP+FN)", fontdict={"fontsize": 22})
    ax.set_ylabel("Precision = TP/(TP+FP)", fontdict={"fontsize": 22})
    ax.set_title(title, fontdict={"fontsize": 15}, y=1.05)
    
    return AUPRC


if __name__ == "__main__":
    y_true = [0,   0,   0,   0,   0,   0,   1,   1,   1,   1,   1,   1  ]
    y_pred = [0.0+1e-6, 0.2, 0.4, 0.6, 0.8, 1.0-1e-6, 0.0+1e-6, 0.2, 0.4, 0.6, 0.8, 1.0-1e-6]
    auprc = auprc_curve(y_true,y_pred)
    print(f"auprc:{auprc}")
    plt.show()

