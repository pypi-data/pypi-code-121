from typing import cast
from zipfile import ZipFile
from pathlib import Path
import eyed3
import re
import sys
import io

from eyed3.core import AudioFile, Tag


class Beatmap:
    beatmap_path: Path = Path("")
    output_dir: Path = Path("")
    audiofile_path = Path()
    tags_file: str = ""
    audiofile_name: str = ""

    title: str = ""
    artist: str = ""
    album_name: str = ""
    song_genre: list[str] = []

    def __init__(self, beatmap_path: Path, output_dir_path: Path) -> None:
        """ class constructor """
        self.beatmap_path = beatmap_path
        self.output_dir = output_dir_path

    def extract(self):
        """ locate the .mp3 and the .osu files and read them into memory """

        with ZipFile(self.beatmap_path, 'r') as zip:
            if zip.testzip() != None:
                print("Bad zip file")
                sys.exit(0)

            osu_file_name = ""

            for file_name in zip.namelist():
                if file_name.endswith(".osu"):
                    osu_file_name = file_name

            with zip.open(osu_file_name) as osu_file:
                self.tags_file = io.TextIOWrapper(osu_file).read()

            self.read_tags()

            self.audiofile_path = zip.extract(
                self.audiofile_name, self.output_dir)

    def read_tags(self):
        """ search the .osu file for relevant tags """
        audiofile_re = re.compile("AudioFilename: (?P<audiofile>\\w*.mp3)")
        title_re = re.compile(r"Title:(?P<title>.*)\n")
        album_re = re.compile(r"Source:(?P<album>.*)\n")
        artist_re = re.compile(r"Artist:(?P<artist>.*)\n")
        genre_re = re.compile(r"Tags:(?P<tags>.*)\n")

        tags_file = self.tags_file

        self.audiofile_name = re.findall(audiofile_re, tags_file)[0]
        self.title = re.findall(title_re, tags_file)[0]
        self.album_name = re.findall(album_re, tags_file)[0]
        self.artist = re.findall(artist_re, tags_file)[0]
        self.song_genre = re.findall(genre_re, tags_file)[0].split(" ")

    def tag_mp3(self):
        """ use eyed3 to tag the mp3 file """
        audiofile: AudioFile = eyed3.load(self.audiofile_path)

        if audiofile.tag == None:
            audiofile.initTag()

        tag: Tag = cast(Tag, audiofile.tag)

        tag.title = self.title
        tag.artist = self.artist
        tag.album = self.album_name

        tag.save()  # member "save" is not a member of type "tag" but still works, wtf

        Path(self.audiofile_path).rename(Path.joinpath(
            self.output_dir, f"{self.artist} - {self.title}.mp3"))
