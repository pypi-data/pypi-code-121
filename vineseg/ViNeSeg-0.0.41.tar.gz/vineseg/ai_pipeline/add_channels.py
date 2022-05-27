from skimage.filters.rank import autolevel, enhance_contrast, entropy
from skimage.restoration import denoise_nl_means, estimate_sigma
from skimage.morphology import disk, white_tophat, black_tophat
from skimage import exposure 
from copy import deepcopy
from skimage import data, img_as_float
import numpy as np

def subtract_background( image
                       , radius = 3
                       , light_bg = False
                       ):
    str_el = disk(radius) 
    if light_bg:
        return  black_tophat(image, str_el)
    else:
        return  white_tophat(image, str_el)

def channelProcessingInput(list_processing):
    list_channels = []
    for channel in list_processing:
        if channel == "identity":
            def identity(image):
                return image
            list_channels.append(identity)
        if channel == "clahe":
            def clahe(image):
                image_clahe = np.asarray(image).astype(float)
                image_clahe -= image_clahe.mean()
                image_clahe /= image_clahe.std()
                image_clahe = exposure.rescale_intensity(image_clahe, out_range=(0,1))
                image_clahe = exposure.equalize_adapthist(image_clahe, clip_limit = 0.03) #CLAHE operator
                return image_clahe
            list_channels.append(clahe)
        if channel == "nl_means":
            def nl_means(image):
                image_clahe = np.asarray(image).astype(float)
                image_clahe -= image_clahe.mean()
                image_clahe /= image_clahe.std()
                image_clahe = exposure.rescale_intensity(image_clahe, out_range=(0,1))
                image_clahe = exposure.equalize_adapthist(image_clahe, clip_limit = 0.03) #CLAHE operator
                image = img_as_float(np.asarray(image_clahe))
                sigma_est = 0.03
                patch_kw = dict( patch_size = 5     
                               , patch_distance = 6  
                               , multichannel = True
                               )
                denoise2_fast = denoise_nl_means( image
                                                , h = 0.6 * sigma_est
                                                , sigma = sigma_est
                                                , fast_mode = True
                                                , **patch_kw
                                                )
                return denoise2_fast
            list_channels.append(nl_means)
        if channel == "autolevel":
            def autolevel(image):
                image_autolevel = exposure.rescale_intensity(image, out_range=(-1,1))
                image_autolevel = autolevel(image_autolevel, disk(20))
                return image_autolevel
            list_channels.append(autolevel)
        if channel == "gamma low":
            def gamma_low(image):
                image_gamma_low = exposure.rescale_intensity(image, out_range=(0,1))
                image_gamma_low =  exposure.adjust_gamma(image_gamma_low, gamma = 0.5)
                return image_gamma_low
            list_channels.append(gamma_low)
        if channel == "gamma high":
            def gamma_high(image):
                image_gamma_high = exposure.rescale_intensity(image, out_range=(0,1))
                image_gamma_high =  exposure.adjust_gamma(image_gamma_high, gamma = 0.5)
                return image_gamma_high
            list_channels.append(gamma_high)
        if channel == "rolling ball":
            def rolling_ball(image):
                rolling_ball_image = subtract_background(image)
                return rolling_ball_image
            list_channels.append(rolling_ball)
        if channel == "adjust sigmoid":
            def adjust_sigmoid(image):
                sigmoid_image = exposure.adjust_sigmoid(image)
                return sigmoid_image
            list_channels.append(adjust_sigmoid)
    return list_channels

def channelProcessingOutput(image, list_processing):
    list_channels = []
    for channel in list_processing:
        if image is None:
            list_channels.append(None)
            break
        if channel == "identity":
            def identity(image):
                return image
            list_channels.append(identity)
        if channel == "split foreground background":
            def split_foreground_background(image):
                image = np.array(image)
                foreground_image = image > 0
                background_image = 1 - foreground_image
                return foreground_image, background_image
            list_channels.append(split_foreground_background)
    return np.array(list_channels)
