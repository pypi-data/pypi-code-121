from ast import Assert
from math import log, sqrt
import torch
import numpy as np
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
import matplotlib.pyplot as plt
from torchmetrics.functional import dice_score

from typing import Union, List, Dict, Any, Optional

def column_or_1d(y):
    y = torch.as_tensor(y)
    shape = y.shape
    if (len(shape) == 1) or (len(shape) == 2 and shape[1] == 1):
        return torch.ravel(y)
    
    raise ValueError("y should be a 1d tensor, got a tensor of shape {} instead.".format(shape))
class BCELossAccuracy():
    def __init__(self):
        self.loss_function = nn.BCELoss()
    
    @staticmethod
    def accuracy(y_hat, labels):
        with torch.no_grad():
            y_tilde = (y_hat > 0.5).int()
            accuracy = (y_tilde == labels.int()).float().mean().item()
        return accuracy
    
    def __call__(
        self, 
        y_hat : "torch.Tensor", 
        labels : "torch.Tensor"
    ):
        
        loss = self.loss_function(y_hat, labels.reshape(-1).long()).squeeze()
        accuracy = self.accuracy(y_hat, labels)
        return loss, accuracy
class CELossAccuracy():
    def __init__(self):
        self.loss_function = nn.CrossEntropyLoss()
    
    @staticmethod
    def accuracy(y_hat, labels):
        with torch.no_grad():
            y_tilde = y_hat.argmax(axis=1)
            accuracy = (y_tilde == labels).float().mean().item()
        return accuracy
    
    def __call__(
        self, 
        y_hat, 
        labels : "torch.Tensor"
    ):
        
        loss = self.loss_function(y_hat, labels.reshape(-1).long()).squeeze()
        accuracy = self.accuracy(y_hat, labels)
        return loss, accuracy

class MSELoss():
    def __init__(self):
        pass
    def __call__(
        self,
        y_hat : "torch.Tensor", 
        labels : "torch.Tensor"
    ):
        criterion = nn.MSELoss()
        loss = criterion(y_hat, labels.reshape(-1)).squeeze()
        return loss
class RMSELoss():
    def __init__(self):
        pass

    def __call__(
        self,
        y_hat : "torch.Tensor", 
        labels : "torch.Tensor"
    ):        
        criterion = nn.MSELoss()
        loss = torch.sqrt(criterion(y_hat, labels.reshape(-1))).squeeze()
        return loss

class R2Score():
    def __init__(self):
        pass
    def __call__(
        self, 
        y_hat, 
        labels : "torch.Tensor", 
        sample_weight : Optional["torch.Tensor"] = None,
        multioutput : Union[str, "torch.Tensor"] = "uniform_average"
    ):
        if len(y_hat) < 2:
            raise ValueError("R^2 score is not well-defined with less than 2 samples.")
        if sample_weight is not None:
            sample_weight = column_or_1d(sample_weight).type_as(labels)
            weight = torch.unsqueeze(sample_weight, dim=1).type_as(labels)
        else:
            weight = torch.ones_like(labels).unsqueeze(dim=1).type_as(labels)

        numerator = torch.sum(weight * (labels - y_hat)**2, dim=0).float()
        weighted_sum = (weight * labels.unsqueeze(dim=1)).squeeze()
        denominator = weight * torch.sum(labels - torch.mean(weighted_sum, dim=0)**2, dim=0).float()
        
        nonzero_denominator = denominator != 0
        nonzero_numerator = numerator != 0
        valid_score = nonzero_denominator & nonzero_numerator
        output_scores = torch.ones(size=labels.shape[1])
        output_scores[valid_score] = 1 - (numerator[valid_score]/denominator[valid_score])
        # arbitrary set to zero to avoid -inf scores, having a constant
        # labels are not interesting for scoring a regression anyway
        output_scores[nonzero_numerator & ~nonzero_denominator] = 0.0
        if isinstance(multioutput, str):
            if multioutput == "raw_values":
                # return scores individually
                return output_scores
            elif multioutput == "uniform_average":
                # passing None as weights results is uniform mean
                avg_weights = None
            elif multioutput == "variance_weighted":
                avg_weights = denominator.type_as(weight)
                # avoid fail on constant y or one-element arrays
                if not np.any(nonzero_denominator):
                    if not np.any(nonzero_numerator):
                        return torch.ones_like(labels).type_as(labels)
                    else:
                        return torch.zeros_like(labels).type_as(labels)
        else:
            avg_weights = multioutput

        output_weighted_sum = avg_weights * output_scores
        loss = torch.mean(output_weighted_sum)
        return loss


class CEDiceLossAccuracy():
    def __init__(self, n_classes):
        self.loss_function = nn.CrossEntropyLoss()
        self.n_classes = n_classes
    @staticmethod
    def accuracy(y_hat, labels):
        with torch.no_grad():
            y_tilde = y_hat.argmax(axis=1)
            accuracy = (y_tilde == labels).float().mean().item()
        return accuracy

    def __call__(
        self, 
        y_hat, 
        labels : "torch.Tensor"
    ):
        
        loss = self.loss_function(y_hat, labels.reshape(-1)).squeeze()
        """
        loss += dice_loss(
                    F.softmax(y_hat, dim=1).float(),
                    F.one_hot(labels, self.n_classes).permute(0,3,1,2).float(),
                    multiclass=True
                )
        
        """
        loss += dice_score(F.softmax(y_hat, dim=1).float(), labels.reshape(-1)).squeeze()
        accuracy = self.accuracy(y_hat, labels)
        return loss, accuracy



def dice_coeff(
    input: Tensor,
    target: Tensor,
    reduce_batch_first: bool = False, epsilon=1e-6
):
    # Average of Dice coefficient for all batches, or for a single mask
    if (input.size() == target.size()):
        raise AssertionError("Size mismatch between input and target.")
    if (input.dim() == 2 and reduce_batch_first):
        raise ValueError(f'Dice: asked to reduce batch but got tensor without batch dimension (shape {input.shape})')

    if input.dim() == 2 or reduce_batch_first:
        inter = torch.dot(input.reshape(-1), target.reshape(-1))
        sets_sum = torch.sum(input) + torch.sum(target)

        if sets_sum.item() == 0:
            sets_sum = 2 * inter

        return (2 * inter + epsilon) / (sets_sum + epsilon)

    else:
        # compute and average metric for each batch element
        dice = 0
        for i in range(input.shape[0]):
            dice += dice_coeff(input[i, ...], target[i, ...])

        return dice / input.shape[0]


def multiclass_dice_coeff(
    input: Tensor, 
    target: Tensor, 
    reduce_batch_first: bool = False, 
    epsilon=1e-6
):
    # Average of Dice coefficient for all classes
    if (input.size() == target.size()):
        raise AssertionError("Size mismatch between input and target.")
    dice = 0
    for channel in range(input.shape[1]):
        dice += dice_coeff(input[:, channel, ...], target[:, channel, ...], reduce_batch_first, epsilon)

    return dice / input.shape[1]


def dice_loss(
    input: Tensor, 
    target: Tensor, 
    multiclass: bool = False
):
    # Dice loss (objective to minimize) between 0 and 1
    if (input.size() == target.size()):
        raise AssertionError("Size mismatch between input and target.")
    fn = multiclass_dice_coeff if multiclass else dice_coeff

    return 1 - fn(input, target, reduce_batch_first=True)
    


def plot_img_and_mask(img, mask):
    classes = mask.shape[0] if len(mask.shape) > 2 else 1
    fig, ax = plt.subplots(1, classes + 1)
    ax[0].set_title('Input image')
    ax[0].imshow(img)
    if classes > 1:
        for i in range(classes):
            ax[i + 1].set_title(f'Output mask (class {i + 1})')
            ax[i + 1].imshow(mask[1, :, :])
    else:
        ax[1].set_title(f'Output mask')
        ax[1].imshow(mask)
    plt.xticks([]), plt.yticks([])
    plt.show()


# for binary_tree.py
def unique_counts(labels):
    results = {}
    for label in labels:
        value = label.item()
        if value not in results.keys():
            results.update({value : 0})
        
        results[value] += 1
    
    return results

def log2(x):
    return log(x) / log(2)
    
# H(labels) with base 2
def entropy(labels):
    results = unique_counts(labels)
    ent = 0.0
    for r in results.keys():
        p = float(results[r]) / len(labels)
        ent = ent - p * log2(p)
    return ent

def split_function(vector, column, value):
    """
    Split function
    """
    return vector[column] >= value


def divide_set(X, y, column, value):
    """
    Divide the sets into two different sets along a specific dimension and value.
    """
    set_1 = [(vector, label) for vector, label in zip(X, y) if split_function(vector, column, value)]
    set_2 = [(vector, label) for vector, label in zip(X, y) if not split_function(vector, column, value)]

    X_set_1 = [element[0] for element in set_1]
    X_set_2 = [element[0] for element in set_2]
    y_set_1 = [element[1] for element in set_1]
    y_set_2 = [element[1] for element in set_2]

    return X_set_1, y_set_1, X_set_2, y_set_2
