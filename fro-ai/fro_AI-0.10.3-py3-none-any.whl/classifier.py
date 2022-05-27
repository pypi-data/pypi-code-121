import cv2
import numpy as np
import torch
import torch.nn as nn
from torchvision import models
import torchvision.transforms.functional as TF
import os

configs = {
    'ImageNet': {
        'mean': np.array([0.485, 0.456, 0.406]),
        'std': np.array([0.229, 0.224, 0.225]),
        'size': (224, 224)
    }
}


def _get_dataset_from_model_name(model):
    """
    获取模型训练所用的数据集

    Parameters
    ----------
    model: str
        model name format: <dataset_name>[_model_arch][_backend]
    """
    idx = model.find('_')
    if idx == -1:
        return model
    return model[:idx]


def _get_arch_from_model_name(model):
    """
    获取模型结构

    Parameters
    ----------
    model: str
        model name format: <dataset_name>[_model_arch][_backend]
    """
    idx = model.find('_')
    if idx == -1:
        return
    return model[idx + 1:]


class Classifier(object):
    """
    一个简单的物体分类模块

    Parameters
    ----------
    model: str
        物体分类模型名称
    weight_path: str 或 None
        模型权重文件路径。当不为None时，会从该路径载入模型参数。
    """
    def __init__(self, model='ImageNet', weight_path=None):
        super().__init__()
        self._device = torch.device(
            "cuda:0" if torch.cuda.is_available() else "cpu")
        self._class_name = None
        self._mean = 0.5
        self._std = 0
        self._size = (224, 224)
        if model is not None:
            self.load_model(model, weight_path)

    def _load_weights(self, weight_path):
        self._model.load_state_dict(
            torch.load(weight_path,
                       map_location=torch.device(
                           "cuda:0" if torch.cuda.is_available() else "cpu")))

    def _load_config(self, ds):
        if ds == 'ImageNet':
            self._mean = np.array([0.485, 0.456, 0.406])
            self._std = np.array([0.229, 0.224, 0.225])
            self._size = (224, 224)
            cur_dir = os.path.split(os.path.realpath(__file__))[0]
            label_path = os.path.join(cur_dir, 'data/imageNet_labels.txt')
            with open(label_path, 'r') as f:
                self._class_name = eval(f.read())

    def load_model(self, model, weight_path=None):
        """
        载入模型

        Parameters
        ----------
        model: str
            物体分类模型名称
        weight_path: str 或 None
            模型权重文件路径。当不为None时，会从该路径载入模型参数。
        """
        dataset = _get_dataset_from_model_name(model)
        if dataset == 'ImageNet':
            arch = _get_arch_from_model_name(model)
            if arch is not None:
                pt_string = '(pretrained=True)' if weight_path is None else '(pretrained=False)'
                load_string = 'models.' + arch + pt_string
                self._model = eval(load_string)
                if weight_path is not None:
                    self._load_weights(weight_path)
            else:
                self._model = models.resnet18(
                    pretrained=True if weight_path is None else False)
                if weight_path is not None:
                    self._load_weights(weight_path)
        else:
            raise RuntimeError(f'未知的模型：{model}')

        self._load_config(dataset)
        self._model = self._model.to(self._device)

    def _preprocess(self, bgr):
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        rgb = cv2.resize(rgb, self._size)
        tensor = TF.to_tensor(rgb)
        tensor = TF.normalize(tensor, self._mean, self._std)
        tensor = torch.unsqueeze(tensor, 0)
        return tensor

    def predict(self, input_data):
        """
        执行一次模型推理

        Parameters
        ----------
        input_data:
            BGR格式的图像

        Returns
        -------
        predictions: numpy.ndarray
            返回一个N个元素的数组，N是模型的分类数目，每个元素代表相应分类的可能性。
        """
        self._model.eval()
        tensor = self._preprocess(input_data)
        with torch.no_grad():
            tensor = tensor.to(self._device)
            output = self._model(tensor)
            return nn.functional.softmax(output, dim=1).cpu().numpy()[0]

    def show_readable_result(self, predictions, top_k=1):
        """
        根据模型的推理结果，以一种易于理解的方式将结果打印出来

        Parameters
        ----------
        predictions: numpy.ndarray
            :py:meth:`predict` 方法返回的结果
        top_k: int, optional
            打印可能性最高的 `top_k` 个分类
        """
        idx_score_pairs = self.get_top_k(predictions, top_k)
        print('该物体')
        for t in idx_score_pairs:
            print(f"有{t[1]*100:.1f}%的可能是'{self._class_name[t[0]]}'")

    def get_top_k(self, predictions, top_k=1):
        """
        根据模型的推理结果，返回分数最高的 `top_k` 个结果

        Parameters
        ----------
        predictions: numpy.ndarray
            :py:meth:`predict` 方法返回的结果
        top_k: int, optional
            该数值决定返回的元组个数

        Returns
        -------
        list(tuple)
            每个元组都是一个“索引-分数”对，元组内的“分数”就是 `predictions` 中
            成绩最高的 `top_k` 个之一，而“索引”就是该“分数”在 `predictions` 的索引号。
        """
        if top_k > len(predictions):
            top_k = len(predictions)
        top_k_idx = np.argpartition(predictions, -top_k)[-top_k:]
        scores = [predictions[i] for i in top_k_idx]
        return list(zip(list(top_k_idx), scores))

    def get_class_name(self, idx):
        """
        根据索引号，返回分类名称

        Parameters
        ----------
        idx: int
            索引号

        Returns
        -------
        str
            分类名称
        """
        return self._class_name[idx]
