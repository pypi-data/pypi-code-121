import numpy as np
import monai
from monai.transforms.transform import MapTransform
from monai.data import WSIReader
from monai.data.image_reader import ITKReader       
from monai.transforms import ( AddChanneld
                             , RandRotate90d
                             , ScaleIntensityd
                             , ToTensord
                             , ScaleIntensityRanged
                             , NormalizeIntensityd
                             , RandFlipd
                             , RandRotate90d
                             , RandSpatialCropd
                             , RandZoomd
                             , Rand2DElasticd
                             , RandAffined
                             , LabelToContourd
                             , ToNumpy
                             , LoadImaged
                             , Zoomd
                             , CastToType
                             , RandGaussianNoised
                             )
                                        
def preprocessing( list_steps, zoom_factor = 1, keys = ["img", "seg"], image_size = 512):
    preprocessing_list = []
    for step in list_steps:
        if step == "ScaleIntensity":
            preprocessing_list.append(ScaleIntensityd(keys = keys))
        if step == "Normalize":
            preprocessing_list.append(NormalizeIntensityd(keys = ["img"]))
    preprocessing_list.append(Zoomd(keys = keys, zoom = zoom_factor, keep_size = False))
    return preprocessing_list

def augmentation(list_steps, size, aug_prob, keys = ["img", "seg"]):
    zoom_mode = monai.utils.enums.InterpolateMode.NEAREST
    elast_mode = monai.utils.enums.GridSampleMode.BILINEAR, monai.utils.enums.GridSampleMode.NEAREST
    augmentation_list = []
    for step in list_steps:
        if step == "GaussianNoise":
            augmentation_list.append(RandGaussianNoised(keys = ["img"], prob = aug_prob, mean = 0.0, std = 0.1))
        if step == "SpatialCrop":
            augmentation_list.append(RandSpatialCropd(keys = keys, roi_size = (size, size), random_center = True, random_size=False))
        if step == "Rotate":
            augmentation_list.append(RandRotate90d(keys = keys, prob = aug_prob))
        if step == "Flip":
            augmentation_list.append(RandFlipd(keys = keys, prob = aug_prob))
        if step == "Zoom":
            augmentation_list.append(RandZoomd(keys = keys, prob = aug_prob, mode = zoom_mode))
        if step == "ElasticDeformation":
            augmentation_list.append(Rand2DElasticd(keys = keys, prob = aug_prob, spacing = 10, magnitude_range = (-2, 2), mode = elast_mode))
        if step == "AffineTransformation":
            augmentation_list.append(RandAffined(keys = keys, prob = aug_prob, rotate_range = 1, translate_range = 16, mode = elast_mode))
    return augmentation_list

def feature_engineering(list_preprocessing_functions, keys = ["img", "seg"]):
    class RGBtoGray(MapTransform):
        def __init__(self, keys):
            self.keys = keys
        def __call__(self, img_seg_dict):
            for key in self.keys:
                try:
                    if len(img_seg_dict[key].shape) == 3:
                        img_seg_dict[key] = np.dot(img_seg_dict[key][... , :3] , [0.299 , 0.587, 0.114]) 
                except KeyError:
                    raise ValueError(f"{key} not in given dictionary")
            return img_seg_dict
            
    class MultiChannelPreprocessingInput(MapTransform):
        def __init__(self, keys, list_preprocessing_functions):
            self.keys = keys
            self.list_preprocessing_functions = list_preprocessing_functions
        def __call__(self, img_seg_dict):
            original_image = img_seg_dict["img"]
            if "seg" in img_seg_dict.keys():
                original_mask = img_seg_dict["seg"]
                img_seg_dict["seg"] = np.array([original_mask])
            list_preprocessed_images = []
            for preprocessing_function in self.list_preprocessing_functions:
                list_preprocessed_images.append(preprocessing_function(original_image))
            img_seg_dict["img"] = np.array(list_preprocessed_images)
            return img_seg_dict
        
    class SwitchAxis(MapTransform):
        def __init__(self, keys):
            self.keys = keys
        def __call__(self, img_seg_dict):
            for key in self.keys:
                img_seg_dict[key] = np.moveaxis(img_seg_dict[key], 0, 1)
            return img_seg_dict
        
    feature_engineering_list = []
    feature_engineering_list.append(LoadImaged(keys=keys))
    feature_engineering_list.append(SwitchAxis(keys=keys))
    feature_engineering_list.append(RGBtoGray(keys=keys))
    feature_engineering_list.append(MultiChannelPreprocessingInput(keys = keys, list_preprocessing_functions = list_preprocessing_functions))
    return feature_engineering_list
    
           
def convert_to_tensor(keys = ["img", "seg"]):
    list_tensor = [ ToTensord(keys=keys)
                  ]
    return list_tensor
