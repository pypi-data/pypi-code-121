import numpy as np
from sklearn.metrics import roc_curve, precision_recall_curve, auc

def evaluate(gold_standard, y_pred, negative_links='as_positive', print_auc=True):
    y_true = np.array(gold_standard)
    if negative_links == 'as_positive':
        y_true[y_true != 0] = 1
    elif negative_links == 'ignore':
        y_true[y_true < 0] = 0
        y_true[y_true > 0] = 1
    
    fpr, tpr, _ = roc_curve(y_true, y_pred, pos_label = 1)
    prec, recall, _ = precision_recall_curve(y_true, y_pred, pos_label = 1)
    
    auroc = auc(fpr, tpr)
    auprc = auc(recall, prec)
    
    if print_auc:
        print("AUROC:{:.4f}   AUPRC:{:.4f}".format(auroc, auprc))
    
    return {
        'fpr': fpr,
        'tpr': tpr,
        'prec': prec,
        'recall': recall,
        'AUROC': auroc,
        'AUPRC': auprc
    }