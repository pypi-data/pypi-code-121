import asyncio

from naff.api.voice.audio import AudioVolume
from typing_extensions import Self
from yt_dlp import YoutubeDL

__all__ = ("YTAudio",)

youtube_dl = YoutubeDL(
    {
        "format": "bestaudio/best",
        "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
        "restrictfilenames": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "logtostderr": False,
        "quiet": True,
        "no_warnings": True,
        "default_search": "auto",
        "source_address": "0.0.0.0",  # noqa: S104
    }
)


class YTAudio(AudioVolume):
    def __init__(self, src: str) -> None:
        super().__init__(src)
        self.entry: dict | None = None
        """The audio entry this audio object represents."""

    @classmethod
    async def from_url(
        cls, url: str, stream: bool = True, ytdl: YoutubeDL | None = None
    ) -> Self:
        """
        Create this object from a YTDL supported url

        Args:
            url: The url to play from
            stream: Should this audio be streamed, or downloaded
            ytdl: An optional YoutubeDL like object to use to fetch

        Returns:
            A YTAudio object
        """
        if not ytdl:
            ytdl = youtube_dl

        data = await asyncio.to_thread(
            lambda: ytdl.extract_info(url, download=not stream)
        )

        if "entries" in data:
            data = data["entries"][0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)

        new_cls = cls(filename)

        if stream:
            new_cls.ffmpeg_before_args = (
                "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
            )

        new_cls.entry = data
        return new_cls
