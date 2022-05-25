import numpy as np
from sklearn import metrics


def scores(y_true:int, y_pred:float, threshold=0.5, show=False):
    """
    y_true:true label
    y_prob:pred label with probility
    threshold:Negative if y_pred < threshold, positive if y_pred > threshold.

    multi scores of binnary class:
    (1) first layer score
        TP : true positive
        TN : true negative
        FP : false positive
        FN : false engative

    (2) second layer score
        precision   = TP/(TP+FP)
        recall      = TP/(TP+FN)   
        sensitivity = TP/(TP+FN)   
        specificity = TN/(TN+FP)
        Accuracy    = (TP+TN)/(TP+TN+FP+FN)  

    (3) third layer score
         mcc = (TP*TN - FP*FN)/sqrt((TP+FP)*(TP+FN)*(TN+FP)*(TN+FN))
         f1 = 2*(precision*recall)/(precision+recall)

    (4) area score
        auc : Area under the curve of ROC(receipt operator curve) 
        auprc:Area under the precision recall curve
        ap:   Average precision-recall score

    more info:
        TPR = TP/(TP+FN) :true positive rate 
        TNR = TN/(TN+FP) :true negative rate
        FPR = FP/(TN+FP) :false positive rate
        FNR = FN/(TP+FN) :false negative rate

        PPV = TP/(TP+FP):positive predictive value
        NPV = TN/(TN+FN):negative predictive value
 
        PPV=precision
        TPR=Recall=sensitivity
        TNR=specificity

    example:

    test = scores(
            y_true = [0,   0,   0,   0,   0,   0,   1,   1,   1,   1,   1,   1  ],
            y_pred = [0., 0.2, 0.4, 0.6, 0.8, 1., 0., 0.2, 0.4, 0.6, 0.8, 1],show=True)

    """

    if max(y_true) > 1 or min(y_true)< 0 :
        raise Exception("label not in range (0, 1)!")
    
    if max(y_pred) > 1 or min(y_pred) <0:
        raise Exception("y_prob value not in range (0, 1)!")

    y_true = np.array(y_true,float)
    y_pred = np.array(y_pred,float)

    y_true_label = np.round(y_true)
    y_pred_label = np.round(y_pred)
    
    TP = sum((y_true >  threshold) & (y_pred >  threshold ))
    TN = sum((y_true <= threshold) & (y_pred <= threshold ))
    FP = sum((y_true <= threshold) & (y_pred >  threshold ))
    FN = sum((y_true >  threshold) & (y_pred <= threshold ))
    
    precision =     np.round(metrics.precision_score(y_true_label, y_pred_label),5)
    recall =        np.round(metrics.recall_score(y_true_label, y_pred_label),5)
    sensitivity =   recall
    specificity =   np.round(TN/(TN+FP+1e-6),5)
    
    accuracy =      np.round(metrics.accuracy_score(y_true_label, y_pred_label),5)
    mcc =           np.round(metrics.matthews_corrcoef(y_true_label, y_pred_label),5)
    f1 =            np.round(metrics.f1_score(y_true_label, y_pred_label),5)

    precisions, recalls,_ = metrics.precision_recall_curve(y_true, y_pred)
    auroc =         np.round(metrics.roc_auc_score(y_true, y_pred),5)
    auprc =         np.round(metrics.auc(recalls, precisions),5)
    ap =            np.round(metrics.average_precision_score(y_true, y_pred),5)
    
    if show:
        np.set_printoptions(suppress=True)
        print("TP,TN,FP,FN, precision, recall,sensitivity, specificity, accuracy, mcc, f1, AUROC, AUPRC, AP")
        print( TP,TN,FP,FN, precision, recall,sensitivity, specificity, accuracy, mcc, f1, auroc, auprc,ap)

    return TP,TN,FP,FN, precision, recall, sensitivity, specificity, accuracy, mcc, f1, auroc, auprc,ap


if __name__ == "__main__":
    test = scores(
            [0,   0,   0,   0,   0,   0,   1,   1,   1,   1,   1,   1  ],
            [0.001, 0.2, 0.4, 0.6, 0.8, 0.999, 0.001, 0.2, 0.4, 0.6, 0.8, 0.999],show=True)
    #TP,TN,FP,FN, precision, recall, sensitivity, specificity, accuracy, mcc, f1, auroc, auprc,ap = test
    #print(f"TP, TN, FP, FN: {TP}\t{TN}\t{FP}\t{FN}")
    #print(f"precision, recall,sensitivity, specificity: {precision}\t{recall}\t{sensitivity}\t{specificity}")
    #print(f"accuracy, mcc, f1: {accuracy}\t{mcc}\t{f1}" )
    #print(f"auroc, auprc, ap: {auroc}\t{auprc}\t{ap}")

