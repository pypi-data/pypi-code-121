from .helper_func import flatten, find


def parse_file_name(file, dataset):
    flatten_file_name = list(flatten([i.split(".") for i in file.split("_")]))
    idx_dataset_name = find(flatten_file_name, dataset)[0]
    sample = flatten_file_name[idx_dataset_name + 1: -1][-1]
    version = flatten_file_name[idx_dataset_name + 1: -1][-2]
    transformation = "_".join(flatten_file_name[idx_dataset_name + 1: -1][:-2])
    return sample, version, transformation
