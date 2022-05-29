import argparse
import os.path as osp
import shutil
import sys
import pytorch_lightning as pl
from pytorch_lightning import seed_everything
from pytorch_lightning.callbacks import LearningRateMonitor, ModelCheckpoint
from pytorch_lightning.plugins import DDPPlugin
from pytorch_lightning.trainer import Trainer

from ..io.io import mkdir
from ..system import get_cpu_info, get_gpu_info, get_package_info
from ..tools import Logger, get_time_str
from .config import (get_log_dir, instantiate_from_config, load_config,
                     save_config)
from .dataset import LightningDataset
from .model import LightningModel
from .train_tips import get_train_tips

def train(config_filename: str) -> None:

    root_path = osp.abspath(config_filename).split("configs")[0]
    sys.path.insert(0, root_path)
    Logger.info(f"sys.path.insert(0, {root_path})")

    config = load_config(config_filename)

    task_name = config_filename.split("/")[1]
    exp_name = config_filename.split("/")[-1].split(".")[0]

    # log_dir
    log_dir = get_log_dir(config_filename)
    if osp.exists(log_dir):
        Logger.error("please create a new config!")
        return
    mkdir(log_dir)
    Logger.logfile(osp.join(log_dir, "train.log"), clear=True)
    Logger.info(f"mkdir: {log_dir}")

    # copy file
    copy_file_list = config.copy_file_list
    if copy_file_list is not None:
        for filename in copy_file_list:
            full_filename = osp.join(root_path, filename)
            if osp.exists(full_filename):
                dst = osp.join(log_dir, "code", filename)
                mkdir(osp.dirname(dst))
                shutil.copy(src=full_filename, dst=dst)
            else:
                Logger.warn(f"not exists: {full_filename}")

    # config
    new_config = osp.join(log_dir, "config.yaml")
    save_config(new_config, config)

    # log file
    Logger.info(f"train: {get_time_str()}")
    Logger.info(f"config: {config_filename}")

    # gpu, cpu, package info
    for key, value in get_gpu_info().items():
        Logger.info(f"{key}: {value}")
    for key, value in get_cpu_info().items():
        Logger.info(f"{key}: {value}")
    for key, value in get_package_info().items():
        Logger.info(f"{key}: {value}")

    # seed
    seed_everything(config.seed)
    Logger.info(f"seed:{config.seed}")

    Logger.info(f"gpus:{config.gpus}")
    Logger.info(f"precision:{config.precision}")
    Logger.info(f"train batch_size:{config.data.train.data_loader.batch_size}")
    Logger.info(f"train num_workers:{config.data.train.data_loader.num_workers}")
    Logger.info(f"save_top_k: {config.checkpoint.save_top_k}")
    Logger.info(f"save_last: {config.checkpoint.save_last}")

    resume_from_checkpoint = config.checkpoint.resume_from
    if resume_from_checkpoint:
        Logger.warn(f"resume from:{resume_from_checkpoint}")
    else:
        resume_from_checkpoint = None

    trainer = Trainer(
        precision=config.precision,
        gpus=config.gpus,
        sync_batchnorm=True,
        check_val_every_n_epoch=config.check_val_every_n_epoch,
        accumulate_grad_batches=config.accumulate_grad_batches,
        max_epochs=config.max_epochs,
        logger=[
            pl.loggers.TensorBoardLogger(
                save_dir="logs",
                name=task_name,
                version=exp_name,
            ),
        ],
        callbacks=[
            LearningRateMonitor(logging_interval="step"),
            ModelCheckpoint(
                dirpath=f"logs/{task_name}/{exp_name}/checkpoint",
                monitor="eval_loss",
                filename="{epoch:03d}_{eval_loss:.5f}",
                save_last=config.checkpoint.save_last,
                save_top_k=config.checkpoint.save_top_k,
            ),
        ],
        plugins=DDPPlugin(find_unused_parameters=config.find_unused_parameters),
        resume_from_checkpoint=resume_from_checkpoint,
        log_every_n_steps=config.log_every_n_steps,
        profiler="simple",
    )

    Logger.info("prepare to build model...")
    model = instantiate_from_config(config.model)
    lightning_model = LightningModel(
        model=model, optimizer_cfg=config.optimizer, scheduler_cfg=config.scheduler
    )

    Logger.info("prepare to build dataset...")
    data = LightningDataset(**config.data)
    
    Logger.info("prepare to train...")
    Logger.warn(f"tensorboard --logdir=logs/{task_name}")
    trainer.fit(lightning_model, data)


def train_main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "config", default="config.yaml", type=str, help="config filename"
    )

    args = parser.parse_args()

    if args.config == "tips":
        for cnt, tip in enumerate(get_train_tips()):
            title = tip["title"]
            url = tip["url"]
            Logger.warn(f"Tip {cnt+1}:")
            Logger.info(f"title: {title}")
            Logger.info(f"url: {url}")
            print()
        return
    elif not osp.exists(args.config):
        Logger.error(f"not exists: {args.config}")
        sys.exit(0)

    train(args.config)
