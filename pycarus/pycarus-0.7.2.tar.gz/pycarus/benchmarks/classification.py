from ast import literal_eval
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

import numpy as np
from sklearn.metrics import confusion_matrix  # type: ignore

from pycarus.utils import get_conf_matrix_img


def _get_conf_mat_from_file(pred_file: Path) -> np.ndarray:
    """Compute confusion matrix from a prediction file.

    Args:
        pred_file: The path to the prediction file.

    Returns:
        The confusion matrix.
    """
    with open(pred_file) as f:
        items = [line.strip().split(";") for line in f.readlines()]

    labels = np.array([float(item[0]) for item in items])
    logits = np.array([literal_eval(item[1]) for item in items])
    predictions = np.argmax(logits, axis=1)

    return confusion_matrix(y_true=labels, y_pred=predictions)


def classification_evaluation(classes: List[str], pred_files: List[Path], outdir: Path) -> None:
    """Evaluation for a generic classification task.

    This function aggregates results reported in prediction files to compute:
    - class accuracies (mean and std)
    - mean class accuracy (mean and std)
    - overall accuracy (mean and std)
    - confusion matrix (mean)

    Each prediction file is expected to be produced by a different run
    and should be a txt file with one line for each prediction,
    formatted as "LABEL;LOGITS", where LABEL is a single integer and
    LOGITS is the comma separated sequence of predictions logits (floats),
    with "[" as first character and "]" as last character.
    For instance, a row could be something like:
        10;[0.1, 1.23, ..., 0.001]

    The results of the evaluation are saved in "outdir".
    In particular, the following elements will be saved:
    - results.csv, with class accuracies, mean class accuracy and overall accuracy
    - conf_matrix.png, with the confusion matrix

    Args:
        classes: A list with all the classes. The order in the list is assumed to
                 to be coherent with the labels reported in "predictions_file".
        pred_files: The list of file with all the predictions.
        outdir: The path to the directory where results will be saved.
    """
    outdir.mkdir(parents=True, exist_ok=True)

    conf_mats = [_get_conf_mat_from_file(pred_file) for pred_file in pred_files]

    num_samples: List[int] = []
    mean_accs: List[float] = []
    class_accs: Dict[int, List[float]] = defaultdict(list)
    for conf_mat in conf_mats:
        num_samples = np.sum(conf_mat, axis=1).tolist()
        class_acc = np.diag(conf_mat) / np.sum(conf_mat, axis=1)
        mean_accs.append(float(np.nanmean(class_acc)))

        for c in range(len(classes)):
            class_accs[c].append(float(class_acc[c]))

    results_file = outdir / "results.csv"

    with open(results_file, "wt") as f:
        f.write("Class,ID,# Samples,Accuracy,std\n")
        for c, class_name in enumerate(classes):
            accs = class_accs[c]
            if len(accs) > 1:
                mean = np.mean(np.array(accs))
                std = np.std(np.array(accs))
                f.write(f"{class_name},{c},{num_samples[c]},{mean * 100:.3f},{std * 100:.3f}\n")
            else:
                f.write(f"{class_name},{c},{num_samples[c]},{accs[0] * 100:.3f},-\n")

        f.write("\n")

        if len(mean_accs) > 1:
            mean = np.mean(np.array(mean_accs))
            std = np.std(np.array(mean_accs))
            f.write(f",,Mean,{mean * 100:.3f},{std * 100:.3f}\n")
        else:
            f.write(f",,Mean,{mean_accs[0] * 100:.3f},-\n")

        f.write("\n")

        overall_accs = [float(np.sum(np.diag(m)) / np.sum(m)) for m in conf_mats]

        if len(mean_accs) > 1:
            mean = np.mean(np.array(overall_accs))
            std = np.std(np.array(overall_accs))
            f.write(f",,Overall,{mean * 100:.3f},{std * 100:.3f}\n")
        else:
            f.write(f",,Overall,{overall_accs[0] * 100:.3f},-\n")

    conf_mat_img = get_conf_matrix_img(conf_mats[0])
    conf_mat_img.save(outdir / "conf_matrix.png")
