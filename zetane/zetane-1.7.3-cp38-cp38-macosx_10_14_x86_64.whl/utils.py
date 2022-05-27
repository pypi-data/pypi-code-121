

def get_binary():
    """ Return path to the Zetane Binaries. """
    return None


def get_project_root():
    """Return project root folder."""
    return None


def confusion_matrix(label, pred, nc=None):
    """Generates a confusion matrix for given predictions and target labels.

    :param label: Array of target classes
    :type label: np.ndarray

    :param pred: Array of predicted classes,
    :type pred: np.ndarray

    :param nc: Number of classes, inferred automatically if not specified
    :type nc: int

    :return: A confusion matrix as a [nc, nc] NumPy array.
    :rtype: np.ndarray
    """
    return None


def precision_score(label, pred, nc=None):
    """Calculates precision for given predictions and target labels.
    Precision is defined as sum(true_positives)/sum(all_pred_positives).

    :param label: Array of target classes
    :type label: np.ndarray

    :param pred: Array of predicted classes,
    :type pred: np.ndarray

    :param nc: Number of classes, inferred automatically if not specified
    :type nc: int

    :return: A confusion matrix as a [nc, nc] NumPy array.
    :rtype: np.ndarray
    """
    return None


def recall_score(label, pred, nc = None):
    """Calculates recall for given predictions and target labels.
    Recall is defined as sum(true_positives)/sum(all_label_positives).

    :param label: Array of target classes
    :type label: np.ndarray

    :param pred: Array of predicted classes,
    :type pred: np.ndarray

    :param nc: Number of classes, inferred automatically if not specified
    :type nc: int

    :return: A confusion matrix as a [nc, nc] NumPy array.
    :rtype: np.ndarray
    """
    return None


def plot_confusion_matrix(conf_mat, classes, normalize=False, title='Confusion matrix', cmap=None):
    """Plots a confusion matrix.

    :param conf_mat: Confusion matrix as an ndarray object
    :type conf_mat: np.ndarray

    :param classes: List of class labels
    :type classes: list<str>

    :param normalize: Whether to normalize matrix values, defaults to False
    :type normalize: bool, optional

    :param title: Title of the confusion matrix, defaults to 'Confusion matrix'
    :type title: str, optional

    :param cmap: Matplotlib color mapping, defaults to plt.cm.Blues
    :type cmap: plt.cm.cmap, optional

    :return: None, plots a Matplotlib graph
    :rtype: None
    """
    return None


def f1_score(label, pred, nc=None):
    return None


def grid_placement(list_of_zobjs, max_number_of_columns = 3, flip_y_order = False, padding = 1.0, origin = (0.0, 0.0, 0.0)):
    return None


def remap(in_values, in_range=None, out_range=[0.0, 1.0], clamp=False):
    """ Read values of a given numpy array, returning a numerically remapped copy

    :param in_values: input numpy array
    :type label: np.ndarray

    :param in_range: if not provided, assumes range is in_value [min,max]
    :type label: tuple

    :param out_range: target range of values
    :type label: tuple

    :param clamp: in_values outside of in_range are clamped
    :type label: bool

    :return: remapped copy of in_values
    :rtype: np.ndarray
    """
    return None


def wait_until(predicate_fn, timeout):
    """
        Poll the predicate until it becomes True. Non-busy wait; sleeps the
        thread between polls.

    Args:
        predicate_fn (function): a function that returns a Boolean.
        timeout (float): period in seconds to wait for the predicate to be met.

    Returns:
        True when the predicate is met; or False on timeout.
    """
    return None
