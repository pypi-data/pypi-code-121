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
        lr: float = 0.001,
        rng_key: int = 254,
        num_epochs: int = 30000,
        num_samples: int = 1000,
        log_freq=10,
        to_numpy: bool = True,
        optimizer_kwargs: dict = {"lr": 1e-3},
        scheduler_kwargs: dict = {"factor": 0.99},
        loss_kwargs: dict = {"num_particles": 1},
    ):
        pyro.clear_param_store()
        self.model = model
        self.guide = guide
        self.loss = loss(**loss_kwargs)
        self.scheduler = False if scheduler is None else True

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

        self.svi = SVI(self.model, self.guide, self.optimizer, loss=self.loss)
        self.init_state = None

        self.log_freq = log_freq
        self.num_epochs = num_epochs
        self.num_samples = num_samples

        self.loss = None
        self.to_numpy = to_numpy
        self.steps = 0

        self._register_gradient_hook()

    def _register_gradient_hook(self):
        # Register hooks to monitor gradient norms.
        self.gradient_norms = defaultdict(list)
        for name, value in pyro.get_param_store().named_parameters():
            value.register_hook(
                lambda g, name=name: self.gradient_norms[name].append(g.norm().item())
            )

    def _fit(self, *args, **kwargs):
        losses = []
        pbar = tqdm(range(self.steps, self.steps + self.num_epochs))
        previous_elbo = 0
        delta = 0
        for i in pbar:
            current_elbo = self.svi.step(*args, **kwargs)
            losses.append(current_elbo)

            if i % self.log_freq == 0:
                if self.scheduler:
                    # lr = self.optimizer.get_last_lr()
                    for k, v in self.optimizer.get_state().items():
                        lr = v["optimizer"]["param_groups"][0]["lr"]
                        break
                    pbar.set_description(
                        f"It: {i} | lr: {lr:.6f} | ELBO {current_elbo:.2f} | Δ_{self.log_freq} {delta:.2f}"
                    )
                else:
                    pbar.set_description(
                        f"It: {i} | ELBO {current_elbo:.2f} | Δ_{self.log_freq} {delta:.2f}"
                    )
                delta = previous_elbo - current_elbo
                previous_elbo = current_elbo

            if self.scheduler:
                if issubclass(
                    self.optimizer.pt_scheduler_constructor,
                    torch.optim.lr_scheduler.ReduceLROnPlateau,
                ):
                    self.optimizer.step(current_elbo)
                else:
                    self.optimizer.step()

        self.steps += self.num_epochs

        return losses

    def _update_state(self, loss):
        self.loss = loss if self.loss is None else np.concatenate([self.loss, loss])

    def fit(self, *args, **kwargs):
        self.num_epochs = kwargs.pop("num_epochs", self.num_epochs)

        # reset learning rates
        #         lr = kwargs.pop("lr", None)
        #         if lr is not None:
        #             state = self.optimizer.get_state()
        #             for k, v in state.items():
        #                 v['param_groups'][0]['lr'] = lr

        #             self.optimizer.set_state(state)
        predictive_kwargs = kwargs.pop("predictive_kwargs", {})

        # if self.init_state is None:
        #     self.init_state = self.svi.init(self.rng_key, *args)

        loss = self._fit(*args, **kwargs)
        self._update_state(loss)
        self.params = {
            k: v.detach().cpu().numpy() for k, v in dict(pyro.get_param_store()).items()
        }

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

        self.fit(self, predictive_kwargs=predictive_kwargs, *args, **kwargs)

        if deterministic:
            self.deterministic()

    def deterministic(self):
        pass
