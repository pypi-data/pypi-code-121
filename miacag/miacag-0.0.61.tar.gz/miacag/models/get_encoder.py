from monai.networks import nets
from torch import nn
import torch
import os


class Identity(nn.Module):
    def __init__(self):
        super(Identity, self).__init__()

    def forward(self, x):
        return x


def getPretrainedWeights(config, model, device):
    if config['model']['pretrained'] != "None":
        if torch.distributed.get_rank() == 0:
            dirname = os.path.dirname(__file__)
            model_path = os.path.join(
                            dirname,
                            "torchhub",
                            config['model']['dimension'],
                            config['model']['backbone'],
                            'model.pt')
            loaded_model = torch.load(
                    model_path,
                    map_location=device)

            if config['model']['backbone'] in \
                    ['x3d_s', 'slowfast8x8', 'MVIT-16', 'MVIT-32']:

                model.load_state_dict(loaded_model['model_state'])
            else:
                model.load_state_dict(loaded_model)
    else:
        pass
    return model


def get_encoder(config, device):
    if config['loaders']['mode'] != 'testing':
        pretrained = config['model']['pretrained']
    else:
        pretrained = False

    # Get model
    if config['model']['backbone'] == 'r3d_18':
        model = nets.torchvision_fc.models.video.resnet.r3d_18(
            pretrained=pretrained)
        in_features = model.fc.in_features
        model = nn.Sequential(*list(model.children())[:-2])
        # model.fc = nn.Identity()
    elif config['model']['backbone'] == 'r2plus1d_18':
        model = nets.torchvision_fc.models.video.resnet.r2plus1d_18(
            pretrained=False)
        if config['loaders']['mode'] != 'testing':
            model = getPretrainedWeights(config, model, device)
        in_features = model.fc.in_features
        model = nn.Sequential(*list(model.children())[:-2])
    elif config['model']['backbone'] == 'x3d_l':
        print('not implemented jet')
    elif config['model']['backbone'] == 'slowfast8x8':
        print('not impl')
        import pytorchvideo.models.slowfast as slowfast
        model = slowfast.create_slowfast()
        model = getPretrainedWeights(config, model, device)
        in_features = model.blocks[-1].proj.in_features
        model = nn.Sequential(
            *(list(model.blocks[:-1].children()) +
              list(model.blocks[-1].children())[:-2]))
    elif config['model']['backbone'] == 'x3d_s':
        import pytorchvideo.models.x3d as x3d
        model = x3d.create_x3d()  # default args creates x3d_s
        if config['loaders']['mode'] != 'testing':
            model = getPretrainedWeights(config, model, device)
        in_features = model.blocks[-1].proj.in_features
        model = nn.Sequential(
            *(list(model.blocks[:-1].children()) +
              list(model.blocks[-1].children())[:-3]))

    elif config['model']['backbone'] in ['MVIT-16', 'MVIT-32']:
        import pytorchvideo.models.vision_transformers as VT
        model = VT.create_multiscale_vision_transformers(
            spatial_size=(config['loaders']['Crop_height'],
                          config['loaders']['Crop_width']),
            temporal_size=config['loaders']['Crop_depth'],
            embed_dim_mul=[[1, 2.0], [3, 2.0], [14, 2.0]],
            atten_head_mul=[[1, 2.0], [3, 2.0], [14, 2.0]],
            pool_q_stride_size=[[1, 1, 2, 2], [3, 1, 2, 2], [14, 1, 2, 2]],
            pool_kv_stride_size=None,
            pool_kv_stride_adaptive=[1, 8, 8],
            pool_kvq_kernel=[3, 3, 3])
        if config['loaders']['mode'] != 'testing':
            model = getPretrainedWeights(config, model, device)
        in_features = model.head.proj.in_features
        model.head.proj = Identity()

    elif config['model']['backbone'] == 'linear':
        from models.backbone_encoders.tabular.base_encoders \
            import LinearEncoder
        model = LinearEncoder(config['model']['incomming_features'])
        in_features = config['model']['incomming_features']

    elif config['model']['backbone'] == 'mlp':
        from models.mlps import projection_MLP
        in_features = 128
        model = projection_MLP(config['model']['incomming_features'],
                               in_features)
    else:
        raise ValueError('not implemented')
    return model, in_features


def modelsRequiredPermute():
    model_list = [
        'r3d_18', 'r2plus1d_18',
        'x3d_l', 'x3d_s', 'MVIT-16', 'MVIT-32', 'slowfast8x8']
    return model_list
