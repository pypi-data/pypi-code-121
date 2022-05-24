# -*- coding: utf-8 -*-

from __future__ import annotations

import logging
import os
import traceback
from collections.abc import Callable
from typing import Mapping, Optional, Union

import ignite.distributed as idist
import torch
import torch.nn as nn
from carton.logger import log_dict
from carton.logger import setup_logger as carton_setup_logger
from carton.random import set_seed
from ignite.contrib.engines.common import ProgressBar, setup_common_training_handlers
from ignite.contrib.handlers.base_logger import BaseLogger
from ignite.engine import Engine, Events
from ignite.handlers import DiskSaver
from ignite.metrics import BatchWise, EpochWise, Metric
from ignite.utils import convert_tensor, setup_logger
from torch.optim import Optimizer
from torch.optim.lr_scheduler import _LRScheduler
from torch.utils.data import DataLoader

from torchlight.training.handlers import handle_collator_mode, setup_extra_handlers
from torchlight.training.params import Params
from torchlight.utils.phase import ModeKeys

logger = logging.getLogger(__name__)

Dataflows = Mapping[str, DataLoader]
Metrics = Mapping[str, Metric]


def setup_env(params: Params):
    set_seed(params["seed"])

    os.makedirs(os.path.dirname(params["log_file"]), exist_ok=True)
    carton_setup_logger(level=params["log_level"], filename=params["log_file"])

    params.to_yaml(os.path.join(params.save_path, "params.yaml"))


def setup_engine(
    engine: Engine,
    name: str,
    log_file: Optional[str] = None,
    metrics: Optional[Metrics] = None,
    train: bool = True,
) -> Engine:
    engine.logger = setup_logger(name, filepath=log_file)

    if metrics:
        for metric_name, metric in metrics.items():
            metric.attach(
                engine, metric_name, usage=BatchWise() if train else EpochWise()
            )
    return engine


def create_trainer(
    train_step: Callable,
    params: Params,
    model: Union[nn.Module, nn.parallel.DistributedDataParallel],
    criteria: nn.Module,
    optimizer: Optimizer,
    lr_scheduler: Optional[_LRScheduler] = None,
    metrics: Optional[Metrics] = None,
    name: str = "trainer",
    with_handlers: bool = True,
) -> Engine:
    def step(engine, batch):
        model.train()
        batch = convert_tensor(
            batch, device=idist.device(), non_blocking=params.non_blocking
        )
        output = train_step(
            engine,
            model.module
            if isinstance(model, nn.parallel.DistributedDataParallel)
            else model,
            batch,
            criteria,
        )
        loss = output["loss"]
        loss.backward()
        if (
            not params.gradient_accumulation_steps
            or engine.state.iteration % params.gradient_accumulation_steps == 0
        ):
            if params.max_grad_norm is not None:
                torch.nn.utils.clip_grad_norm_(model.parameters(), params.max_grad_norm)
            optimizer.step()
            optimizer.zero_grad()
        engine.state.metrics["loss"] = loss.item()

        return output

    trainer = Engine(step)
    trainer = setup_engine(
        trainer, name, log_file=params.log_file, metrics=metrics, train=True
    )

    if with_handlers:
        if params.pbar_steps > 0:
            ProgressBar(ncols=0).attach(
                trainer,
                metric_names="all",
                event_name=Events.ITERATION_COMPLETED(every=params.pbar_steps),
                closing_event_name=Events.EPOCH_COMPLETED,
            )

        trainer.add_event_handler(
            Events.EPOCH_STARTED,
            handle_collator_mode,
            "train",
            ModeKeys.TRAIN,
        )

        to_save = {
            "trainer": trainer,
            "model": model,
            "optimizer": optimizer,
        }
        if lr_scheduler is not None:
            to_save.update({"lr_scheduler": lr_scheduler})

        setup_common_training_handlers(
            trainer,
            train_sampler=None,  # TODO
            to_save=to_save,
            save_every_iters=params.save_steps,
            lr_scheduler=lr_scheduler,  # TODO
            with_gpu_stats=False,
            output_names=["loss"],
            with_pbars=False,
            with_pbar_on_iters=False,
            log_every_iters=params.pbar_steps,
            stop_on_nan=True,
            clear_cuda_cache=False,
            save_handler=DiskSaver(params.save_path, require_empty=False),
        )
        logger.info("Setup common training handlers.")

        @trainer.on(Events.EXCEPTION_RAISED)
        def handle_exceptions(engine, e):
            if isinstance(e, KeyboardInterrupt):
                engine.logger.info("KeyboardInterrupt caught. Exiting gracefully.")
                trainer.terminate()
            else:
                traceback.print_exc()
                raise e

        logger.info("Setup exception handler.")

    return trainer


def create_evaluator(
    eval_step: Callable,
    params: Params,
    model: Union[nn.Module, nn.parallel.DistributedDataParallel],
    tag: str,
    metrics: Optional[Metrics] = None,
    with_handlers: bool = True,
) -> Engine:
    @torch.no_grad()
    def step(engine, batch):
        model.eval()
        batch = convert_tensor(
            batch, device=idist.device(), non_blocking=params.non_blocking
        )
        output = eval_step(
            engine,
            model.module
            if isinstance(model, nn.parallel.DistributedDataParallel)
            else model,
            batch,
        )

        return output

    evaluator = Engine(step)
    evaluator = setup_engine(
        evaluator,
        f"evaluator/{tag}",
        log_file=params.log_file,
        metrics=metrics,
        train=False,
    )

    if with_handlers:
        ProgressBar(ncols=0, desc=f"Evaluation [{tag}]").attach(
            evaluator,
            event_name=Events.ITERATION_COMPLETED(every=params.pbar_steps),
            closing_event_name=Events.EPOCH_COMPLETED,
        )

        evaluator.add_event_handler(
            Events.EPOCH_STARTED,
            handle_collator_mode,
            tag,
            ModeKeys.EVAL,
        )

    return evaluator


def create_evaluators(
    eval_step: Callable,
    params: Params,
    model: nn.Module,
    metrics: Optional[Metrics] = None,
    with_handlers: bool = True,
) -> dict[str, Engine]:
    return {
        mode: create_evaluator(
            eval_step, params, model, mode, metrics=metrics, with_handlers=with_handlers
        )
        for mode in ["train", "val", "test"]
    }


def create_engines(
    params: Params,
    train_step: Callable,
    eval_step: Callable,
    dataflows: Dataflows,
    model: Union[nn.Module, nn.parallel.DistributedDataParallel],
    criteria: nn.Module,
    optimizer: Optimizer,
    lr_scheduler: Optional[_LRScheduler] = None,
    train_metrics: Optional[Metrics] = None,
    eval_metrics: Optional[Metrics] = None,
    metrics: Optional[Metrics] = None,
    with_handlers: bool = True,
) -> Union[
    tuple[Engine, dict[str, Engine]],
    tuple[Engine, dict[str, Engine], dict[str, BaseLogger]],
]:
    # pylint: disable=too-many-arguments
    logger.info("Creating engines with params:")
    log_dict(logger, params.to_dict())

    if metrics:
        if train_metrics or eval_metrics:
            raise ValueError(
                "Either `metrics` or `train_metrics` and `eval_metrics`"
                " should be given"
            )
        train_metrics = metrics
        eval_metrics = metrics

    trainer = create_trainer(
        train_step,
        params,
        model,
        criteria,
        optimizer,
        lr_scheduler=lr_scheduler,
        metrics=train_metrics,
        with_handlers=with_handlers,
    )
    evaluators = create_evaluators(
        eval_step, params, model, eval_metrics, with_handlers=with_handlers
    )

    if with_handlers:
        loggers = setup_extra_handlers(
            params, trainer, evaluators, dataflows, model, optimizer
        )

        return trainer, evaluators, loggers

    return trainer, evaluators


def run(fn: Callable, params: Params, *args, **kwargs) -> None:
    with idist.Parallel(
        backend=params.backend,
        nnodes=params.nnodes,
        node_rank=params.node_rank,
        nproc_per_node=params.nproc_per_node,
        master_addr=params.master_addr,
        master_port=params.master_port,
        init_method=params.init_method,
    ) as parallel:
        parallel.run(fn, params, *args, **kwargs)
