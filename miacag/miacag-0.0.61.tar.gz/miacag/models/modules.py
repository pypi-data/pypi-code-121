from torch import nn
from miacag.models.mlps import prediction_MLP, projection_MLP
from miacag.models.get_encoder import get_encoder, modelsRequiredPermute
import torch.nn.functional as F
import torch


def maybePermuteInput(x, config):
    model_list = modelsRequiredPermute()
    if config['model']['backbone'] in model_list:
        x = x.permute(0, 1, 4, 2, 3)
        return x
    else:
        return x


def maybePackPathway(frames, config):
    if config['model']['backbone'] == 'slowfast8x8':
        fast_pathway = frames
        alpha = 4
        # Perform temporal sampling from the fast pathway.
        slow_pathway = torch.index_select(
            frames,
            1,
            torch.linspace(
                0, frames.shape[1] - 1, frames.shape[1] // alpha
            ).long())
        frame_list = [slow_pathway, fast_pathway]
        return frame_list
    else:
        return frames


class EncoderModel(nn.Module):
    def __init__(self, config, device):
        super(EncoderModel, self).__init__()

        self.encoder, self.in_features = get_encoder(config, device)

    def forward(self, x):
        x = maybePermuteInput(x, self.config)
        z = self.encoder(x)
        return z


class ClassificationModel(EncoderModel):
    def __init__(self, config, device):
        super(ClassificationModel, self).__init__(config, device)
        self.config = config
        self.fcs = []
        for head in range(0, len(self.config['labels_names'])):
            self.fcs.append(
                nn.Linear(self.in_features,
                          config['model']['num_classes']).to(device))
        self.dimension = config['model']['dimension']

    def forward(self, x):
        x = maybePermuteInput(x, self.config)
        p = self.encoder(x)
        if self.dimension in ['3D', '2D+T']:
            if self.config['model']['backbone'] not in ["MVIT-16", "MVIT-32"]:
                p = p.mean(dim=(-3, -2, -1))
            else:
                pass
        elif self.dimension == 'tabular':
            p = p
        else:
            p = p.mean(dim=(-2, -1))
        ps = []
        for fc in self.fcs:
            ps.append(fc(p))
        return ps


class SimSiam(EncoderModel):
    def __init__(self, config, device):
        super(SimSiam, self).__init__(
            config, device)
        self.projector = projection_MLP(self.in_features,
                                        config['model']['feat_dim'],
                                        config['model']['num_proj_layers'],
                                        config['model']['dimension'])

        self.encoder_projector = nn.Sequential(
            self.encoder,
            self.projector
        )

        self.predictor = prediction_MLP(config['model']['feat_dim'])

    def forward(self, x):
        
        im_aug1 = x[:, 0]
        im_aug2 = x[:, 1]
       # im_aug1 = maybePermuteInput(im_aug1, self.config)
      #  im_aug2 = maybePermuteInput(im_aug2, self.config)
        z1 = self.encoder_projector(im_aug1)
        z2 = self.encoder_projector(im_aug2)

        p1 = self.predictor(z1)
        p2 = self.predictor(z2)

        outputs = {'z1': z1, 'z2': z2, 'p1': p1, 'p2': p2}
        return outputs
