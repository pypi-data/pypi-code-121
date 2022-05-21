import os
from typing import List, Optional, Any

from functools import partial
import tensorflow as tf

from tensorflow_similarity.types import Tensor
from tensorflow_similarity.augmenters.augmenter import Augmenter
from tensorflow_similarity.augmenters.augmentation_utils.cropping import (
    random_resized_crop,
)
from tensorflow_similarity.augmenters.augmentation_utils.flip import (
    random_random_flip_left_right,
)
from tensorflow_similarity.augmenters.augmentation_utils.color_jitter import (
    random_color_jitter,
)
from tensorflow_similarity.augmenters.augmentation_utils.blur import random_blur
from tensorflow_similarity.augmenters.augmentation_utils.solarize import (
    random_solarize,
)


@tf.function
def augment_barlow(
    image: Tensor,
    height: int,
    width: int,
    flip_probability=0.5,
    brightness_multiplier=0.8,
    contrast_multiplier=0.6,
    saturation_multiplier=0.6,
    hue_multiplier=0.2,
    jitter_probability=0.8,
    greyscale_probability=0.2,
    blur_probability=0.2,
    blur_min_sigma=0,
    blur_max_sigma=1,
    solarize_probability=0.2,
    solarize_pixel_min=0,
    solarize_pixel_max=255,
    solarize_thresh=10,
):
    image = tf.cast(image, dtype="float32")
    image = random_resized_crop(image, height, width)
    image = random_random_flip_left_right(image, p=flip_probability)
    image = random_color_jitter(
        image,
        p_jitter=jitter_probability,
        p_grey=greyscale_probability,
        strength=1.0,
        brightness_multiplier=brightness_multiplier,
        contrast_multiplier=contrast_multiplier,
        saturation_multiplier=saturation_multiplier,
        hue_multiplier=hue_multiplier,
        impl="additive",
    )
    image = random_blur(
        image=image,
        height=height,
        width=width,
        p=blur_probability,
        min_sigma=blur_min_sigma,
        max_sigma=blur_max_sigma,
    )
    image = random_solarize(
        image,
        thresh=solarize_thresh,
        p=solarize_probability,
        pixel_min=solarize_pixel_min,
        pixel_max=solarize_pixel_max,
    )
    image = tf.clip_by_value(image, 0, 1)

    return image


class BarlowAugmenter(Augmenter):
    def __init__(
        self,
        width: int,
        height: int,
        flip_probability=0.5,
        brightness_multiplier=0.8,
        contrast_multiplier=0.6,
        saturation_multiplier=0.6,
        hue_multiplier=0.2,
        jitter_probability=0.8,
        greyscale_probability=0.2,
        blur_probability=0.2,
        blur_min_sigma=0,
        blur_max_sigma=1,
        solarize_probability=0.2,
        solarize_pixel_min=0,
        solarize_pixel_max=255,
        solarize_thresh=10,
        num_cpu: Optional[int] = os.cpu_count(),
    ):
        super().__init__()
        self.num_cpu = num_cpu
        self.width = width
        self.height = height
        self.flip_probability = flip_probability
        self.brightness_multiplier = brightness_multiplier
        self.contrast_multiplier = contrast_multiplier
        self.saturation_multiplier = saturation_multiplier
        self.hue_multiplier = hue_multiplier
        self.jitter_probability = jitter_probability
        self.greyscale_probability = greyscale_probability
        self.blur_probability = blur_probability
        self.blur_min_sigma = blur_min_sigma
        self.blur_max_sigma = blur_max_sigma
        self.solarize_probability = solarize_probability
        self.solarize_pixel_min = solarize_pixel_min
        self.solarize_pixel_max = solarize_pixel_max
        self.solarize_thresh = solarize_thresh

    @tf.function
    def augment(
        self,
        x: Any,
        y: Any = tf.constant([0]),
        num_augmentations_per_example: int = 2,
        is_warmup: bool = True,
    ) -> List[Any]:

        with tf.device("/cpu:0"):
            inputs = tf.stack(x)
            inputs = tf.cast(inputs, dtype="float32")

            views = []

            augment_fn = partial(
                augment_barlow,
                # image=img,
                height=self.height,
                width=self.width,
                flip_probability=self.flip_probability,
                brightness_multiplier=self.brightness_multiplier,
                contrast_multiplier=self.contrast_multiplier,
                saturation_multiplier=self.saturation_multiplier,
                hue_multiplier=self.hue_multiplier,
                jitter_probability=self.jitter_probability,
                greyscale_probability=self.greyscale_probability,
                blur_probability=self.blur_probability,
                blur_min_sigma=self.blur_min_sigma,
                blur_max_sigma=self.blur_max_sigma,
                solarize_probability=self.solarize_probability,
                solarize_pixel_min=self.solarize_pixel_min,
                solarize_pixel_max=self.solarize_pixel_max,
                solarize_thresh=self.solarize_thresh,
            )
            for _ in range(num_augmentations_per_example):

                view = tf.map_fn(
                    lambda img: augment_fn(image=img),
                    inputs,
                    parallel_iterations=self.num_cpu,
                )
                views.append(view)
        return views

    def __call__(
        self,
        x: Any,
        y: Any = tf.constant([0]),
        num_augmentations_per_example: int = 2,
        is_warmup: bool = True,
    ) -> List[Any]:
        return list(self.augment(x))
