from abc import ABC
from dataclasses import dataclass, field
from email.mime import audio
from pathlib import Path

import wget
from moviepy.video.io.ffmpeg_tools import ffmpeg_merge_video_audio

from src.model.video import Video
from src.house_keeping import house_keeper


@dataclass
class VideoDownloader(ABC):
    video: Video
    __tmp_output_path: str = str(Path(__file__).parents[1])
    __video_output_path: Path = Path(__file__).parents[2] / 'downloaded_videos'
    video_quality: str = field(init=False, default='720')

    def download(self):
        self.is_resolution_available()
        video_file_name = wget.download(self.video.video_links[self.video_quality], self.__tmp_output_path)
        audio_file_name = wget.download(self.video.audio_link, self.__tmp_output_path)
        video_output = f'{self.__video_output_path}/{self.video.id}.mp4'
        ffmpeg_merge_video_audio(video_file_name, audio_file_name, output=video_output, vcodec='mpeg4')
        return Path(video_output)

        # house_keeper.delete_temp_files()

    def is_resolution_available(self) -> None:
        if self.video_quality not in self.video.video_links:
            raise f'Resolution {self.video_quality} is not supported for this video'


class Video180Downloader(VideoDownloader):
    video_quality: str = '180'


class Video240Downloader(VideoDownloader):
    video_quality: str = '240'


class Video270Downloader(VideoDownloader):
    video_quality: str = '270'


class Video360Downloader(VideoDownloader):
    video_quality: str = '360'


class Video480Downloader(VideoDownloader):
    video_quality: str = '480'


class Video640Downloader(VideoDownloader):
    video_quality: str = '640'


class Video720Downloader(VideoDownloader):
    video_quality: str = '720'


class Video860Downloader(VideoDownloader):
    video_quality: str = '860'


class Video1080Downloader(VideoDownloader):
    video_quality: str = '1080'
