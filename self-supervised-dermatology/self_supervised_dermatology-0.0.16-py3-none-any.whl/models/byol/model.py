from torch import nn
import torchvision.models as models

from src.models.byol.predictor import MLP


class BYOLModel(nn.Module):
    def __init__(self,
                 base_model,
                 projection_size=256,
                 projection_hidden_size=4096):
        super(BYOLModel, self).__init__()

        # get the resnet backbone
        self.resnet_dict = {
            "resnet18": models.resnet18(pretrained=True),
            "resnet50": models.resnet50(pretrained=True)
        }
        resnet = self._get_basemodel(base_model)

        # ResNet Model without last layer
        self.encoder = nn.Sequential(*list(resnet.children())[:-1])

        # projection head
        self.projection = MLP(in_channels=resnet.fc.in_features,
                              projection_size=projection_size,
                              hidden_size=projection_hidden_size)

    def _get_basemodel(self, model_name):
        try:
            model = self.resnet_dict[model_name]
            print("Feature extractor:", model_name)
            return model
        except:
            raise ValueError("Invalid model name. Check the config file and"
                             "pass one of: resnet18 or resnet50")

    def forward(self, x, return_embedding=False):
        # embedding
        e = self.encoder(x)
        e = e.squeeze()
        if return_embedding:
            return e
        # project
        z = self.projection(e)
        return z
