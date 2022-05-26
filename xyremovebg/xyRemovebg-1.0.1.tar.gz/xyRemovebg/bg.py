import io
from typing import Optional

import numpy as np
import onnxruntime as ort
import cv2 as cv
from PIL import Image, ImageEnhance, ImageChops
from pymatting.alpha.estimate_alpha_cf import estimate_alpha_cf
from pymatting.foreground.estimate_foreground_ml import estimate_foreground_ml
from pymatting.util.util import stack_images
from scipy.ndimage.morphology import binary_erosion

from .detect import ort_session, predict

def bi_mopi(image: Image, mpdepth: int) -> Image:
    _mpdepth = mpdepth * 20 #基础强度20

    # image to cv
    img = cv.cvtColor(np.asarray(image), cv.COLOR_BGR2RGB)  
    blur_img = cv.bilateralFilter(img, 31, _mpdepth, _mpdepth)

    #图像融合
    result_img = cv.addWeighted(img, 0.3, blur_img, 0.7, 0)

    # 锐度调节
    enh_img = ImageEnhance.Sharpness(Image.fromarray(cv.cvtColor(result_img, cv.COLOR_BGR2RGB)))
    image_sharped = enh_img.enhance(1.5)
    # 对比度调节
    con_img = ImageEnhance.Contrast(image_sharped)  
    image_con = con_img.enhance(1)

    return image_con


def autocrop(img):
    bg = Image.new(img.mode, img.size, img.getpixel((0,0)))
    diff = ImageChops.difference(img, bg)
    diff = ImageChops.add(diff, diff, 0.2, -100)
    bbox = diff.getbbox()
    if bbox:
        return img.crop(bbox)


def alpha_matting_cutout(
    img: Image,
    mask: Image,
    foreground_threshold: int,
    background_threshold: int,
    erode_structure_size: int,
) -> Image:
    img = np.asarray(img)
    mask = np.asarray(mask)

    # guess likely foreground/background
    is_foreground = mask > foreground_threshold
    is_background = mask < background_threshold

    # erode foreground/background
    structure = None
    if erode_structure_size > 0:
        structure = np.ones(
            (erode_structure_size, erode_structure_size), dtype=np.uint8
        )

    is_foreground = binary_erosion(is_foreground, structure=structure, border_value=1)
    is_background = binary_erosion(is_background, structure=structure, border_value=1)

    # build trimap
    # 0   = background
    # 128 = unknown
    # 255 = foreground
    trimap = np.full(mask.shape, dtype=np.uint8, fill_value=128)
    trimap[is_foreground] = 255
    trimap[is_background] = 0

    # # build the cutout image
    img_normalized = img / 255.0
    trimap_normalized = trimap / 255.0

    alpha = estimate_alpha_cf(img_normalized, trimap_normalized, laplacian_kwargs=dict(epsilon=1e-5))
    foreground = estimate_foreground_ml(img_normalized, alpha)
    cutout = stack_images(foreground, alpha)

    cutout = np.clip(cutout * 255, 0, 255).astype(np.uint8)
    cutout = Image.fromarray(cutout)

    return cutout


def naive_cutout(img: Image, mask: Image) -> Image:
    empty = Image.new("RGBA", (img.size))

    cutout = Image.composite(img, empty, mask)
    
    return cutout


def remove(
    data: bytes,
    alpha_matting: bool = False,
    alpha_matting_foreground_threshold: int = 240,
    alpha_matting_background_threshold: int = 10,
    alpha_matting_erode_size: int = 10,
    session: Optional[ort.InferenceSession] = None,
    only_mask: bool = False,
    mp: bool = False,
    mpdepth: int = 1,
) -> bytes:
    img = Image.open(io.BytesIO(data)).convert("RGB")

    if session is None:
        session = ort_session("u2net")

    mask = predict(session, np.array(img)).convert("L")
    # img.thumbnail((4000, 4000), Image.LANCZOS)
    mask = mask.resize(img.size, Image.LANCZOS)

    if mp: 
        img = bi_mopi(img, mpdepth)

    if only_mask:
        cutout = mask

    elif alpha_matting:
        try:
            cutout = alpha_matting_cutout(
                img,
                mask,
                alpha_matting_foreground_threshold,
                alpha_matting_background_threshold,
                alpha_matting_erode_size,
            )
            # cutout = naive_cutout(img, mask)
        except Exception:
            cutout = naive_cutout(img, mask)
    else:
        cutout = naive_cutout(img, mask)

    cutout = autocrop(cutout)

    bio = io.BytesIO()
    cutout.save(bio, "PNG")
    bio.seek(0)

    return bio.read()