#  Copyright (c) 2020 Caliber Data Labs.
#  All rights reserved.
#
import os

import mock
from ....models.annotation_transformers.scale import \
    ScaleAnnotation, convert_to_scale_format
from shared.tools.misc import json_file_to_dic

my_path = path = os.path.dirname(os.path.abspath(__file__))


def test_get_scaleapi():
    annotation = ScaleAnnotation(json_file_to_dic(
        os.path.join(my_path, 'resources/889fa13h29.ann')))
    assert 'polygon' == annotation.annotation_type
    assert '2019_05_14_17_38_55left_raw_raw_00362.png' == annotation.asset_id
    assert 'Drivable Space' == annotation.annotation_entities[0].label
    assert 15 == len(annotation.annotation_entities[1].coordinates)
    assert 3 == len(annotation.annotation_entities)


def test_get_scaleapi_2():
    annotation = ScaleAnnotation(json_file_to_dic(
        os.path.join(my_path, 'resources/5ecc2f9736e6f30047b66f58.ann')))
    assert 'polygon' == annotation.annotation_type
    assert 'kitti_2011_09_28_drive_2_kitti_camera_color_right_image_raw_1317213980051.png' == annotation.asset_id
    assert 'Bicyclist' == annotation.annotation_entities[0].label
    assert 3 == len(annotation.annotation_entities[0].coordinates)
    assert ["Bicyclist"] == annotation.to_dic().get("labels")


def test_get_scaleapi_3():
    annotation = ScaleAnnotation(json_file_to_dic(
        os.path.join(my_path, 'resources/5eface514847b300269ab604.ann')))
    assert 'polygon' == annotation.annotation_type
    assert 'axis_front_image_raw_compressed_data_1581036613006.jpeg' == annotation.asset_id
    assert 'Sedan' == annotation.annotation_entities[0].label
    assert 3 == len(annotation.annotation_entities[0].coordinates)
    assert 1 == len(annotation.annotation_entities)
    assert "Sedan" in annotation.to_dic().get("labels")


def test_convert_to_scaleapi_bbox():
    annotation_metadata = [
        {
            "id": "ooc_1.000.0000000003-cor.ann",
            "session_name": "ooc_1",
            "timestamp": "2020-07-31T19:13:31.004260+00:00",
            "asset_id": "ooc_1.000.0000000003-cor.png",
            "media_type": "images",
            "provider": "rendered",
            "annotation_type": "two_d_bounding_box",
            "annotation_entities": [],
            "sets": ["2ef58f20-cd29-437d-aac5-b71f2d267431"],
            "binary_id": None,
            "labels": [],
        },
        {
            "id": "ooc_1.000.0000000010-cor.ann",
            "session_name": "ooc_1",
            "timestamp": "2020-07-31T19:14:06.435951+00:00",
            "asset_id": "ooc_1.000.0000000010-cor.png",
            "media_type": "images",
            "provider": "rendered",
            "annotation_type": "two_d_bounding_box",
            "annotation_entities": [
                {
                    "uid": "ec868ba6f16a8a2b4a5622af2b76c733",
                    "label": "car",
                    "annotation_type": "two_d_bounding_box",
                    "attributes": None,
                    "url": None,
                    "resource": None,
                    "coordinates": [
                        {"x": 167.5, "y": 121.5},
                        {"x": 194.5, "y": 121.5},
                        {"x": 194.5, "y": 157.5},
                        {"x": 167.5, "y": 157.5},
                    ],
                    "related_annotations": [],
                    "binary_id": None,
                    "category_id": 1,
                }
            ],
            "sets": ["2ef58f20-cd29-437d-aac5-b71f2d267431"],
            "binary_id": None,
            "labels": ["car"],
        },
    ]

    for annotation_metadatum in annotation_metadata:
        scale_annotations, scale_labels = convert_to_scale_format(annotation_metadatum)
        for i, scale_annotation in enumerate(scale_annotations):
            assert scale_annotation["uuid"] == annotation_metadatum["annotation_entities"][i]["uid"]
            assert scale_annotation["annotation_id"] == annotation_metadatum["id"]

            coordinates = annotation_metadatum["annotation_entities"][i]["coordinates"]
            top, left = coordinates[0]["y"], coordinates[0]["x"]
            bottom, right = coordinates[2]["y"], coordinates[2]["x"]
            width = right - left
            height = bottom - top

            assert scale_annotation["left"] == left
            assert scale_annotation["top"] == top
            assert scale_annotation["width"] == width
            assert scale_annotation["height"] == height


def test_convert_to_scaleapi_polygon():
    annotation_metadata = [
        {
            "id": "ooc_1.000.0000000003-cor.ann",
            "session_name": "ooc_1",
            "timestamp": "2020-07-31T19:13:31.004260+00:00",
            "asset_id": "ooc_1.000.0000000003-cor.png",
            "media_type": "images",
            "provider": "rendered",
            "annotation_type": "polygon",
            "annotation_entities": [],
            "sets": ["2ef58f20-cd29-437d-aac5-b71f2d267431"],
            "binary_id": None,
            "labels": [],
        },
        {
            "id": "ooc_1.000.0000000010-cor.ann",
            "session_name": "ooc_1",
            "timestamp": "2020-07-31T19:14:06.435951+00:00",
            "asset_id": "ooc_1.000.0000000010-cor.png",
            "media_type": "images",
            "provider": "rendered",
            "annotation_type": "polygon",
            "annotation_entities": [
                {
                    "uid": "ec868ba6f16a8a2b4a5622af2b76c733",
                    "label": "car",
                    "annotation_type": "polygon",
                    "attributes": None,
                    "url": None,
                    "resource": None,
                    "coordinates": [
                        {"x": 167.5, "y": 121.5},
                        {"x": 194.5, "y": 121.5},
                        {"x": 194.5, "y": 157.5},
                        {"x": 167.5, "y": 157.5},
                    ],
                    "related_annotations": [],
                    "binary_id": None,
                    "category_id": 1,
                }
            ],
            "sets": ["2ef58f20-cd29-437d-aac5-b71f2d267431"],
            "binary_id": None,
            "labels": ["car"],
        },
    ]

    for annotation_metadatum in annotation_metadata:
        scale_annotations, scale_labels = convert_to_scale_format(annotation_metadatum)
        for i, scale_annotation in enumerate(scale_annotations):
            assert scale_annotation["uuid"] == annotation_metadatum["annotation_entities"][i]["uid"]
            assert scale_annotation["annotation_id"] == annotation_metadatum["id"]

            coordinates = annotation_metadatum["annotation_entities"][i]["coordinates"]
            assert scale_annotation["vertices"] == coordinates


def test_convert_to_scaleapi_line():
    annotation_metadata = [
        {
            "id": "ooc_1.000.0000000003-cor.ann",
            "session_name": "ooc_1",
            "timestamp": "2020-07-31T19:13:31.004260+00:00",
            "asset_id": "ooc_1.000.0000000003-cor.png",
            "media_type": "images",
            "provider": "rendered",
            "annotation_type": "line",
            "annotation_entities": [],
            "sets": ["2ef58f20-cd29-437d-aac5-b71f2d267431"],
            "binary_id": None,
            "labels": [],
        },
        {
            "id": "ooc_1.000.0000000010-cor.ann",
            "session_name": "ooc_1",
            "timestamp": "2020-07-31T19:14:06.435951+00:00",
            "asset_id": "ooc_1.000.0000000010-cor.png",
            "media_type": "images",
            "provider": "rendered",
            "annotation_type": "line",
            "annotation_entities": [
                {
                    "uid": "ec868ba6f16a8a2b4a5622af2b76c733",
                    "label": "car",
                    "annotation_type": "line",
                    "attributes": None,
                    "url": None,
                    "resource": None,
                    "coordinates": [
                        {"x": 167.5, "y": 121.5},
                        {"x": 194.5, "y": 121.5},
                        {"x": 194.5, "y": 157.5},
                        {"x": 167.5, "y": 157.5},
                    ],
                    "related_annotations": [],
                    "binary_id": None,
                    "category_id": 1,
                }
            ],
            "sets": ["2ef58f20-cd29-437d-aac5-b71f2d267431"],
            "binary_id": None,
            "labels": ["car"],
        },
    ]

    for annotation_metadatum in annotation_metadata:
        scale_annotations, scale_labels = convert_to_scale_format(annotation_metadatum)
        for i, scale_annotation in enumerate(scale_annotations):
            assert scale_annotation["uuid"] == annotation_metadatum["annotation_entities"][i]["uid"]
            assert scale_annotation["annotation_id"] == annotation_metadatum["id"]

            coordinates = annotation_metadatum["annotation_entities"][i]["coordinates"]
            assert scale_annotation["vertices"] == coordinates


def test_convert_to_scaleapi_point():
    annotation_metadata = [
        {
            "id": "ooc_1.000.0000000003-cor.ann",
            "session_name": "ooc_1",
            "timestamp": "2020-07-31T19:13:31.004260+00:00",
            "asset_id": "ooc_1.000.0000000003-cor.png",
            "media_type": "images",
            "provider": "rendered",
            "annotation_type": "point",
            "annotation_entities": [],
            "sets": ["2ef58f20-cd29-437d-aac5-b71f2d267431"],
            "binary_id": None,
            "labels": [],
        },
        {
            "id": "ooc_1.000.0000000010-cor.ann",
            "session_name": "ooc_1",
            "timestamp": "2020-07-31T19:14:06.435951+00:00",
            "asset_id": "ooc_1.000.0000000010-cor.png",
            "media_type": "images",
            "provider": "rendered",
            "annotation_type": "point",
            "annotation_entities": [
                {
                    "uid": "ec868ba6f16a8a2b4a5622af2b76c733",
                    "label": "car",
                    "annotation_type": "point",
                    "attributes": None,
                    "url": None,
                    "resource": None,
                    "coordinates": [
                        {"x": 167.5, "y": 121.5},
                    ],
                    "related_annotations": [],
                    "binary_id": None,
                    "category_id": 1,
                },
                {
                    "uid": "ec868ba6f16a8a2b4a5622af9876c733",
                    "label": "truck",
                    "annotation_type": "point",
                    "attributes": None,
                    "url": None,
                    "resource": None,
                    "coordinates": [
                        {"x": 194.5, "y": 121.5},
                    ],
                    "related_annotations": [],
                    "binary_id": None,
                    "category_id": 1,
                }
            ],
            "sets": ["2ef58f20-cd29-437d-aac5-b71f2d267431"],
            "binary_id": None,
            "labels": ["car"],
        },
    ]

    for annotation_metadatum in annotation_metadata:
        scale_annotations, scale_labels = convert_to_scale_format(annotation_metadatum)
        for i, scale_annotation in enumerate(scale_annotations):
            assert scale_annotation["uuid"] == annotation_metadatum["annotation_entities"][i]["uid"]
            assert scale_annotation["annotation_id"] == annotation_metadatum["id"]

            coordinates = annotation_metadatum["annotation_entities"][i]["coordinates"][0]
            assert scale_annotation["x"] == coordinates["x"]
            assert scale_annotation["y"] == coordinates["y"]