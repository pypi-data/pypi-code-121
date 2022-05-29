"""
Loader functions for the datasets. You can add yours to here.

The function requires 2 inputs:
- name: Name of dataset as the name of the file without suffix
- path: Path to where the file is located

The functions return 2 outputs:
- dict_snapshots: Dictionary of snapshots, where keys are time stamps and values are list of edges occurring at this
                    time.
- dict_weights: Dictionary of weights according to dict_snapshots - keys are the time stamps and values are list of
                weight edges corresponding to the order of edges in dict_snapshots.

Note that if you change the name of the function "data_loader", you have to change it as well in the file "main.py" in
in line 51.
"""

from datetime import datetime
import os
import numpy as np


def data_loader(name, path):
    """
    Data loader for all datasets used.
    :param name: Name of the file (str, without .txt)
    :param path: Path to where it is
    :return:
    """
    if name == "dblp":
        dict_snapshots, dict_weights = load_dblp(name, path)
    else:
        dict_snapshots, dict_weights, times = {}, {}, []
        with open(os.path.join(path, name + ".txt"), 'r') as filehandle:
            for line in filehandle:
                a = line.split(" ")
                if len(a) == 1:
                    a = line.split(",")
                if "%" in a[0]:
                    continue
                else:
                    node1 = a[0]
                    node2 = a[1]
                    if node1 == node2:
                        continue
                    try:
                        w = float(a[2])
                        t = a[3].split("\n")[0]
                    except:
                        w = 1.
                        t = a[2].split("\n")[0]
                    if t == '0':
                        date = int(t)
                    else:
                        x = datetime.fromtimestamp(int(t))
                        times.append(x)
                        month = x.month
                        year = x.year
                        date = "{}.{}".format(month, year)
                    if dict_snapshots.get(date) is None:
                        dict_snapshots.update({date: [(node1, node2)]})
                    else:
                        dict_snapshots[date].append((node1, node2))
                    if dict_weights.get(date) is None:
                        dict_weights.update({date: [w]})
                    else:
                        dict_weights[date].append(w)
        times.sort()
        sorted_times = sort_keys(times)
        dict_snapshots = sort_dict_snapshots(dict_snapshots, sorted_times)
        if name == "facebook-wosn-wall":
            del dict_snapshots["10.2004"]
            del dict_snapshots["11.2004"]
            del dict_snapshots["12.2004"]
    return dict_snapshots, dict_weights


def load_dblp(name, path, is_weighted=False):
    """
    DBLP dataset
    """
    dict_snapshots = {}
    with open(os.path.join(path, name + ".txt"), 'r') as filehandle:
        for line in filehandle:
            a = line.split(" ")
            node1 = a[0]
            node2 = a[1]
            if is_weighted:
                w = float(a[2])
                t = a[3].split("\n")[0]
            else:
                w = 1.
                t = a[2].split("\n")[0]
            if dict_snapshots.get(t) is None:
                dict_snapshots.update({t: [(node1, node2, w)]})
            else:
                dict_snapshots[t].append((node1, node2, w))
    sorted_dict = dict(sorted(dict_snapshots.items(), key=lambda kv: kv[0]))
    keys = sorted_dict.keys()
    dict_weights = {key: [] for key in keys}
    new_dict = {key: [] for key in keys}
    for key in keys:
        for edge in sorted_dict[key]:
            dict_weights[key].append(edge[2])
            new_dict[key].append((edge[0], edge[1]))
    return new_dict, dict_weights


def sort_keys(times):
    """
    Function to sort the times
    """
    sorted_times = []
    for t in times:
        year = t.year
        month = t.month
        date = "{}.{}".format(month, year)
        if date in sorted_times:
            continue
        else:
            sorted_times.append(date)
    return sorted_times


def sort_dict_snapshots(dict_snapshots, times):
    """
    Sort dictionary of snapshots by time
    :param dict_snapshots:
    :param times:
    :return:
    """
    new_dict = {t: dict_snapshots[t] for t in times}
    return new_dict


def load_embedding(path, file_name):
    """
    Given a .npy file - embedding of a given graph. return the embedding dictionary
    :param path: Where this file is saved.
    :param file_name: The name of the file
    :return: Embedding dictionary
    """
    data = np.load(os.path.join(path, '{}.npy'.format(file_name)), allow_pickle=True)
    dict_embedding = data.item()
    return dict_embedding
