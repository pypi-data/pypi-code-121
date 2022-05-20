# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""This module implements the ModelValidator class to validate the model parameters provided by users.
"""
import sys
import logging

from learner.configuration.defaults import DEEP_CLASSIFIER_PARAMS, DEEP_REGRESSOR_PARAMS, IMAGE_CLASSIFIER_PARAMS
from jsonschema import Draft7Validator, validators


def extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for property, subschema in properties.items():
            if "type" in instance and "type" in properties and \
               instance["type"] == properties["type"]["enum"][0] and \
               "default" in subschema:
                instance.setdefault(property, subschema["default"])
            if "type" not in instance and "default" in subschema:
                instance.setdefault(property, subschema["default"])
        for error in validate_properties(validator, properties, instance, schema,):
            yield error

    return validators.extend(validator_class, {"properties": set_defaults},)


DefaultValidatingDraft7Validator = extend_with_default(Draft7Validator)


class ModelValidator:
    """Validate the model parameters defined in the configuration file. This class only validates the custom models
    such as DeepClassifier and DeepRegressor. We currently do not validate standard models such as RandomForest, etc.
    To understand what models are validates, look at DEFAULT_MODEL_PARAMS
    """
    def __init__(self, conf):
        self.conf = conf

    def validate_models(self):
        """The main method that communicates with other methods to validate the model parameters. The name of each
        validator method ends with the "type" of the model.

        :return: None
        """
        self.validate_deep_classifier()
        self.validate_deep_regressor()
        self.validate_image_classifier()

    def validate_deep_classifier(self):
        for tag, mdl in self.conf.model.models_dict.items():
            # we currently only need to do the validation for certain type of models. Segmentation is not supported
            # for these models. As such, we are limiting validations to only dict types
            if not isinstance(mdl, dict):
                return
            if mdl["type"] == "DeepClassifier":
                DefaultValidatingDraft7Validator(DEEP_CLASSIFIER_PARAMS).validate(mdl["params"])
                # make sure the loss function is consistent with the last layer
                if mdl["params"]["fully_connected_layers"][-1]["type"] == "LogSoftmax" and mdl["params"]["loss"]["type"] == "CrossEntropyLoss":
                    logging.critical("You last fully connected layer is LogSoftmax and you are using CrossEntropyLoss. "
                                     "The CrossEntropyLoss already includes LogSoftmax for you. Please delete that "
                                     "layer or use NLLLoss instead. Exiting...")
                    sys.exit(1)

    def validate_deep_regressor(self):
        for tag, mdl in self.conf.model.models_dict.items():
            # we currently only need to do the validation for certain type of models. Segmentation is not supported
            # for these models. As such, we are limiting validations to only dict types
            if not isinstance(mdl, dict):
                return
            if mdl["type"] == "DeepRegressor":
                DefaultValidatingDraft7Validator(DEEP_REGRESSOR_PARAMS).validate(mdl["params"])
                # we need to make sure the last Linear layer has 1 node
                i = -1
                while abs(i) <= len(mdl["params"]["fully_connected_layers"]):
                    if mdl["params"]["fully_connected_layers"][i]["type"] == "Linear":
                        if mdl["params"]["fully_connected_layers"][i]["out_features"] != 1:
                            logging.critical("In deep_regressor engine, the last Linear layer should have only 1 node, "
                                             "i.e. out_features: 1. Please update the configuration file and try "
                                             "again. Existing...")
                            sys.exit(1)
                        break
                    i -= 1

    def validate_image_classifier(self):
        if self.conf.engine != "ImageClassifier":
            return
        for tag, mdl in self.conf.model.models_dict.items():
            # we currently only need to do the validation for certain type of models. Segmentation is not supported
            # for these models. As such, we are limiting validations to only dict types
            if not isinstance(mdl, dict):
                return
            DefaultValidatingDraft7Validator(IMAGE_CLASSIFIER_PARAMS).validate(mdl["params"])
            # make sure the loss function is consistent with the last layer
            if mdl["params"]["classifier"][-1]["type"] == "LogSoftmax" and mdl["params"]["loss"]["type"] == "CrossEntropyLoss":
                logging.critical("You last classifier layer is LogSoftmax and you are using CrossEntropyLoss. The "
                                 "CrossEntropyLoss already includes LogSoftmax for you. Please delete that layer or "
                                 "use NLLLoss instead. Exiting...")
                sys.exit(1)
            # make sure "stride" is set to "kernel_size" in MaxPool2d if it is undefined, i.e. None
            if "features" in mdl["params"]:
                for layer in mdl["params"]["features"]:
                    if layer["type"] == "MaxPool2d" and layer["stride"] is None:
                        layer["stride"] = layer["kernel_size"]
            # TODO: convert the weight parameter in NLLLoss to a tensor
