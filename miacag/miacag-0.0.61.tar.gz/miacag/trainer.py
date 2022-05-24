from miacag.dataloader.get_dataloader import get_dataloader_train
import torch
from miacag.models.BuildModel import ModelBuilder
from miacag.configs.config import load_config, maybe_create_tensorboard_logdir
from torch.utils.tensorboard import SummaryWriter
from miacag.model_utils.get_optimizer import get_optimizer
from miacag.model_utils.get_loss_func import get_loss_func
from miacag.configs.options import TrainOptions
from miacag.model_utils.train_utils import set_random_seeds, \
    train_one_epoch, early_stopping, \
    get_device, saver, save_model
from miacag.metrics.metrics_utils import init_metrics
from miacag.model_utils.eval_utils import val_one_epoch
import time
import torch.distributed as dist
from monai.utils import set_determinism


def train(config):
    config['loaders']['mode'] = 'training'
    set_random_seeds(random_seed=config['manual_seed'])
    set_determinism(seed=config['manual_seed'])

    device = get_device(config)

    if torch.distributed.get_rank() == 0:
        writer = SummaryWriter(config['output_directory'])
    else:
        writer = False
    if config["cpu"] == "False":
        torch.cuda.set_device(device)
        torch.backends.cudnn.benchmark = True

    BuildModel = ModelBuilder(config, device)
    model = BuildModel()

    # Get data loaders
    train_loader, val_loader, train_ds, _ = get_dataloader_train(config)

    # Get loss func
    criterion = get_loss_func(config)
    # Get optimizer
    optimizer, lr_scheduler = get_optimizer(config,
                                            model,
                                            len(train_loader))

    # Use AMP for speedup:
    scaler = torch.cuda.amp.GradScaler() \
        if config['loaders']['use_amp'] else None
    best_val_loss, best_val_epoch = None, None
    early_stop = False
    if config['cache_num'] != 'None':
        train_ds.start()

    starter = time.time()

    config['loss']['name'] = config['loss']['name'] + ['total']
    running_loss_train = init_metrics(config['loss']['name'], config,
                                      ptype='loss')
    running_metric_train = init_metrics(
            config['eval_metric_train']['name'], config)
    running_loss_val = init_metrics(config['loss']['name'], config,
                                    ptype='loss')
    running_metric_val = init_metrics(
                config['eval_metric_val']['name'], config)

    #  ---- Start training loop ----#
    for epoch in range(0, config['trainer']['epochs']):
        print('epoch nr', epoch)
        # train one epoch

        train_one_epoch(model, criterion,
                        train_loader, device, epoch,
                        optimizer, lr_scheduler,
                        running_metric_train, running_loss_train,
                        writer, config, scaler)

        if config['cache_num'] != 'None':
            train_ds.update_cache()

        #  validation one epoch (but not necessarily each)
        if epoch % config['trainer']['validate_frequency'] == 0:
            metric_dict_val = val_one_epoch(model, criterion, config,
                                            val_loader, device,
                                            running_metric_val,
                                            running_loss_val, writer, epoch)
            # early stopping
            early_stop, best_val_loss, best_val_epoch = early_stopping(
                best_val_loss, best_val_epoch,
                metric_dict_val['total'],
                epoch, config['trainer']['max_stagnation'])
            config['best_val_epoch'] = best_val_epoch
            # save model
            if best_val_epoch == epoch:
                if torch.distributed.get_rank() == 0:
                    save_model(model, writer, config)
            if early_stop is True:
                break

    if config['cache_num'] != 'None':
        train_ds.shutdown()

    if early_stop is False:
        if torch.distributed.get_rank() == 0:
            save_model(model, writer, config)
    if torch.distributed.get_rank() == 0:
        saver(metric_dict_val, writer, config)
    print('Finished Training')
    print('training loop (s)', time.time()-starter)
    # dist.destroy_process_group()
    torch.cuda.empty_cache()


if __name__ == '__main__':
    config = vars(TrainOptions().parse())
    config = load_config(config['config'], config)
    config = maybe_create_tensorboard_logdir(config)
    torch.distributed.init_process_group(
            backend="nccl" if config["cpu"] == "False" else "Gloo",
            init_method="env://"
            )
    train(config)
