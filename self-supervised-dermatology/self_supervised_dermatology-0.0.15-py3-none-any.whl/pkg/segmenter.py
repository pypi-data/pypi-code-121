import copy
import torch
import tempfile
import numpy as np
import torchvision.models as models
from types import SimpleNamespace

from .wrappers import ColorMeSegWrapper
from ..models.vit.vision_transformer import vit_tiny
from ..models.segmentation import ViTSeg
from ..utils.utils import compare_models
from ..utils.utils import set_requires_grad
from .embedder import Embedder


class Segmenter:
    base_path = 'https://github.com/vm02-self-supervised-dermatology/self-supervised-models/raw/main'

    @staticmethod
    def load_pretrained(ssl: str,
                        n_classes: int,
                        return_info: bool = False,
                        debug: bool = False):
        # get the model url
        model_url = Embedder.get_model_url(ssl)
        # download the model checkpoint
        with tempfile.NamedTemporaryFile() as tmp:
            try:
                if model_url != '':
                    torch.hub.download_url_to_file(model_url,
                                                   tmp.name,
                                                   progress=True)
            except Exception as e:
                print(e)
                print('Trying again.')
                torch.hub.download_url_to_file(model_url, tmp.name, progress=True)
            # get the loader function
            loader_func = Segmenter.get_model_func(ssl)
            # load the model
            load_ret = loader_func(ckp_path=tmp.name,
                                   n_classes=n_classes,
                                   return_info=return_info,
                                   debug=debug)
        return load_ret

    @staticmethod
    def get_model_func(ssl: str):
        model_dict_func = {
            'simclr': Segmenter.load_simclr,
            'byol': Segmenter.load_byol,
            'colorme': Segmenter.load_colorme,
            'dino': Segmenter.load_dino,
            'ibot': Segmenter.load_ibot,
            'imagenet': Segmenter.load_imagenet,
        }
        model_func = model_dict_func.get(ssl, np.nan)
        if model_func is np.nan:
            raise ValueError('Unrecognized model name.')
        return model_func

    @staticmethod
    def load_imagenet(ckp_path: str,
                      n_classes: int,
                      return_info: bool = False,
                      debug: bool = False):
        raise NotImplementedError('ImageNet Unet not implemented yet.')

    @staticmethod
    def load_simclr(ckp_path: str,
                    n_classes: int,
                    return_info: bool = False,
                    debug: bool = False):
        import segmentation_models_pytorch as smp
        # load the model checkpoint
        checkpoint = torch.load(ckp_path, map_location="cpu")
        # load our dummy models
        model = models.resnet50(pretrained=False)
        unet = smp.Unet(encoder_name='resnet50',
                        in_channels=3,
                        classes=n_classes)
        dummy_model = copy.deepcopy(unet)
        # rename the keys of the checkpoint
        state_dict = checkpoint['state_dict']
        for id_key, new_key in enumerate(list(model.state_dict().keys())):
            old_key = list(state_dict.keys())[id_key]
            for key in list(state_dict.keys()):
                state_dict[key.replace(old_key, new_key)] = state_dict.pop(key)
        # load the encoder of the unet
        unet.encoder.load_state_dict(state_dict, strict=False)
        # check if the dummy model params and the loaded differ
        n_differs = compare_models(dummy_model, unet)
        if n_differs == 0:
            raise ValueError("Dummy model and loaded model are not different, "
                             "checkpoint wasn't loaded correctly")
        set_requires_grad(unet, True)
        if return_info:
            # information about the model
            info = SimpleNamespace()
            info.model_type = 'ResNet'
            info.ssl_type = 'SimCLR'
            return unet, info
        return unet

    @staticmethod
    def load_byol(ckp_path: str,
                  n_classes: int,
                  return_info: bool = False,
                  debug: bool = False):
        import segmentation_models_pytorch as smp
        # load the model checkpoint
        checkpoint = torch.load(ckp_path, map_location="cpu")
        # load our dummy models
        model = models.resnet50(pretrained=False)
        unet = smp.Unet(encoder_name='resnet50',
                        in_channels=3,
                        classes=n_classes)
        dummy_model = copy.deepcopy(unet)
        # rename the keys of the checkpoint
        state_dict = checkpoint['state_dict']
        for id_key, new_key in enumerate(list(model.state_dict().keys())):
            old_key = list(state_dict.keys())[id_key]
            for key in list(state_dict.keys()):
                state_dict[key.replace(old_key, new_key)] = state_dict.pop(key)
        # load the encoder of the unet
        unet.encoder.load_state_dict(state_dict, strict=False)
        # check if the dummy model params and the loaded differ
        n_differs = compare_models(dummy_model, unet)
        if n_differs == 0:
            raise ValueError("Dummy model and loaded model are not different, "
                             "checkpoint wasn't loaded correctly")
        set_requires_grad(unet, True)
        if return_info:
            # information about the model
            info = SimpleNamespace()
            info.model_type = 'ResNet'
            info.ssl_type = 'BYOL'
            return unet, info
        return unet

    @staticmethod
    def load_colorme(ckp_path: str,
                     n_classes: int,
                     return_info: bool = False,
                     debug: bool = False):
        # load a dummy model
        import segmentation_models_pytorch as smp
        model = smp.Unet(encoder_name='resnet50',
                         in_channels=1,
                         classes=2,
                         encoder_weights=None)
        dummy_model = copy.deepcopy(model)
        # load the trained model
        Embedder.restart_from_checkpoint(
            ckp_path,
            state_dict=model,
            replace_ckp_str='enc_dec_model.',
            debug=debug,
        )
        # check if the dummy model params and the loaded differ
        n_differs = compare_models(dummy_model, model)
        if n_differs == 0:
            raise ValueError("Dummy model and loaded model are not different, "
                             "checkpoint wasn't loaded correctly")
        # replace the default segmentation head
        helper_model = smp.Unet(encoder_name='resnet50',
                                in_channels=1,
                                classes=n_classes,
                                encoder_weights=None)
        model.segmentation_head[0] = helper_model.segmentation_head[0]
        # wrap the UNet encoder with a helper
        model = ColorMeSegWrapper(model)
        set_requires_grad(model, True)
        if return_info:
            # information about the model
            info = SimpleNamespace()
            info.model_type = 'ResNet-1Channel'
            info.ssl_type = 'ColorMe'
            info.out_dim = 2048
            return model, info
        return model

    @staticmethod
    def load_dino(ckp_path: str,
                  n_classes: int,
                  return_info: bool = False,
                  debug: bool = False):
        # load a dummy model
        model = vit_tiny()
        dummy_model = copy.deepcopy(model)
        # retreive the config file
        config = {}
        to_restore = {'config': config}
        # load the trained model
        Embedder.restart_from_checkpoint(
            ckp_path,
            student=model,
            replace_ckp_str='backbone.',
            debug=debug,
            run_variables=to_restore,
        )
        config = to_restore['config']
        model.masked_im_modeling = False
        # check if the dummy model params and the loaded differ
        n_differs = compare_models(dummy_model, model)
        if n_differs == 0:
            raise ValueError("Dummy model and loaded model are not different, "
                             "checkpoint wasn't loaded correctly")
        # wrap the ViT to create a Seg model
        model = ViTSeg(model, num_classes=n_classes)
        set_requires_grad(model, True)
        if return_info:
            # information about the model
            info = SimpleNamespace()
            info.model_type = 'ViT'
            info.ssl_type = 'DINO'
            return model, info
        return model

    @staticmethod
    def load_ibot(ckp_path: str,
                  n_classes: int,
                  return_info: bool = False,
                  debug: bool = False):
        # load a dummy model
        model = vit_tiny()
        dummy_model = copy.deepcopy(model)
        # retreive the config file
        config = {}
        to_restore = {'config': config}
        # load the trained model
        Embedder.restart_from_checkpoint(
            ckp_path,
            student=model,
            replace_ckp_str='backbone.',
            debug=debug,
            run_variables=to_restore,
        )
        config = to_restore['config']
        model.masked_im_modeling = False
        # check if the dummy model params and the loaded differ
        n_differs = compare_models(dummy_model, model)
        if n_differs == 0:
            raise ValueError("Dummy model and loaded model are not different, "
                             "checkpoint wasn't loaded correctly")
        # wrap the ViT to create a Seg model
        model = ViTSeg(model, num_classes=n_classes)
        set_requires_grad(model, True)
        if return_info:
            # information about the model
            info = SimpleNamespace()
            info.model_type = 'ViT'
            info.ssl_type = 'iBOT'
            return model, info
        return model
