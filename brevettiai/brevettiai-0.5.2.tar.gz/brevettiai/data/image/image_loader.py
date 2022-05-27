import json
import tensorflow as tf
import numpy as np

from pydantic import Field, root_validator
from pydantic.typing import Literal
from typing import Optional, ClassVar, Type, Union
from brevettiai.data import FileLoader
from brevettiai.data.image import ImageKeys
from brevettiai.data.image.image_processor import ImageProcessor
from brevettiai.data.tf_types import TfRange, BBOX


class ScalingProcessor(ImageProcessor):
    type: Literal["ScalingProcessor"] = "ScalingProcessor"

    def process(self, image):
        """Process image according to processor"""
        max_ = tf.reduce_max(image)
        min_ = tf.reduce_min(image)
        image = (image - min_) / (max_ - min_)
        return image


class CropResizeProcessor(ImageProcessor):
    type: Literal["CropResizeProcessor"] = "CropResizeProcessor"
    output_height: int = Field(default=0, ge=0, description="Leave at 0 to infer")
    output_width: int = Field(default=0, ge=0, description="Leave at 0 to infer")

    roi_horizontal_offset: int = Field(
        default=0, ge=0, description="Horizontal coordinate of the top-left corner of the bounding box in image.")
    roi_vertical_offset: int = Field(
        default=0, ge=0, description="Vertical coordinate of the top-left corner of the bounding box in image.")
    roi_width: int = Field(default=0, ge=0, description="Width of the bounding box. Zero uses image boundary")
    roi_height: int = Field(default=0, ge=0, description="Height of the bounding box. Zero uses image boundary")

    interpolation: Literal["bilinear", "nearest"] = Field(
        default="bilinear", description="Interpolation mode of cropping and resizing")

    def output_size(self, input_height, input_width):
        """Calculated output size of output after postprocessing, given input image sizes"""
        height = self.roi_height or input_height
        width = self.roi_width or input_width
        return self.output_height or height, self.output_width or width

    def crop_size(self, input_height, input_width):
        height = input_height - self.roi_vertical_offset if self.roi_height == 0 else self.roi_height
        width = input_width - self.roi_horizontal_offset if self.roi_width == 0 else self.roi_width
        return height, width

    def bbox(self, input_height, input_width) -> BBOX:
        """
        Calculate bounding box specified in pixel coordinates [y1, x1, y2, x2]
        The points both being included in the region of interest
        :param input_height: specifying image height to use full image instead of self.roi_height
        :param input_width: specifying image height to use full image instead of self.roi_width
        """
        height, width = self.crop_size(input_height, input_width)
        return BBOX(self.roi_vertical_offset, self.roi_horizontal_offset,
                    self.roi_vertical_offset + height - 1, self.roi_horizontal_offset + width - 1)

    def set_bbox(self, bbox: BBOX):
        self.roi_vertical_offset = bbox.y1
        self.roi_horizontal_offset = bbox.x1
        self.roi_height = bbox.y2 - bbox.y1 + 1
        self.roi_width = bbox.x2 - bbox.x1 + 1
        return self

    def scale(self, input_height, input_width):
        """
        Calculate output image scale given input image size
        returns scale in height then width (sy, sx)
        """
        crop_height, crop_width = self.crop_size(input_height, input_width)
        output_height, output_width = self.output_size(input_width, input_height)
        return (crop_height-1) / (output_height-1), (crop_width-1) / (output_width-1),

    def affine_transform(self, input_height, input_width):
        sy, sx = self.scale(input_height, input_width)

        return np.array([
            [sx,  0, self.roi_horizontal_offset],
            [0, sy, self.roi_vertical_offset],
            [0, 0, 1]
        ])

    def process(self, image):
        shape = tf.shape(image)[:2]
        input_height, input_width = shape[0], shape[1]

        size = self.output_size(input_height, input_width)

        # Normalize bounding box to match crop_and_resize
        # https://www.tensorflow.org/api_docs/python/tf/image/crop_and_resize
        norm = tf.cast([input_height, input_width, input_height, input_width], tf.float32)-1
        bbox = tf.cast(tuple(self.bbox(input_height, input_width)), tf.float32)
        boxes = [bbox / norm]

        # Crop and resize, attach batch dimension to match tf call
        return tf.image.crop_and_resize(
            image[None], boxes, box_indices=[0], crop_size=size, method=self.interpolation,
            extrapolation_value=0.0
        )[0]


class ImageLoader(FileLoader):
    type: Literal["ImageLoader"] = "ImageLoader"
    output_key: str = Field(default="img", exclude=True)
    postprocessor: Optional[Union[CropResizeProcessor, ImageProcessor]] = Field(default_factory=CropResizeProcessor)
    interpolation_method: Optional[Literal["bilinear", "nearest"]] = Field(default="bilinear")
    channels: Literal[0, 1, 3, 4] = Field(default=0, description="Number of channels in images, 0 to autodetect")
    metadata_spec = {
        ImageKeys.BOUNDING_BOX: BBOX.build
    }

    def output_shape(self, image_height=None, image_width=None):
        output_channels = self.channels if self.channels else None
        if self.postprocessor is None:
            return image_height, image_width, output_channels
        else:
            return (*self.postprocessor.output_size(image_height, image_width),
                    self.postprocessor.output_channels(output_channels))

    def load(self, path, metadata=None, postprocess=True, default_shape=(1, 1, 1), bbox: BBOX = BBOX()):
        metadata = metadata or dict()
        data, meta = super().load(path, metadata)
        bbox = metadata.get(ImageKeys.BOUNDING_BOX, bbox)

        if tf.strings.length(data) > 0:
            image = tf.io.decode_image(data, expand_animations=False, channels=self.channels)
            if bbox.area > 1:
                ifs = tf.convert_to_tensor(tf.shape(image))
                image = tf.image.crop_and_resize(image[None],
                                                 [[bbox.y1 / ifs[0], bbox.x1 / ifs[1],
                                                   bbox.y1 / ifs[0] + 1, bbox.x1 / ifs[1] + 1]],
                                                 box_indices=[0],
                                                 crop_size=ifs[:2],
                                                 method=self.interpolation_method,
                                                 extrapolation_value=0.0)[0, :bbox.shape[0], :bbox.shape[1]]
            else:
                image = tf.cast(image, tf.float32)
            _image_file_shape = tf.convert_to_tensor(tf.shape(image))
            if postprocess and self.postprocessor is not None:
                image = self.postprocessor.process(image)
        else:
            image = tf.zeros(shape=default_shape, dtype=tf.float32)
            _image_file_shape = tf.convert_to_tensor(tf.shape(image))

        meta["_image_file_shape"] = _image_file_shape

        return image, meta


class ImageStabiliser(FileLoader):
    type: Literal["ImageStabilisationLoader"] = "ImageStabilisationLoader"

    interpolation: Literal["NEAREST", "BILINEAR"] = Field(default="NEAREST")
    image_key: str = Field(default="img")
    label_key: str = Field(default="segmentation")

    enabled: bool = Field(default=False)

    def load_matrix(self, path):
        bcfile = json.loads(self._io.read_file(path))
        matrices = bcfile.get("transforms", np.eye(2, 3))
        matrices = np.array(matrices).astype(np.float32)
        return np.pad(matrices.reshape((-1, 6)), [[0, 0], [0, 2]])

    def __call__(self, x, *args, **kwargs):
        matrices = tf.numpy_function(self.load_matrix, [x["path"]], [tf.float32], name="load_matrix")
        image_shape = tf.shape(x[self.image_key][0])
        print(image_shape)
        x[self.image_key] = tf.raw_ops.ImageProjectiveTransformV3(images=x[self.image_key],
                                                       transforms=matrices[0],
                                                       output_shape=image_shape[:2],
                                                       fill_value=0,
                                                       interpolation=self.interpolation)
        if self.label_key in x:
            x[self.label_key] = tf.raw_ops.ImageProjectiveTransformV3(images=x[self.label_key],
                                                                        transforms=matrices[0],
                                                                        output_shape=image_shape[:2],
                                                                        fill_value=0,
                                                                        interpolation=self.interpolation)

        return x


class BcimgSequenceLoader(ImageLoader):
    type: Literal["BcimgSequenceLoader"] = "BcimgSequenceLoader"
    stack_channels: bool = True
    range_meta: ClassVar[Type] = TfRange
    metadata_spec = {
        ImageKeys.BOUNDING_BOX: BBOX.build,
        ImageKeys.SEQUENCE_RANGE: range_meta.build,
        "index_prefix": int
    }

    def load_sequence(self, path, prefix=6, postprocess=True):
        try:
            path = path.item()
        except AttributeError:
            pass
        header = json.loads(self._io.read_file(path))["Image"]

        if header["DType"] == "eGrayScale8":
            channels = 1
        else:
            raise NotImplementedError(f"dtype of bcimg.json '{header['DType']}' not implemented")
        shape = np.array((
            int(header["Frames"]),
            int(header["OriginalSize"]["Height"]),
            int(header["OriginalSize"]["Width"]),
            channels
        ), np.int32)
        pth_ = path[:-10].decode() if type(path) == bytes else path[:-10]

        sequence_fmt = self._io.path.join(pth_, "image_files", f"{{:0{prefix}d}}.{header['Format']}").format # Prefixed?
        sequence_files = np.array([sequence_fmt(i) for i in range(shape[0])])
        return sequence_files, shape

    def load(self, path, metadata=None, postprocess=True):
        index_prefix = 6 if metadata is None else metadata.get("index_prefix", 6)
        files, shape = tf.numpy_function(self.load_sequence, [path, index_prefix], [tf.string, tf.int32], name="load_header")

        default_shape = shape[1:]
        if metadata is not None:
            # Select frames
            if ImageKeys.SEQUENCE_RANGE in metadata:
                files = metadata[ImageKeys.SEQUENCE_RANGE].slice_padded(files, "")
            if ImageKeys.BOUNDING_BOX in metadata:
                default_shape = (*metadata[ImageKeys.BOUNDING_BOX].shape, shape[-1])

        if self.postprocessor and postprocess:
            default_shape = (*self.postprocessor.output_size(default_shape[0], default_shape[1]),
                             self.postprocessor.output_channels(default_shape[2]))

        images, meta = tf.map_fn(
            fn=lambda x: super(BcimgSequenceLoader, self).load(x, metadata, postprocess=postprocess,
                                                               default_shape=default_shape),
            elems=files,
            fn_output_signature=(tf.float32, {'_image_file_shape': tf.int32}),
            parallel_iterations=16
        )
        if self.stack_channels:
            images = tf.transpose(images, [1, 2, 0, 3])
            sh = tf.shape(images)
            images = tf.reshape(images, [sh[0], sh[1], sh[2] * sh[3]])

        _image_file_shape = meta["_image_file_shape"][0]

        return images, {"_image_file_shape": _image_file_shape, "_sequence_files": files}

