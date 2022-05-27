import monai
import torch
from monai.networks.layers.factories import Act, Norm

def get_model( model_name: str
             , input_channels: int
             , output_channels: int
             , device
             , image_size: int = 0
             ) -> monai.networks.nets:
    if model_name == "U-Net big":
        model = get_multiple_channel_UNet( input_channels
                                         , output_channels
                                         , device
                                         )
    if model_name == "U-Net small":
        model = get_multiple_channel_UNet( input_channels
                                         , output_channels
                                         , device
                                         , type_network = "small"
                                         )
    if model_name == "SegResNet":
        model = get_multiple_channel_SegResNet( input_channels
                                              , output_channels
                                              , device
                                              )
    if model_name == "UNetTransformer":
        model = get_multiple_channel_UNetTransformer( input_channels
                                                    , output_channels
                                                    , image_size
                                                    , device
                                                    )
    return model 

def get_multiple_channel_UNet( input_channels: int
                             , output_channels: int
                             , device
                             , type_network: str = "big"
                             )-> monai.networks.nets:
    if type_network == "big":
        model = monai.networks.nets.UNet( dimensions = 2
                                        , in_channels = input_channels
                                        , out_channels = output_channels
                                        , channels = (64, 64, 128, 128, 256, 512)
                                        , strides = (2, 2, 2, 2, 2,2)
                                        , num_res_units = 4
                                        , norm = "batch" #added new
                                        , dropout = 0.2
                                        ).to(device, dtype = torch.float)
    if type_network == "small":
        model = monai.networks.nets.UNet( dimensions = 2
                                        , in_channels = input_channels
                                        , out_channels = output_channels
                                        , channels = (64, 64)
                                        , strides = (2, 2)
                                        , num_res_units = 2
                                        , norm =  "batch"
                                        , dropout = 0.2
                                        ).to(device, dtype = torch.float)
    
    return model

def get_multiple_channel_UNetTransformer( input_channels
                                        , output_channels
                                        , image_size
                                        , device
                                        )-> monai.networks.nets:
    model = monai.networks.nets.UNETR( in_channels= input_channels
                                     , out_channels = output_channels
                                     , img_size=(image_size, image_size)
                                     , feature_size=32
                                     , hidden_size = 768
                                     , mlp_dim = 3072
                                     , num_heads = 12
                                     , pos_embed = "perceptron"
                                     , norm_name="instance"
                                     , res_block = True
                                     , spatial_dims=2
                                     ).to(device, dtype = torch.float)
    return model

def get_multiple_channel_DynUNet( input_channels
                                , output_channels
                                , device
                                )-> monai.networks.nets:
    model = monai.networks.nets.DynUNet( spatial_dims = 2
                                       , in_channels = input_channels
                                       , out_channels = output_channels
                                       , kernel_size = (3,3,3,3,3,3)
                                       , strides = (2,2,2,2,2,2)
                                       , upsample_kernel_size = (3,3,3,3,3,3)
                                       , deep_supervision = True
                                       , norm_name = "batch"
                                       ).to(device, dtype = torch.float)
    return model

def get_multiple_channel_SegResNet( input_channels
                                  , output_channels
                                  , device
                                  )-> monai.networks.nets:
    model = monai.networks.nets.SegResNet( spatial_dims = 2
                                         , init_filters = 8
                                         , in_channels = 2
                                         , out_channels = 1
                                         , dropout_prob = 0.2
                                         , norm_name = 'group'
                                         , num_groups = 2
                                         , use_conv_final = True
                                         , blocks_down = (1, 2, 2, 4)
                                         , blocks_up=(1, 1, 1)
                                         ).to(device, dtype = torch.float)
    return model
