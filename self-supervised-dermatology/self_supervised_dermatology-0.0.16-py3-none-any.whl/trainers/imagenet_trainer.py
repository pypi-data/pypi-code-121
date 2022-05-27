import torch
import torch.nn as nn
import torchvision.models as models
from torchvision.models.feature_extraction import create_feature_extractor

from src.trainers.base_trainer import Trainer
from src.utils.utils import set_requires_grad


class ImageNetTrainer(Trainer):
    def __init__(self,
                 train_dataset,
                 val_dataset,
                 config: dict,
                 config_path: str,
                 evaluation: bool = False,
                 debug: bool = False):
        super().__init__(train_dataset,
                         val_dataset,
                         config,
                         config_path,
                         evaluation=evaluation,
                         debug=debug,
                         arch_name='ImageNet')

    def fit(self):
        raise NotImplementedError('Fit is not available for ImageNet.')

    def eval(self):
        # load the pretrained model
        resnet_dict = {
            "resnet18": models.resnet18(pretrained=True),
            "resnet50": models.resnet50(pretrained=True)
        }
        resnet = resnet_dict.get(self.config['model']['base_model'], None)
        if resnet is None:
            raise ValueError('Unknown model.')
        # ResNet Model without last layer
        self.model = nn.Sequential(*list(resnet.children())[:-1])
        self.model = self.model.to(self.device)
        self.model = self.distribute_model(self.model)

        # set all the required attributes of the model
        self.set_model_attributes()
        # load the downstream tasks and classifiers
        self.load_downstream_tasks()

        # set the backbone
        return_nodes = {'4': 'feat1', '5': 'feat3', '6': 'feat4', '7': 'feat5'}
        backbone = create_feature_extractor(self.model,
                                            return_nodes=return_nodes)

        # evaluate the model
        self.eval_downstream_tasks(self.model, backbone=backbone, n_iter=0)

    def _get_embedding(self, model, img) -> torch.Tensor:
        emb = self.model(img)
        emb = emb.squeeze()
        return emb
