from typing import Union, List, Dict, Any, Optional, cast



def val_metric_check(applicable_val_metric_list, val_metric):
    if val_metric not in applicable_val_metric_list:
        raise ValueError("Invalid validation metric. It should be one of " + str([item for item in applicable_val_metric_list]))

def X_y_check(X, y):
    if X.shape[0] != y.shape[0]:
        raise ValueError("Mistmatch between the dimensions of training data and labels.")

def optimizer_type_check(applicable_optimizer_type_list, optimizer_type):
    if optimizer_type not in applicable_optimizer_type_list:
        raise ValueError("Invalid optimizer type. It should be one of " + str([item for item in applicable_optimizer_type_list]))

def sanity_check(
    applicable_val_metric_list : List[str],
    applicable_optimizer_type_list : List[str],
    kwargs : dict
):
    """
    kwargs dictionary of : {
                            "val_metric" : val_metric
                            "X" : X,
                            "y" : y,
                            "optimizer_type" : optimizer_type
                            } 
    """

    
    if "val_metric" in kwargs:
        val_metric_check(applicable_val_metric_list, kwargs["val_metric"])
    if "X" in kwargs:
        if "y" in kwargs:
            X_y_check(kwargs["X"], kwargs["y"])
        else:
            raise AssertionError('Keyword "X" should be with "y"')
    if "optimizer_type" in kwargs:
        optimizer_type_check(applicable_optimizer_type_list, kwargs["optimizer_type"])
