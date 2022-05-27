import torch
import torch.nn.functional as F
import wandb
from typing import Union
from pathlib import Path
from tqdm import tqdm
from torchinfo import summary
from torchvision.models.feature_extraction import create_feature_extractor

from src.losses.nt_xent import NTXentLoss
from src.models.simclr.model import ResNetSimCLR
from src.trainers.base_trainer import Trainer
from src.models.utils import cosine_scheduler
from src.utils.utils import clip_gradients
from src.utils.utils import get_world_size
from src.utils.utils import set_requires_grad


class SimCLRTrainer(Trainer):

    def __init__(self,
                 train_dataset,
                 val_dataset,
                 config: dict,
                 config_path: Union[str, Path],
                 evaluation: bool = False,
                 debug: bool = False):
        super().__init__(train_dataset,
                         val_dataset,
                         config,
                         config_path,
                         evaluation=evaluation,
                         debug=debug,
                         arch_name='SimCLR')
        if not evaluation:
            self.loss = NTXentLoss(self.device,
                                   config['batch_size'],
                                   **config['loss'])
            self.loss = self.loss.to(self.device)
            # create model
            self.model = ResNetSimCLR(**self.config["model"])
            self.model = self.model.to(self.device)
            self.model = torch.nn.SyncBatchNorm.convert_sync_batchnorm(
                self.model)
            self.model = self.distribute_model(self.model)
            wandb.watch(self.model, log='all')

            # summary of our model
            summary(self.model,
                    input_size=(self.config['batch_size'], 3, 224, 224))

    def fit(self):
        # create optimizer
        optimizer_cls = self.get_optimizer(self.config['optim'])
        optimizer = optimizer_cls(
            params=self.model.parameters(),
            lr=self.config['lr'],
            weight_decay=eval(self.config['weight_decay']))

        # create schedulers
        lr_schedule = cosine_scheduler(
            # linear scaling rule
            self.config['lr'] * (self.config['batch_size'] * get_world_size()) / 256.,
            eval(self.config['min_lr']),
            self.config['epochs'],
            len(self.train_dataset),
            warmup_epochs=self.config['warmup_epochs'],
        )
        wd_schedule = cosine_scheduler(
            eval(self.config['weight_decay']),
            self.config['weight_decay_end'],
            self.config['epochs'],
            len(self.train_dataset),
        )

        # load the model from checkpoint if provided
        to_restore = {"epoch": 1, 'config': self.config}
        self.restart_from_checkpoint(
            self.get_ckp_path / 'model_best.pth',
            run_variables=to_restore,
            state_dict=self.model,
            optimizer=optimizer,
            loss=self.loss,
        )
        self.start_epoch = to_restore["epoch"]
        self.config = to_restore["config"]

        # save the config.yaml file
        self._save_config_file(self.run_dir / 'checkpoints')

        # training loop
        n_iter = 0
        for epoch in range(self.start_epoch, self.config['epochs'] + 1):
            self.train_dataset.sampler.set_epoch(epoch-1)
            self.model.train()
            prog_bar = tqdm(self.train_dataset)
            for (xis, xjs), _ in prog_bar:
                # update weight decay and learning rate according to their schedule
                self.update_optim_from_schedulers(optimizer, lr_schedule,
                                                  wd_schedule, n_iter)

                # move batch to device
                xis, xjs = xis.to(self.device), xjs.to(self.device)

                # zero the parameter gradients
                optimizer.zero_grad()

                # forward pass
                loss, entropy = self._model_step(self.model, xis, xjs)
                ent_avg, ent_min, ent_max, ent_std, ent_med = entropy

                # check if loss is not infinite
                self.check_loss_nan(loss.detach())

                # update model
                loss.backward()
                if self.config['clip_grad']:
                    _ = clip_gradients(self.model, self.config['clip_grad'])
                optimizer.step()

                # log metrics
                prog_bar.set_description(f'Epoch: {epoch}, Train loss: {loss}')
                log_dict = {
                    'train_loss': loss,
                    'train_step': n_iter,
                    'lr': optimizer.param_groups[0]["lr"],
                    'weight_decay': optimizer.param_groups[0]["weight_decay"],
                    'epoch': epoch,
                    'entropy/train_ent_avg': ent_avg,
                    'entropy/train_ent_min': ent_min,
                    'entropy/train_ent_max': ent_max,
                    'entropy/train_ent_std': ent_std,
                    'entropy/train_ent_med': ent_med,
                }
                wandb.log(log_dict, step=n_iter)
                n_iter += 1

            # log the embeddings if wanted
            if epoch % self.config['embed_vis_every_n_epochs'] == 0:
                self._log_embeddings(self.model, n_iter=n_iter)

            # save the model
            if epoch % self.config['save_every_n_epochs'] == 0:
                if self.multi_gpu:
                    model = self.model.module.state_dict()
                else:
                    model = self.model.state_dict()
                save_dict = {
                    'arch': type(self.model).__name__,
                    'epoch': epoch,
                    'state_dict': model,
                    'optimizer': optimizer.state_dict(),
                    'config': self.config,
                    'loss': self.loss.state_dict(),
                }
                self._save_checkpoint(save_dict, epoch)
        # finish the run
        wandb.finish()

    def _model_step(self, model, xis, xjs):
        # get the embeddings and the projections
        eis, zis = model(xis)  # [N,C]
        ejs, zjs = model(xjs)  # [N,C]

        # calculate the entropy of the emb. space
        entropy = self.calculate_embedding_entropy(torch.concat([eis, ejs]))

        # normalize projection feature vectors
        zis = F.normalize(zis, dim=1)
        zjs = F.normalize(zjs, dim=1)

        return self.loss(zis, zjs), entropy

    def _validate(self, model, valid_loader):
        model.eval()
        with torch.no_grad():
            valid_loss = 0.0
            counter = 0
            for (xis, xjs), _ in valid_loader:
                xis, xjs = xis.to(self.device), xjs.to(self.device)
                loss, _ = self._model_step(model, xis, xjs)
                valid_loss += loss.detach()
                counter += 1
            valid_loss /= counter
        return valid_loss

    def _get_embedding(self, model, img) -> torch.Tensor:
        emb, _ = model(img)
        return emb
