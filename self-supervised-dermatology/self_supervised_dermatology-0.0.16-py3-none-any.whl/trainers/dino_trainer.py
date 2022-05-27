import torch
import wandb
import numpy as np
from tqdm import tqdm
from torchinfo import summary

from src.trainers.base_trainer import Trainer
from src.models.vit.vision_transformer import vit_tiny, vit_small, vit_base
from src.models.dino.head import DINOHead
from src.models.dino.multi_crop_wrapper import MultiCropWrapper
from src.losses.dino_loss import DINOLoss
from src.models.utils import get_params_groups, cosine_scheduler, cancel_gradients_last_layer
from src.utils.utils import set_requires_grad
from src.utils.utils import clip_gradients
from src.utils.utils import get_world_size
from src.utils.utils import set_requires_grad


class DINOTrainer(Trainer):

    def __init__(self,
                 train_dataset,
                 val_dataset,
                 config,
                 config_path,
                 evaluation: bool = False,
                 debug: bool = False):
        super().__init__(train_dataset,
                         val_dataset,
                         config,
                         config_path,
                         evaluation=evaluation,
                         debug=debug,
                         arch_name='DINO')
        # get the architecture for student and teacher
        self.vit_dict = {
            "vit_tiny": vit_tiny,
            "vit_small": vit_small,
            "vit_base": vit_base,
        }
        if not evaluation:
            model_arch = self.vit_dict.get(self.config['model']['base_model'],
                                           np.nan)
            if model_arch is np.nan:
                raise ValueError('Invalid base model name')
            self.student = model_arch(**self.config['model']['student'])
            self.teacher = model_arch(**self.config['model']['teacher'])
            self.embed_dim = self.student.embed_dim

            # useful configs
            self.n_g_crops = self.config['dataset']['augmentations']['global_crops_number']
            self.n_l_crops = self.config['dataset']['augmentations']['local_crops_number']

            # define the loss function
            self.loss = DINOLoss(out_dim=self.config['model']['out_dim'],
                                 n_epochs=self.config['epochs'],
                                 n_crops=self.n_g_crops + self.n_l_crops,
                                 n_g_crops=self.n_g_crops,
                                 **self.config['loss'])
            self.loss = self.loss.to(self.device)

    def fit(self):
        # build models (student and teacher)
        # multi-crop wrapper handles forward with inputs of diff. resolutions
        self.student = MultiCropWrapper(
            backbone=self.student,
            head=DINOHead(
                self.embed_dim,
                self.config['model']['out_dim'],
                use_bn=self.config['model']['use_bn_in_head'],
                norm_last_layer=self.config['model']['norm_last_layer'],
            ))
        self.student = self.student.to(self.device)
        self.student = self.distribute_model(self.student)
        wandb.watch(self.student, log='all')

        self.teacher = MultiCropWrapper(
            backbone=self.teacher,
            head=DINOHead(
                self.embed_dim,
                self.config['model']['out_dim'],
                use_bn=self.config['model']['use_bn_in_head']
            ))
        self.teacher = self.teacher.to(self.device)
        self.teacher = self.distribute_model(self.teacher)
        wandb.watch(self.teacher, log='all')

        # teacher and student start with the same weights
        self.teacher.load_state_dict(self.student.state_dict())
        # no backpropagation through the teacher, so no need for gradients
        set_requires_grad(self.teacher, False)
        print(f"Student and Teacher are built: they are both "
              f"{self.config['model']['base_model']} network.")

        # summary of the student and teacher
        print('*' * 20 + ' Student ' + '*' * 20)
        summary(self.student,
                input_size=(self.config['batch_size'], 3, 224, 224))
        print('*' * 20 + ' Teacher ' + '*' * 20)
        summary(self.teacher,
                input_size=(self.config['batch_size'], 3, 224, 224))

        # create optimizer
        params_groups = get_params_groups(self.student)
        # AdamW for ViT
        optimizer_cls = self.get_optimizer(self.config['optim'])
        optimizer = optimizer_cls(params_groups)

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
            self.config['weight_decay'],
            self.config['weight_decay_end'],
            self.config['epochs'],
            len(self.train_dataset),
        )
        # momentum parameter is increased to 1. during training with a cosine schedule
        momentum_schedule = cosine_scheduler(
            self.config['momentum_teacher'],
            1,
            self.config['epochs'],
            len(self.train_dataset),
        )

        # load the model from checkpoint if provided
        to_restore = {"epoch": 1, 'config': self.config}
        self.restart_from_checkpoint(
            self.get_ckp_path / 'model_best.pth',
            run_variables=to_restore,
            student=self.student,
            teacher=self.teacher,
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
            self.student.train()
            prog_bar = tqdm(self.train_dataset)
            for images, _ in prog_bar:
                # update weight decay and learning rate according to their schedule
                self.update_optim_from_schedulers(optimizer, lr_schedule,
                                                  wd_schedule, n_iter)

                # move images to device
                images = [im.to(self.device, non_blocking=True) for im in images]

                # zero the parameter gradients
                optimizer.zero_grad()

                # --- forward pass ---
                # only the 2 global views pass through the teacher
                teacher_output = self.teacher(images[:self.n_g_crops])
                student_output = self.student(images)
                loss = self.loss(student_output, teacher_output, epoch-1)

                # calculate the entropy of the emb. space
                emb_glob = self._get_embedding(self.student,
                                               torch.concat(images[:self.n_g_crops]))
                emb_loc = self._get_embedding(self.student,
                                              torch.concat(images[self.n_g_crops:]))
                entropy = self.calculate_embedding_entropy(
                    torch.concat([emb_glob, emb_loc]))
                ent_avg, ent_min, ent_max, ent_std, ent_med = entropy

                # check if loss is not infinite
                self.check_loss_nan(loss.detach())

                # student update
                loss.backward()
                if self.config['clip_grad']:
                    _ = clip_gradients(self.student, self.config['clip_grad'])
                cancel_gradients_last_layer(
                    epoch-1,
                    self.student,
                    self.config['optimizer']['freeze_last_layer'])
                optimizer.step()

                # EMA update for the teacher
                self.ema_update_teacher(student=self.student,
                                        teacher=self.teacher,
                                        momentum_schedule=momentum_schedule,
                                        n_iter=n_iter)

                # log metrics
                acc = self.calculate_student_teacher_acc(
                    teacher_output, student_output[:self.n_g_crops],
                    self.n_g_crops)
                prog_bar.set_description(
                    f'Epoch: {epoch}, Train loss: {loss}, Train stud/teach acc: {acc}'
                )
                log_dict = {
                    'train_loss': loss,
                    'train_step': n_iter,
                    'train_stud_teach_acc': acc,
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
                    model=self.student,
                    n_iter=n_iter,
                    log_self_attention=self.config['visualize_attention'])

            # save the model
            if epoch % self.config['save_every_n_epochs'] == 0:
                if self.multi_gpu:
                    student = self.student.module.state_dict()
                    teacher = self.teacher.module.state_dict()
                else:
                    student = self.student.state_dict()
                    teacher = self.teacher.state_dict()
                save_dict = {
                    'arch': type(self.student).__name__,
                    'epoch': epoch,
                    'student': student,
                    'teacher': teacher,
                    'optimizer': optimizer.state_dict(),
                    'config': self.config,
                    'loss': self.loss.state_dict(),
                }
                self._save_checkpoint(save_dict, epoch, save_best=True)
        # finish the run
        wandb.finish()

    def _get_embedding(self, model: torch.nn.Module, images: torch.Tensor):
        if self.multi_gpu:
            model = model.module
        n = self.config['model']['eval']['n_last_blocks']
        inter_out = model.backbone.get_intermediate_layers(images, n)
        emb = torch.cat([x[:, 0] for x in inter_out], dim=-1)
        if self.config['model']['eval']['avgpool_patchtokens']:
            emb = torch.cat((emb.unsqueeze(-1), torch.mean(inter_out[-1][:, 1:], dim=1).unsqueeze(-1)), dim=-1)
            emb = emb.reshape(emb.shape[0], -1)
        return emb
