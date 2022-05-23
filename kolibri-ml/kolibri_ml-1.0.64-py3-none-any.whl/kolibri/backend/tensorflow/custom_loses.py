import numpy as np
import tensorflow as tf
from scipy.sparse import coo_matrix
from tensorflow.keras import backend as K


def confusion_matrix(y_true, y_pred, sample_weight=None):
    y_pred = np.array(y_pred)
    y_true = np.array(y_true)
    labels = np.unique(np.hstack([y_true, y_pred]))
    n_labels = len(labels)

    if sample_weight is None:
        sample_weight = np.ones(y_true.shape[0], dtype=np.int64)
    else:
        sample_weight = np.asarray(sample_weight)

    #    n_labels = y_values.size
    #    label_to_ind = {y: x for x, y in enumerate(y_values)}
    # convert yt, yp into index
    #    y_pred = np.array([label_to_ind.get(x, n_labels + 1) for x in y_pred])
    #    y_true = np.array([label_to_ind.get(x, n_labels + 1) for x in y_true])

    # intersect y_pred, y_true with y_values, eliminate items not in y_values
    #    ind = np.logical_and(y_pred < n_labels, y_true < n_labels)
    #    y_pred = y_pred[ind]
    #    y_true = y_true[ind]
    # also eliminate weights of eliminated items
    #    sample_weight = sample_weight[ind]

    # Choose the accumulator dtype to always have high precision

    cm = coo_matrix((sample_weight, (y_true, y_pred)),
                    shape=(n_labels, n_labels),
                    ).toarray()

    cm = np.nan_to_num(cm)

    return cm


def mean_false_error(y_true, y_pred):
    diff = 0.5 * (K.square(y_true - y_pred))
    segments = K.argmax(y_true)

    return K.sum(K.square(tf.math.unsorted_segment_mean(
        diff, segments, num_segments=K.max(segments) + 1
    )), axis=0)


def mean_false_error_2(y_true, y_pred):
    neg_y_true = 1 - y_true
    neg_y_pred = 1 - y_pred

    FN = K.sum(y_true * neg_y_pred, axis=0)
    FP = K.sum(neg_y_true * y_pred, axis=0)
    TP = K.sum(y_true * y_pred, axis=0)
    TN = K.sum(neg_y_true * neg_y_pred, axis=0)

    fpe = FP / (TP + FP)
    fne = FN / (TN + FN)
    score = fne * fne + fpe * fpe
    score = tf.where(tf.math.is_nan(score), tf.ones_like(score) * 0, score)
    return score


def mean_squared_false_error(y_true, y_preficted):
    m = confusion_matrix(y_true, y_preficted)
    class_counts = m.sum(axis=1)
    FP = m.sum(axis=0) - np.diag(m)
    FN = m.sum(axis=1) - np.diag(m)

    fpe = np.mean(FP / class_counts)
    fne = np.mean(FN / class_counts)
    return (fpe * fpe) + (fne * fne)


def mean_false_error2(y_true, y_pred):
    diff = 0.5 * (K.square(y_true - y_pred))
    segments = K.argmax(y_true)

    return K.sum(tf.math.unsorted_segment_mean(
        diff, segments, num_segments=K.max(segments) + 1
    ), axis=0)


if __name__ == '__main__':
    y_true = K.variable([[0, 0, 1], [1, 0, 0], [0, 0, 1], [0, 0, 1], [1, 0, 0], [0, 1, 0]])
    y_pred = K.variable([[1, 0, 0], [1, 0, 0], [0, 0, 1], [0, 0, 1], [1, 0, 0], [0, 0, 1]])
    print(K.eval(mean_false_error2(y_true, y_pred)))
#  y_true = np.array([1,0, 1, 1,0 ,0])
#  y_pred = np.array([0,0, 1,1,0, 1])
# #
#  print(mean_false_error(y_true, y_pred))
#
