import torch
import wandb
import pandas as pd
import numpy as np
from typing import Union
from pathlib import Path
from torchinfo import summary
from tqdm import tqdm
from torchvision.utils import make_grid

from src.models.colorme.model import ColorMeModel
from src.trainers.base_trainer import Trainer
from src.models.utils import cosine_scheduler
from src.utils.utils import clip_gradients
from src.utils.utils import get_world_size
from src.utils.utils import set_requires_grad


class ColorMeTrainer(Trainer):

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
                         arch_name='ColorMe')
        if not evaluation:
            # configs for easy access
            self.w_mse = config['loss']['weight_mse']
            self.w_kld = config['loss']['weight_kld']
            # MSE: reconstruction of original image
            self.mse_loss = torch.nn.MSELoss(reduction='mean')
            self.mse_loss = self.mse_loss.to(self.device)
            # KLD: color distribution prediction
            self.kld_loss = torch.nn.KLDivLoss(reduction='sum')
            self.kld_loss = self.kld_loss.to(self.device)
            # create model
            self.model = ColorMeModel(
                num_classes=2, encoder_name=self.config['model']['base_model'])
            self.model = self.model.to(self.device)
            self.model = torch.nn.SyncBatchNorm.convert_sync_batchnorm(
                self.model)
            self.model = self.distribute_model(self.model)
            wandb.watch(self.model, log='all')

            # summary of our model
            summary(self.model,
                    input_size=(self.config['batch_size'], 1, 224, 224))

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
            self.config['fine_tune_from'],
            run_variables=to_restore,
            state_dict=self.model,
            optimizer=optimizer,
            mse_loss=self.mse_loss,
            kld_loss=self.kld_loss,
        )
        self.start_epoch = to_restore["epoch"]
        self.config = to_restore["config"]

        # save the config.yaml file
        self._save_config_file(self.run_dir / 'checkpoints')

        # training loop
        n_iter = 0
        for epoch in range(self.start_epoch, self.config['epochs'] + 1):
            self.train_dataset.sampler.set_epoch(epoch-1)
            prog_bar = tqdm(self.train_dataset)
            self.model.train()
            for imgs, imgs_g, hists, _ in prog_bar:
                # update weight decay and LR according to their schedule
                self.update_optim_from_schedulers(optimizer, lr_schedule,
                                                  wd_schedule, n_iter)

                # move batch to device
                imgs = imgs.to(self.device)
                imgs_g = imgs_g.to(self.device)
                hists = hists.to(self.device)

                # zero the parameter gradients
                optimizer.zero_grad()

                # forward pass
                loss, l_kld, l_mse, entropy = self._model_step(
                    self.model, imgs, imgs_g, hists, n_iter)
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
                    'kld_loss': l_kld,
                    'mse_loss': l_mse,
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
                self._log_embeddings(
                    self.model,
                    n_iter=n_iter,
                    log_reconstruction=self.config['visualize_reconstruction'])

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
                    'mse_loss': self.mse_loss.state_dict(),
                    'kld_loss': self.kld_loss.state_dict(),
                }
                self._save_checkpoint(save_dict, epoch)

    def _model_step(self,
                    model,
                    imgs,
                    imgs_g,
                    hists,
                    n_iter: int,
                    log_artifacts=False):
        # run one forward pass
        pred_imgs, pred_hists = model(imgs_g)

        # reconstruct the original image back and compare it to
        # the true images (according to the paper)
        pred_imgs = torch.concat([
            pred_imgs[:, 0, :, :][:, None, :, :],
            imgs_g,
            pred_imgs[:, 1, :, :][:, None, :, :]
        ], dim=1)

        # calculate losses
        l_kld = self.kld_loss(pred_hists.log(), hists) * self.w_kld
        l_mse = self.mse_loss(pred_imgs, imgs) * self.w_mse
        loss = l_mse + l_kld

        # calculate the entropy of the emb. space
        embeds = model(imgs_g, return_embedding=True)
        entropy = self.calculate_embedding_entropy(embeds)

        # logging artifacts
        if log_artifacts:
            for idx in range(self.config['imgs_to_visualize']):
                # create reconstructed grid
                img_grid = make_grid([pred_imgs[idx], imgs[idx]])

                # color distribution
                pred_hist = pred_hists[idx].detach().cpu().numpy()
                true_hist = hists[idx].detach().cpu().numpy()
                groups = {
                    'predicted': pred_hist,
                    'actual': true_hist,
                }
                cols = [f'red_{x}' for x in range(5)]
                cols += [f'blue_{x}' for x in range(5)]

                data = []
                for g, values in groups.items():
                    for v, k in zip(values, cols):
                        data.append([g, k, v])

                table = wandb.Table(data=data,
                                    columns=['group', 'key', 'value'])

                wandb.log(
                    {
                        f'ColorMe/example_rec_{idx}': wandb.Image(img_grid),
                        f'ColorMe/color_distribution_{idx}': table
                    },
                    step=n_iter)

        return loss, l_kld, l_mse, entropy

    def _validate(self, model, valid_loader, n_iter: int):
        model.eval()
        with torch.no_grad():
            valid_loss = 0.0
            counter = 0
            for imgs, imgs_g, hists, _ in valid_loader:
                imgs = imgs.to(self.device)
                imgs_g = imgs_g.to(self.device)
                hists = hists.to(self.device)
                loss, _, _, _ = self._model_step(model,
                                                 imgs,
                                                 imgs_g,
                                                 hists,
                                                 n_iter=n_iter,
                                                 log_artifacts=(counter == 0))
                valid_loss += loss.item()
                counter += 1
            valid_loss /= counter
        return valid_loss

    def _log_embeddings(self,
                        model,
                        n_iter: int,
                        n_items: int = 1_000,
                        log_reconstruction: bool = False):
        model.eval()
        with torch.no_grad():
            l_imgs = []
            l_lbls = []
            l_embeddings = []
            l_entropy = []
            for idx, (imgs, imgs_g, hists, lbl) in enumerate(self.val_dataset):
                imgs = imgs.to(self.device)
                imgs_g = imgs_g.to(self.device)
                hists = hists.to(self.device)
                # get the embeddings
                embeds = self._get_embedding(model, imgs_g)
                ent_emb = self.calculate_embedding_entropy(embeds)
                # log one reconstructed image
                if log_reconstruction:
                    if idx == 0:
                        self._model_step(model,
                                         imgs,
                                         imgs_g,
                                         hists,
                                         n_iter=n_iter,
                                         log_artifacts=True)
                # add info to lists
                l_embeddings.append(embeds.cpu().numpy())
                l_imgs.append(imgs.cpu().numpy())
                l_lbls.append(lbl.cpu())
                l_entropy.append(ent_emb)

        # create (concat) our embedding space
        embeddings = np.concatenate(l_embeddings, axis=0)
        embeddings = torch.Tensor(embeddings)
        imgs = np.concatenate(l_imgs, axis=0)
        imgs = torch.Tensor(imgs)

        # entropy embedding space
        ent_avg = torch.mean(torch.Tensor(l_entropy)[:, 0])
        ent_min = torch.mean(torch.Tensor(l_entropy)[:, 1])
        ent_max = torch.mean(torch.Tensor(l_entropy)[:, 2])
        ent_std = torch.mean(torch.Tensor(l_entropy)[:, 3])
        ent_med = torch.mean(torch.Tensor(l_entropy)[:, 4])

        # nearest neighbors
        self._visualize_nearest_neighbors(embeddings, imgs, n_iter=n_iter)

        # select only N items (otherwise the embedding logging is to slow)
        lbls = torch.cat(l_lbls, dim=0)
        embeddings = embeddings[:n_items]
        imgs = imgs[:n_items]
        lbls = lbls[:n_items]

        # log the embeddings to wandb
        imgs = [wandb.Image(x) for x in imgs]
        df_emb = pd.DataFrame(embeddings.tolist())
        emb_cols = [f"dim_{x+1}" for x in range(embeddings[0].size()[0])]
        df_emb.columns = emb_cols
        df_emb['lbls'] = lbls.tolist()
        df_emb['image'] = imgs
        cols = df_emb.columns.tolist()
        df_emb = df_emb[cols[-1:] + cols[:-1]]
        wandb.log({
            "embeddings": df_emb,
            'entropy/val_ent_avg': ent_avg,
            'entropy/val_ent_min': ent_min,
            'entropy/val_ent_max': ent_max,
            'entropy/val_ent_std': ent_std,
            'entropy/val_ent_med': ent_med,
        }, step=n_iter)

    def _get_embedding(self, model, imgs_g):
        embeddings = model(imgs_g, return_embedding=True)
        return embeddings
