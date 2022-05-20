# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""This class implements the DeepTrainManager class to train and validate deep learning models."""
import logging
import numpy as np
import torch
from torch.nn.functional import softmax


from learner.callback_manager.callback import MetricLogger, CallbackManager, ModelSaver
from learner.model_manager.scoring_manager import DeepClassifierScorer, DeepRegressorScorer
from learner.data_worker.data_mover import move_to_device


class DeepLoopManager:
    """The DeepTrainManager implements the main loops for building deep learning models. This class contains two main
    methods namely "train" and "validation". This class uses a callback/event handling process to modify the
    training/validation loops, log the outputs, save the models or any other operations. Currently, the "validate"
    method is specific to the image_classifier engine but this will be updated once we implement other deep learning
    engines.
    """
    def __init__(self, conf, model, criterion, optimizer, scheduler, epochs, tag, mdl, train_loader=None,
                 validation_loader=None, callbacks=None, processor=None, feature_engineering=None):
        """Initialize a DeepTrainManager using the input arguments.

        :param conf: a conf object
        :param model: a PyTorch model that is ready to be trained.
        :param criterion: the loss object. This is built using the loss_manager module
        :param optimizer: the optimizer object. This is built using the optimizer_manager module.
        :param epochs: the number of epochs to train the model for. This is an integer.
        :param tag: the tag of the model. This is a key in models_dict.
        :param mdl: an item (value) in models_dict.
        :param train_loader: the train_loader to loop through the training data.
        :param validation_loader: the validation_loader to loop through the validation data.
        :param callbacks: a list of callbacks
        :param processor: the processor object - this is optional and only relevant for deep_classifier and deep_regressor engines
        :param feature_engineering: the feature_engineering object - this is optional and only relevant for deep_classifier and deep_regressor engines
        """
        self.conf = conf
        self.epochs = epochs
        self.tag = tag
        self.mdl = mdl
        self.train_loader = train_loader
        self.validation_loader = validation_loader
        self.device = conf.model.device
        self.model = model.to(self.device)
        self.criterion = criterion
        self.optimizer = optimizer
        self.scheduler = scheduler
        self.callbacks = callbacks
        self.processor = processor
        self.feature_engineering = feature_engineering
        self.metrics = {}
        # the Event classes can modify this to stop the process when needed
        self.should_stop = False

    def train(self):
        """Implement the main training loop. Here, we first use a list of event objects to create an event_manager
        object. Currently, we perform this operation in this methods but we may need to change this in the future.
        We then perform the main training loop and call the "validation" method after each epoch.

        :return: None
        """
        event_manager = CallbackManager(*self.callbacks)
        logging.info(f"Training {self.tag} model ")
        for epoch in range(self.epochs):
            self.metrics["epoch"] = epoch
            self.model.train()

            train_losses = np.zeros(len(self.train_loader))
            for b, (X_train, y_train) in enumerate(self.train_loader):
                X_train, y_train = move_to_device(X_train, self.device), move_to_device(y_train, self.device)

                y_pred = self.model(*X_train) if isinstance(X_train, list) else self.model(X_train)

                loss = self.criterion(y_pred, y_train)
                train_losses[b] = loss

                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

                event_manager.on_batch_end(deep_trainer=self,
                                           iteration=epoch*len(self.train_loader)+b,
                                           loss=loss)
                if self.should_stop: return

            self.metrics["train_loss"] = train_losses.mean()
            self.validate()
            if self.scheduler: self.scheduler.step()

            event_manager.on_epoch_end(conf=self.conf,
                                       tag=self.tag,
                                       mdl=self.mdl,
                                       metrics=self.metrics,
                                       model=self.model,
                                       epoch=epoch,
                                       processor=self.processor,
                                       feature_engineering=self.feature_engineering)
            if self.should_stop: return

    def validate(self):
        """If validation_loader is provided, we need to put the model in validation mode to validate it against the
        validation data. Since there are some nuances in the classification vs regression models, we implemented
        specific methods for those models. In the future, we may consider implementing subclasses for this.

        :return: None
        """
        # return if we don't have validation loader, we can't score
        if not self.validation_loader:
            return

        if self.conf.engine in ["DeepClassifier", "ImageClassifier"]:
            self._validate_classifier()
        else:
            self._validate_regressor()

    def _validate_classifier(self):
        """We first put the model in validation mode to validate it against the validation data. We then run the
        validation loop to get the validation data and compute the scores. This method is specifically designed for the
        classification as it deals with the probabilities and uses the classification scorer class.

        :return: None
        """
        y_true = []
        pred_proba = []
        with torch.no_grad():
            # put the model to evaluation mode. This is very important otherwise the results will not be correct
            self.model.eval()
            validation_losses = np.zeros(len(self.train_loader))
            for b, (X_test, y_test) in enumerate(self.train_loader):
                X_test, y_test = move_to_device(X_test, self.device), move_to_device(y_test, self.device)

                y_val = self.model(*X_test) if isinstance(X_test, list) else self.model(X_test)

                loss = self.criterion(y_val, y_test)

                y_val = self._handle_engine_y_val(y_val)
                y_true.extend(y_test.cpu().numpy())
                pred_proba.extend(y_val.cpu().numpy())

                validation_losses[b] = loss

            self.metrics["validation_loss"] = validation_losses.mean()
            scorer = DeepClassifierScorer(conf=self.conf,
                                          models_dict=None,
                                          y_true=y_true,
                                          pred_proba=pred_proba,
                                          metrics=self.metrics)
            scorer.score()

    def _validate_regressor(self):
        """We first put the model in validation mode to validate it against the validation data. We then run the
        validation loop to get the validation data and compute the scores. This method is specifically designed for the
        regression and uses the regression scorer class.

        :return: None
        """
        y_true = []
        pred = []
        with torch.no_grad():
            # put the model to evaluation mode. This is very important otherwise the results will not be correct
            self.model.eval()
            validation_losses = np.zeros(len(self.train_loader))
            for b, (X_test, y_test) in enumerate(self.train_loader):
                X_test, y_test = move_to_device(X_test, self.device), move_to_device(y_test, self.device)

                y_val = self.model(*X_test) if isinstance(X_test, list) else self.model(X_test)

                loss = self.criterion(y_val, y_test)

                y_true.extend(y_test.cpu().numpy())
                pred.extend(y_val.cpu().numpy())

                validation_losses[b] = loss

            self.metrics["validation_loss"] = validation_losses.mean()
            scorer = DeepRegressorScorer(conf=self.conf,
                                         models_dict=None,
                                         y_true=y_true,
                                         pred=pred,
                                         metrics=self.metrics)
            scorer.score()

    def _handle_engine_y_val(self, y_val):
        """Depending on the type of the models and their last layer, we may need to process the output if the last
        layer in order to correctly compute the scores. For example, if the last layer is LogSoftmax, we need to do the
        exp to get the probabilities. This method handles those calculations. Currently, the regression models don't
        need any additional calculations.

        :param y_val:
        :return:
        """
        if self.conf.engine == "ImageClassifier":
            # if the activation is LogSoftmax, do the exponential to get the probabilities
            from learner.model_manager.image_classifiers import mdl_to_head
            if isinstance(getattr(self.model, mdl_to_head[self.mdl["type"]])[-1], torch.nn.LogSoftmax):
                y_val = torch.exp(y_val)
            # if activation is not LogSoftmax and not Softmax, we need to pass it through a softmax function to get
            # the probabilities
            if not isinstance(getattr(self.model, mdl_to_head[self.mdl["type"]])[-1], torch.nn.LogSoftmax) and \
                    not isinstance(getattr(self.model, mdl_to_head[self.mdl["type"]])[-1], torch.nn.Softmax):
                y_val = torch.nn.functional.softmax(y_val, dim=1)
        elif self.conf.engine == "DeepClassifier":
            # if the activation is LogSoftmax, do the exponential to get the probabilities
            if isinstance(getattr(self.model, "fully_connected_layers")[-1], torch.nn.LogSoftmax):
                y_val = torch.exp(y_val)
            # if activation is not LogSoftmax and not Softmax, we need to pass it through a softmax function to get
            # the probabilities
            if not isinstance(getattr(self.model, "fully_connected_layers")[-1], torch.nn.LogSoftmax) and \
                    not isinstance(getattr(self.model, "fully_connected_layers")[-1], torch.nn.Softmax):
                y_val = torch.nn.functional.softmax(y_val, dim=1)
        return y_val
