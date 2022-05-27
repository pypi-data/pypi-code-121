import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models


class ResNetSimCLR(nn.Module):
    def __init__(self, base_model, out_dim, **kwargs):
        super(ResNetSimCLR, self).__init__()
        self.resnet_dict = {
            "resnet18": models.resnet18(pretrained=True),
            "resnet50": models.resnet50(pretrained=True)
        }
        resnet = self._get_basemodel(base_model)
        n_feat = resnet.fc.in_features

        # ResNet Model without last layer
        self.model = nn.Sequential(*list(resnet.children())[:-1])
        # projection MLP
        self.dense1 = nn.Linear(n_feat, n_feat)
        self.dense2 = nn.Linear(n_feat, out_dim)

    def _get_basemodel(self, model_name):
        try:
            model = self.resnet_dict[model_name]
            print("Feature extractor:", model_name)
            return model
        except:
            raise ValueError("Invalid model name. Check the config file and"
                             "pass one of: resnet18 or resnet50")

    def forward(self, z):
        # embed
        e = self.model(z)
        e = e.squeeze()
        # project
        z = self.dense1(e)
        z = F.relu(z)
        z = self.dense2(z)
        return e, z
