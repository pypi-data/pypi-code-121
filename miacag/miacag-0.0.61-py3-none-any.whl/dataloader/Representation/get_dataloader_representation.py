from torch.utils.data import DataLoader
import torch
from monai.data import list_data_collate
from torchvision import datasets
from torchvision import transforms
from dataloader.dataloader_base import TwoCropsTransform


class RepresentationLoader():
    def get_representation_loader_train(self, config):
        if config['model']['dimension'] in ['2D']:
            if config['loaders']['format'] == 'rgb':
                from dataloader.Representation._2D.\
                    dataloader_monai_representation_2D_RGB \
                    import train_monai_representation_loader \
                    as train_loader_rep
                from dataloader.Representation._2D.\
                    dataloader_monai_representation_2D_RGB \
                    import val_monai_representation_loader \
                    as val_loader_rep
            elif config['loaders']['format'] == 'nifty':
                print('not implemented')
                raise NotImplementedError('not implemented jet')
            else:
                raise ValueError('Unknown format')

        elif config['model']['dimension'] in ['3D', '2D+T']:
            if config['loaders']['format'] == 'avi':
                print('NOT IMPLEMENTED: AVI for representation learning')
                #return train_loader, val_loader

            elif config['loaders']['format'] == 'nifty':
                from dataloader.Representation._3D.dataloader_monai_representation_3D import \
                    train_monai_representation_loader as train_loader_rep
                from dataloader.Representation._3D.dataloader_monai_representation_3D import \
                    val_monai_representation_loader as val_loader_rep
            else:
                raise ValueError("Data type is not implemented")
        else:
            raise ValueError("Model dimension type not understood")
        train_loader = train_loader_rep(
            config['TraindataRoot'],
            config['TraindataCSV'],
            config,
            use_complete_data=False)

        val_phase_train_loader = train_loader_rep(
            config['ValdataRoot'],
            config['ValdataCSV'],
            config,
            use_complete_data=False)
        val_phase_train_loader_metric = val_loader_rep(
            config['TraindataRoot'],
            config['TraindataCSV'],
            config,
            use_complete_data=True)
        val_phase_val_loader_metric = val_loader_rep(
            config['ValdataRoot'],
            config['ValdataCSV'],
            config,
            use_complete_data=True)
        if config['loaders']['store_memory'] is True:
            train_loader = datasets.CIFAR10(
                root=config['TraindataRoot'],
                train=True,
                download=True,
                transform=self.get_train_transforms_cifar10(config))
            val_phase_train_loader = datasets.CIFAR10(
                root=config['ValdataRoot'],
                train=False,
                download=True,
                transform=self.get_train_transforms_cifar10(config))
            val_phase_train_loader_metric = datasets.CIFAR10(
                root=config['TraindataRoot'],
                train=True,
                download=True,
                transform=self.get_val_transforms_cifar10(config))

            val_phase_val_loader_metric = datasets.CIFAR10(
                root=config['ValdataRoot'],
                train=False,
                download=True,
                transform=self.get_val_transforms_cifar10(config))
        train_loader = DataLoader(
            train_loader() if config['loaders']['store_memory'] is False else train_loader,
            drop_last=True,
            batch_size=config['loaders']['batchSize'],
            shuffle=True,
            num_workers=config['num_workers'],
            collate_fn=list_data_collate,
            pin_memory=torch.cuda.is_available(),)

        val_phase_train_loader = DataLoader(
            val_phase_train_loader() if config['loaders']['store_memory'] is False else val_phase_train_loader,
            drop_last=True,
            batch_size=config['loaders']['batchSize'],
            shuffle=False,
            num_workers=config['num_workers'],
            collate_fn=list_data_collate,
            pin_memory=torch.cuda.is_available(),)

        val_phase_train_loader_metric = DataLoader(
            val_phase_train_loader_metric() if config['loaders']['store_memory'] is False else val_phase_train_loader_metric,
            drop_last=True,
            batch_size=config['loaders']['batchSize'],
            shuffle=False,
            num_workers=config['num_workers'],
            collate_fn=list_data_collate,
            pin_memory=torch.cuda.is_available(),)
        val_phase_val_loader_metric = DataLoader(
            val_phase_val_loader_metric() if config['loaders']['store_memory'] is False else val_phase_val_loader_metric,
            drop_last=True,
            batch_size=config['loaders']['batchSize'],
            shuffle=False,
            num_workers=config['num_workers'],
            collate_fn=list_data_collate,
            pin_memory=torch.cuda.is_available(),)

        val_loader = (val_phase_train_loader,
                      val_phase_train_loader_metric,
                      val_phase_val_loader_metric)
        return train_loader, val_loader

    def get_train_transforms_cifar10(self, config):
        train_transforms = [
                transforms.RandomResizedCrop((
                    config['loaders']['Resize_height'],
                    config['loaders']['Resize_width']),
                    scale=(0.2, 1.)),
                transforms.RandomHorizontalFlip(),
                transforms.RandomApply([
                    transforms.ColorJitter(0.4, 0.4, 0.4, 0.1)
                ], p=0.8),
                transforms.RandomGrayscale(p=0.2),
                transforms.ToTensor(),
                transforms.Normalize((0.4914, 0.4822, 0.4465),
                                     (0.2023, 0.1994, 0.2010))]
        train_transforms = transforms.Compose(train_transforms)
        train_transforms = TwoCropsTransform(train_transforms)
        return train_transforms

    def get_val_transforms_cifar10(self, config):
        val_transforms = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize((0.4914, 0.4822, 0.4465),
                                     (0.2023, 0.1994, 0.2010))])
        return val_transforms

    def get_test_type(self, config):
        if config['loaders']['val_method']['type'] == 'patch_lvl':
            test_loader = self.get_classificationloader_patch_lvl_test(config)
            return test_loader
        elif config['loaders']['val_method']['type'] in \
                ['image_lvl+saliency_maps', 'image_lvl']:
            test_loader = self.get_classificationloader_image_lvl_test(config)
            return test_loader
        else:
            raise ValueError(
                "Data test loader type is not implemented %s" % repr(
                    config['loaders']['type']))

    def get_representation_patch_lvl_test(self, config):
        if config['loaders']['format'] == 'avi':
            from dataloader.dataloader_base_video import \
                getVideoTestTransforms
            from dataloader.dataloader_avi_video import \
                VideoDataloaderAVITrain
            transforms_test = getVideoTestTransforms(
                nr_frames=config['loaders']['Crop_depth'],
                crop_size=(config['loaders']['Crop_height'],
                           config['loaders']['Crop_width']))
            test_loader = VideoDataloaderAVITrain(
                config['loaders']['TestdataRoot'],
                config['loaders']['TestdataCSV'],
                transforms_test)
            with torch.no_grad():
                test_loader = DataLoader(test_loader,
                                         batch_size=config[
                                             'loaders']['batchSize'],
                                         num_workers=config[
                                            'loaders']['numWorkers'],
                                         shuffle=False)
            return test_loader
        elif config['loaders']['format'] == 'nifty':
            from dataloader.dataloader_monai_classification_3D \
                import test_monai_classification_loader

            test_loader = test_monai_classification_loader(
                config['loaders']['TestdataRoot'],
                config['loaders']['TestdataCSV'],
                config)
            test_loader = DataLoader(
                test_loader(),
                batch_size=config['loaders']['batchSize'],
                shuffle=False,
                num_workers=config['loaders']['numWorkers'],
                collate_fn=list_data_collate,
                pin_memory=torch.cuda.is_available(),)

            return test_loader

    def get_representation_image_lvl_test(self, config):
        if config['loaders']['format'] == 'avi':
            from dataloader.dataloader_base_video import \
                getVideoTestTransforms
            from dataloader.dataloader_avi_video import \
                VideoDataloaderAVITest
            transforms_test = getVideoTestTransforms(
                nr_frames=config['loaders']['Crop_depth'],
                crop_size=(config['loaders']['Crop_height'],
                           config['loaders']['Crop_width']))
            test_loader = VideoDataloaderAVITest(
                config['loaders']['TestdataRoot'],
                config['loaders']['TestdataCSV'],
                config['loaders']['Crop_depth'],
                transforms_test)

            test_loader = DataLoader(test_loader,
                                     batch_size=1,
                                     num_workers=config[
                                         'loaders']['numWorkers'],
                                     shuffle=False)

            return test_loader
        elif config['loaders']['format'] == 'nifty':
            from dataloader.dataloader_monai_classification_3D \
                import test_monai_classification_loader

            test_loader = test_monai_classification_loader(
                config['loaders']['TestdataRoot'],
                config['loaders']['TestdataCSV'],
                config)
            test_loader = DataLoader(
                test_loader(),
                batch_size=config['loaders']['batchSize'],
                shuffle=False,
                num_workers=config['loaders']['numWorkers'],
                collate_fn=list_data_collate,
                pin_memory=torch.cuda.is_available(),)

            return test_loader
