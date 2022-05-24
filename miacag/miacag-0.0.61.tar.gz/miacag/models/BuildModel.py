import yaml
import torch
import os


class ModelBuilder():
    def __init__(self, config, device):
        self.config = config
        self.device = device

    def getFingerPrint(self, filename):
        with open(filename) as file:
            fingerprint = yaml.load(file, Loader=yaml.FullLoader)
        return fingerprint

    def getTuplesFromDict(self, dictionary):
        for d in dictionary:
            if isinstance(dictionary[d], str):
                dictionary[d] = self.convert_string_to_tuple(dictionary[d])
        return dictionary

    def convert_string_to_tuple(self, field):
        res = []
        temp = []
        for token in field.split(", "):
            num = int(token.replace("(", "").replace(")", ""))
            temp.append(num)
            if ")" in token:
                res.append(tuple(temp))
                temp = []
        return res[0]

    def get_representation_learning_model(self):
        path = self.config['model']['pretrain_model']
        from models.modules import SimSiam as m
        model = m(self.config)
        if path != "None":
            model.load_state_dict(torch.load(path))
        return model

    def get_mayby_DDP(self, model):
        model.to(self.device)
        if self.config["cpu"] == "False":
            model = torch.nn.SyncBatchNorm.convert_sync_batchnorm(model)
    #if config['cpu'] == "False":
        if self.config['use_DDP'] == 'True':
            model = torch.nn.parallel.DistributedDataParallel(
                    model,
                    device_ids=[self.device] if self.config["cpu"] == "False" else None,
                    find_unused_parameters=False)
        return model

    def get_classification_model(self):
        path_model = self.config['model']['pretrain_model']
        path_encoder = self.config['model']['pretrain_encoder']
        from miacag.models.modules import ClassificationModel as m
        model = m(self.config, self.device)
        model = self.get_mayby_DDP(model)
        if path_encoder != 'None':
            model.module.encoder.load_state_dict(torch.load(path_encoder))

        if path_model != 'None':
            if self.config["use_DDP"] == "False":
                #if self.config['use_DDP'] == 'True':
                model.load_state_dict(
                    torch.load(os.path.join(path_model, 'model.pt')))
            else:
                if torch.distributed.get_rank() == 0:
                    if self.config['cpu'] == 'True':
                        model.load_state_dict(
                            torch.load(os.path.join(path_model, 'model.pt')))
                    else:
                        model.module.load_state_dict(
                            torch.load(os.path.join(path_model, 'model.pt')))
        return model

    def get_segmentation_model(self):
        path_model = self.config['model']['pretrain_model']
        path_encoder = self.config['model']['pretrain_encoder']
        if self.config['model']['model_name'] in ['UNet2D_pretrained_enc',
                                                  'UNet3D_pretrained_enc']:
            import segmentation_models_pytorch as smp
            model = smp.Unet(
                            dimensions=self.config['model']['dimension'],
                            encoder_name=self.config['model']['backbone'],
                            encoder_weights=None,
                            decoder_channels=self.convert_string_to_tuple(self.config['model']['decoder_channels']),
                            encoder_depth=self.config['model']['encoder_depth'],
                            in_channels=self.config['model']['in_channels'],
                            classes=self.config['model']['num_classes'])
            if path_encoder != "None":
                model.encoder.load_state_dict(torch.load(path_encoder))

        elif self.config['model']['model_name'] == 'UNet':
            import monai.networks.nets as m
            model = m.UNet(
                dimensions=2 if
                self.config['model']['dimension'] == '2D' else 3,
                in_channels=self.config['model']['in_channels'],
                out_channels=self.config['model']['num_classes'],
                channels=self.convert_string_to_tuple(
                    self.config['model']['channels']),
                strides=self.convert_string_to_tuple(self.config['model']['strides'])
                )

        elif self.config['model']['model_name'] == 'DynUNet':
            print('to be implemented')
            #unpack_fingerprint(self, config)
            # import monai.networks.nets as m
            # model = m.DYNUNet(
        else:
            raise ValueError('model not implemented')

        if path_model != "None":
            model.load_state_dict(torch.load(path_model))
        return model

    def get_model(self):
        if self.config['task_type'] == "representation_learning":
            model = self.get_representation_learning_model()
        elif self.config['task_type'] == "classification":
            model = self.get_classification_model()
        elif self.config['task_type'] == "segmentation":
            model = self.get_segmentation_model()
        return model

    def __call__(self):
        if self.config['datasetFingerprintFile'] is not None:
            self.config = self.unpack_fingerprint(self.config)
        model = self.get_model()
        return model

    def unpack_fingerprint(self, config):
        dataset_fingerprint = self.getFingerPrint(
            config['datasetFingerprintFile'])
        config['loaders']['pixdim_height'] = \
            dataset_fingerprint['original_spacing'][0]
        config['loaders']['pixdim_width'] = \
            dataset_fingerprint['original_spacing'][1]
        config['loaders']['pixdim_depth'] = \
            dataset_fingerprint['original_spacing'][2]
        if self.config['task_type'] == 'segmentation':
            if config['loaders']['Crop_height'] is None:
                config['loaders']['Crop_height'] = dataset_fingerprint['patch_size'][0]
            if config['loaders']['Crop_width'] is None:
                config['loaders']['Crop_width'] = dataset_fingerprint['patch_size'][1]
            if config['loaders']['Crop_depth'] is None:
                config['loaders']['Crop_depth'] = dataset_fingerprint['patch_size'][2]
            config['loaders']['batchSize'] = dataset_fingerprint['batch_size']

            configuration = config['model'].copy()
            configuration['spatial_dims'] = configuration['dimension']
            configuration['out_channels'] = configuration['classes']
            configuration['kernel_size'] = dataset_fingerprint['conv_kernel_sizes']
            configuration['strides_temp'] = dataset_fingerprint['pool_op_kernel_sizes']
            configuration['strides'] = []
            for i in range(0, len(configuration['strides_temp'])):
                if i == 0:
                    configuration['strides'].append([1, 1, 1])
                    configuration['strides'].append(configuration['strides_temp'][i])
                else:
                    configuration['strides'].append(configuration['strides_temp'][i])
            configuration['upsample_kernel_size'] = configuration['strides'][1:]
            configuration['norm_name'] = "instance"
            configuration['deep_supr_num'] = 2
            configuration['res_block'] = False
            del configuration['dimension']
            del configuration['classes']
            del configuration['strides_temp']

            return configuration
        else:
            return config