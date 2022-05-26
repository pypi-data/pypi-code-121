from abc import ABC
from dataclasses import dataclass, field

import wget
from facebook_video_downloader.house_keeping import house_keeper
from facebook_video_downloader.model.video import Video
from moviepy.video.io.ffmpeg_tools import ffmpeg_merge_video_audio


@dataclass
class VideoDownloader(ABC):
    video: Video
    video_quality: str = field(default='720')

    def download(self) -> str:
        self.is_resolution_available()
        video_file_name = wget.download(self.video.video_links[self.video_quality])
        audio_file_name = wget.download(self.video.audio_link)
        video_output = f'{self.video.id}.mp4'
        ffmpeg_merge_video_audio(
            video_file_name, audio_file_name, output=video_output, vcodec='mpeg4')
        file = open(video_output, 'rb').read()
        house_keeper.delete_temp_files()
        return file

    def is_resolution_available(self) -> None:
        if self.video_quality not in self.video.video_links:
            raise f'Resolution {self.video_quality} is not supported for this video'
