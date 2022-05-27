from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import importlib
import logging
import progress.bar
import torch


def prep_batch(batchdata, device, non_blocking=False):
    batchdata['image']=batchdata['image'].to(device=device, non_blocking=non_blocking)
    batchdata['label']=batchdata['label'].to(device=device, non_blocking=non_blocking)
    return batchdata
    

def get_engine(config_object):

    if not hasattr(config_object.args.engine, 'prepare_batch'):
        config_object.args.engine.prepare_batch = prep_batch
    
    if config_object.args.engine.state_name == 'training':
        if config_object.args.engine.trainerModule == 'monai':
            from monai.engines import SupervisedTrainer
            from monai.handlers import StatsHandler
            trainer_ = SupervisedTrainer(device=config_object.args.engine.device,
                        max_epochs=config_object.args.engine.epochs,
                        train_data_loader=config_object.args.engine.dataloader,
                        network=config_object.args.engine.inference_model,
                        optimizer=config_object.args.engine.optimizer,
                        loss_function=config_object.args.engine.objective_fun,
                        train_handlers=StatsHandler(tag_name="train_loss", output_transform=lambda x: x["loss"]),
                        prepare_batch=config_object.args.engine.prepare_batch
                )
            config_object.args.engine.trainer = trainer_
        elif config_object.args.engine.trainerModule == 'emcqmri':
            from core.engine.train_model import Trainer
            trainer_ = Trainer(device = config_object.args.engine.device,
                            max_epochs=config_object.args.engine.epochs,
                            train_data_loader=config_object.args.engine.dataloader,
                            network=config_object.args.engine.inference_model,
                            optimizer=config_object.args.engine.optimizer,
                            loss_function=config_object.args.engine.objective_fun,
                            prepare_batch = config_object.args.engine.prepare_batch,
                            log_training_fun=config_object.args.engine.log_training_fun,
                            config_object = config_object
                )
            config_object.args.engine.trainer = trainer_
        else:
            logging.error("Selected trainer not available")
            
    elif config_object.args.engine.state_name == 'testing':
        if config_object.args.engine.estimatorModule == 'emcqmri':
            from core.engine.estimate import Infer
            estimator_ = Infer(device = config_object.args.engine.device,
                            validation_dataloader=config_object.args.engine.dataloader,
                            network=config_object.args.engine.inference_model,
                            metric=config_object.args.engine.objective_fun,
                            prepare_batch = config_object.args.engine.prepare_batch,
                            compute_loss = False,
                            log_training_fun=config_object.args.engine.log_training_fun,
                            config_object = config_object
                    )
            config_object.args.engine.estimator = estimator_
        else:
            logging.error("Only the 'emcqmri' estimator is available.")


def load_ext_module(module_link, module_name, config_object):
    module = importlib.import_module(module_link)
    loaded_module = str_to_class(module, module_name.capitalize())
    return loaded_module(config_object)


def str_to_class(module, classname):
    return getattr(module, classname)


class ProgressWrapper(progress.bar.FillingSquaresBar):
    def __init__(self, *args, **kwargs):
        super(ProgressWrapper, self).__init__(*args, **kwargs)
    
    def update(self):
        filled_length = int(self.width * self.progress)
        empty_length = self.width - filled_length
        message = self.message % self
        bar_ = self.fill * filled_length
        empty = self.empty_fill * empty_length
        suffix = self.suffix % self
        self.loss = '  Loss:  '+str(self.loss_)
        self.subs = 'Subject: '+str(self.it_sub)+'/'+str(self.total_subs) + '  '
        line = ''.join([self.subs, message, self.bar_prefix, bar_, empty, self.bar_suffix,
                        suffix, self.loss])
        self.writeln(line)

    def set_total_sub(self, total_subs):
        self.total_subs = total_subs

    def set_max(self, max_):
        self.max = max_

    def reset(self):
        self.index = 0
        self.loss_ = 0
        self.it_sub = 0

    def update_ext_par(self, loss, it_sub):
        self.loss_ = loss
        self.it_sub = it_sub


def ProgressBarWrap(func):
    bar = ProgressWrapper('', max=1, suffix='%(percent)d%%', loss=10)
    def wrapper(self, loss, args):
        bar.set_max(args.inference.inferenceSteps)
        bar.set_total_sub(args.engine.dataloader.__len__())
        bar.update_ext_par(loss, args.engine.iter)
        bar.next()
        
        if bar.index == args.inference.inferenceSteps:
            bar.finish()
            bar.reset()
    return wrapper


