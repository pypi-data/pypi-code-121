import torch
import numpy as np
import random
from miacag.metrics.metrics_utils import get_metrics, get_losses_metric
from miacag.metrics.metrics_utils import create_loss_dict, get_loss_metric_class
from miacag.metrics.metrics_utils import normalize_metrics, write_tensorboard
from miacag.dataloader.get_dataloader import get_data_from_loader
from miacag.model_utils.eval_utils import get_loss, get_losses_class
from miacag.configs.config import save_config
from miacag.metrics.metrics_utils import flatten, \
    unroll_list_in_dict
import os


def set_random_seeds(random_seed=0):
    torch.manual_seed(random_seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    np.random.seed(random_seed)
    random.seed(random_seed)


def train_one_step(model, data, criterion,
                   optimizer, lr_scheduler, writer, config,
                   running_loss_train,
                   running_metric_train,
                   tb_step_writer, scaler):
    model.train()
    # zero the parameter gradients
    optimizer.zero_grad()

    # forward + backward + optimize
    if scaler is not None:  # use AMP
        with torch.cuda.amp.autocast():
            outputs = model(data['inputs'])
            losses, loss = get_losses_class(config,
                                            outputs,
                                            data,
                                            criterion)
            # losses, loss = get_losses(config, outputs,
            #                           data[config['labels_names']],
            #                           criterion)
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
    else:
        outputs = model(data['inputs'])
        losses, loss = get_losses_class(config,
                                        outputs,
                                        data,
                                        criterion)
        loss.backward()
        optimizer.step()

    losses = create_loss_dict(config, losses, loss)
    metrics, losses_metric = get_loss_metric_class(
        config, outputs, data, losses, running_metric_train,
        running_loss_train, criterion)

    return outputs, losses, metrics, losses_metric


def train_one_epoch(model, criterion,
                    train_loader, device, epoch,
                    optimizer, lr_scheduler,
                    running_metric_train, running_loss_train,
                    writer, config, scaler):
    for i, data in enumerate(train_loader, 0):
        data = get_data_from_loader(data, config, device)
        outputs, loss, metrics, loss_metric = train_one_step(
            model,
            data,
            criterion,
            optimizer,
            lr_scheduler,
            writer,
            config,
            running_loss_train,
            running_metric_train,
            tb_step_writer=i,
            scaler=scaler)
        # running_metric_train = increment_metrics(running_metric_train,
        #                                          metrics)
       # running_loss_train = increment_metrics(running_loss_train, loss)
    
    if lr_scheduler is not False:
        lr_scheduler.step()

    running_metric_train, metric_tb = normalize_metrics(
        metrics)
    running_loss_train, loss_tb = normalize_metrics(
        loss_metric)
    # running_loss_train = normalize_metrics(
    #     running_loss_train,
    #     config,
    #     len(train_loader.dataset.data)
    #     if config['cache_num'] == 'None' else config['cache_num_train'])

    loss_tbe, metric_tb = write_tensorboard(loss_tb,
                                            metric_tb,
                                            writer,
                                            epoch,
                                            'train')


def test_best_loss(best_val_loss, best_val_epoch, val_loss, epoch):
    if best_val_loss is None or best_val_loss > val_loss:
        best_val_loss, best_val_epoch = val_loss, epoch
    return best_val_loss, best_val_epoch


def early_stopping(best_val_loss, best_val_epoch,
                   val_loss, epoch, max_stagnation):
    early_stop = False

    best_val_loss, best_val_epoch = test_best_loss(best_val_loss,
                                                   best_val_epoch,
                                                   val_loss,
                                                   epoch)

    if best_val_epoch < epoch - max_stagnation:
        # nothing is improving for a while
        early_stop = True

    return early_stop, best_val_loss, best_val_epoch



def get_device(config):
    if config["cpu"] == "False":
        #if config['loaders']['mode'] == 'training':
        device = "cuda:{}".format(os.environ['LOCAL_RANK'])
       # else:
       #     device = "cuda:0"
    else:
        device = 'cpu'
    device = torch.device(device)
    return device


def save_model(model, writer, config):
    model_file_path = os.path.join(writer.log_dir, 'model.pt')
    model_encoder_file_path = os.path.join(
            writer.log_dir, 'model_encoder.pt')

    if config["cpu"] == "False":
        torch.save(model.module.state_dict(), model_file_path)
    else:
        torch.save(model.state_dict(), model_file_path)

    if config["task_type"] in ["representation_learning"]:
        if config["cpu"] == "False":
            torch.save(model.module.encoder.state_dict(), model_encoder_file_path)
        else:
            torch.save(model.encoder.state_dict(), model_encoder_file_path)


def saver(metric_dict_val, writer, config):
    # prepare dicts by flattening
    config_tensorboard = unroll_list_in_dict(flatten(config))
    metric_dict_val = {str(key)+'/val': val
                       for key, val in metric_dict_val.items()}
    # save config
    config_tensorboard.update(metric_dict_val)
    save_config(writer, config, 'config.yaml')
    save_config(writer, metric_dict_val, 'metrics.yaml')
    # save tensorboard
    writer.add_hparams(config_tensorboard, metric_dict=metric_dict_val)
    writer.flush()
    writer.close()
