import base64
import io
import os
from functools import wraps
from typing import Tuple, Union

import cv2
import numpy as np
import requests
from PIL.Image import Image, fromarray, LINEAR, ANTIALIAS
from aio_pika import Message

from logger import logger
from botocore.config import Config
import boto3
import pix_plus.pix_plus.protos.proto_pixplus_pb2 as ptype


def async_log_error():
    def wrapper(func):
        @wraps(func)
        async def wrapped(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as err:
                logger.debug(f"An error was occurred at {func.__name__} function. Traceback: {err}")

        return wrapped

    return wrapper


def log_error():
    def wrapper(func):
        @wraps(func)
        def wrapped(*args):
            try:
                return func(*args)
            except Exception as err:
                logger.debug(f"An error was occurred at {func.__name__} function. Traceback: {err}")

        return wrapped

    return wrapper


async def throw_exception(error_message, query_message, message, exchange, message_proto, traceback="", version=""):
    """
    :param error_message:
    :param query_message:
    :param message:
    :param exchange:
    :param message_type: proto type of the message to be passed
    :param traceback:
    :param version:
    :return:
    """
    exception_log = {
        "id_user": query_message.id_user,
        "id_job": query_message.id_job,
        "timestamp": query_message.timestamp,
        "traceback": traceback,
        "version": version,
    }
    logger.error("{}, {}, {}".format(error_message, traceback, exception_log))
    output_msg = message_proto(success=False, service_debug=ptype.ServiceDebug(traceback=traceback, version=version), )
    await exchange.publish(
        Message(body=output_msg.SerializeToString(), correlation_id=message.correlation_id,),
        routing_key=message.reply_to,
    )
    return



def download_dir_s3(prefix, local, bucket, client):
    """
    params:
    - prefix: pattern to match in s3
    - local: local path to folder in which to place files
    - bucket: s3 bucket with target contents
    - client: initialized s3 client object
    """
    keys = []
    dirs = []
    next_token = ""
    base_kwargs = {
        "Bucket": bucket,
        "Prefix": prefix,
    }
    while next_token is not None:

        kwargs = base_kwargs.copy()
        if next_token != "":
            kwargs.update({"ContinuationToken": next_token})
        results = client.list_objects_v2(**kwargs)
        contents = results.get("Contents")
        for i in contents:
            k = i.get("Key")
            if k[-1] != "/":
                keys.append(k)
            else:
                dirs.append(k)
        next_token = results.get("NextContinuationToken")

    for d in dirs:
        dest_pathname = os.path.join(local, d)
        if not os.path.exists(os.path.dirname(dest_pathname)):
            os.makedirs(os.path.dirname(dest_pathname))

    for k in keys:
        dest_pathname = os.path.join(local, "/".join(k.split("/")[1:]))
        if not os.path.exists(os.path.dirname(dest_pathname)):
            os.makedirs(os.path.dirname(dest_pathname))
        if not os.path.exists(dest_pathname):
            client.download_file(bucket, k, dest_pathname)

    return


def get_image_with_scale_min_dim(
        image_arg: Union[Image, np.ndarray], ref_dim: int = 533
) -> Tuple[Union[Image, np.ndarray], float]:
    """
    rescale image
    :param image_arg: image (it can be an array or PIL)
    :param ref_dim: got from training phase, constant
    :return: resized image and the scale
    """
    if isinstance(image_arg, Image):
        logger.info(f"Rescaling Image")
        min_dim = min(image_arg.width, image_arg.height)
        scale = ref_dim / min_dim
        img = image_arg.resize((int(image_arg.width * scale), int(image_arg.height * scale)), ANTIALIAS)
        resized_image = np.array(np.asarray(img), dtype=np.uint8)

    elif isinstance(image_arg, np.ndarray):
        logger.info(f"Rescaling Image as numpy.array")
        scale = ref_dim / min(image_arg.shape[0], image_arg.shape[1])
        rows = scale * image_arg.shape[0]
        cols = scale * image_arg.shape[1]
        resized_image = cv2.resize(image_arg, (int(cols), int(rows)))

    else:
        raise ValueError(
            f"Passed parameter image_arg has type {type(image_arg)}, which is not supported in the resize function"
        )

    return resized_image, scale


def get_output_image_resolution(
        image_arg: Union[Image, np.ndarray], output_ref_dim: Union[int, float] = 1000
) -> Tuple[Image, np.ndarray, int, Tuple[int, int]]:
    """
    rescale image
    :param image_arg: image (it can be an array or PIL)
    :param output_ref_dim: desired output dimension
    :return:
    """

    if isinstance(image_arg, Image):
        scale = image_arg.height / output_ref_dim
        rows = output_ref_dim
        cols = output_ref_dim * 0.75
        resized_image = image_arg.resize((int(cols), int(rows)), ANTIALIAS)

    elif isinstance(image_arg, np.ndarray):
        min_dim = min(image_arg.shape[0], image_arg.shape[1])
        if min_dim <= output_ref_dim:
            rows = output_ref_dim
            cols = output_ref_dim * 0.75
            return fromarray(image_arg), image_arg, 1, (int(cols), int(rows))
        else:
            scale = image_arg.shape[0] / output_ref_dim
            rows = output_ref_dim
            cols = output_ref_dim * 0.75
            resized_image = cv2.resize(image_arg, (int(cols), int(rows)))
    else:
        logger.error("Unknown image type has been passed", extra={"image_type": str(type(image_arg))})
        raise NotImplementedError("Unknown image type has been passed")

    return fromarray(resized_image), resized_image, scale, (int(cols), int(rows))


def image_preprocess(
        input_message: ptype.PixPlusInputMessage, classification_result: ptype.PhotoClassificationMessage, ref_dim=533
) -> Union[Image, np.ndarray]:
    logger.info(
        f"Image preprocessing started: input message {input_message}, classification_result: {classification_result}"
    )
    image_orientation: int = classification_result.image_orientation
    image_pose: ptype.ImagePose = classification_result.image_pose

    try:
        input_image_stream = io.BytesIO(requests.get(input_message.imageUrl).content)
    except Exception as err:
        logger.error(f"Couldn't get the image: error {err}")
        raise ValueError("Stopped the image preprocessing.")
    orig_np_img: np.ndarray = cv2.imdecode(np.frombuffer(input_image_stream.read(), np.uint8), 1)
    min_dim: int = min(orig_np_img.shape)
    if min_dim != ref_dim:
        logger.info(f"Getting the image with scale minimal dimension")
        r_np_img, scale_factor = get_image_with_scale_min_dim(orig_np_img, ref_dim=ref_dim)
        r_pil_img = fromarray(r_np_img)
    else:
        logger.info(f"Getting the original image as array")
        r_np_img, scale_factor = orig_np_img.copy()
        r_pil_img = fromarray(r_np_img)

    logger.info(f"Starting image correction")
    r_pil_img, r_np_img, corr_orig_np_img, rot_angle = image_correction(
        r_pil_img, orig_np_img, image_orientation, image_pose
    )

    (
        output_image,
        np_output_image,
        output_scale,
        output_resolution,
    ) = get_output_image_resolution(corr_orig_np_img, output_ref_dim=ref_dim)

    return np_output_image


def image_preprocess_with_np_image(original_np_image, ref_dim):
    min_dim = min(original_np_image.shape)
    if min_dim != ref_dim:
        r_np_img, scale_factor = get_image_with_scale_min_dim(original_np_image, ref_dim=ref_dim)
        r_pil_img = fromarray(r_np_img)
    else:
        r_np_img, scale_factor = original_np_image.copy()
        r_pil_img = fromarray(r_np_img)
    return r_np_img, r_pil_img, scale_factor


def upload_image_s3(input_image, output_url=None, is_local=False):
    if is_local and output_url:
        fromarray(input_image).save(output_url)
    else:
        image = np.ascontiguousarray(input_image)
        _, buffer = cv2.imencode(".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        processed_string = base64.b64encode(buffer)
        image = base64.b64decode(processed_string)
        requests.put(output_url, data=image, headers={"Content-Type": "image/jpeg"})
    return


def image_correction(
        image: Image, orig_np_img: np.ndarray, image_orientation: int, image_pose: ptype.ImagePose
) -> Tuple[Image, np.ndarray, np.ndarray, int]:
    g_rotations = [0, 90, 180, -90]

    if image_pose in [ptype.INTRAORAL_OCCLUSAL_LOWER, ptype.INTRAORAL_OCCLUSAL_UPPER]:
        logger.info(f"Image pose is INTRAORAL_LATERAL_RIGHT or INTRAORAL_OCCLUSAL_LOWER")
        if image_pose == ptype.INTRAORAL_OCCLUSAL_UPPER and image_orientation in [ptype.DEGREE_90, ptype.DEGREE_270]:
            logger.info(f"Image pose is INTRAORAL_OCCLUSAL_UPPER and image_orientation in 90 OR -90 degrees")
            rot_angle: int = -g_rotations[image_orientation]
            orig_pil_img: Image = fromarray(orig_np_img).rotate(-g_rotations[image_orientation], LINEAR, expand=True)
            r_pil_img: Image = image.rotate(-g_rotations[image_orientation], LINEAR, expand=True)

        elif image_pose == ptype.INTRAORAL_OCCLUSAL_LOWER and image_orientation in [ptype.DEGREE_90, ptype.DEGREE_270]:
            logger.info(f"Image pose is INTRAORAL_OCCLUSAL_LOWER and image_orientation in 90 OR -90 degrees")
            rot_angle: int = g_rotations[image_orientation]
            orig_pil_img: Image = fromarray(orig_np_img).rotate(g_rotations[image_orientation], LINEAR, expand=True)
            r_pil_img: Image = image.rotate(g_rotations[image_orientation], LINEAR, expand=True)

        elif (image_pose == ptype.INTRAORAL_OCCLUSAL_UPPER and image_orientation == ptype.DEGREE_180) or (
                image_pose == ptype.INTRAORAL_OCCLUSAL_LOWER and image_orientation == 0
        ):
            logger.info(f"Image pose is INTRAORAL_OCCLUSAL_UPPER and image_orientation in 90 OR -90 degrees")
            logger.debug(
                "Image pose is INTRAORAL_OCCLUSAL_UPPER and image_orientation is 2 OR INTRAORAL_OCCLUSAL_LOWER and image_orientation is 0"
            )
            logger.info(f"Image will be rotated by 180 degrees")
            rot_angle = 180
            orig_pil_img: Image = fromarray(orig_np_img).rotate(180, LINEAR, expand=True)
            r_pil_img: Image = image.rotate(180, LINEAR, expand=True)
        else:
            logger.info(f"Image won't be rotated")
            rot_angle = 0
            orig_pil_img: Image = fromarray(orig_np_img)
            r_pil_img = image
    else:
        logger.debug(f"Image pose is NOT the INTRAORAL_LATERAL_RIGHT or INTRAORAL_OCCLUSAL_LOWER")
        rot_angle: int = -g_rotations[image_orientation]
        orig_pil_img: Image = fromarray(orig_np_img).rotate(-g_rotations[image_orientation], LINEAR, expand=True)
        r_pil_img: Image = image.rotate(-g_rotations[image_orientation], LINEAR, expand=True)

    r_np_img = np.array(r_pil_img)
    orig_np_img = np.array(orig_pil_img)
    return r_pil_img, r_np_img, orig_np_img, rot_angle


def download_models(aws_access_key_id, aws_secret_access_key, region_name, models_bucket, service_name):
    config = Config(s3={"use_accelerate_endpoint": True})
    s3 = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name,
        config=config,
    )
    try:
        logger.info("Downloading models from S3..")
        download_dir_s3(prefix=service_name, local="./models", bucket=models_bucket, client=s3)
        logger.info("Successfully downloaded models from S3")
        del s3
    except Exception as err:
        logger.debug(
            "Error downloading models from S3",
            extra={"init error": "downloading models", "service_error": str(err)},
        )
