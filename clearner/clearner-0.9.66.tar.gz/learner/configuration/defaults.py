# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential


DEFINITIONS = {
        #############################################################################################################
        #                                                LAYER SECTION                                              #
        #############################################################################################################
        "Linear": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type", "out_features"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["Linear"]
                },
                "out_features": {
                    "type": "integer"
                },
                "bias": {
                    "type": "boolean",
                    "default": True
                }
            }
        },
        "ReLU": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["ReLU"]
                }
            }
        },
        "Dropout": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["Dropout"]
                },
                "p": {
                    "type": "number",
                    "default": 0.5
                }
            }
        },
        "LogSoftmax": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["LogSoftmax"]
                },
                "dim": {
                    "type": ["integer", "null"],
                    "default": 1
                }
            }
        },
        "Softmax": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["Softmax"]
                },
                "dim": {
                    "type": ["integer", "null"],
                    "default": 1
                }
            }
        },
        "Conv2d": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type", "out_channels", "kernel_size"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["Conv2d"]
                },
                "out_channels": {
                    "type": "integer"
                },
                "kernel_size": {
                    "type": "integer"
                },
                "stride": {
                    "type": "integer",
                    "default": 1
                },
                "padding": {
                    "type": "integer",
                    "default": 0
                },
                "dilation": {
                    "type": "integer",
                    "default": 1
                },
                "groups": {
                    "type": "integer",
                    "default": 1
                },
                "bias": {
                    "type": "boolean",
                    "default": True
                },
                "padding_mode": {
                    "type": "string",
                    "default": "zeros"
                },
            }
        },
        "MaxPool2d": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type", "kernel_size"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["MaxPool2d"]
                },
                "kernel_size": {
                    "type": "integer"
                },
                "stride": {
                    "type": ["integer", "null"],
                    "default": None
                },
                "padding": {
                    "type": "integer",
                    "default": 0
                },
                "dilation": {
                    "type": "integer",
                    "default": 0
                },
                "ceil_mode": {
                    "type": "boolean",
                    "default": False
                }
            }
        },
        "BatchNorm1d": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["BatchNorm1d"]
                },
                "eps": {
                    "type": ["number", "null"],
                    "default": 1e-5
                },
                "momentum": {
                    "type": "number",
                    "default": 0.1
                },
                "affine": {
                    "type": "boolean",
                    "default": True
                },
                "track_running_stats": {
                    "type": ["boolean", "null"],
                    "default": True
                }
            }
        },
        #############################################################################################################
        #                                            OPTIMIZER SECTION                                              #
        #############################################################################################################
        "Adam": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["Adam"]
                },
                "lr": {
                    "type": "number",
                    "default": 0.001
                },
                "betas": {
                    "type": "array",
                    "default": [0.9, 0.999]
                },
                "eps": {
                    "type": "number",
                    "default": 1e-8
                },
                "weight_decay": {
                    "type": "number",
                    "default": 0
                },
                "amsgrad": {
                    "type": "boolean",
                    "default": False
                }
            }
        },
        "AdamW": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["AdamW"]
                },
                "lr": {
                    "type": "number",
                    "default": 0.001
                },
                "betas": {
                    "type": "array",
                    "default": [0.9, 0.999]
                },
                "eps": {
                    "type": "number",
                    "default": 1e-8
                },
                "weight_decay": {
                    "type": "number",
                    "default": 0.01
                },
                "amsgrad": {
                    "type": "boolean",
                    "default": False
                }
            }
        },
        "SparseAdam": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["SparseAdam"]
                },
                "lr": {
                    "type": "number",
                    "default": 0.001
                },
                "betas": {
                    "type": "array",
                    "default": [0.9, 0.999]
                },
                "eps": {
                    "type": "number",
                    "default": 1e-8
                }
            }
        },
        "Adamax": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["Adamax"]
                },
                "lr": {
                    "type": "number",
                    "default": 0.002
                },
                "betas": {
                    "type": "array",
                    "default": [0.9, 0.999]
                },
                "eps": {
                    "type": "number",
                    "default": 1e-8
                },
                "weight_decay": {
                    "type": "number",
                    "default": 0
                }
            }
        },
        "ASGD": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["ASGD"]
                },
                "lr": {
                    "type": "number",
                    "default": 0.01
                },
                "lambd": {
                    "type": "number",
                    "default": 0.0001
                },
                "alpha": {
                    "type": "number",
                    "default": 0.75
                },
                "t0": {
                    "type": "number",
                    "default": 1000000.0
                },
                "weight_decay": {
                    "type": "number",
                    "default": 0
                }
            }
        },
        "LBFGS": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["LBFGS"]
                },
                "lr": {
                    "type": "number",
                    "default": 1
                },
                "max_iter": {
                    "type": "integer",
                    "default": 20
                },
                "max_eval": {
                    "type": "integer",
                    "default": 25
                },
                "tolerance_grad": {
                    "type": "number",
                    "default": 1e-05
                },
                "tolerance_change": {
                    "type": "number",
                    "default": 1e-09
                },
                "history_size": {
                    "type": "integer",
                    "default": 100
                },
                "line_search_fn": {
                    "type": ["string", "null"],
                    "default": None
                },
            }
        },
        "RMSprop": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["RMSprop"]
                },
                "lr": {
                    "type": "number",
                    "default": 0.01
                },
                "alpha": {
                    "type": "number",
                    "default": 0.99
                },
                "eps": {
                    "type": "number",
                    "default": 1e-08
                },
                "weight_decay": {
                    "type": "number",
                    "default": 0
                },
                "momentum": {
                    "type": "number",
                    "default": 0
                },
                "centered": {
                    "type": "boolean",
                    "default": False
                }
            }
        },
        "Rprop": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["Rprop"]
                },
                "lr": {
                    "type": "number",
                    "default": 0.01
                },
                "etas": {
                    "type": "array",
                    "default": [0.5, 1.2]
                },
                "step_sizes": {
                    "type": "array",
                    "default": [1e-06, 50]
                }
            }
        },
        "SGD": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type", "lr"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["SGD"]
                },
                "lr": {
                    "type": "number",
                    "default": 0.01
                },
                "momentum": {
                    "type": "number",
                    "default": 0
                },
                "dampening": {
                    "type": "number",
                    "default": 0
                },
                "weight_decay": {
                    "type": "number",
                    "default": 0
                },
                "nesterov": {
                    "type": "boolean",
                    "default": False
                }
            }
        },
        #############################################################################################################
        #                                                LOSS SECTION                                              #
        #############################################################################################################
        "CrossEntropyLoss": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["CrossEntropyLoss"]
                },
                "weight": {
                    "type": ["array", "null"],
                    "default": None
                },
                "ignore_index": {
                    "type": "integer",
                    "default": -100
                },
                "reduction": {
                    "type": "string",
                    "default": "mean"
                }
            }
        },
        "NLLLoss": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["NLLLoss"]
                },
                "weight": {
                    "type": ["array", "null"],
                    "default": None
                },
                "ignore_index": {
                    "type": "integer",
                    "default": -100
                },
                "reduction": {
                    "type": "string",
                    "default": "mean"
                }
            }
        },
        "L1Loss": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["L1Loss"]
                },
                "reduction": {
                    "type": "string",
                    "default": "mean",
                    "enum": ["none", "mean", "sum"]
                }
            }
        },
        "MSELoss": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["MSELoss"]
                },
                "reduction": {
                    "type": "string",
                    "default": "mean",
                    "enum": ["none", "mean", "sum"]
                }
            }
        },
        #############################################################################################################
        #                                                SCHEDULER SECTION                                          #
        #############################################################################################################
        "ExponentialLR": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type", "gamma"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["ExponentialLR"]
                },
                "gamma": {
                    "type": "number",
                    "default": None
                },
                "verbose": {
                    "type": "boolean",
                    "default": False
                }
            }
        },
        "StepLR": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type", "step_size"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["StepLR"]
                },
                "step_size": {
                    "type": "integer"
                },
                "gamma": {
                    "type": "number",
                    "default": 0.1
                },
                "verbose": {
                    "type": "boolean",
                    "default": False
                }
            }
        },
        "MultiStepLR": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type", "milestones"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["MultiStepLR"]
                },
                "milestones": {
                    "type": "array"
                },
                "gamma": {
                    "type": "number",
                    "default": 0.1
                },
                "verbose": {
                    "type": "boolean",
                    "default": False
                }
            }
        },
        "CosineAnnealingLR": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type", "T_max"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["CosineAnnealingLR"]
                },
                "T_max": {
                    "type": "integer"
                },
                "eta_min": {
                    "type": "number",
                    "default": 0
                },
                "verbose": {
                    "type": "boolean",
                    "default": False
                }
            }
        },
        "ReduceLROnPlateau": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["ReduceLROnPlateau"]
                },
                "mode": {
                    "type": "string",
                    "default": "min"
                },
                "factor": {
                    "type": "number",
                    "default": 0.1
                },
                "patience": {
                    "type": "integer",
                    "default": 10
                },
                "threshold": {
                    "type": "number",
                    "default": 0.0001
                },
                "threshold_mode": {
                    "type": "string",
                    "default": "rel"
                },
                "cooldown": {
                    "type": "integer",
                    "default": 0
                },
                "min_lr": {
                    "type": ["number", "array"],
                    "default": 0
                },
                "eps": {
                    "type": "number",
                    "default": 1e-08
                },
                "verbose": {
                    "type": "boolean",
                    "default": False
                }
            }
        },
        "CyclicLR": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type", "base_lr", "max_lr"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["CyclicLR"]
                },
                "base_lr": {
                    "type": ["number", "array"]
                },
                "max_lr": {
                    "type": ["number", "array"]
                },
                "step_size_up": {
                    "type": "integer",
                    "default": 2000
                },
                "step_size_down": {
                    "type": ["null", "integer"],
                    "default": None
                },
                "mode": {
                    "type": "string",
                    "default": "triangular"
                },
                "gamma": {
                    "type": "number",
                    "default": 1.0
                },
                "scale_mode": {
                    "type": "string",
                    "default": "cycle"
                },
                "cycle_momentum": {
                    "type": "boolean",
                    "default": True
                },
                "base_momentum": {
                    "type": ["number", "array"],
                    "default": 0.8
                },
                "max_momentum": {
                    "type": ["number", "array"],
                    "default": 0.9
                },
                "verbose": {
                    "type": "boolean",
                    "default": False
                }
            }
        },
        "OneCycleLR": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type", "max_lr"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["OneCycleLR"]
                },
                "max_lr": {
                    "type": ["number", "array"]
                },
                "total_steps": {
                    "type": ["null", "integer"],
                    "default": None
                },
                "epochs": {
                    "type": ["null", "integer"],
                    "default": None
                },
                "steps_per_epoch": {
                    "type": ["null", "integer"],
                    "default": None
                },
                "pct_start": {
                    "type": "number",
                    "default": 0.3
                },
                "anneal_strategy": {
                    "type": "string",
                    "default": "cos"
                },
                "cycle_momentum": {
                    "type": "boolean",
                    "default": True
                },
                "base_momentum": {
                    "type": ["number", "array"],
                    "default": 0.85
                },
                "max_momentum": {
                    "type": ["number", "array"],
                    "default": 0.95
                },
                "div_factor": {
                    "type": "number",
                    "default": 25.0
                },
                "final_div_factor": {
                    "type": "number",
                    "default": 10000.0
                },
                "three_phase": {
                    "type": "boolean",
                    "default": False
                },
                "verbose": {
                    "type": "boolean",
                    "default": False
                }
            }
        },
        "CosineAnnealingWarmRestarts": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type", "T_0"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["CosineAnnealingWarmRestarts"]
                },
                "T_0": {
                    "type": "integer"
                },
                "T_mult": {
                    "type": "integer",
                    "default": 1
                },
                "eta_min": {
                    "type": "number",
                    "default": 0
                },
                "verbose": {
                    "type": "boolean",
                    "default": False
                }
            }
        },
}


DEEP_CLASSIFIER_PARAMS = {
    "type": "object",
    "default": {},
    "additionalProperties": False,
    "required": ["fully_connected_layers"],
    "properties": {
        "fully_connected_layers": {
            "type": "array",
            "additionalItems": False,
            "minItems": 1,
            "items": {
                "oneOf": [
                    {"$ref": "#/definitions/Linear"},
                    {"$ref": "#/definitions/ReLU"},
                    {"$ref": "#/definitions/Dropout"},
                    {"$ref": "#/definitions/LogSoftmax"},
                    {"$ref": "#/definitions/Softmax"},
                    {"$ref": "#/definitions/BatchNorm1d"},
                ]
            }
        },
        "embedding_dropout": {
            "type": "number",
            "default": 0.5,
            "minimum": 0,
            "maximum": 1
        },
        "epochs": {
            "type": "integer",
            "default": 1,
            "minimum": 1,
        },
        "batch_size": {
            "type": "integer",
            "additionalItems": False,
            "default": 64,
            "minimum": 1,
        },
        "save_interval": {
            "type": "integer",
            "additionalItems": False,
            "default": 2,
            "minimum": 1,
        },
        "embedding_sizes": {
            "type": ["object", "null"],
            "default": None,
        },
        "y_range": {
            "type": ["array", "null"],
            "additionalItems": False,
            "default": None,
            "minItems": 2,
            "maxItems": 2,
            "items": {
                "type": "number"
            }
        },
        "loss": {
            "type": "object",
            "additionalItems": False,
            "default": {"type": "NLLLoss", "weight": None, "ignore_index": -100, "reduction": 'mean'},
            "oneOf": [
                {"$ref": "#/definitions/CrossEntropyLoss"},
                {"$ref": "#/definitions/NLLLoss"}
            ]
        },
        "scheduler": {
            "type": "object",
            "additionalItems": False,
            "oneOf": [
                {"$ref": "#/definitions/StepLR"},
                {"$ref": "#/definitions/MultiStepLR"},
                {"$ref": "#/definitions/CosineAnnealingLR"},
                {"$ref": "#/definitions/ExponentialLR"},
                {"$ref": "#/definitions/ReduceLROnPlateau"},
                {"$ref": "#/definitions/CyclicLR"},
                {"$ref": "#/definitions/CosineAnnealingWarmRestarts"},
            ]
        },
        "optimizer": {
            "type": "object",
            "additionalItems": False,
            "default": {"type": "Adam", "lr": 0.001, 'betas': [0.9, 0.999], 'eps': 1e-08, 'weight_decay': 0,
                        'amsgrad': False},
            "oneOf": [
                {"$ref": "#/definitions/Adam"},
                {"$ref": "#/definitions/AdamW"},
                {"$ref": "#/definitions/SparseAdam"},
                {"$ref": "#/definitions/Adamax"},
                {"$ref": "#/definitions/ASGD"},
                {"$ref": "#/definitions/LBFGS"},
                {"$ref": "#/definitions/RMSprop"},
                {"$ref": "#/definitions/Rprop"},
                {"$ref": "#/definitions/SGD"},
            ]
        },
    },
    "definitions": DEFINITIONS
}


DEEP_REGRESSOR_PARAMS = {
    "type": "object",
    "default": {},
    "additionalProperties": False,
    "required": ["fully_connected_layers"],
    "properties": {
        "fully_connected_layers": {
            "type": "array",
            "additionalItems": False,
            "minItems": 1,
            "items": {
                "oneOf": [
                    {"$ref": "#/definitions/Linear"},
                    {"$ref": "#/definitions/ReLU"},
                    {"$ref": "#/definitions/Dropout"},
                    {"$ref": "#/definitions/BatchNorm1d"},
                ]
            }
        },
        "embedding_dropout": {
            "type": "number",
            "default": 0.5,
            "minimum": 0,
            "maximum": 1
        },
        "epochs": {
            "type": "integer",
            "default": 1,
            "minimum": 1,
        },
        "batch_size": {
            "type": "integer",
            "additionalItems": False,
            "default": 64,
            "minimum": 1,
        },
        "save_interval": {
            "type": "integer",
            "additionalItems": False,
            "default": 2,
            "minimum": 1,
        },
        "embedding_sizes": {
            "type": ["object", "null"],
            "default": None,
        },
        "y_range": {
            "type": ["array", "null"],
            "additionalItems": False,
            "default": None,
            "minItems": 2,
            "maxItems": 2,
            "items": {
                "type": "number"
            }
        },
        "loss": {
            "type": "object",
            "additionalItems": False,
            "default": {"type": "MSELoss", "reduction": "mean"},
            "oneOf": [
                {"$ref": "#/definitions/L1Loss"},
                {"$ref": "#/definitions/MSELoss"},
            ]
        },
        "scheduler": {
            "type": "object",
            "additionalItems": False,
            "oneOf": [
                {"$ref": "#/definitions/StepLR"},
                {"$ref": "#/definitions/MultiStepLR"},
                {"$ref": "#/definitions/CosineAnnealingLR"},
                {"$ref": "#/definitions/ExponentialLR"},
                {"$ref": "#/definitions/ReduceLROnPlateau"},
                {"$ref": "#/definitions/CyclicLR"},
                {"$ref": "#/definitions/CosineAnnealingWarmRestarts"},
            ]
        },
        "optimizer": {
            "type": "object",
            "additionalItems": False,
            "default": {"type": "Adam", "lr": 0.001, 'betas': [0.9, 0.999], 'eps': 1e-08, 'weight_decay': 0,
                        'amsgrad': False},
            "oneOf": [
                {"$ref": "#/definitions/Adam"},
                {"$ref": "#/definitions/AdamW"},
                {"$ref": "#/definitions/SparseAdam"},
                {"$ref": "#/definitions/Adamax"},
                {"$ref": "#/definitions/ASGD"},
                {"$ref": "#/definitions/LBFGS"},
                {"$ref": "#/definitions/RMSprop"},
                {"$ref": "#/definitions/Rprop"},
                {"$ref": "#/definitions/SGD"},
            ]
        },
    },
    "definitions": DEFINITIONS
}


IMAGE_CLASSIFIER_PARAMS = {
    "type": "object",
    "default": {},
    "additionalProperties": False,
    "required": ["classifier"],
    "properties": {
        "classifier": {
            "type": "array",
            "additionalItems": False,
            "minItems": 1,
            "items": {
                "oneOf": [
                    {"$ref": "#/definitions/Linear"},
                    {"$ref": "#/definitions/ReLU"},
                    {"$ref": "#/definitions/Dropout"},
                    {"$ref": "#/definitions/LogSoftmax"},
                    {"$ref": "#/definitions/Softmax"},
                ]
            }
        },
        "features": {
            "type": "array",
            "additionalItems": False,
            "minItems": 1,
            "items": {
                "oneOf": [
                    {"$ref": "#/definitions/Conv2d"},
                    {"$ref": "#/definitions/ReLU"},
                    {"$ref": "#/definitions/MaxPool2d"}
                ]
            }
        },
        "freeze_features": {
            "type": "boolean",
            "default": True,
        },
        "loss": {
            "type": "object",
            "additionalItems": False,
            "default": {"type": "NLLLoss", "weight": None, "ignore_index": -100, "reduction": 'mean'},
            "oneOf": [
                {"$ref": "#/definitions/CrossEntropyLoss"},
                {"$ref": "#/definitions/NLLLoss"},
            ]
        },
        "scheduler": {
            "type": "object",
            "additionalItems": False,
            "oneOf": [
                {"$ref": "#/definitions/StepLR"},
                {"$ref": "#/definitions/MultiStepLR"},
                {"$ref": "#/definitions/CosineAnnealingLR"},
                {"$ref": "#/definitions/ExponentialLR"},
                {"$ref": "#/definitions/ReduceLROnPlateau"},
                {"$ref": "#/definitions/CyclicLR"},
                {"$ref": "#/definitions/CosineAnnealingWarmRestarts"},
            ]
        },
        "optimizer": {
            "type": "object",
            "additionalItems": False,
            "default": {"type": "Adam", "lr": 0.001, 'betas': [0.9, 0.999], 'eps': 1e-08, 'weight_decay': 0, 'amsgrad': False},
            "oneOf": [
                {"$ref": "#/definitions/Adam"},
                {"$ref": "#/definitions/AdamW"},
                {"$ref": "#/definitions/SparseAdam"},
                {"$ref": "#/definitions/Adamax"},
                {"$ref": "#/definitions/ASGD"},
                {"$ref": "#/definitions/LBFGS"},
                {"$ref": "#/definitions/RMSprop"},
                {"$ref": "#/definitions/Rprop"},
                {"$ref": "#/definitions/SGD"},
            ]
        },
        "epochs": {
            "type": "integer",
            "additionalItems": False,
            "default": 1,
            "minimum": 1,
        },
        "save_interval": {
            "type": "integer",
            "additionalItems": False,
            "default": 2,
            "minimum": 1,
        },
        "batch_size": {
            "type": "integer",
            "additionalItems": False,
            "default": 64,
            "minimum": 1,
        }
    },
    "definitions": DEFINITIONS
}


IMAGE_TRANSFORM_PARAMS = {
    "type": "array",
    "additionalItems": False,
    "minItems": 1,
    "items": {
        "oneOf": [
            {
                "type": "object",
                "additionalProperties": False,
                "required": ["type", "degrees"],
                "properties": {
                     "type": {
                         "type": "string",
                         "enum": ["RandomRotation"]
                     },
                     "activate": {
                         "type": "boolean",
                         "default": True
                     },
                     "degrees": {
                         "type": ["number", "array"]
                     },
                     "expand": {
                        "type": "boolean",
                        "default": False
                     },
                     "center": {
                        "type": ["null", "array"],
                        "default": None
                     },
                     "fill": {
                        "type": ["number", "array"],
                        "default": 0
                     },
                }
            },
            {
                "type": "object",
                "additionalProperties": False,
                "required": ["type"],
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["RandomHorizontalFlip"]
                    },
                    "activate": {
                        "type": "boolean",
                        "default": True
                    },
                    "p": {
                        "type": "number",
                        "default": 0.5
                    },
                }
            },
            {
                "type": "object",
                "additionalProperties": False,
                "required": ["type", "size"],
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["Resize"]
                    },
                    "activate": {
                        "type": "boolean",
                        "default": True
                    },
                    "size": {
                        "type": ["integer", "array"]
                    },
                }
            },
            {
                "type": "object",
                "additionalProperties": False,
                "required": ["type", "size"],
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["CenterCrop"]
                    },
                    "activate": {
                        "type": "boolean",
                        "default": True
                    },
                    "size": {
                        "type": ["integer", "array"]
                    },
                }
            },
            {
                "type": "object",
                "additionalProperties": False,
                "required": ["type"],
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["ToTensor"]
                    },
                    "activate": {
                        "type": "boolean",
                        "default": True
                    }
                }
            },
            {
                "type": "object",
                "additionalProperties": False,
                "required": ["type", "mean", "std"],
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["Normalize"]
                    },
                    "activate": {
                        "type": "boolean",
                        "default": True
                    },
                    "mean": {
                        "type": "array"
                    },
                    "std": {
                        "type": "array"
                    },
                }
            },
        ]
    }
}

