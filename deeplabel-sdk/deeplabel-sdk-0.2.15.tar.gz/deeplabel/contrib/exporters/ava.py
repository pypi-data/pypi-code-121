import cv2
import dataclasses
import os
from logging import getLogger
from pydantic import BaseModel
import deeplabel.label.folders
import deeplabel.label.gallery
from deeplabel.label.videos.detections import DetectionType as VideoDetectionType
from deeplabel.label.gallery.detections import ImageDetectionType
from deeplabel.label.gallery.images import Image
import deeplabel.types.bounding_box as bounding_box
import deeplabel.label.label_maps
from deeplabel.contrib.utils import image_to_name, pascal_voc_color_map
from tqdm.contrib.concurrent import process_map
import deeplabel.label.videos
import deeplabel.client
import PIL.Image
from typing import List, Dict, Any, Tuple
import numpy as np
from deeplabel.contrib.downloaders.frame_downloader import (
    GalleryImageDownloader,
    VideoAndFrameDownloader,
)
import pascal_voc_writer


logger = getLogger(__name__)

@dataclasses.dataclass
class VideoExporter:
    """Exporter to export 1 video in coco format"""

    root_dir: str
    client: deeplabel.client.BaseClient
    label_to_int:Dict[str,int]
    categories_memo: Dict[str, Dict[str, Any]] = dataclasses.field(
        default_factory=dict
    )  # Mapping between label_id -> label

    def __post_init__(self):
        os.makedirs(self.root_dir, exist_ok=True)

    def run(
        self,
        video: "deeplabel.label.videos.Video",
    ):
        video_path = os.path.join(self.root_dir, "videos", video.video_id + ".mp4")
        frame_downloader = VideoAndFrameDownloader(video, video_path)
        for frame in video.frames:
            if not frame.detections:
                continue  # skip empty frames
            frame_path = os.path.join(self.root_dir, "JPEGImages", frame.frame_id + ".jpg")
            frame_downloader.download(frame, frame_path)
            height = int(frame_downloader.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            width = int(frame_downloader.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            print(height, width)
            segmented = np.any(
                [1 for d in frame.detections if d.type == VideoDetectionType.polygon]
            )
            if segmented:
                mask = np.zeros((height, width), dtype='uint8')
            pascal_voc_frame_annotation=pascal_voc_writer.Writer(frame_path, width, height, database=video.video_id, segmented=int(segmented))
            for detection in frame.detections:
                if detection.type == VideoDetectionType.bounding_box and isinstance(
                    detection.bounding_box, bounding_box.BoundingBox
                ):
                    bbox = detection.bounding_box
                    pascal_voc_frame_annotation.addObject(
                        detection.label_id.name,
                        int(detection.bounding_box.xmin*width),
                        int(detection.bounding_box.ymin*height),
                        int(detection.bounding_box.xmax*width),
                        int(detection.bounding_box.ymax*height),
                    )
                elif detection.type == VideoDetectionType.polygon:
                    poly = detection.polygon.to_shapely( scale_x=width, scale_y=height)
                    pts = [np.asarray(poly.exterior.coords).astype(int)]
                    mask = cv2.fillPoly(mask, pts, [self.label_to_int[detection.label_id.label_id]])
                    mask = cv2.polylines(mask, pts, isClosed=True, color=[255], thickness=5)
                else:
                    raise Exception(f"Unsupported Detection Type: {detection.type}")
            os.makedirs(os.path.join(self.root_dir,'Annotations'), exist_ok=True)
            os.makedirs(os.path.join(self.root_dir,'SegmentationClass'), exist_ok=True)
            # save annotation
            pascal_voc_frame_annotation.save(os.path.join(self.root_dir, 'Annotations', frame.frame_id+'.xml'))
            # save segmentation mask if any
            if segmented:
                segmentation = PIL.Image.fromarray(mask)
                segmentation.putpalette(pascal_voc_color_map())
                segmentation.save(os.path.join(self.root_dir,'SegmentationClass',frame.frame_id+'.png'))
            


@dataclasses.dataclass
class PascalVocExporter:
    root_dir: str
    client: "deeplabel.client.BaseClient"

    def export(self, folder: deeplabel.label.folders.RootFolder):
        # map label_id -> 1,2,3,...
        label_to_int = self.project_label_ints(folder.project_id, self.client)
        if folder.type == deeplabel.label.folders.FolderType.VIDEO:
            exporter = VideoExporter(root_dir=self.root_dir, client=self.client, label_to_int=label_to_int)
            process_map(exporter.run, folder.videos)
        elif folder.type == deeplabel.label.folders.FolderType.GALLERY:
            raise ValueError(f"Ava Exporter is only meant to export Sequence data from Videos. Received Gallery Folder")

    @staticmethod
    def project_label_ints(project_id, client: "deeplabel.client.BaseClient"):
        """
        Map label_id -> 1,2,3,...
        """
        LabelMap = deeplabel.label.label_maps.LabelMap
        labelmaps: List[LabelMap] = LabelMap.from_search_params(
            {"projectId": project_id, "limit": "-1"}, client
        )
        labelmaps = sorted(labelmaps, key=lambda labelmap:labelmap.label_id)
        return {labelmap.label_id:i for i,labelmap in enumerate(labelmaps)}
