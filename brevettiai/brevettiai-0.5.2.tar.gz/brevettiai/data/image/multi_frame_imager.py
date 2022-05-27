import tensorflow as tf
from pydantic import BaseModel, PrivateAttr, Field
from typing import List


class MultiFrameImager(BaseModel):
    """
    Module to concatenate multiple image frames to a sequence
    call generate_paths and set_image_pipeline before use
    """
    frames: List[int] = Field(default=(0,),
        description="List of frames relative to the target frame to load as channels, in the order of the list")

    _image_pipeline = PrivateAttr(default=None)
    _image_pipelines: dict = PrivateAttr(default_factory=dict)
    _frame_columns = PrivateAttr(default=None)
    _target_size_image_ix = PrivateAttr(default=None)
    # path is xxx/[id].xxx
    _frame_id_extractor = PrivateAttr(default=r"^(?P<prefix>.+\D)(?P<frame>\d+)(?P<postfix>\.\S+)$")
    _frame_prefix_length = PrivateAttr(default=6)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Index of image to match target size (first time 0 occurs in frames)
        self._target_size_image_ix = next((i for i, f in enumerate(self.frames) if f is 0), None)

    @property
    def apply_unbatched(self):
        if hasattr(self._image_pipeline, "apply_unbatched"):
            return self._image_pipeline.apply_unbatched
        else:
            return False

    def frame_index_format(self, is_prefixed):
        """Return format of frame index"""
        return f"0{self._frame_prefix_length}d" if is_prefixed else "00d"

    def generate_paths(self, df):
        info = df["path"].str.extract(self._frame_id_extractor)
        info["dataset_id"] = df.get("dataset_id", "unknown")

        is_prefixed = info.groupby("dataset_id")\
            .apply(lambda x: (x["frame"].str.len() == self._frame_prefix_length).all())
        info["fmt"] = is_prefixed.apply(self.frame_index_format).reindex(info["dataset_id"]).values

        info["frame"] = info["frame"].astype(int)

        self._frame_columns = []
        for frame_offset in self.frames:
            if frame_offset != 0:
                key = f"path_t{frame_offset}"
                df[key] = info.apply(
                    lambda x: f'{x["prefix"]}{format(x["frame"] + frame_offset, x["fmt"])}{x["postfix"]}',
                    axis="columns")
                self._frame_columns.append(key)
            else:
                self._frame_columns.append("path")

        return df

    def set_image_pipeline(self, image_pipeline):
        self._image_pipeline = image_pipeline
        self._image_pipelines = {"path": image_pipeline}
        for key in set(self._frame_columns).difference({image_pipeline.path_key}):
            if isinstance(image_pipeline, BaseModel):
                ip = type(image_pipeline)(**image_pipeline.dict())
            else:
                ip = image_pipeline.copy()
            if hasattr(ip, "segmentation"):
                ip.segmentation = None
            ip.path_key = key
            self._image_pipelines[key] = ip

    def loading_extra_frames(self):
        return tuple(self.frames) != (0,)

    def __call__(self, x, *args, **kwargs):
        imgs = []
        for path_key in self._frame_columns:
            ip = self._image_pipelines[path_key]
            imgs.append(ip(x)[ip.output_key])

        if self._target_size_image_ix is not None and self.loading_extra_frames():
            # extract target size for both batched and unbatched states
            sh = tf.shape(imgs[self._target_size_image_ix])[-3:-1]
            for ix in range(len(imgs)):
                # Resize to match
                imgs[ix] = tf.image.resize(imgs[ix], sh)

        return {**x, self._image_pipeline.output_key: tf.concat(imgs, -1)}

    @property
    def output_shape(self):
        if self._image_pipeline is None:
            raise AttributeError(f'Image pipeline not added yet, call set_image_pipeline')
        else:
            sh = self._image_pipeline.output_shape
            return (*sh[:2], sh[2]*len(self.frames))

    def __getattr__(self, item):
        if self._image_pipeline is None:
            raise AttributeError(f'Image pipeline not added yet, attribute {item} not found')
        else:
            return getattr(self._image_pipeline, item)
