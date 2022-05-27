"""
Image tools for handling image pipelines, augmentation and for loading annotations
"""
from .image_processor import ImageProcessor


class ImageKeys:
    BOUNDING_BOX = "bbox"
    ZOOM = "zoom_factor"
    SIZE = "size"
    SEQUENCE_RANGE = "sequence_range"
    INSIDE_POINTS = "inside_points"
    BBOX_SIZE_ADJUST = "bbox_size_adjust"
    ANNOTATION = "segmentation_path"


try:
    from .image_loader import ImageLoader, BcimgSequenceLoader, CropResizeProcessor
    from .annotation_loader import AnnotationLoader
    from .image_pipeline import ImagePipeline
    from .segmentation_loader import SegmentationLoader
    from .image_augmenter import ImageAugmenter
except Exception:
    pass

