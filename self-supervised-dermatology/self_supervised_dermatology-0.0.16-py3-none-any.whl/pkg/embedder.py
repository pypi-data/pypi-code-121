import os
import copy
import torch
import tempfile
import numpy as np
import torchvision.models as models
from collections import OrderedDict
from types import SimpleNamespace

from .wrappers import ViTWrapper, UNetWrapper
from ..models.vit.vision_transformer import vit_tiny
from ..models.ibot.head import iBOTHead
from ..models.dino.head import DINOHead
from ..utils.utils import compare_models
from ..utils.utils import set_requires_grad


class Embedder:
    base_path = 'https://github.com/vm02-self-supervised-dermatology/self-supervised-models/raw/main'

    @staticmethod
    def load_resnet(ssl: str, return_info: bool = False, debug: bool = False):
        if ssl in ['byol', 'simclr', 'colorme']:
            return Embedder.load_pretrained(ssl=ssl,
                                            return_info=return_info,
                                            debug=debug)
        else:
            raise ValueError('The given SSL model to load has not a ResNet architecture.')

    @staticmethod
    def load_vit(ssl: str, return_info: bool = False, debug: bool = False):
        if ssl in ['dino', 'ibot']:
            return Embedder.load_pretrained(ssl=ssl,
                                            return_info=return_info,
                                            debug=debug)
        else:
            raise ValueError('The given SSL model to load has not a ViT architecture.')

    @staticmethod
    def load_pretrained(ssl: str,
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
            loader_func = Embedder.get_model_func(ssl)
            # load the model
            load_ret = loader_func(ckp_path=tmp.name,
                                   return_info=return_info,
                                   debug=debug)
        return load_ret

    @staticmethod
    def get_model_url(ssl: str):
        model_dict = {
            'byol': f'{Embedder.base_path}/byol/checkpoint-epoch100.pth',
            'simclr': f'{Embedder.base_path}/simclr/checkpoint-epoch100.pth',
            'colorme': f'{Embedder.base_path}/colorme/checkpoint-epoch100.pth',
            'dino': f'{Embedder.base_path}/dino/checkpoint-epoch100.pth',
            'ibot': f'{Embedder.base_path}/ibot/model_best.pth',
            'imagenet': '',
        }
        # get the model url
        model_url = model_dict.get(ssl, np.nan)
        if model_url is np.nan:
            raise ValueError('Unrecognized model name.')
        return model_url

    @staticmethod
    def get_model_func(ssl: str):
        model_dict_func = {
            'simclr': Embedder.load_simclr,
            'byol': Embedder.load_byol,
            'colorme': Embedder.load_colorme,
            'dino': Embedder.load_dino,
            'ibot': Embedder.load_ibot,
            'imagenet': Embedder.load_imagenet,
        }
        model_func = model_dict_func.get(ssl, np.nan)
        if model_func is np.nan:
            raise ValueError('Unrecognized model name.')
        return model_func

    @staticmethod
    def load_imagenet(ckp_path: str,
                      return_info: bool = False,
                      debug: bool = False):
        # load a dummy model
        model = models.resnet50(pretrained=True)
        # ResNet Model without last layer
        model = torch.nn.Sequential(*list(model.children())[:-1])
        set_requires_grad(model, True)
        if return_info:
            # information about the model
            info = SimpleNamespace()
            info.model_type = 'ResNet'
            info.ssl_type = 'ImageNet'
            info.out_dim = 2048
            return model, info
        return model

    @staticmethod
    def load_simclr(ckp_path: str,
                    return_info: bool = False,
                    debug: bool = False):
        # load a dummy model
        model = models.resnet50(pretrained=False)
        # ResNet Model without last layer
        model = torch.nn.Sequential(*list(model.children())[:-1])
        dummy_model = copy.deepcopy(model)
        # load the trained model
        Embedder.restart_from_checkpoint(
            ckp_path,
            state_dict=model,
            replace_ckp_str='model.',
            debug=debug,
        )
        # check if the dummy model params and the loaded differ
        n_differs = compare_models(dummy_model, model)
        if n_differs == 0:
            raise ValueError("Dummy model and loaded model are not different, "
                             "checkpoint wasn't loaded correctly")
        set_requires_grad(model, True)
        if return_info:
            # information about the model
            info = SimpleNamespace()
            info.model_type = 'ResNet'
            info.ssl_type = 'SimCLR'
            info.out_dim = 2048
            return model, info
        return model

    @staticmethod
    def load_byol(ckp_path: str,
                  return_info: bool = False,
                  debug: bool = False):
        # load a dummy model
        model = models.resnet50(pretrained=False)
        dummy_model = copy.deepcopy(model)
        # load the trained model
        Embedder.restart_from_checkpoint(
            ckp_path,
            state_dict=model,
            replace_ckp_str='net.',
            debug=debug,
        )
        # check if the dummy model params and the loaded differ
        n_differs = compare_models(dummy_model, model)
        if n_differs == 0:
            raise ValueError("Dummy model and loaded model are not different, "
                             "checkpoint wasn't loaded correctly")
        # ResNet Model without last layer
        model = torch.nn.Sequential(*list(model.children())[:-1])
        set_requires_grad(model, True)
        if return_info:
            # information about the model
            info = SimpleNamespace()
            info.model_type = 'ResNet'
            info.ssl_type = 'BYOL'
            info.out_dim = 2048
            return model, info
        return model

    @staticmethod
    def load_colorme(ckp_path: str,
                     return_info: bool = False,
                     debug: bool = False):
        # load a dummy model
        import segmentation_models_pytorch as smp
        model = smp.Unet(encoder_name='resnet50',
                         in_channels=1,
                         classes=2,
                         encoder_weights=None)
        model = model.encoder
        dummy_model = copy.deepcopy(model)
        # load the trained model
        Embedder.restart_from_checkpoint(
            ckp_path,
            state_dict=model,
            replace_ckp_str='enc_dec_model.encoder.',
            debug=debug,
        )
        # check if the dummy model params and the loaded differ
        n_differs = compare_models(dummy_model, model)
        if n_differs == 0:
            raise ValueError("Dummy model and loaded model are not different, "
                             "checkpoint wasn't loaded correctly")
        # wrap the UNet encoder with a helper
        model = UNetWrapper(model)
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
        # load the head
        head = DINOHead(
            768,
            config['model']['out_dim'],
            use_bn=config['model']['use_bn_in_head'],
            norm_last_layer=config['model']['norm_last_layer'],
        )
        Embedder.restart_from_checkpoint(
            ckp_path,
            student=head,
            replace_ckp_str='head.',
            debug=debug,
        )
        # wrap the ViT with a helper
        model = ViTWrapper(model, head)
        set_requires_grad(model, True)
        if return_info:
            # information about the model
            info = SimpleNamespace()
            info.model_type = 'ViT'
            info.ssl_type = 'DINO'
            info.out_dim = 256
            return model, info
        return model

    @staticmethod
    def load_ibot(ckp_path: str,
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
        # load the head
        head = iBOTHead(
            768,
            config['model']['out_dim'],
            patch_out_dim=config['model']['patch_out_dim'],
            use_bn=config['model']['use_bn_in_head'],
            norm_last_layer=config['model']['norm_last_layer'],
            shared_head=config['model']['shared_head'],
        )
        Embedder.restart_from_checkpoint(
            ckp_path,
            student=head,
            replace_ckp_str='head.',
            debug=debug,
        )
        # wrap the ViT with a helper
        model = ViTWrapper(model, head)
        set_requires_grad(model, True)
        if return_info:
            # information about the model
            info = SimpleNamespace()
            info.model_type = 'ViT'
            info.ssl_type = 'iBOT'
            info.out_dim = 256
            return model, info
        return model

    @staticmethod
    def restart_from_checkpoint(ckp_path,
                                run_variables=None,
                                replace_ckp_str='module.',
                                debug=False,
                                **kwargs):
        if not os.path.isfile(ckp_path):
            print("Pre-trained weights not found. Training from scratch.")
            return
        print("Found checkpoint at {}".format(ckp_path))

        # open checkpoint file
        checkpoint = torch.load(ckp_path, map_location="cpu")

        # key is what to look for in the checkpoint file
        # value is the object to load
        # example: {'state_dict': model}
        for key, value in kwargs.items():
            if key in checkpoint and value is not None:
                try:
                    msg = value.load_state_dict(checkpoint[key], strict=False)
                    if msg is None or len(msg.missing_keys) > 0:
                        k = next(iter(checkpoint[key]))
                        if replace_ckp_str in k:
                            if debug:
                                print(f'=> Found `module` in {key}, trying to transform.')
                            transf_state_dict = OrderedDict()
                            for k, v in checkpoint[key].items():
                                # remove the module from the key
                                # this is caused by the distributed training
                                k = k.replace(replace_ckp_str, '')
                                transf_state_dict[k] = v
                            msg = value.load_state_dict(transf_state_dict,
                                                        strict=False)
                    if debug:
                        print("=> loaded '{}' from checkpoint '{}' with msg {}".
                              format(key, ckp_path, msg))
                except TypeError:
                    try:
                        msg = value.load_state_dict(checkpoint[key])
                        print("=> loaded '{}' from checkpoint: '{}'".format(key, ckp_path))
                    except ValueError:
                        print("=> failed to load '{}' from checkpoint: '{}'".format(key, ckp_path))
            else:
                print("=> key '{}' not found in checkpoint: '{}'".format(key, ckp_path))

        # reload variable important for the run
        if run_variables is not None:
            for var_name in run_variables:
                if var_name in checkpoint:
                    run_variables[var_name] = checkpoint[var_name]
