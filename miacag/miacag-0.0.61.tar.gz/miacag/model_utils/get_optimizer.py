import os
import torch
from miacag.model_utils.scheduler import WarmupMultiStepLR


def get_optimizer(config, model, len_train):
    if config['use_DDP'] == 'False':
        os.environ['WORLD_SIZE'] = '1'
    if config['optimizer']['type'] == 'adam':
        optimizer = torch.optim.Adam(
            model.parameters(),
            lr=config['optimizer']['learning_rate'] *
            float(os.environ['WORLD_SIZE']),
            weight_decay=config['optimizer']['weight_decay'])

    elif config['optimizer']['type'] == 'sgd':

        optimizer = torch.optim.SGD(
            model.parameters(),
            lr=config['optimizer']['learning_rate'] *
            float(os.environ['WORLD_SIZE']),
            momentum=config['optimizer']['momentum'],
            weight_decay=config['optimizer']
                                ['weight_decay'])
    # Set learning rate scheduler
    if config['lr_scheduler']['type'] == 'step':
        lr_scheduler = torch.optim.lr_scheduler.StepLR(
            optimizer,
            step_size=config['lr_scheduler']['steps_for_drop'],
            gamma=0.1)
    elif config['lr_scheduler']['type'] in ['MultiStepLR', 'poly', 'cos']:
        if config['lr_scheduler']['type'] == 'poly':
            print('to be implemented')
            lr_scheduler = PolynomialLRDecay(
                optimizer,
                max_decay_steps=config['trainer']['epochs'],
                end_learning_rate=config['lr_scheduler']['end_lr'],
                power=config['lr_scheduler']['power'])

        elif config['lr_scheduler']['type'] == 'MultiStepLR':
            warmup_iters = config['lr_scheduler']['lr_warmup_epochs'] \
                * len_train
            lr_milestones = [
                len_train * m for m in config['lr_scheduler']['milestones']]
            lr_scheduler = WarmupMultiStepLR(
                    optimizer,
                    milestones=lr_milestones,
                    gamma=config['lr_scheduler']['gamma'],
                    warmup_iters=warmup_iters,
                    warmup_factor=1e-5,
                )
        elif config['lr_scheduler']['type'] == 'cos':
            lr_scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
                optimizer, config['trainer']['epochs'])
    else:
        lr_scheduler = False

    return optimizer, lr_scheduler

# def poly_lr_scheduler(optimizer, init_lr, iter, lr_decay_iter=1,
#                         max_iter=100, power=0.9):
#     """Polynomial decay of learning rate
#         :param init_lr is base learning rate
#         :param iter is a current iteration
#         :param lr_decay_iter how frequently decay occurs, default is 1
#         :param max_iter is number of maximum iterations
#         :param power is a polymomial power

#     """
#     if iter % lr_decay_iter or iter > max_iter:
#         return optimizer

#     lr = init_lr*(1 - iter/max_iter)**power
#     for param_group in optimizer.param_groups:
#         param_group['lr'] = lr

#     return lr
