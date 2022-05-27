import unittest
from itertools import chain

from brevettiai.model.metadata import ModelMetadata
from brevettiai.model.metadata.image_segmentation import ImageSegmentationModelMetadata


class ParsingException(Exception):
    pass


class TestModelMetadata(unittest.TestCase):
    metadata = [
        """
        {
          "id": "5f0bc78e-8470-403e-a257-f7310bb41297",
          "run_id": "0000-00-00 00:00:00",
          "name": "minimal_metadata",
          "producer": "Manual",
          "host_name": null
        }
        """,
        """
        {
          "id": "5f0bc78e-8470-403e-a257-f7310bb41298",
          "run_id": "0000-00-00 00:00:00",
          "name": "simple_metadata_with_host",
          "producer": "Manual",
          "host_name": "http://platform.brevetti.ai"
        }
        """,
    ]
    image_segmentation_metadata = [
        """
{
  "id": "c5daf50b-4d77-4435-9f15-e4148fbac032",
  "run_id": "2022-01-28T132225",
  "name": "Particle segmentation Emil data 39",
  "producer": "ImageSegmentation",
  "host_name": "https://platform.brevetti.ai",
  "classes": [
    "Container",
    "Miniscus",
    "Particle",
    "Bubble",
    "Good"
  ],
  "suggested_input_shape": [
    480,
    360
  ],
  "zoom_factor": 1.0,
  "image_pipeline": {
    "target_size": [150, 50],
    "rois": [[[50,0],[100,150]]],
    "roi_mode": "concatenate_height",
    "path_key": "path",
    "output_key": "img",
    "color_mode": "greyscale",
    "segmentation": {
      "classes": [
        "Container",
        "Miniscus",
        "Particle",
        "Bubble",
        "Good"
      ],
      "mapping": {
        "Container": "Container",
        "Miniscus": "Container|Miniscus",
        "Particle": "Container|Particle",
        "Bubble": "Bubble|Container",
        "Good": "Good",
        "container": "Container",
        "miniscus": "Container|Miniscus",
        "particle": "Container|Particle",
        "bubble": "Bubble|Container",
        "good": "Good"
      },
      "sparse": false,
      "input_key": "segmentation_path",
      "output_key": "segmentation"
    },
    "keep_aspect_ratio": false,
    "rescale": "None",
    "resize_method": "bilinear",
    "antialias": false,
    "padding_mode": "CONSTANT",
    "center_padding": false
  },
  "multi_frame_imager": {
    "frames": [
      -1,
      0,
      1
    ]
  },
  "annotation_pooling": {
    "extra": {},
    "pooling_method": "max",
    "input_key": "segmentation",
    "output_key": "downscaled_annotation",
    "pool_size": [
      8,
      8
    ]
  }
}
        """
    ]

    def test_ensure_all_examples_are_valid_with_modelmetadata(self):
        for data in chain(self.metadata, self.image_segmentation_metadata):
            try:
                ModelMetadata.parse_raw(data)
            except Exception as e:
                raise ParsingException(f"Error parsing: \n{data}") from e

    def test_ensure_examples_are_valid_with_imagesegmentationmodelmetadata(self):
        for data in self.image_segmentation_metadata:
            try:
                ImageSegmentationModelMetadata.parse_raw(data)
            except Exception as e:
                raise ParsingException(f"Error parsing: \n{data}") from e


if __name__ == '__main__':
    unittest.main()
