import pickle
from collections import defaultdict

import numpy as np
import pyro
import torch
from pyro.infer import SVI, Predictive, Trace_ELBO
from tqdm import tqdm

from pyromaniac.posterior import Posterior


class Handler(object):
    def __init__(self, *args, **kwargs):
        pass

    def fit(self):
        raise NotImplementedError

    def predict(self):
        raise NotImplementedError

    def dump_posterior(self, file_name: str):
        assert self.posterior is not None, "'init_svi' needs to be called first"
        pickle.dump(self.posterior.data, open(file_name, "wb"))

    def load_posterior(self, file_name):
        self.posterior = Posterior(pickle.load(open(file_name, "rb")))


class SVIHandler(Handler):
    """
    Helper object that abstracts some of numpyros complexities. Inspired
    by an implementation of Florian Wilhelm.
    :param model: A numpyro model.
    :param guide: A numpyro guide.
    :param loss: Loss function, defaults to Trace_ELBO.
    :param lr: Learning rate, defaults to 0.01.
    :param rng_key: Random seed, defaults to 254.
    :param num_epochs: Number of epochs to train the model, defaults to 5000.
    :param num_samples: Number of posterior samples.
    :param log_func: Logging function, defaults to print.
    :param log_freq: Frequency of logging, defaults to 0 (no logging).
    :param to_numpy: Convert the posterior distribution to numpy array(s),
        defaults to True.
    """

    def __init__(
        self,
        model,
        guide,
        loss: Trace_ELBO = pyro.infer.Trace_ELBO,
        optimizer=torch.optim.Adam,
        scheduler=pyro.optim.ReduceLROnPlateau,
        seed=None,
        num_epochs: int = 30000,
        num_samples: int = 1000,
        log_freq: int = 10,
        checkpoint_freq: int = 500,
        dev=True,
        to_numpy: bool = True,
        optimizer_kwargs: dict = {"lr": 1e-2},
        scheduler_kwargs: dict = {"factor": 0.99},
        loss_kwargs: dict = {"num_particles": 1},
    ):
        pyro.clear_param_store()
        if seed is not None:
            pyro.set_rng_seed(seed)
        self.model = model
        self.guide = guide
        self.loss = loss(**loss_kwargs)
        self.scheduler = False if scheduler is None else True
        self.seed = seed

        if self.scheduler:
            self.optimizer = scheduler(
                {
                    "optimizer": optimizer,
                    "optim_args": optimizer_kwargs,
                    **scheduler_kwargs,
                }
            )
        else:
            self.optimizer = optimizer(optimizer_kwargs)

        self.svi = self._init_svi()
        self.init_state = None

        self.log_freq = log_freq
        self.checkpoint_freq = checkpoint_freq
        self.log_learning_rates = defaultdict(list)
        self.log_gradient_norms = defaultdict(list)
        self.log_parameter_vals = defaultdict(list)
        self.checkpoints = {}
        self.num_epochs = num_epochs
        self.num_samples = num_samples

        self.loss = None
        self.to_numpy = to_numpy
        self.steps = 0
        self.dev = dev

    def _update_state(self, loss):
        self.loss = loss if self.loss is None else np.concatenate([self.loss, loss])

    def _init_svi(self):
        """
        Initialises the SVI.
        """
        return SVI(self.model, self.guide, self.optimizer, loss=self.loss)

    def _set_lr(self, lr):
        # this works for CLIPPED adam
        # checl if optim_objs is presetn
        if hasattr(self.optimizer, "optim_objs"):
            for opt in self.optimizer.optim_objs.values():
                for group in opt.param_groups:
                    group["lr"] = lr
        else:
            pass
            # for group in self.optimizer.optim_objs.values():
            #     group['lr'] = lr

    def _get_learning_rate(self):
        """
        Extracts the learning rate from the first parameter.
        TODO: return a dict(lr: [params])
        """
        for name, param in self.optimizer.get_state().items():
            if "optimizer" in param:
                lr = param["optimizer"]["param_groups"][0]["lr"]
            else:
                lr = param["param_groups"][0]["lr"]
            break
        return lr

    def _get_param_store(self):
        return {
            k: v.detach().cpu().numpy() for k, v in dict(pyro.get_param_store()).items()
        }

    def _track_learning_rate(self):
        """
        Tracks the learning rate during training.
        """
        for name, param in self.optimizer.get_state().items():
            if "optimizer" in param:
                self.log_learning_rates[name].append(
                    param["optimizer"]["param_groups"][0]["lr"]
                )
            else:
                self.log_learning_rates[name].append(param["param_groups"][0]["lr"])

    def initialize(self, seed):
        pyro.set_rng_seed(seed)
        pyro.clear_param_store()
        self._init_svi()
        return self.svi.step()

    def _register_gradient_hook(self):
        # Register hooks to monitor gradient norms.

        for name, value in pyro.get_param_store().named_parameters():
            value.register_hook(
                lambda g, name=name: self.log_gradient_norms[name].append(
                    g.norm().item()
                )
            )

    def _fit(self, *args, **kwargs):
        losses = []
        pbar = tqdm(range(self.steps, self.steps + self.num_epochs))
        failure = False

        previous_elbo = 0
        best_elbo = np.inf
        delta = 0

        try:
            for i in pbar:
                current_elbo = self.svi.step(*args, **kwargs)
                losses.append(current_elbo)

                if i == 0:
                    self._register_gradient_hook()
                    best_elbo = current_elbo
                else:
                    improvement = best_elbo - current_elbo
                    if improvement > 0:
                        best_elbo = current_elbo

                if self.dev:
                    self._track_learning_rate()

                if i % self.log_freq == 0:
                    lr = self._get_learning_rate()
                    pbar.set_description(
                        f"Epoch: {i} | lr: {lr:.2E} | ELBO: {current_elbo:.0f} | Δ_{self.log_freq}: {delta:.2f} | Best: {best_elbo:.0f}"
                    )
                    if i > 0:
                        delta = previous_elbo - current_elbo
                    previous_elbo = current_elbo

                if i % self.checkpoint_freq == 0:
                    self.checkpoints[i] = self._get_param_store()

                if self.scheduler:
                    if issubclass(
                        self.optimizer.pt_scheduler_constructor,
                        torch.optim.lr_scheduler.ReduceLROnPlateau,
                    ):
                        self.optimizer.step(current_elbo)
                    else:
                        self.optimizer.step()
        except KeyboardInterrupt:
            # TODO: use warning
            print("Stoping training ...")
            failure = True

        if failure:
            self.steps += i
        else:
            self.steps += self.num_epochs

        return losses

    def fit(self, *args, **kwargs):
        self.num_epochs = kwargs.pop("num_epochs", self.num_epochs)
        lr = kwargs.pop("lr", None)
        if lr is not None:
            self._set_lr(lr)
        predictive_kwargs = kwargs.pop("predictive_kwargs", {})

        # if self.init_state is None:
        #     self.init_state = self.svi.init(self.rng_key, *args)

        loss = self._fit(*args, **kwargs)
        self._update_state(loss)
        self.params = self._get_param_store()

        predictive = Predictive(
            self.model,
            guide=self.guide,
            num_samples=self.num_samples,
            **predictive_kwargs,
        )

        self.posterior = Posterior(
            {k: v for k, v in predictive(*args, **kwargs).items()},
            to_numpy=self.to_numpy,
        )

    def predict(self, *args, **kwargs):
        """kwargs -> Predictive, args -> predictive"""
        num_samples = kwargs.pop("num_samples", self.num_samples)
        # rng_key = kwargs.pop("rng_key", self.rng_key)

        predictive = Predictive(
            self.model,
            guide=self.guide,
            # posterior_samples=self.params,
            num_samples=num_samples,
            **kwargs,
        )

        self.predictive = Posterior(predictive(*args), self.to_numpy)

    def dump_params(self, file_name: str):
        assert self.params is not None, "'init_svi' needs to be called first"
        pickle.dump(self.params, open(file_name, "wb"))

    def load_params(self, file_name):
        self.params = pickle.load(open(file_name, "rb"))


class SVIModel(SVIHandler):
    """
    Abstract class of the SVI handler. To be used classes that implement
    a numpyro model and guide.
    """

    def __init__(self, **kwargs):
        super().__init__(self.model, self.guide, **kwargs)

    @property
    def _latent_variables(self):
        """
        Returns the latent variables of the model.
        """
        raise NotImplementedError()

    def model(self):
        raise NotImplementedError()

    def guide(self):
        raise NotImplementedError()

    def fit(
        self, predictive_kwargs: dict = {}, deterministic: bool = True, *args, **kwargs
    ):
        if len(predictive_kwargs) == 0:
            predictive_kwargs["return_sites"] = tuple(self._latent_variables)

        super().fit(self, predictive_kwargs=predictive_kwargs, *args, **kwargs)

        if deterministic:
            self.deterministic()

    def deterministic(self):
        pass
