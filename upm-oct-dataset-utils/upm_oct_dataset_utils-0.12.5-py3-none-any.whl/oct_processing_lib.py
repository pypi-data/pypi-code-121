
import os
import math
from pathlib import Path
from copy import deepcopy

import tqdm

import cv2
import numpy as np
from PIL import Image
import tensorflow.keras as keras

from .visualization_lib import show_image

this_dir_path =  Path(__file__).parent.resolve()

# --------------- RAW PROCESSING ---------------
# ----------------------------------------------
class Cube():
    def __init__(self, np_array) -> None:
        np_arr_cp = deepcopy(np_array)
        if type(np_arr_cp) is list:
            np_arr_cp = np.array(np_arr_cp)
        self.value = np_arr_cp

    def as_nparray(self):
        return self.value

    def rotate_face(self, axis:int=1):
        """ axes = 'x, 'y' and 'z' | cube shape assumed = (z, y, x)
            -> Rotates the face of the cube 90 degrees over the axes selected
        """
        rotated_cube = []
        
        for i in range(self.value.shape[axis]):
            if axis == 0:
                rotated_cube.append(self.value[i, :, :])
            elif axis == 1:
                rotated_cube.append(self.value[:, i, :])
            elif axis == 2:
                rotated_cube.append(self.value[:, :, i])
                
        c = Cube(rotated_cube)

        return c

    def resize_slices(self, size:tuple[int,int]):
        resized = []
        for i in range(self.value.shape[0]):
            img_obj = Image.fromarray(self.value[i]).resize(size)
            resized.append(np.array(img_obj))
        c = Cube(np.array(resized))

        return c

    def project(self):
        _, y_elements, x_elements = self.value.shape
        max_slice_vals = np.zeros((y_elements, x_elements))
        for y in range(y_elements):
            for x in range(x_elements):
                transposed = np.transpose(self.value)
                pixel_max = np.max(transposed[x][y])
                max_slice_vals[y][x] = pixel_max
        p = np.array(max_slice_vals)
        c = Cube(p)

        return c

    def vflip_slices(self):
        vflipped = []
        for slice_ in self.value:
            vflipped.append(np.flipud(slice_))
        return Cube(np.array(vflipped))

    def hflip_slices(self):
        hflipped = []
        for slice_ in self.value:
            hflipped.append(np.fliplr(slice_))
        return Cube(np.array(hflipped))


def segment_vascular_layer(octa_volume:np.ndarray, oct_volume:np.ndarray, img_bit_depth:int=16, filt=False):
    # Cargamos el modelo de segmentacion
    input_width = 384; input_height = 384; input_size = (input_width, input_height)
    model_fname = "70_0.81_unet-mini_val-jaccard-coef_adam_384-384_70_16_0.001.h5"
    #model_fname = f"197_0.89_unet-mini_val-jaccard-coef_adam_{input_width}-{input_height}_200_16_0.001.h5"
    model_url = "https://github.com/pgmesa-packages/upm_oct_dataset_utils/files/8748253/70_0.81_unet-mini_val-jaccard-coef_adam_384-384_70_16_0.001.zip"
    seg_model_dir = this_dir_path/"oct_sup_vascular_seg_model"
    model_path = seg_model_dir/model_fname
    if not os.path.exists(seg_model_dir):
        os.mkdir(seg_model_dir)
    if not os.path.exists(model_path):
        keras.utils.get_file(
            model_fname.replace(".h5", ".zip"),
            origin=model_url,
            archive_format='zip',
            extract=True,
            cache_subdir=seg_model_dir
        )
    seg_model = keras.models.load_model(model_path, compile=False)
    # Preparamos los datos y segmentamos cada bscan 
    
    max_val = math.pow(2, img_bit_depth) - 1
    oct_volume_norm = oct_volume/max_val
    masks = []
    pbar = tqdm.tqdm(total=oct_volume.shape[0], desc="Segmenting volume", unit=" bscans")
    for oct_bscan in oct_volume_norm:
        if filt:
            kernel = np.ones((7,7),np.float32)/49
            oct_bscan = oct_bscan*cv2.filter2D(oct_bscan,-1,kernel)
        oct_bscan_res = np.array(Image.fromarray(oct_bscan).resize(input_size))
        rgb_bscan = np.stack((oct_bscan_res,)*3, axis=-1)
        bs_input = np.expand_dims(rgb_bscan, axis=0)
        mask = np.squeeze(seg_model.predict(bs_input))
        mask = np.around(mask)
        mask = np.array(Image.fromarray(mask).resize(oct_bscan.shape))
        masks.append(mask)
        pbar.update(1)
        
    masks = np.array(masks)
    seg_volume = []
    half_window = 30
    for i, (mask, octa_img) in enumerate(zip(masks, octa_volume)):
        start = i - half_window if i >= half_window else 0
        end = i+half_window if i < masks.shape[0]-half_window else masks.shape[0]
        mask = np.average(masks[start:end], axis=0)
        # masks[i] = mask
        mask[mask < 0.5] = 0; mask[mask >= 0.5] = 1
        segmented = octa_img*mask
        # show_image([mask, segmented], cmap='gray', multi=True)
        seg_volume.append(segmented)
        
    seg_volume = np.array(seg_volume)
    if img_bit_depth == 16:
        seg_volume = seg_volume.astype(np.uint16)
    
    assert seg_volume.shape[0] == octa_volume.shape[0]
    
    return seg_volume

def norm_volume(volume, bit_depth:int=None, max_value=1, np_type=None):
    """Normalize volume between 0 and max_value"""
    if bit_depth is None:
        maxim = 1
    else:
        maxim = math.pow(2, bit_depth) - 1
    norm_v = ((volume / maxim)*max_value)
    if np_type is not None:
        norm_v = norm_v.astype(np_type)
    
    return norm_v

class RawProcessingError(Exception):
    pass

def process_oct(raw_path:str, width_pixels:int, height_pixels:int, num_images:int=1, horizontal_flip:bool=True,
                    vertical_flip:bool=False, resize:tuple[int, int]=None, reverse:bool=True) -> Cube:
    """ Returns Cube Object.
        --> horizontal_flip and reverse options are True by default due to that cirrus volumes are
        saved backwards

        -> reads cube with bit_depth=16, mode='unsigned'
        -> Volume values will be between 0 and 65535
    """
    if num_images < 1:
        raise RawProcessingError("'num_images' can't be less than 1")

    # En binario con 16 bits representamos del 0 - 65535
    # En hexadecimal con 2 byte representamos del 0 - 65535 (FFFF) (La info de un pixel)
    bit_depth = 16
    binary_hex_ratio = 16/2
    hex_depth = int(bit_depth/binary_hex_ratio)
    pixel_length = hex_depth
    slice_pixels = width_pixels*height_pixels
    slice_length = slice_pixels*pixel_length

    cube_data = []
    with open(raw_path, 'rb') as raw_file:
        volume:str = raw_file.read()
        if len(volume) < slice_length*num_images:
            msg = "'num_images' is incorrect (too much images with that image size)"
            raise RawProcessingError(msg)
        for i in range(num_images):
            raw_slice = volume[i*slice_length:(i+1)*slice_length]
            # Usamos Image.frombytes porque lo lee muy rapido (optimizado), usando bucles normales tarda mucho
            slice_ = Image.frombytes(mode="I;16", size=(width_pixels, height_pixels), data=raw_slice)
            if resize is not None: slice_ = slice_.resize(resize)
            slice_ = np.array(slice_)
            if vertical_flip: slice_ = np.flipud(slice_)
            cube_data.append(slice_)

    cube_data = np.array(cube_data).astype(np.uint16)

    if reverse: cube_data = np.flip(cube_data, axis=1)
    
    cube = Cube(cube_data)
    if horizontal_flip: cube = cube.hflip_slices()

    return cube