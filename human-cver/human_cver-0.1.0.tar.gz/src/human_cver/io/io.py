import json
import cv2
import pickle
import yaml
import scipy.io as scio
import numpy as np
import os
import os.path as osp


def load_json(filename):
    with open(filename, "r") as fr:
        data = json.load(fr)
    return data


def load_img(filename):
    return cv2.imread(filename)


def load_pkl(filename):
    return pickle.load(open(filename, "rb"), encoding="latin1")


def load_yaml(filename):
    return yaml.load(open(filename, "r"))


def load_ply(filename):
    return o3d.io.read_triangle_mesh(filename)


def load_mat(filename):
    return scio.loadmat(filename)


def load_npz(filename):
    """print(data.files)"""
    return np.load(filename, allow_pickle=True)


def load_txt(filename):
    with open(filename, "r") as fr:
        lines = fr.readlines()
    return lines


def load_obj(obj_filename):
    v_list = []
    f_list = []

    with open(obj_filename, "r") as fr:
        for line in fr.readlines():
            segs = line.split(" ")
            if segs[0] == "v":
                x = float(segs[1])
                y = float(segs[2])
                z = float(segs[3])
                v_list.append([x, y, z])

            elif segs[0] == "f":
                a = int(segs[1])
                b = int(segs[2])
                c = int(segs[3])
                f_list.append([a, b, c])
    vertices = np.array(v_list, dtype=np.float)
    faces = np.array(f_list, dtype=np.int)

    if np.min(faces) == 1:
        faces -= 1
    print("face index start from:", np.min(faces))
    return vertices, faces


def load_file(filename):
    """supported filetype:
    @txt, json, pkl, yaml, ply, mat, npz
    @jpg, jpeg, png
    """
    if filename.endswith(".txt"):
        return load_txt(filename)

    if filename.endswith(".json"):
        return load_json(filename)

    if filename.endswith(".jpg"):
        return load_img(filename)
    if filename.endswith(".jpeg"):
        return load_img(filename)
    if filename.endswith(".png"):
        return load_img(filename)

    if filename.endswith(".pkl"):
        return load_pkl(filename)

    if filename.endswith(".yaml"):
        return load_yaml(filename)

    if filename.endswith(".ply"):
        return load_ply(filename)

    if filename.endswith(".mat"):
        return load_mat(filename)

    # print(data.files)
    if filename.endswith(".npz"):
        return load_npz(filename)

    assert "Wrong file type" and False
    return None


def save_file(filename, data):
    """.json .yaml .mat"""
    file_type = filename.split(".")[-1]

    if file_type == "mat":
        scio.savemat(filename, data)

    elif file_type == "json":
        save_json(filename, data)

    elif file_type == "yaml":
        save_yaml(filename, data)

    else:
        print("file_type", file_type)
        assert False


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as fw:
        json.dump(data, fw, ensure_ascii=False, indent=4)


def save_yaml(filename, data):
    with open(filename, "w", encoding="utf-8") as fw:
        yaml.dump(data, fw)


def mkdir(path: str) -> None:
    if not osp.exists(path):
        os.makedirs(path, exist_ok=True)
