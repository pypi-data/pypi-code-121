from pathlib import Path
from ..progressbar.progressbar import progressbar
from ..beatmap.beatmap import Beatmap
import sys
import os


class App():
    def __init__(self, input_dir_path, output_dir_path):
        """ App constructor """
        self.input_dir = Path(input_dir_path)
        self.output_dir = Path(output_dir_path)
        self.beatmaps: list[Beatmap] = []
        self.bar_width: int = 60
        self.disp_length: int = 150

    def run(self, silent: bool) -> None:
        """ Run application """
        if not self.input_dir.is_dir() or not self.output_dir.is_dir():
            print(
                "Either {input_dir.name} or {output_dir.name} is not a directory")
            sys.exit(1)

        if silent:
            beatmaps = [Beatmap(f.absolute(), Path.joinpath(self.input_dir, Path("")))
                        for f in self.input_dir.iterdir() if f.suffix == ".osz"]

            for osz in beatmaps:
                osz.extract()
                osz.tag_mp3()

        else:
            self.adjust_pb_size()
            self.read_beatmaps()
            self.process_beatmaps()

    def process_beatmaps(self) -> None:
        """ extract audio file to output dir and tag """
        total_steps = len(self.beatmaps) * 2
        step_counter = 0

        for osz in self.beatmaps:
            step_counter += 1
            progressbar(step=step_counter,
                        total=total_steps,
                        print_perc=True,
                        title=f"Extracting audio file from {osz.beatmap_path.name} to {osz.output_dir}'",
                        bar_width=self.bar_width,
                        disp_len=self.disp_length
                        )
            osz.extract()

            step_counter += 1
            progressbar(step=step_counter,
                        total=total_steps,
                        print_perc=True,
                        title=f"Tagging {osz.title}",
                        bar_width=self.bar_width,
                        disp_len=self.disp_length
                        )

            osz.tag_mp3()

    def read_beatmaps(self) -> None:
        """ locate beatmaps in input dir and display progress bar """
        input_dir_contents = list(self.input_dir.iterdir())
        total_steps = len(input_dir_contents)
        step_counter = 0

        for file in input_dir_contents:
            step_counter += 1

            progressbar(step=step_counter,
                        total=total_steps,
                        print_perc=True,
                        title=f"Reading {file.name}",
                        bar_width=self.bar_width,
                        disp_len=self.disp_length
                        )

            if(file.suffix == ".osz"):
                self.beatmaps.append(
                    Beatmap(file.absolute(), self.output_dir))

    def adjust_pb_size(self) -> tuple[int, int]:
        """ automatically adjust progress bar size: 150 columns or 80 columns """
        if os.get_terminal_size().columns >= 150:
            self.bar_width = 80
            self.disp_length = 150
        elif os.get_terminal_size().columns >= 80:
            self.bar_width = 40
            self.disp_length = 80
        else:
            print("Terminal window too small")
            sys.exit(1)

        return (self.bar_width, self.disp_length)
