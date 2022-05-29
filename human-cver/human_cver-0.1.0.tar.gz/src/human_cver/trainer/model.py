import pytorch_lightning as pl
import torch  # do not remove
import torch.nn as nn
from torchvision.utils import make_grid

from ..tools.logger import Logger


class BaseModel(nn.Module):
    def __init__(self):
        super().__init__()

    def run_train(self, batch):
        raise NotImplementedError("not implemented!")

    def run_validation(self, batch):
        raise NotImplementedError("not implemented!")


class LightningModel(pl.LightningModule):
    def __init__(self, model, optimizer_cfg, scheduler_cfg) -> None:
        super().__init__()

        self.model = model
        self.optimizer_cfg = optimizer_cfg
        self.scheduler_cfg = scheduler_cfg
        self.log_img_cnt = 0

    def configure_optimizers(self):

        # optimizer
        optimizer_cls = f"torch.optim.{self.optimizer_cfg.target}"
        Logger.info(f"optimizer:{optimizer_cls}")
        optimizer = eval(optimizer_cls)(
            filter(lambda p: p.requires_grad, self.model.parameters()),
            **self.optimizer_cfg.params,
        )

        # scheduler
        scheduler_cls = f"torch.optim.lr_scheduler.{self.scheduler_cfg.target}"
        Logger.info(f"scheduler:{scheduler_cls}")
        scheduler = eval(scheduler_cls)(optimizer, **self.scheduler_cfg.params)

        return ({"optimizer": optimizer, "lr_scheduler": scheduler},)

    def log_img(self, img_dict_list):
        self.log_img_cnt += 1

        if img_dict_list is not None:
            tensorboard = self.logger.experiment[0]
            for img_dict in img_dict_list:
                name = img_dict["name"]
                img = img_dict["img"]
                nrow = img_dict["nrow"] if "nrow" in img_dict else 8
                tensorboard.add_image(name, make_grid(img, nrow=nrow), self.log_img_cnt)

    def training_step(self, batch, batch_idx):
        # run_train
        if not hasattr(self.model, "current_epoch"):
            setattr(self.model, "current_epoch", self.current_epoch)
        else:
            self.model.current_epoch = self.current_epoch

        total_loss, loss_dict, img_dict_list = self.model.run_train(batch)
        self.log_img(img_dict_list)

        for name, value in loss_dict.items():
            self.log(f"train/{name}", value, on_step=True, on_epoch=False)

        for name, value in loss_dict.items():
            self.log(f"train_epoch/{name}", value, on_step=False, on_epoch=True)

        return total_loss

    def validation_step(self, batch, batch_idx):
        # run_eval
        batch_size = batch[list(batch.keys())[0]].shape[0]
        total_loss, loss_dict, img_dict_list = self.model.run_validation(batch)
        self.log_img(img_dict_list)

        for name, value in loss_dict.items():
            self.log(f"eval/{name}", value, on_epoch=True)

        self.log(
            "eval_loss",
            total_loss,
            prog_bar=True,
        )
        loss_dict["_batch_size"] = batch_size
        return loss_dict

    def validation_epoch_end(self, loss_list):
        total_loss = dict()

        total_cnt = 0
        for loss_dict in loss_list:
            batch_size = loss_dict["_batch_size"]
            total_cnt += batch_size

            for name, loss in loss_dict.items():
                if name == "_batch_size":
                    continue

                if name not in total_loss:
                    total_loss[name] = 0
                total_loss[name] += loss * batch_size

        text = f"epoch={self.current_epoch:03d}, "
        for name in total_loss:
            loss = total_loss[name] / total_cnt
            text += f"{name}={loss:.5f}, "

        Logger.info(text[:-2])
