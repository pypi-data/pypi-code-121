import torch


class ViTWrapper(torch.nn.Module):
    def __init__(self, model, head):
        super(ViTWrapper, self).__init__()
        self.model = model
        self.head = head.mlp

    def forward(self, x, n_layers=4):
        # extract the embeddings from the last N layers and combine
        inter_out = self.model.get_intermediate_layers(x, n_layers)
        emb = torch.cat([x[:, 0] for x in inter_out], dim=-1)
        #emb = self.head(emb)
        return emb


class UNetWrapper(torch.nn.Module):
    def __init__(self, model):
        super(UNetWrapper, self).__init__()
        self.model = model

    def forward(self, x):
        # extract only the green channel (input colorme)
        x = x[:, 1, :, :][:, None, :, :]
        # get the last features from the encoder
        emb = self.model(x)[-1]
        emb = torch.nn.AdaptiveAvgPool2d((1, 1))(emb)
        return emb


class ColorMeSegWrapper(torch.nn.Module):
    def __init__(self, model):
        super(ColorMeSegWrapper, self).__init__()
        self.model = model

    def forward(self, x):
        # extract only the green channel (input colorme)
        x = x[:, 1, :, :][:, None, :, :]
        # get the last features from the encoder
        mask = self.model(x)
        return mask
