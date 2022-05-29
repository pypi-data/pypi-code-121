"""
Merges the frames in png format to a video file.
"""

import argparse
import sys
import os
import shutil
import cv2
from pathlib import Path

import spvideoutils.video


def create_parser():
    """Command line parser."""
    parser = argparse.ArgumentParser(
        description="Merge the frames in png file in dir to a mp4 video file."
    )
    parser.add_argument(
        "--fps", "-f", default=120, type=int, help="Output video file frame rate."
    )
    parser.add_argument(
        "--out", "-o", default="merge.mp4", type=str, help="Output video file name."
    )
    parser.add_argument(
        "frame_dir", type=str, help="Dir holding all the frames in sequential order."
    )

    return parser


def main():
    """Main program."""
    opt = create_parser().parse_args()
    fnames = [
        os.path.join(opt.frame_dir, f)
        for f in os.listdir(opt.frame_dir)
        if os.path.isfile(os.path.join(opt.frame_dir, f))
    ]
    fnames.sort()
    print(f"Creating '{opt.out}' from  {len(fnames)} files in '{opt.frame_dir}'")

    if len(fnames) == 0:
        raise ValueError("No input frame files")

    init_frame = cv2.imread(fnames[0])
    height, width, channels = init_frame.shape

    video = cv2.VideoWriter(
        opt.out, cv2.VideoWriter_fourcc(*"mp4v"), opt.fps, (width, height)
    )

    for fname in fnames:
        frame = cv2.imread(fname)
        video.write(frame)

    video.release()


if __name__ == "__main__":
    main()
