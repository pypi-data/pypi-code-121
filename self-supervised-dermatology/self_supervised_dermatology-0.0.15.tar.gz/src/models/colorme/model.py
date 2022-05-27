import segmentation_models_pytorch as smp
from torch import nn


class MLPHead(nn.Module):
    def __init__(self, out_features: int = 512):
        super(MLPHead, self).__init__()
        self.head = nn.Sequential(
            nn.Linear(out_features, 10),
            nn.Softmax(dim=-1),
        )

    def forward(self, x):
        return self.head(x)


class ColorMeModel(nn.Module):
    def __init__(self, num_classes=2, encoder_name='resnet18'):
        super(ColorMeModel, self).__init__()
        # create our encoder decoder model
        self.enc_dec_model = smp.Unet(encoder_name=encoder_name,
                                      encoder_weights='imagenet',
                                      in_channels=1,
                                      classes=num_classes)

        # color distribution MLP head
        if encoder_name == 'resnet18':
            self.color_dist_mlp = MLPHead(out_features=512)
        elif encoder_name == 'resnet50':
            self.color_dist_mlp = MLPHead(out_features=2048)
        else:
            raise ValueError('Unrecognized encoder')

    def forward(self, x, return_embedding=False):
        # color reconstruction
        rec = self.enc_dec_model(x)
        # retreive embedding
        emb = self.enc_dec_model.encoder(x)[-1]
        emb = nn.AdaptiveAvgPool2d((1, 1))(emb)
        emb = emb.squeeze()
        # return the embedding if needed
        if return_embedding:
            return emb
        # color distribution
        dist = self.color_dist_mlp(emb)

        return rec, dist
