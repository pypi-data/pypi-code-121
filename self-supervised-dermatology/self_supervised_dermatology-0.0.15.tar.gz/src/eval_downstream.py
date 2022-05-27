import yaml
import argparse
import wandb
from pathlib import Path
from functools import partial

from src.trainers.simclr_trainer import SimCLRTrainer
from src.trainers.byol_trainer import BYOLTrainer
from src.trainers.colorme_trainer import ColorMeTrainer
from src.trainers.dino_trainer import DINOTrainer
from src.trainers.ibot_trainer import iBOTTrainer
from src.trainers.imagenet_trainer import ImageNetTrainer
from src.utils.utils import fix_random_seeds
from src.utils.loader import Loader

my_parser = argparse.ArgumentParser(
    description='Evaluates SSL models on downstream tasks.')
my_parser.add_argument('--config_path',
                       type=str,
                       required=True,
                       help='Path to the config yaml.')
my_parser.add_argument('--datasets',
                       nargs='+',
                       default=[
                           'fitzpatrick17k',
                           'pad_ufes_20',
                           'ham10000',
                           'body_loc',
                       ],
                       help='Name of the datasets to evaluate on.')
args = my_parser.parse_args()

if __name__ == "__main__":
    # load config yaml
    args.config_path = Path(args.config_path)
    if not args.config_path.exists():
        raise ValueError(
            f'Unable to find config yaml file: {args.config_path}')
    config = yaml.load(open(args.config_path, "r"), Loader=Loader)

    # seed everything
    fix_random_seeds(config['seed'])

    # get the correct trainer
    trainer_dict = {
        'ImageNet': ImageNetTrainer,
        'SimCLR': SimCLRTrainer,
        'BYOL': BYOLTrainer,
        'ColorMe': ColorMeTrainer,
        'DINO': DINOTrainer,
        'iBOT': iBOTTrainer,
    }
    trainer_cls = trainer_dict.get(config['SSL_model'], None)
    if trainer_cls is None:
        raise ValueError('Unknown SSL model.')

    sweep_config = {
        'method': 'bayes',
        'name': None,
        'metric': {
            'name': None,
            'goal': 'maximize'
        },
        'early_terminate': {
            'type': 'hyperband',
            'min_iter': 30,
        },
        'parameters': {
            'optim': {
                'values': ['adam', 'sgd', 'adamw'],
            },
            'batch_size': {
                'values': [32, 64, 128],
            },
            'lr': {
                'values': [0.01, 0.03, 0.001, 0.003],
            },
            'loss_fn': {
                'values': ['ce', 'nll'],
            },
            'label_smoothing': {
                'values': [0.2, 0.1, 0.01],
            },
            'dropout': {
                'values': [0.2, 0.3, 0.5],
            },
            'use_bn': {
                'values': [True, False],
            },
            'use_mixup': {
                'values': [True, False],
            },
        },
    }

    # loop over all given datasets
    for dataset_name in args.datasets:
        # initialize the trainer
        trainer = trainer_cls(None,
                              None,
                              config,
                              args.config_path,
                              evaluation=True)
        # start the sweep
        sweep_config['name'] = f'{dataset_name}-{config["SSL_model"]}'
        sweep_config['metric']['name'] = f'Downstream/{dataset_name}/valid_f1'
        sweep_id = wandb.sweep(sweep_config, project="vm02-SSL")
        dataset_func = partial(trainer.hyperopt_downstream,
                               dataset=dataset_name)
        wandb.agent(sweep_id, dataset_func, count=20)
