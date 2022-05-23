import numpy as np
import tensorflow as tf
from typing import *


@tf.function
def _model_slice_inputs(inputs, i):
    # slice out model index from inputs
    if type(inputs) is tuple:
        return tuple(_model_slice_inputs(x, i) for x in inputs)
    return inputs[:, i]


@tf.function
def _tuple_stack(x, axis=1):
    # check if we have a list of tuples, if so then
    # we actually want to have a tuple of stacks
    if type(x[0]) is tuple:
        return tuple(tf.stack([xi[i] for xi in x], axis=axis) for i in range(len(x[0])))
    return tf.stack(x, axis=axis)


@tf.keras.utils.register_keras_serializable(package="kdens")
def neg_ll(y_true, y_pred):
    """Negative log-likelihood loss"""
    y_pred = tf.convert_to_tensor(y_pred)
    y_true = tf.cast(y_true, y_pred.dtype)
    loss = 0.5 * (
        tf.math.log(y_pred[..., 1])
        + tf.math.divide_no_nan((y_pred[..., 0] - y_true) ** 2, y_pred[..., 1])
    )
    return loss


def resample(
    y: np.ndarray, output_shape: tuple = (None, 5), nclasses: int = 10
) -> np.ndarray:
    """Resample the given y-vector to have a uniform classes,
    where the classes are chosen via histogramming y if doing regression.
    It returns **idx**, which is the index of the resampled y-vector, not
    the actual values.

    :param y: The vector of class labels.
    :param output_shape: The shape of the output array.
    :param nclasses: If regression task, will quantize y into nclasses. If 1, will simply resample
    :return: The index of the resampled y-vector.
    """
    if nclasses == 1:
        return np.random.choice(np.arange(y.shape[0]), size=output_shape)
    if len(y.shape) == 1:
        # regression
        _, bins = np.histogram(y, bins=nclasses)
        classes = np.digitize(y, bins)
    elif len(y.shape) == 2:
        # classification
        classes = np.argmax(y, axis=1)
        nclasses = y.shape[1]
    else:
        raise ValueError("y must rank 1 or 2")
    if output_shape[0] is None:
        output_shape = (y.shape[0], *output_shape[1:])
    uc = np.unique(classes)
    nclasses = uc.shape[0]
    idx = [np.where(classes == uc[i])[0] for i in range(nclasses)]
    c = np.random.choice(np.arange(nclasses), size=output_shape)
    f = np.vectorize(lambda i: np.random.choice(idx[i]))
    return f(c)


def map_tile(nmodels: int = 5, is_batched=False) -> Callable[..., Tuple[tf.Tensor]]:
    """Duplicate the given record to be compatible with the ensemble model.'

    Each record will be tiled and shaped to (nmodels, *x.shape) or (B, nmodels, *x.shape) if `is_batched = True`

    :param nmodels: The number of ensemble models
    :param is_batched: If the input is batched, so `nmodels` will go in the first axis.
    :return: A function to be used in `tf.data.Dataset.map`
    """

    def f(*xs: Union[Tuple[tf.Tensor], tf.Tensor]) -> Any:
        # xs can be tuple of tensors or tuple of tuples of tensors
        def parse_record(x: tf.Tensor) -> tf.Tensor:
            if is_batched:
                return tf.tile(
                    x[:, None],
                    tf.concat(
                        ([1], [nmodels], tf.ones(tf.rank(x) - 1, dtype=tf.int32)),
                        axis=0,
                    ),
                )
            else:
                return tf.tile(
                    x[None],
                    tf.concat(([nmodels], tf.ones(tf.rank(x), dtype=tf.int32)), axis=0),
                )

        return tuple(f(*x) if type(x) is tuple else parse_record(x) for x in xs)

    return f


def map_batch_reshape(nmodels: int = 5) -> Callable[..., Tuple[tf.Tensor]]:
    """Reshape the given batched record to be compatible with the ensemble model.'

    Each record will be reshaped to (B, nmodels, *x.shape[1:]). The batch size
    must be a multiple of the number of ensemble models

    :param nmodels: The number of ensemble models
    :return: A function to be used in `tf.data.Dataset.map`
    """

    def f(*xs: Union[Tuple[tf.Tensor], tf.Tensor]) -> Any:
        # xs can be tuple of tensors or tuple of tuples of tensors
        def parse_record(x: tf.Tensor) -> tf.Tensor:
            return tf.reshape(x, tf.concat(([-1], [nmodels], tf.shape(x)[1:]), axis=0))

        return tuple(f(*x) if type(x) is tuple else parse_record(x) for x in xs)

    return f


@tf.keras.utils.register_keras_serializable(package="kdens")
class DeepEnsemble(tf.keras.Model):
    """Bayesian Deep Ensemble model

    This model is a Bayesian Deep Ensemble model as described by Lakshminarayanan et al. It fits an ensemble
    of given models with negative log-likelihood loss. The output is 3 values --
    the mean, the variance, and the epistemic variance. This uses adversarial
    training that perturbs features following the original paper.

    If you would like the adveserial perturbation
    done at some intermediate layer (e.g., because your input is a discrete sequence), then
    set ``partial=True`` and have your ``build_fxn`` return a tuple of three models: the complete model,
    the first half of model which outputs the value to be adversarially perturbed, and the rest of the model.

    Citation: Lakshminarayanan, Balaji, Alexander Pritzel, and Charles Blundell. "Simple and scalable predictive uncertainty estimation using deep ensembles." Advances in neural information processing systems 30 (2017).

    :param build_fxn: A function that returns a :py:class:`tf.keras.model` or a tuple of :py:class:`tf.keras.model` (if ``partial=True``)
    :param nmodels: The number of models to use in the ensemble.
    :param adv_epsilon: The epsilon for adversarial perturbation.
    :param partial: Whether the build fxn breaks up model to enable perturabtion at intermediate layers.
    :param name: The name of the model.
    :param kwargs: Any additional arguments to pass to the keras model.
    """

    def __init__(
        self,
        build_fxn: Callable[[], Union[tf.keras.Model, Tuple[tf.keras.Model]]] = None,
        nmodels: int = 5,
        adv_epsilon: float = 1e-3,
        partial: bool = False,
        name: str = "deep-ensemble",
        **kwargs
    ):
        super(DeepEnsemble, self).__init__(name=name, **kwargs)
        self.nmodels = nmodels

        if build_fxn:
            if partial:
                self.models = []
                self.partials = []
                for i in range(self.nmodels):
                    m = build_fxn()
                    if len(m) != 3:
                        raise ValueError("Must return 3 models in partial mode")
                    self.models.append(m[0])
                    self.partials.append(m[1:])
            else:
                self.models = [build_fxn() for _ in range(nmodels)]
                self.partials = None
        self.loss_tracker = tf.keras.metrics.Mean(name="loss")
        self.adv_loss_tracker = tf.keras.metrics.Mean(name="adv_loss")
        self.eps = adv_epsilon

    def get_config(self):
        config = super(DeepEnsemble, self).get_config()
        config["nmodels"] = self.nmodels
        config["adv_epsilon"] = self.eps
        config["partial"] = self.partials is not None
        config["partials"] = self.partials
        config["models"] = self.models
        return config

    @classmethod
    def from_config(cls, config):
        m = config["models"]
        p = config["partials"]
        del config["models"]
        del config["partials"]
        obj = cls(**config)
        obj.partials = p
        obj.models = m

    def call(self, inputs, training=None):
        """See :py:class:`tf.keras.Model.call`"""
        outs = tf.stack(
            [self.models[i](inputs, training) for i in range(self.nmodels)], axis=1
        )
        outs = tf.stack(
            [outs[..., 0], tf.clip_by_value(outs[..., 1], 0, np.inf)], axis=-1
        )
        mu = tf.reduce_mean(outs[..., 0], axis=1)
        epi_var = tf.math.reduce_variance(outs[..., 0], axis=1)
        var = tf.reduce_mean(outs[..., 1] + outs[..., 0] ** 2, axis=1) - mu**2
        outs = tf.stack([mu, var, epi_var], axis=-1)
        return outs

    def full_call(self, inputs, training=None):
        """Call of models with complete model output (one for each ensemble model)

        :param inputs: The inputs to the model - tensor or tuple of tensors
        :param training: `training` flag passed to individual models
        """
        outs = tf.stack(
            [
                self.models[i](_model_slice_inputs(inputs, i), training)
                for i in range(self.nmodels)
            ],
            axis=1,
        )
        outs = tf.stack(
            [outs[..., 0], tf.clip_by_value(outs[..., 1], 0, np.inf)], axis=-1
        )
        return outs

    @property
    def metrics(self):
        """See :py:class:`tf.keras.Model.metrics`"""
        return [self.loss_tracker] + super(DeepEnsemble, self).metrics

    def train_step(self, data):
        """See :py:class:`tf.keras.Model.train_step`"""
        # Unpack the data. Its structure depends on your model and
        # on what you pass to `fit()`.
        if len(data) == 3:
            x, y, sample_weight = data
        else:
            x, y = data
            sample_weight = tf.ones_like(y)
        with tf.GradientTape() as tape:
            # do we need to do adv step partway through model?
            if self.partials:
                xh = _tuple_stack(
                    [
                        self.partials[i][0](_model_slice_inputs(x, i), True)
                        for i in range(self.nmodels)
                    ],
                    axis=1,
                )
                if type(xh) is tuple:
                    tape.watch(xh[0])
                else:
                    tape.watch(xh)
                outs = tf.stack(
                    [
                        self.partials[i][1](_model_slice_inputs(xh, i), True)
                        for i in range(self.nmodels)
                    ],
                    axis=1,
                )
            else:
                xh = x
                if type(xh) is tuple:
                    tape.watch(xh[0])
                else:
                    tape.watch(xh)
                outs = self.full_call(xh, training=True)  # Forward pass
            # Compute the loss value
            loss = self.compiled_loss(y, outs, regularization_losses=self.losses)

        # Compute gradients
        trainable_vars = self.trainable_variables
        if type(xh) is tuple:
            gradients, xgrad = tape.gradient(loss, [trainable_vars, xh[0]])
        else:
            gradients, xgrad = tape.gradient(loss, [trainable_vars, xh])
        # Update weights
        self.optimizer.apply_gradients(zip(gradients, trainable_vars))

        # adv step
        if type(xh) is tuple:
            xp = xh[0] + self.eps * tf.math.sign(xgrad), *xh[1:]
        else:
            xp = xh + self.eps * tf.math.sign(xgrad)

        with tf.GradientTape() as tape:
            if self.partials:
                outs = tf.stack(
                    [
                        self.partials[i][1](_model_slice_inputs(xp, i), True)
                        for i in range(self.nmodels)
                    ],
                    axis=1,
                )
            else:
                outs = self.full_call(xp, training=True)  # Forward pazss
            # Compute the loss value
            # (the loss function is configured in `compile()`)
            adv_loss = self.compiled_loss(y, outs, regularization_losses=self.losses)

        # Compute gradients
        trainable_vars = self.trainable_variables
        gradients = tape.gradient(adv_loss, trainable_vars)
        # Update weights
        self.optimizer.apply_gradients(
            [
                (grad, var)
                for (grad, var) in zip(gradients, self.trainable_variables)
                if grad is not None
            ]
        )

        # Update metrics (includes the metric that tracks the loss)
        self.compiled_metrics.update_state(y, outs[..., 0])
        self.loss_tracker.update_state(loss)
        self.adv_loss_tracker.update_state(adv_loss)
        # Return a dict mapping metric names to current value
        result = {
            "loss": self.loss_tracker.result(),
            "adv_loss": self.adv_loss_tracker.result(),
        }
        result.update({m.name: m.result() for m in self.metrics})
        return result

    def test_step(self, data):
        """See :py:class:`tf.keras.Model.test_step`"""
        # custom test step so metrics will receive just predicted valus
        # Unpack the data
        if len(data) == 3:
            x, y, sample_weight = data
        else:
            x, y = data
            sample_weight = tf.ones_like(y)
        # Compute predictions
        outs = self(x, training=False)
        mu = outs[..., 0]
        var = outs[..., 1]
        loss = self.compiled_loss(y, outs, regularization_losses=self.losses)
        self.compiled_metrics.update_state(y, mu)
        self.loss_tracker.update_state(loss)
        # Return a dict mapping metric names to current value
        result = {"loss": self.loss_tracker.result()}
        result.update({m.name: m.result() for m in self.metrics})
        return result
