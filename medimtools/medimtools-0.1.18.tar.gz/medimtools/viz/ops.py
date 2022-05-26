import SimpleITK as sitk
from loguru import logger
import numpy as np


def make_isotropic(image, interpolator=sitk.sitkLinear):
    # TODO: If not a CT scan, what is the default value to be set while resampling?
    """
    # Source: http://insightsoftwareconsortium.github.io/SimpleITK-Notebooks/Python_html/05_Results_Visualization.html
    Resample an image to isotropic pixels (using smallest spacing from original) and save to file. Many file formats
    (jpg, png,...) expect the pixels to be isotropic. By default the function uses a linear interpolator. For
    label images one should use the sitkNearestNeighbor interpolator so as not to introduce non-existant labels.
    """
    original_spacing = image.GetSpacing()
    # Image is already isotropic, just return a copy.
    if all(spc == original_spacing[0] for spc in original_spacing):
        return sitk.Image(image)
    # Make image isotropic via resampling.
    original_size = image.GetSize()
    min_spacing = min(original_spacing)
    new_spacing = [min_spacing] * image.GetDimension()
    new_size = [
        int(round(osz * ospc / min_spacing))
        for osz, ospc in zip(original_size, original_spacing)
    ]
    return sitk.Resample(
        image,
        new_size,
        sitk.Transform(),
        interpolator,
        image.GetOrigin(),
        new_spacing,
        image.GetDirection(),
        -1024,
        image.GetPixelID(),
    )


def get_image_preview(sitk_image, orientation="horizontal", coords=None):
    """Saves a preview image for a given SimpleITK object. In case of 3D image, saves
    an image combined of middle slices from axial, coronal and saggital views.
    """
    dims = sitk_image.GetDimension()
    image = sitk.GetArrayFromImage(sitk_image)

    _coords = [image.shape[idx] // 2 for idx in range(3)]

    if coords is not None:
        # SITK to numpy is x,y,z -> z,x,y
        coords = [coords[2], coords[0], coords[1]]
        coords = [
            coord if coord != -1 else _coords[idx] for idx, coord in enumerate(coords)
        ]
    else:
        coords = _coords

    if dims == 3:
        middle_axial = image[coords[0]]
        middle_coronal = image[:, coords[1]]
        middle_sagittal = image[:, :, coords[2]]

        # Flip for correct visual
        middle_sagittal = np.flipud(middle_sagittal)
        middle_coronal = np.flipud(middle_coronal)

        preview_image = padded_stack(
            (middle_axial, middle_sagittal, middle_coronal), orientation=orientation
        )

    elif dims == 2:
        preview_image = image

    else:
        logger.error("Image preview not implemented for 4D images")
        return  # TODO: implement for 4D
    return preview_image


"""

Simplified Utilities

"""


def all_identical(sequence):
    """Check if all values of a list or tuple are identical."""
    return sequence.count(sequence[0]) == len(
        sequence
    )  # https://stackoverflow.com/a/3844948


def pad_to(arr, target, index):
    ndim = len(arr.shape)
    # Pad needs to be ndimx2 of the array
    pad_tuple = np.zeros((ndim, 2), dtype=int)
    pad_tuple[index][1] = target - arr.shape[index]
    pad_tuple = [list(v) for v in pad_tuple]

    return np.pad(arr, pad_tuple)


def padded_stack(arrays, orientation="vertical"):
    if orientation == "vertical":
        # 1st index is the width, if vertical stacking needs to
        # be done, it will be stacked along the width
        index = 1
        stack_fn = np.vstack

    elif orientation == "horizontal":
        # 0th index is the height, if horizontal stacking needs to
        # be done, it will be stacked along the height
        index = 0
        stack_fn = np.hstack

    dims = [arr.shape[index] for arr in arrays]

    if not all_identical(dims):
        arrays = [pad_to(arr, max(dims), index) for arr in arrays]

    return stack_fn(arrays)


def get_contour(mask):
    filter = sitk.LabelContourImageFilter()
    mask = filter.Execute(mask)

    return mask
