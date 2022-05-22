import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix


def show_evaluation_report(y_true: np.ndarray, y_pred: np.ndarray) -> None:
    """sklearn.metrics.classification_reportと混合行列を表示する。

    Parameters
    ----------
    y_true : np.ndarray
        正解ラベル
    y_pred : np.ndarray
        予測ラベル
    """
    print(classification_report(y_true, y_pred, zero_division=0))

    show_ratio_confusion_matrix(y_true, y_pred)


def show_ratio_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray) -> None:
    """混合行列を表示する。

    Parameters
    ----------
    y_true : np.ndarray
        正解ラベル
    y_pred : np.ndarray
        予測ラベル
    """
    labels, counts = np.unique(y_true, return_counts=True)
    counts = counts.reshape(-1, 1)
    ratio_confusion_matrix = confusion_matrix(y_true, y_pred, labels=labels) / counts
    confusion_matrix_df = pd.DataFrame(
        ratio_confusion_matrix, index=labels, columns=labels
    )

    label_num = np.unique(y_true).size
    fig = plt.figure(figsize=(label_num * 0.7, label_num * 0.5))
    ax = fig.add_subplot(1, 1, 1)
    sns.heatmap(confusion_matrix_df, annot=True, fmt=".2f", vmin=0.0, vmax=1.0, ax=ax)
    plt.show()
