# I'm going to allow that torch is not installed, it seemed a unwise to demand the installation of such a large library
_TORCH_FOUND = True
try:
    import torch
except ModuleNotFoundError:
    _TORCH_FOUND = False

import PIL
from PIL import Image
import requests
from rectpack import newPacker
import cv2 as cv2
import numpy as np
import warnings as warnings
from . import __checker as checker
import os
import re

def _get_collage_image(images:list, allow_rotations:bool=False):
    """
    Used to pack `images` into a single image.
    NOTE: This function is only intended to be used by `show()`

    @param images: list of images in np.ndarray format
    @param allow_rotations: Determine if the packing algorithm is allowed to rotate the images
    @return: A single collage image build from `images` in `np.ndarray` format
    """

    # A lot of the complexity is removed if all the images are of the same size. This means that a much more constrained approached can be used.
    if all([images[0].shape == image.shape for image in images]):
        cols, rows, resize_factor, _ = _get_grid_parameters(images)
        return _get_grid_image(images, cols, rows, resize_factor)

    # Setup
    rectangles = [(s.shape[0], s.shape[1], i) for i, s in enumerate(images)]
    height_domain = [60 * i for i in range(1, 8)] + [int(1080 * 8 / 1.05 ** i) for i in range(50, 0, -1)]
    width_domain = [100 * i for i in range(1, 8)] + [int(1920 * 8 / 1.05 ** i) for i in range(50, 0, -1)]
    canvas_dims = list(zip(height_domain, width_domain)) # Just different sizes to try
    canvas_image = None
    max_x, min_y = -1, 1e6 # Used to crop the grey parts

    # Attempt to pack all images into the smallest of the predefined width-height combinations
    for canvas_dim in canvas_dims:

        # Try packing
        packer = newPacker(rotation=allow_rotations)
        for r in rectangles: packer.add_rect(*r)
        packer.add_bin(*canvas_dim)
        packer.pack()

        # If all images couldn't fit, try with a larger image
        if len(packer.rect_list()) != len(images):
            continue

        # Setup
        canvas_image = np.zeros((canvas_dim[0], canvas_dim[1], 3)).astype(np.uint8) + 65 # 65 seems to be a pretty versatile grey color i.e. it looks decent no matter the pictures
        H = canvas_image.shape[0]

        for rect in packer[0]:
            image = images[rect.rid]
            h, w, y, x = rect.width, rect.height, rect.x, rect.y

            # Transform origin to upper left corner
            y = H - y - h

            # Handle image rotations if necessary
            if image.shape[:-1] != (h, w): image = image.transpose(1, 0, 2)
            canvas_image[y:y+h, x:x+w, :] = image

            if max_x < (x+w): max_x = x+w
            if min_y > y: min_y = y

        break

    if canvas_image is None:
        raise RuntimeError("Failed to produce mosaic image. This is probably caused by to many and/or to large images")

    if (max_x == -1) or (min_y == 1e6):
        raise RuntimeError("This should not be possible.")

    return canvas_image[min_y:, :max_x, :]


def _get_grid_parameters(images, max_height=1080, max_width=1920, desired_ratio=9/17):
    """
    Try at estimate #cols, #rows and resizing factor necessary for displaying a list of images in a visually pleasing way.
    This is essentially done by minimizing 3 separate parameters:
        (1) difference between `desired_ratio` and height/width of the final image
        (2) Amount of image scaling necessary
        (3) the number of empty cells (e.g. 3 images on a 2x2 --> empty_cell = 1)

    NOTE1: This was a pretty challenging function to write and the solution may appear a bit convoluted.
           I've included some notes at "doc/_get_grid_parameters.jpg" which will hopefully motivate the solution -
           in particular the loss-function used for optimization.
    NOTE2: This function is only intended to be used by `show()`

    @param images: list np.ndarray images
    @param max_height:
    @param max_width:
    @param desired_ratio:
    @return: cols, rows, scaling_factor, loss_info
    """

    N = len(images)
    h, w, _ = images[0].shape
    H, W = max_height, max_width

    losses = {}
    losses_split = []
    for a in [0.05 + 0.01 * i for i in range(96)]:
        for x in range(1, N + 1):
            for y in range(1, N + 1):

                # If the solution is not valid continue
                if (h * a * y > H) or (w * a * x > W) or (x * y < N):
                    continue
                # Otherwise calculate loss
                else:
                    ratio_loss = abs((h * y) / (w * x) - desired_ratio) # (1)
                    scale_loss = (1 - a) ** 2 # (2)
                    empty_cell_loss = x*y/N - 1 # (3)
                    losses[(y, x, a)] = ratio_loss + scale_loss + empty_cell_loss
                    losses_split.append([ratio_loss, scale_loss, empty_cell_loss])

    # pick parameters with the lowest loss
    rl, sl, ecl = losses_split[np.argmin(list(losses.values()))]
    loss_info = {"ratio":rl, "scale":sl, "empty_cell":ecl, "total":rl+sl+ecl}
    cols, rows, scaling_factor = min(losses, key=losses.get)
    return cols, rows, scaling_factor, loss_info


def _get_grid_image(images:list, cols:int, rows:int, resize_factor:float=1.0):
    """
    Put a list of np.ndarray images into a single combined image.
    NOTE: This function is only intended to be used by `show()`

    @param images: list np.ndarray images
    @param cols: Number of columns with images
    @param rows: Number of rows with images
    @param resize_factor: Image resize factor
    @return: On single picture with all the images in `images`
    """

    h_old, w_old, _ = images[0].shape
    h = int(h_old * resize_factor)
    w = int(w_old * resize_factor)
    canvas = np.zeros((int(h_old * resize_factor * cols), int(w_old * resize_factor * rows), 3))
    canvas = canvas.astype(np.uint8)

    image_index = -1
    for col in range(cols):
        for row in range(rows):
            image_index += 1
            if image_index >= len(images): break

            # Load and rescale image
            image = images[image_index]
            image = cv2.resize(image, (w, h), interpolation=cv2.INTER_AREA)

            # Add image to the final image
            canvas[col * h: (col + 1) * h, row * w: (row + 1) * w, :] = image
    return canvas


def _get_image(source, resize_factor: float = 1.0, BGR2RGB: bool = None, image_border:int = None):
    """
    Take an image in format: path, url, np.ndarray, PIL.Image.Image or torch.tensor.
    Returns `source` as np.ndarray image after some processing e.g. remove alpha

    NOTE: This function is only intended to be used by `show()`
    """

    # `source` and `resize` checks
    is_path = os.path.exists(source) if isinstance(source, str) else False
    is_url = True if isinstance(source, str) and checker.is_valid_url(source) is True else False
    is_ndarray = True if isinstance(source, np.ndarray) else False
    is_torch_tensor = True if (_TORCH_FOUND and isinstance(source, torch.Tensor)) else False
    is_pillow = True if isinstance(source, PIL.Image.Image) else False

    if not any([is_path, is_url, is_ndarray, is_torch_tensor, is_pillow]):
        extra = f"You passed the string ´{source}´, is this perhaps an invalid path or URL?" if isinstance(source, str) else ""
        raise ValueError("`source` couldn't be recognized as a path, url, ndarray pillow_image or tensor." + extra)

    if is_path and is_url:
        raise AssertionError("This should not be possible")  # Don't see how a `source` can be a path and a url simultaneously

    if resize_factor < 0:
        raise ValueError(f"`resize_factor` > 0, received value of {resize_factor}")

    if (is_ndarray or is_torch_tensor) and len(source.shape) <= 1:
        raise ValueError(f"Expected image to have at least to channels, but received {len(source.shape)}.")

    if is_torch_tensor and len(source.shape) > 3:
        raise ValueError(f"Expected tensor image to be of shape (channels, height, width), but received: {source.shape}. "
                         f"If you passed a single image as a batch use <YOUR_IMAGE>.squeeze(0). "
                         f"Otherwise pick a single image or split the batch into individual images an pass them all")

    if is_torch_tensor and (len(source.shape) == 3) and (source.shape[0] >= source.shape[1] or source.shape[0] >= source.shape[2]):
        raise ValueError(f"Expect tensor image to be of shape (channels, height, width), but received: {source.shape}. "
                         f"If your image is of shape (height, width, channels) use `<YOUR_IMAGE>.permute(2, 0, 1)`")


    # Remap from various data types to uint8 if possible
    if (is_torch_tensor or is_ndarray) and (re.search("uint8", str(source.dtype)) is None):
        is_float = (re.search("float", str(source.dtype)) is not None)
        is_int = (re.search("int", str(source.dtype)) is not None)
        map_to_uint8 = lambda s: s.astype(np.uint8) if is_ndarray else s.to(torch.uint8)

        # If all pixel values are in range 0-255 --> remap to range 0-255 and cast to unit8
        if (is_float or is_int) and (0.0 <= source ).all() and (source <= 1.0 ).all():
            source = map_to_uint8(source*255)

        # If any pixel value exceed 1 and all pixels are in range 0-255 --> cast to unit8 directly
        elif (is_float or is_int) and (source > 1.0).any() and (0.0 <= source).all() and (source <= 255.0).all():
            source = map_to_uint8(source)

        else:
            suggestion = "<YOUR_IMAGE>.to(torch.uint8)" if is_torch_tensor else "<YOUR_IMAGE>.astype(np.uint8)"
            raise ValueError(f"Expected type `uint8`, but received dtype `{source.dtype}`."
                             f" Try changing the image type with `{suggestion}`")

    # Ensure `source` is a numpy image
    if is_pillow:
        image = np.asarray(source)
    elif is_path:
        image = np.asarray(Image.open(source))
    elif is_url:
        image = np.asarray(Image.open(requests.get(source, stream=True).raw))
    elif is_ndarray:
        image = source
    elif is_torch_tensor:
        source = source.detach().cpu()
        corrected = source.permute(1, 2, 0) if (len(source.shape) > 2) else source
        image = corrected.numpy()
    else:
        raise RuntimeError("Shouldn't have gotten this far")

    # Swap blue and red color channel (cv2 stuff)
    num_channels = len(image.shape)
    bgr2rgb_auto = (BGR2RGB is None) and is_ndarray and (num_channels in [3, 4])
    if BGR2RGB or bgr2rgb_auto:
        # BGR --> RGB or BGRA --> RGBA
        if (num_channels == 3):
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)

    # Resize
    if resize_factor != 1.0:
        width = int(image.shape[1] * resize_factor)
        height = int(image.shape[0] * resize_factor)
        image = cv2.resize(image, (width, height))

    # Add border
    if image_border is not None:
        image = cv2.copyMakeBorder(image, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=[image_border] * 3)

    # Adds 3 identical channels to greyscale images (for compatibility)
    if (len(image.shape) == 2) or (image.shape[-1] == 1):
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

    # Remove alpha channel (for compatibility)
    if image.shape[-1] == 4:
        image = image[:,:,:3]

    return image


def _save_image_to_disk(path:str, image:np.ndarray):
    if os.path.exists(path):
        raise ValueError(f"The file `{path}` already exists.")
    if path[-4:].lower() not in [".jpg", ".png"]:
        raise ValueError("`save_to_path` must be suffixed by `.png` or `.jpg`, but found neither.")
    cv2.imwrite(path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))


def show(source, resize_factor:float=1.0, BGR2RGB:bool=False, return_without_show:bool=False, image_border:int=None, save_to_path:str=None):
    """
    Display a single image or a list of images.
    Accepted image formats: path, np.ndarray, PIL.Image.Image, torch.Tensor and url.

    @param source: path, np.ndarray, PIL.Image.Image, torch.Tensor url pointing to the image you wish to display
    @param resize_factor: Rescale factor in percentage (i.e. 0-1)
    @param BGR2RGB: Convert `source` from BGR to RGB. If `None`, will convert np.ndarray images automatically
    @param return_without_show: In the off change that you need the image returned, but not shown.
    @param image_border: If not None, add border around each image equal to the value of `image_border` must be in [0,255]
    @param save_to_path: Path where the final image should be saved at. NOTE: This path must end on `.jpg` or `png`
    """

    # Checks
    if not _TORCH_FOUND:
        checker.assert_in(type(source), [np.ndarray, PIL.Image.Image, str, list, tuple])
    else:
        checker.assert_in(type(source), [np.ndarray, torch.Tensor, PIL.Image.Image, str, list, tuple])
    checker.assert_types([resize_factor, BGR2RGB, return_without_show, image_border, save_to_path],
                         [float, bool, bool, int, str], [0, 1, 0, 1, 1])

    if isinstance(source, (list, tuple)) and (not len(source)):
        raise ValueError("`source` should contain image-information, but` is empty. Did you perhaps pass an empty list or something similar?")

    if (image_border is not None) and not (0 <= image_border <= 255):
        raise ValueError("`image_border` is a pixel value and must therefore be between [0,255], "
                         f"but received `{image_border}`")


    # Prepare the final image(s)
    if type(source) not in [list, tuple]:
        final_image = _get_image(source, resize_factor, BGR2RGB)
    else:
        if len(source) > 200: # Anything above 200 indexes seems unnecessary
            warnings.warn(
                f"Received `{len(source)}` images, the maximum limit is 200. "
                "Will pick 200 random images from `source` for display and discard the rest"
            )
            random_indexes_200 = np.random.choice(np.arange(len(source)), 200, replace=False)
            source = [source[i] for i in random_indexes_200]

        images = [_get_image(image, resize_factor, BGR2RGB, image_border) for image in source]
        final_image = _get_collage_image(images, allow_rotations=False)


    # Resize the final image if it's larger than 2160x3840
    scale_factor = None
    if final_image.shape[1] > 3840:
        scale_factor = 3840/final_image.shape[1]
    elif final_image.shape[0] > 2160:
        scale_factor = 2160 / final_image.shape[0]
    if scale_factor:
        height = int(final_image.shape[0]*scale_factor)
        width = int(final_image.shape[1]*scale_factor)
        final_image = cv2.resize(final_image, (width, height))

    # Save image
    if save_to_path is not None:
        _save_image_to_disk(save_to_path, final_image)

    # Return image without displaying it
    if return_without_show:
        return final_image

    # Display image
    if checker.in_jupyter():
        final_image = Image.fromarray(final_image)
        display(final_image)
        np.asarray(final_image)
    else:
        cv2.imshow("Just show it", final_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()



__all__=[
    "show"
 ]
