import os
from urllib.error import HTTPError
import cv2
from typing import List, Tuple
from logging import getLogger
import wget  # type: ignore
import dataclasses
from dataclasses import field
from deeplabel.label.videos import Video
from deeplabel.label.gallery import Gallery
from deeplabel.label.videos.frames import Frame
from deeplabel.label.gallery.images import Image
from tqdm.contrib.concurrent import process_map #type: ignore
from deeplabel.exceptions import DownloadFailed

logger = getLogger(__name__)



@dataclasses.dataclass
class VideoAndFrameDownloader:
    """Download frame and extract the required frame"""

    video: Video
    video_path: str
    cap: cv2.VideoCapture = field(init=False)  # cv2.cap object

    def __post_init__(self):
        video: Video = self.video
        os.makedirs(os.path.dirname(self.video_path), exist_ok=True)
        if os.path.exists(self.video_path):
            logger.debug(f"Video {video.video_id} already exists... Skipping Download")
        else:
            try:
                wget.download(video.video_url, self.video_path)  # type: ignore
            except HTTPError as e:
                logger.debug(
                    f"Video Download Failed for videoId {video.video_id}, url {video.video_url}"
                )
                DownloadFailed(f"Download failed for {video.video_id}.. {e}")
        if not os.path.exists(self.video_path):
            raise DownloadFailed(
                f"Video Download failed for videoId: {video.video_id} from "
                f"url: {video.video_url}"
            )
        self.cap = cv2.VideoCapture(self.video_path)

    def download(self, frame: Frame, frame_path: str):
        os.makedirs(os.path.dirname(frame_path), exist_ok=True)
        if frame.video_id != self.video.video_id:
            raise ValueError(
                f"passed frame {frame.frame_id} is not for video {self.video.video_id}"
            )
        if os.path.exists(frame_path):
            logger.debug(f"frame {frame.frame_id} already exists. Skipping")
        else:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame.number)  # type: ignore
            success, img = self.cap.read()  # type: ignore
            if not success:
                raise ValueError(
                    f"Reading frame {frame.frame_id} (number: {frame.number})"
                    f" of video {self.video.video_id} failed."
                )
            cv2.imwrite(frame_path, img)  # type: ignore
        return frame_path


@dataclasses.dataclass
class GalleryImageDownloader:
    """Given a gallery and it's image, download the image in given location"""

    gallery: Gallery

    def download(self, image: Image, image_path: str) -> str:
        """Download the given image and return it's path"""
        if os.path.exists(image_path):
            logger.debug(f"Image {image.image_id} already exists. Skipping download")
        else:
            try:
                wget.download(image.image_url, image_path) #type: ignore
            except HTTPError as e:
                logger.debug(
                    f"Failed downloading image {image.image_id} url {image.image_url}. {e}"
                )
                raise DownloadFailed(
                    f"Failed to download image {image.image_id} at {image_path}"
                )
            if not os.path.exists(image_path):
                raise DownloadFailed(
                    f"Failed to download image {image.image_id} at {image_path}"
                )
        return image_path

    def download_parallel(self, images_and_paths: List[Tuple[Image, str]])->List[str]:
        return process_map(self.download, images_and_paths) #type: ignore
