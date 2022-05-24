import os
import numpy as np
from miacag.utils.sql_utils import getDataFromDatabase
from sklearn.metrics import f1_score, \
     accuracy_score, confusion_matrix, plot_confusion_matrix
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import ticker
import matplotlib
matplotlib.use('Agg')
from sklearn import metrics


def map_1abels_to_0neTohree():
    labels_dict = {
        0: 0,
        1: 1,
        2: 2,
        3: 2,
        4: 2,
        5: 2,
        6: 2,
        7: 2,
        8: 2,
        9: 2,
        10: 2,
        11: 2,
        12: 2,
        13: 2,
        14: 2,
        15: 2,
        16: 2,
        17: 2,
        18: 2,
        19: 2,
        20: 2}
    return labels_dict


def create_empty_csv():
    df = {'Experiment name': [],
          'Test F1 score on data labels transformed': [],
          'Test F1 score on three class labels': [],
          'Test acc on three class labels': []}
    return df


def getNormConfMat(df, labels_col, preds_col,
                   plot_name, f1, output, num_classes, support):
    labels = [i for i in range(0, num_classes)]
    conf_arr = confusion_matrix(df[labels_col], df[preds_col], labels=labels)
    sum = conf_arr.sum()
    conf_arr = conf_arr * 100.0 / (1.0 * sum)
    df_cm = pd.DataFrame(
        conf_arr,
        index=[
            str(i) for i in range(0, num_classes)],
        columns=[
            str(i) for i in range(0, num_classes)])
    fig = plt.figure()
    plt.clf()
    ax = fig.add_subplot(111)
    ax.set_aspect(1)
    cmap = sns.cubehelix_palette(light=1, as_cmap=True)
    res = sns.heatmap(df_cm, annot=True, vmin=0.0, vmax=100.0, fmt='.2f',
                      square=True, linewidths=0.1, annot_kws={"size": 8},
                      cmap=cmap)
    res.invert_yaxis()
    f1 = np.round(f1, 3)
    plt.title(
        plot_name + ': Confusion Matrix, F1-macro:' + str(f1))
    plt.savefig(os.path.join(output, plot_name + '_cmat.png'), dpi=100,
                bbox_inches='tight')
    plt.close()

    plt.title(
        plot_name + ': Confusion Matrix, F1-macro:' + str(f1) +
        ',support(N)=' + str(support))
    plt.savefig(os.path.join(output, plot_name + '_cmat_support.png'), dpi=100,
                bbox_inches='tight')
    plt.close()
    return None


def plot_results(sql_config, output_plots, num_classes, roc=False):
    df, _ = getDataFromDatabase(sql_config)
    for label_name in sql_config['labels_names']:
        df_label = df[df[label_name].notna()]
        df_label[label_name + '_predictions'] = \
            df_label[label_name + '_predictions'].astype(float).astype(int)
        df_label[label_name] = df_label[label_name] \
            .astype(float).astype(int)
        f1_transformed = f1_score(
            df_label[label_name],
            df_label[label_name + '_predictions'],
            average='macro')
        support = len(df_label)

        getNormConfMat(
            df_label,
            label_name,
            label_name + '_predictions',
            label_name,
            f1_transformed,
            output_plots,
            num_classes,
            support)
        df = df.replace(
            {label_name: map_1abels_to_0neTohree()})
        df = df.replace(
            {label_name + '_predictions': map_1abels_to_0neTohree()})
        f1 = f1_score(df[label_name],
                      df[label_name + '_predictions'], average='macro')
        getNormConfMat(df, label_name, label_name + '_predictions',
                       'labels_3_classes', f1, output_plots, 3, support)

        if roc is True:
            plot_roc_curve(df[label_name], df[label_name + '_confidences'],
                           output_plots, label_name, support)
    return None


def convertConfFloats(confidences):
    confidences_conv = []
    for conf in confidences:
        confidences_conv.append(float(conf.split(";1:")[-1][:-1]))
    return np.array(confidences_conv)


def plot_roc_curve(labels, confidences, output_plots, plot_name, support):
    labels = labels.to_numpy()
    confidences = convertConfFloats(confidences)
    fpr, tpr, thresholds = metrics.roc_curve(labels, confidences, pos_label=1)
    roc_auc = metrics.auc(fpr, tpr)
    plt.clf()
    plt.figure()
    plt.title('Receiver Operating Characteristic')
    plt.plot(fpr, tpr, 'b', lw=2, label='AUC = %0.2f' % roc_auc)
    plt.legend(loc='lower right')
    plt.plot([0, 1], [0, 1], 'r--')
    plt.xlim([0, 1.05])
    plt.ylim([0, 1.05])
    plt.ylabel('True Positive Rate (Sensitivity)')
    plt.xlabel('False Positive Rate (1 - Specificity)')
    plt.show()
    plt.savefig(os.path.join(output_plots, plot_name + '_roc.png'), dpi=100,
                bbox_inches='tight')
    plt.close()

    plt.clf()
    plt.figure()
    plt.title('Receiver Operating Characteristic, support(N):' + str(support))
    plt.plot(fpr, tpr, 'b', lw=2, label='AUC = %0.2f' % roc_auc)
    plt.legend(loc='lower right')
    plt.plot([0, 1], [0, 1], 'r--')
    plt.xlim([0, 1.05])
    plt.ylim([0, 1.05])
    plt.ylabel('True Positive Rate (Sensitivity)')
    plt.xlabel('False Positive Rate (1 - Specificity)')
    plt.show()
    plt.savefig(os.path.join(
        output_plots, plot_name + '_roc_support.png'), dpi=100,
                bbox_inches='tight')
    plt.close()

