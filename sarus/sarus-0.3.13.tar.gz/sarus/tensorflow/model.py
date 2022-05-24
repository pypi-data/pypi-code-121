from typing import Any, Callable, Container, Dict, List, Optional, Tuple, Union
import json
import logging
import os
import tarfile
import tempfile
import textwrap

from sarus.tensorflow import Dataset
import cloudpickle
import numpy as np

import tensorflow as tf

Transform = Tuple[str, Dict[str, Any]]
Data = Any


class Model(tf.keras.Model):
    """A class similar to a keras Model and allowing private remote training.

    The sarus.keras.Model class is a wrapper around the
    `tensorflow.keras.Model` class. This class differs from its parent only on
    the `fit` method. The `fit` method accepts a `target_epsilon`
    (Differential Privacy parameter).

        - If the specified `target_epsilon` equals to 0, then the `Model` class launches a standard keras training on the synthetic data.

        - If the specified `target_epsilon` is strictly greater than 0, then the `Model` class calls the Sarus API to launch a remote private training with `target_epsilon` the maximum privacy budget to assign to the differentially-private model fitting.

        - If None, a default `target_epsilon` specific to the current user and access rule is used.
            Default target epsilon is 0 if the access is a Differentially-Private access with
            per-user or per-group limit; default value equals to the per-query limit if the access is
            a Differentially-Private access with a per-query limit only. Meaning Sarus maximizes the result
            accuracy in the given privacy constraints. See user documentation to know more.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(Model, self).__init__(self, *args, **kwargs)

    def predict(
        self,
        x: Data,
        batch_size: Optional[int] = None,
        verbose: int = 0,
        steps: Optional[int] = None,
        callbacks: Optional[List[tf.keras.callbacks.Callback]] = None,
        max_queue_size: int = 10,
        workers: int = 1,
        use_multiprocessing: bool = False,
    ) -> np.ndarray:
        """Generate output predictions for the input samples.

        Computation is done in batches. This method is designed for performance
        in large scale inputs. For small amount of inputs that fit in one batch,
        directly using `__call__` is recommended for faster execution, e.g.,
        `model(x)`, or `model(x, training=False)` if you have layers such as
        `tf.keras.layers.BatchNormalization` that behaves differently during
        inference. Also, note the fact that test loss is not affected by
        regularization layers like noise and dropout.

        Args:

        x: Input samples.
            It could be:

            - A Numpy array (or array-like), or a list of arrays
                in case the model has multiple inputs.
            - A TensorFlow tensor, or a list of tensors
                in case the model has multiple inputs.
            - A `tf.data` dataset.
            - A `sarus.tensorflow.Dataset` dataset.
            - A generator or `keras.utils.Sequence` instance.

        batch_size (int, optional):
            Number of samples per batch.
            If unspecified, `batch_size` will default to 32.
            Do not specify the `batch_size` if your data is in the
            form of dataset, `sarus.tensorflow.Dataset`, generators, or
            `keras.utils.Sequence` instances (since they generate batches).

        verbose (int):
            Verbosity mode, 0 or 1.

        steps (int):
            Total number of steps (batches of samples)
            before declaring the prediction round finished.
            Ignored with the default value of `None`. If x is a `tf.data`
            dataset and `steps` is None, `predict` will
            run until the input dataset is exhausted.

        callbacks: List of `keras.callbacks.Callback` instances.
            List of callbacks to apply during prediction. See
            `Tensorflow callbacks documentation
            <https://www.tensorflow.org/api_docs/python/tf/keras/callbacks>`_.

        max_queue_size (int):
            Used for generator or `keras.utils.Sequence`
            input only. Maximum size for the generator queue.
            If unspecified, `max_queue_size` will default to 10.

        workers (int):
            Used for generator or `keras.utils.Sequence` input
            only. Maximum number of processes to spin up when using
            process-based threading. If unspecified, `workers` will default
            to 1.

        use_multiprocessing (bool):
            Used for generator or
            `keras.utils.Sequence` input only. If `True`, use process-based
            threading. If unspecified, `use_multiprocessing` will default to
            `False`. Note that because this implementation relies on
            multiprocessing, you should not pass non-picklable arguments to
            the generator as they can't be passed easily to children
            processes.

        See the discussion of `Unpacking behavior for iterator-like inputs` for
        `tensorflow.keras.Model.fit`.
        Note that `Model.predict` uses the same interpretation rules
        as `Model.fit` and `Model.evaluate`, so inputs must be unambiguous for
        all three methods.
        `Model.predict` is not yet supported with
        `tf.distribute.experimental.ParameterServerStrategy`.

        Returns:
            Numpy array(s) of predictions.

        Raises:
            RuntimeError:
                If `model.predict` is wrapped in `tf.function`.

            ValueError:
                In case of mismatch between the provided
                input data and the model's expectations,
                or in case a stateful model receives a number of samples
                that is not a multiple of the batch size.
        """
        if isinstance(x, Dataset):
            x = x._tensorflow()
        return super().predict(
            x=x,
            batch_size=batch_size,
            verbose=verbose,
            steps=steps,
            callbacks=callbacks,
            max_queue_size=max_queue_size,
            workers=workers,
            use_multiprocessing=use_multiprocessing,
        )

    def evaluate(
        self,
        x: Data = None,
        y: Data = None,
        batch_size: Optional[int] = None,
        verbose: int = 1,
        sample_weight: Optional[np.ndarray] = None,
        steps: Optional[int] = None,
        callbacks: Optional[List[tf.keras.callbacks.Callback]] = None,
        max_queue_size: int = 10,
        workers: int = 1,
        use_multiprocessing: bool = False,
        return_dict: bool = False,
        **kwargs: Any,
    ) -> Union[float, List[float]]:
        """Return the loss value and metrics values for the model in test mode.

        Computation is done in batches (see the `batch_size`).

        Args:

        x: Input data.
            It could be:

            - A Numpy array (or array-like), or a list of arrays
                in case the model has multiple inputs.
            - A TensorFlow tensor, or a list of tensors
                in case the model has multiple inputs.
            - A dict mapping input names to the corresponding array/tensors
                if the model has named inputs.
            - A `tf.data` dataset.
                Should return a tuple
                of either `(inputs, targets)` or
                `(inputs, targets, sample_weights)`.
            - A `sarus.tensorflow.Dataset` dataset.
                Should return a tuple
                of either `(inputs, targets)` or
                `(inputs, targets, sample_weights)`.
            - A generator or `keras.utils.Sequence`
                returning `(inputs, targets)` or `(inputs, targets,
                sample_weights)`. A more detailed description of unpacking
                behavior for iterator types (Dataset, generator, Sequence)
                is given in the `Unpacking behavior for iterator-like inputs`
                section of `tensorflow.keras.Model.fit`.

        y: Target data.
            Like the input data `x`, it could be either Numpy
            array(s) or TensorFlow tensor(s). It should be consistent with
            `x` (you cannot have Numpy inputs and tensor targets, or
            inversely). If `x` is a dataset, generator or `keras.utils.Sequence`
            instance, `y` should not be specified (since targets
            will be obtained from the iterator/dataset).

        batch_size (int, optional):
            Number of samples per batch of
            computation. If unspecified, `batch_size` will default to 32. Do not
            specify the `batch_size` if your data is in the form of a dataset,
            generators, or `keras.utils.Sequence` instances (since they generate
            batches).

        verbose (int): 0 or 1.
            Verbosity mode. 0 = silent, 1 = progress bar.

        sample_weight (optional):
            Optional Numpy array of weights for the test samples,
            used for weighting the loss function. You can either pass a flat
            (1D) Numpy array with the same length as the input samples
            (1:1 mapping between weights and samples), or in the case of
            temporal data, you can pass a 2D array with shape `(samples,
            sequence_length)`, to apply a different weight to every timestep
            of every sample. This argument is not supported when `x` is a
            dataset, instead pass sample weights as the third element of `x`.

        steps (int, optional):
            Total number of steps (batches of samples)
            before declaring the evaluation round finished. Ignored with the
            default value of `None`. If x is a `tf.data` dataset and `steps` is
            None, `evaluate` will run until the dataset is exhausted. This
            argument is not supported with array inputs.

        callbacks: List of `keras.callbacks.Callback` instances.
            List of callbacks to apply during evaluation. See
            `Tensorflow callbacks documentation
            <https://www.tensorflow.org/api_docs/python/tf/keras/callbacks>`_.

        max_queue_size (int, optional):
            Used for generator or
            `keras.utils.Sequence` input only. Maximum size for the generator
            queue. If unspecified, `max_queue_size` will default to 10.

        workers (int, optional):
            Used for generator or `keras.utils.Sequence` input
            only. Maximum number of processes to spin up when using
            process-based threading. If unspecified, `workers` will default to
            1.

        use_multiprocessing (bool):
            Used for generator or `keras.utils.Sequence` input only. If `True`,
            use process-based threading. If unspecified, `use_multiprocessing`
            will default to `False`. Note that because this implementation
            relies on multiprocessing, you should not pass non-picklable
            arguments to the generator as they can't be passed easily to
            children processes.

        return_dict: If `True`, loss and metric results are returned as a
            dict, with each key being the name of the metric. If `False`, they
            are returned as a list.

        **kwargs:
            Unused at this time.

        See the discussion of `Unpacking behavior for iterator-like inputs` for
        `tensorflow.keras.Model.fit`.
        `Model.evaluate` is not yet supported with
        `tf.distribute.experimental.ParameterServerStrategy`.

        Returns:
            Scalar test loss (if the model has a single output and no metrics)
            or list of scalars (if the model has multiple outputs
            and/or metrics). The attribute `model.metrics_names` will give you
            the display labels for the scalar outputs.

        Raises:
            RuntimeError:
                If `model.evaluate` is wrapped in `tf.function`.

            ValueError:
                in case of invalid arguments.
        """
        if isinstance(x, Dataset):
            x = x._tensorflow()
        return super().evaluate(
            x=x,
            y=y,
            batch_size=batch_size,
            verbose=verbose,
            sample_weight=sample_weight,
            steps=steps,
            callbacks=callbacks,
            max_queue_size=max_queue_size,
            workers=workers,
            use_multiprocessing=use_multiprocessing,
            return_dict=return_dict,
            **kwargs,
        )

    def fit(
        self,
        x: Data = None,
        y: Data = None,
        batch_size: Optional[int] = None,
        epochs: Optional[int] = None,
        verbose: Union[int, str] = "auto",
        callbacks: List[tf.keras.callbacks.Callback] = None,
        validation_split: float = 0.0,
        validation_data=None,
        shuffle: Union[bool, str] = True,
        class_weight: Optional[Dict[int, float]] = None,
        sample_weight: Optional[np.ndarray] = None,
        initial_epoch: int = 0,
        steps_per_epoch: Optional[int] = None,
        validation_steps: Optional[int] = None,
        validation_batch_size: Optional[int] = None,
        validation_freq: Union[int, Container[int]] = 1,
        max_queue_size: int = 10,
        workers: int = 1,
        use_multiprocessing: bool = False,
        target_epsilon: Optional[float] = None,
        dp_l2_norm_clip: float = None,
        dp_noise_multiplier: float = None,
        dp_num_microbatches: Optional[int] = None,  # default: batch size
        **kwargs: Any,
    ) -> tf.keras.callbacks.History:
        """Train the model via the Sarus API.

        Args:

        x: The training data.
            It could be:

            - a sarus.tensorflow.Dataset
            - a tensorflow.data.Dataset

            If `target_epsilon` is greater than 0 then `x` must be a
            `sarus.tensorflow.Dataset`.

        y: Target data.
            Like the input data `x`,
            it could be either Numpy array(s) or TensorFlow tensor(s).
            It should be consistent with `x` (you cannot have Numpy inputs and
            tensor targets, or inversely). If `x` is a dataset, generator,
            or `keras.utils.Sequence` instance, `y` should
            not be specified (since targets will be obtained from `x`).
            Will be ignored if `target_epsilon` is specified.

        batch_size: Integer or `None`.
            Number of samples per gradient update.
            If unspecified, `batch_size` will default to 32.
            Do not specify the `batch_size` if your data is in the
            form of datasets, generators, or `keras.utils.Sequence` instances
            (since they generate batches).
            Will be ignored if `target_epsilon` is specified.

        epochs (int): Number of epochs to train the model.
            An epoch is an iteration over the entire data provided. Defaults to
            None. For remote DP-training (`target_epsilon` > 0), only one
            parameter among `epochs` and `dp_noise_multiplier` can be taken into
            account to satisfy `target_epsilon`. If both are set, the Sarus API
            will change `epochs`.

        verbose: 'auto', 0, 1, or 2. Verbosity mode.
            0 = silent, 1 = progress bar, 2 = one line per epoch.
            'auto' defaults to 1 for most cases, but 2 when used with
            `ParameterServerStrategy`. Note that the progress bar is not
            particularly useful when logged to a file, so verbose=2 is
            recommended when not running interactively (eg, in a production
            environment).

        callbacks: List of `keras.callbacks.Callback` instances.
            List of callbacks to apply during training.
            See `tf.keras.callbacks`. Note `tf.keras.callbacks.ProgbarLogger`
            and `tf.keras.callbacks.History` callbacks are created automatically
            and need not be passed into `model.fit`.
            `tf.keras.callbacks.ProgbarLogger` is created or not based on
            `verbose` argument to `model.fit`.
            Callbacks with batch-level calls are currently unsupported with
            `tf.distribute.experimental.ParameterServerStrategy`, and users are
            advised to implement epoch-level calls instead with an appropriate
            `steps_per_epoch` value.
            Will be ignored if `target_epsilon` is specified.

        validation_split: Float between 0 and 1.
            Fraction of the training data to be used as validation data.
            The model will set apart this fraction of the training data,
            will not train on it, and will evaluate
            the loss and any model metrics
            on this data at the end of each epoch.
            The validation data is selected from the last samples
            in the `x` and `y` data provided, before shuffling. This argument is
            not supported when `x` is a dataset, generator
            or `keras.utils.Sequence` instance.
            `validation_split` is not yet supported with
            `tf.distribute.experimental.ParameterServerStrategy`.
            Will be ignored if `target_epsilon` is specified.

        validation_data: Default to None.
            Data on which to evaluate the loss and any model
            metrics at the end of each epoch. The model will not be trained on
            this data. Thus, note the fact that the validation loss of data
            provided using validation_split or `validation_data` is not affected
            by regularization layers like noise and dropout. `validation_data`
            will override validation_split. `validation_data` could be:

            - a sarus.tensorflow.Dataset
            - a tensorflow.data.Dataset

            If `target_epsilon` is greater than 0 then `validation_data` must
            be None as it is not supported yet.

        shuffle: Boolean or str.
            Boolean (whether to shuffle the training data
            before each epoch) or str (for 'batch'). This argument is ignored
            when `x` is a generator or an object of tf.data.Dataset.
            'batch' is a special option for dealing
            with the limitations of HDF5 data; it shuffles in batch-sized
            chunks. Has no effect when `steps_per_epoch` is not `None`.
            Will be ignored if `target_epsilon` is specified.

        class_weight: Optional dict mapping class indices to a weight.
            Used for weighting the loss function
            (during training only).
            This can be useful to tell the model to
            "pay more attention" to samples from
            an under-represented class.
            Will be ignored if `target_epsilon` is specified.

        sample_weight: Optional Numpy array.
            Optional Numpy array of weights for
            the training samples, used for weighting the loss function
            (during training only). You can either pass a flat (1D)
            Numpy array with the same length as the input samples
            (1:1 mapping between weights and samples),
            or in the case of temporal data,
            you can pass a 2D array with shape `(samples, sequence_length)`,
            to apply a different weight to every timestep of every sample. This
            argument is not supported when `x` is a dataset, generator,
            or `keras.utils.Sequence` instance, instead provide the
            sample_weights as the third element of `x`.
            Will be ignored if `target_epsilon` is specified.

        initial_epoch: Integer.
            Epoch at which to start training
            (useful for resuming a previous training run).
            Will be ignored if `target_epsilon` is specified.

        steps_per_epoch: Integer or `None`.
            Total number of steps (batches of samples)
            before declaring one epoch finished and starting the
            next epoch. When training with input tensors such as
            TensorFlow data tensors, the default `None` is equal to
            the number of samples in your dataset divided by
            the batch size, or 1 if that cannot be determined. If x is a
            `tf.data` dataset, and 'steps_per_epoch'
            is None, the epoch will run until the input dataset is exhausted.
            When passing an infinitely repeating dataset, you must specify the
            `steps_per_epoch` argument. If `steps_per_epoch=-1` the training
            will run indefinitely with an infinitely repeating dataset.
            This argument is not supported with array inputs.
            When using `tf.distribute.experimental.ParameterServerStrategy`:
              * `steps_per_epoch=None` is not supported.
            Will be ignored if `target_epsilon` is specified.

        validation_steps: Optional Integer.
            Only relevant if `validation_data` is provided and
            is a `tf.data` dataset. Total number of steps (batches of
            samples) to draw before stopping when performing validation
            at the end of every epoch. If 'validation_steps' is None, validation
            will run until the `validation_data` dataset is exhausted. In the
            case of an infinitely repeated dataset, it will run into an
            infinite loop. If 'validation_steps' is specified and only part of
            the dataset will be consumed, the evaluation will start from the
            beginning of the dataset at each epoch. This ensures that the same
            validation samples are used every time.
            Will be ignored if `target_epsilon` is specified.

        validation_batch_size: Optional Integer.
            Number of samples per validation batch.
            If unspecified, will default to `batch_size`.
            Do not specify the `validation_batch_size` if your data is in the
            form of datasets, generators, or `keras.utils.Sequence` instances
            (since they generate batches).
            Will be ignored if `target_epsilon` is specified.

        validation_freq:  Integer or `collections.abc.Container` instance.
            Only relevant if validation data is provided.
            If an integer, specifies how many training epochs to run before a
            new validation run is performed, e.g. `validation_freq=2` runs
            validation every 2 epochs. If a Container, specifies the epochs on
            which to run validation, e.g. `validation_freq=[1, 2, 10]` runs
            validation at the end of the 1st, 2nd, and 10th epochs.
            Will be ignored if `target_epsilon` is specified.

        max_queue_size: Integer.
            Used for generator or `keras.utils.Sequence`
            input only. Maximum size for the generator queue.
            If unspecified, `max_queue_size` will default to 10.
            Will be ignored if `target_epsilon` is specified.

        workers: Integer.
            Used for generator or `keras.utils.Sequence` input
            only. Maximum number of processes to spin up
            when using process-based threading. If unspecified, `workers`
            will default to 1.
            Will be ignored if `target_epsilon` is specified.

        use_multiprocessing: Boolean.
            Used for generator or
            `keras.utils.Sequence` input only. If `True`, use process-based
            threading. If unspecified, `use_multiprocessing` will default to
            `False`. Note that because this implementation relies on
            multiprocessing, you should not pass non-picklable arguments to
            the generator as they can't be passed easily to children processes.
            Will be ignored if `target_epsilon` is specified.

        target_epsilon (Optional[float]): Defaults to None.
            Target epsilon for differentially private training.
            There are three behaviors depending on the value of `target_epsilon`:
              * `target_epsilon == 0` the training is performed locally on the
                synthetic data.
              * `target_epsilon > 0` training is performed remotely with
                 DP-SDG and only one parameter among `epochs` and
                 `dp_noise_multiplier` can be taken into account to satisfy
                 `target_epsilon`. If both are set, the Sarus API will
                 change `epochs`.
              * `target_epsilon is None` a default `target_epsilon` specific to
                 the current user and access rule is used.
                 Default target epsilon is 0 if the access is a Differentially-Private
                 access with per-user or per-group limit; default value equals to the
                 per-query limit if the access is a Differentially-Private access with
                 a per-query limit only. Meaning Sarus maximizes the result accuracy
                 in the given privacy constraints. See user documentation to know more.

        dp_l2_norm_clip (float): Defaults to None.
            Advanced DP-SGD parameter. The cumulative gradient across all
            network parameters from each microbatch is clipped so that its L2
            norm is at most this value. You should set this to something close
            to some percentile of what you expect the gradient from each
            microbatch to be. In previous experiments, we've found numbers from
            0.5 to 1.0 to work reasonably well.
            See `Tensorflow Privacy` documentation to know more.

        dp_noise_multiplier (float): Defaults to None.
            Advanced DP-SGD parameter. This governs the amount of noise added
            during training. Generally, more noise results in better privacy and
            lower utility. See `Tensorflow Privacy` documentation to know more.
            Note that for DP training (`target_epsilon`> 0), only one parameter
            among `epochs` and `dp_noise_multiplier` can be taken into account
            to satisfy `target_epsilon`. If both are set, the Sarus API will
            change `epochs`.

        dp_num_microbatches (int): Defaults to batch_size.
            Advanced DP-SGD parameter. The input data for each step (i.e.,
            batch) of your original training algorithm is split into this many
            microbatches. Generally, increasing this will improve your utility
            but slow down your training in terms of wall-clock time. The total
            number of examples consumed in one global step remains the same.
            This number should evenly divide your input batch size.
            See `Tensorflow Privacy` documentation to know more.
            If `None`, will default to `batch_size` of the dataset.

        Returns:
            History (tf.keras.callback.History):
                A history object containing training details.


        """
        if target_epsilon is None:
            client = x.dataset.client

            target_epsilon = client.session.get(
                f"{client.base_url}/datasets/{x.dataset.id}/default_epsilon"
            ).json()

        if target_epsilon < 0:
            raise ValueError(
                f"`target_epsilon` must be positive, got {target_epsilon}"
            )

        if target_epsilon == 0:
            if epochs is None:
                raise ValueError(
                    "The number of `epochs` should be provided when "
                    "`target_epsilon` is 0"
                )

            if dp_l2_norm_clip:
                logging.warning(
                    "Ignoring `dp_l2_norm_clip` with local training "
                    "as `target_epsilon` = 0. Specify `target_epsilon` > 0 "
                    "if you want a remote DP-training"
                )

            if dp_noise_multiplier:
                logging.warning(
                    "Ignoring `dp_noise_multiplier` with local training "
                    "as `target_epsilon` = 0. Specify `target_epsilon` > 0 "
                    "if you want a remote DP-training"
                )

            if dp_num_microbatches:
                logging.warning(
                    "Ignoring `dp_num_microbatches` with local training "
                    "as `target_epsilon` = 0. Specify `target_epsilon` > 0 "
                    "if you want a remote DP-training"
                )

            return self._fit_local(
                x=x,
                y=y,
                batch_size=batch_size,
                verbose=verbose,
                epochs=epochs,
                callbacks=callbacks,
                validation_split=validation_split,
                validation_data=validation_data,
                shuffle=shuffle,
                class_weight=class_weight,
                sample_weight=sample_weight,
                initial_epoch=initial_epoch,
                steps_per_epoch=steps_per_epoch,
                validation_steps=validation_steps,
                validation_batch_size=validation_batch_size,
                validation_freq=validation_freq,
                max_queue_size=max_queue_size,
                workers=workers,
                use_multiprocessing=use_multiprocessing,
                **kwargs,
            )
        else:
            if not isinstance(x, Dataset):
                raise TypeError(
                    "Expected `x` to be a sarus.tensorflow.Dataset when"
                    " `target_epsilon` > 0."
                )

            if x.original is True:
                raise ValueError(
                    "Training a model remotely using a "
                    "sarus.tensorflow.Dataset with `original`=True is not "
                    "supported yet."
                )

            if validation_data:
                logging.warning(
                    "Ignoring `validation_data` with remote training. "
                    "Not supported yet."
                )

            if epochs is not None and dp_noise_multiplier is not None:
                logging.warning(
                    "Only 1 parameter among `epochs` and `dp_noise_multiplier`"
                    " can be taken into account to satisfy `target_epsilon`. "
                    "Changing `epochs`."
                )

            return self._fit_remote(
                x=x,
                epochs=epochs,
                target_epsilon=target_epsilon,
                dp_l2_norm_clip=dp_l2_norm_clip,
                dp_noise_multiplier=dp_noise_multiplier,
                dp_num_microbatches=dp_num_microbatches,
                verbose=verbose,
            )

    def _fit_local(
        self,
        x: Data,
        y: Data,
        batch_size: Optional[int],
        verbose: Union[int, str],
        epochs: int,
        callbacks: List[tf.keras.callbacks.Callback],
        validation_split: float,
        validation_data: Data,
        shuffle: Union[bool, str],
        class_weight: Optional[Dict[int, float]],
        sample_weight: Optional[np.ndarray] = None,
        initial_epoch: int = 0,
        steps_per_epoch: Optional[int] = None,
        validation_steps: Optional[int] = None,
        validation_batch_size: Optional[int] = None,
        validation_freq: Union[int, Container[int]] = 1,
        max_queue_size: int = 10,
        workers: int = 1,
        use_multiprocessing: bool = False,
        **kwargs: Any,
    ) -> tf.keras.callbacks.History:
        if isinstance(x, Dataset):
            x = x._tensorflow()
            logging.info("Fitting model locally on synthetic data.")
        if isinstance(validation_data, Dataset):
            validation_data = validation_data._tensorflow()
        history = super().fit(
            x=x,
            y=y,
            batch_size=batch_size,
            verbose=verbose,
            epochs=epochs,
            callbacks=callbacks,
            validation_split=validation_split,
            validation_data=validation_data,
            shuffle=shuffle,
            class_weight=class_weight,
            initial_epoch=initial_epoch,
            steps_per_epoch=steps_per_epoch,
            validation_steps=validation_steps,
            validation_batch_size=validation_batch_size,
            validation_freq=validation_freq,
            max_queue_size=max_queue_size,
            workers=workers,
            use_multiprocessing=use_multiprocessing,
            **kwargs,
        )
        return history

    def _fit_remote(
        self,
        x: Dataset,
        target_epsilon: float,
        dp_l2_norm_clip: Optional[float] = None,
        dp_noise_multiplier: Optional[float] = None,
        dp_num_microbatches: Optional[int] = None,  # default: batch size
        verbose: bool = True,
        epochs: Optional[int] = None,
        **kwargs: Any,
    ) -> tf.keras.callbacks.History:
        client = x.dataset.client
        if client is None:
            raise ValueError(
                f"The Sarus Dataset client is None: can not fit "
                f"remotely with `target_epsilon`={target_epsilon}."
            )

        batch_size, transforms = Model._refactor_transforms(
            x.dataset.transforms
        )

        if dp_num_microbatches and batch_size % dp_num_microbatches != 0:
            raise ValueError(
                f"`batch_size` should be a multiple of `dp_num_microbatches`, "
                f"got {batch_size} and {dp_num_microbatches}"
            )

        transform_def = Model._make_transform_def(transforms)

        # Set loss reduction to None for DP-SGD
        previous_reduction = self.loss.reduction
        self.loss.reduction = tf.keras.losses.Reduction.NONE
        if previous_reduction != tf.keras.losses.Reduction.NONE:
            logging.info("Setting losses.Reduction to NONE for DP-SGD.")

        try:
            # Build model weights
            self.predict(
                transform_def(
                    x.dataset._synthetic_as_tf_dataset(
                        batch_size=batch_size,
                        rows_number=None,
                        original=False,
                    )
                ).take(1)
            )

            # Push the model to the server
            serialized_model = Model._serialize_model(self)
            keras_model_resp = client.session.post(
                f"{client.base_url}/tasks_input_blobs",
                data=serialized_model,
            )
            if keras_model_resp.status_code > 200:
                raise Exception(
                    "Error while retrieving the model"
                    f"Full Gateway answer was:{keras_model_resp}"
                )
            keras_model_id = keras_model_resp.json()["id"]

            # Push the transform definition to the server
            # WARNING pickled functions require exactly same Python version b/w
            # sender and receiver (currently it is 3.6)
            if verbose:
                logging.info("Retrieving the preprocessing function")
            serialized_transform_def = cloudpickle.dumps(transform_def)
            transform_def_resp = client.session.post(
                f"{client.base_url}/tasks_input_blobs",
                data=serialized_transform_def,
            )
            if transform_def_resp.status_code > 200:
                raise Exception(
                    "Error while retrieving the preprocessing function"
                    f"Full Gateway answer was:{transform_def_resp}"
                )
            transform_def_id = transform_def_resp.json()["id"]

            # Launch the fit tasks
            request = client.session.post(
                f"{client.base_url}/fit",
                json={
                    "transform_def_id": transform_def_id,
                    "keras_model_id": keras_model_id,
                    "x_id": x.dataset.id,
                    "target_epsilon": target_epsilon,
                    "non_DP_training": False,
                    "batch_size": batch_size,
                    "dp_l2_norm_clip": dp_l2_norm_clip,
                    "dp_noise_multiplier": dp_noise_multiplier,
                    "dp_num_microbatches": dp_num_microbatches,
                    "seed": None,
                    "verbose": verbose,
                    "wait_for_completion": False,
                    "epochs": epochs,
                    **kwargs,
                },
            )
            if request.status_code > 200:
                if request.status_code == 403:
                    raise ValueError(
                        "Query failed with the following error: Privacy budget "
                        "limit exceeded"
                    )
                raise Exception(
                    f"Error while training the model.\
                                Full Gateway answer was:{request}"
                )
            task_id = request.json()["task"]
            if verbose:
                logging.info(f"Fitting task id: {task_id}")

            status = client._poll_training_status(task_id)
            error_message = status.get("error_message", None)
            if error_message:
                raise RuntimeError(
                    f"Training failed with the following error:\n"
                    f"{textwrap.indent(error_message, '  |')}"
                )

        finally:
            # Restore previous loss reduction
            self.loss.reduction = previous_reduction

        training_status = client._training_status(task_id)
        if "error_message" not in training_status:
            # Set fetched weights to model
            trained_model: tf.keras.Model = client._fetch_model(task_id)
            self.set_weights(trained_model.get_weights())

            # History
            history = tf.keras.callbacks.History()
            history.history = json.loads(
                training_status["result"].replace("'", '"')
            )
            if "qb_output_params" in training_status:
                history.params = json.loads(
                    training_status["qb_output_params"].replace("'", '"')
                )
            return history

    @staticmethod
    def _refactor_transforms(
        transforms: List[Transform],
    ) -> Tuple[int, List[Transform]]:
        """Refactor the `transforms`.

        Merge consecutive `batch` and `unbatch` operations for more efficient
        processign on the API side.

        Refactor the `split` transform to be applied on a batched dataset.

        NB: this could be removed once the API does not batch by default.
        """
        transform_types = [transform[0] for transform in transforms]

        if transform_types.count("batch") > 1:
            raise ValueError(
                "A Sarus Tensorflow Dataset can only be batched once "
                "for remote private training."
            )
        elif transform_types.count("batch") == 1:
            # The effective batch_size is the one defined in the batch operation
            batch_index = transform_types.index("batch")
            batch_transform = transforms[batch_index]
            batch_size = batch_transform[1]["batch_size"]
        else:
            # Unbatched dataset, rows will be retrieved one by one
            batch_size = 1

        if (
            "map" in transform_types
            and "batch" in transform_types
            and transform_types.index("map") < transform_types.index("batch")
        ):
            logging.warn(
                "A `map` has been applied before `batch`. "
                "The training performance will be degraded."
            )

        if len(transform_types) >= 2 and transform_types[:2] == [
            "unbatch",
            "batch",
        ]:
            # Safely merge batch and unbatch
            transforms = transforms[2:]
        elif len(transform_types) >= 3 and transform_types[:3] == [
            "unbatch",
            "split",
            "batch",
        ]:
            # Merge batch and unbatch but adapt split
            split_transform = transforms[1]
            start, end = split_transform[1]["start"], split_transform[1]["end"]
            new_split_transform = (
                "split",
                {"start": start // batch_size, "end": end // batch_size},
            )
            transforms = [new_split_transform] + transforms[3:]

        return batch_size, transforms

    @staticmethod
    def _make_transform_def(transforms: List[Transform]) -> Callable:
        def transform_def(
            ds: tf.data.Dataset, features: Optional[Dict] = None
        ) -> tf.data.Dataset:
            """Build a function to be sent remotely.

            This function should not make use of objects or functions defined
            in the Sarus module to avoid it being listed as a closure by
            cloudpickle.
            """
            func_mapping = {
                "map": lambda ds, params: ds.map(**params),
                "batch": lambda ds, params: ds.batch(**params),
                "unbatch": lambda ds, params: ds.unbatch(**params),
                "filter": lambda ds, params: ds.filter(**params),
            }
            for name, params in transforms:
                if name in func_mapping:
                    ds = func_mapping[name](ds, params)
                elif name == "split":
                    size = params["end"] - params["start"]
                    ds = ds.skip(params["start"]).take(size)
            return ds

        return transform_def

    @staticmethod
    def _serialize_model(model: tf.keras.Model) -> bytes:
        """Convert a keras Model to compressed archive format."""
        with tempfile.TemporaryDirectory() as _dir:
            logger = logging.getLogger("tensorflow")
            logger.setLevel(logging.WARNING)
            model.save(_dir)
            logger.setLevel(logging.INFO)
            with tempfile.TemporaryDirectory() as _second_dir:
                path = os.path.join(_second_dir, "tmpzip")
                with tarfile.open(path, mode="w:gz") as archive:
                    archive.add(_dir, recursive=True, arcname="")
                with open(path, "rb") as f:
                    ret = f.read()
                    return ret
