"""
Splits the video into frames stored as png files.
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
        description="Split the video file into frames as png files in outdir."
    )
    parser.add_argument(
        "--prefix", "-p", default="frame_", type=str, help="Prefix for out frame filename."
    )
    parser.add_argument(
        "--outdir", "-o", default="", type=str, help="User outdir name else it is videofile name."
    )
    parser.add_argument("videofile", type=str, help="Input video mp4 file.")

    return parser


def main():
    """Main program."""
    opt = create_parser().parse_args()

    video = spvideoutils.video.Splitter(opt.videofile)
    if opt.outdir == "":
        opt.outdir = Path(opt.videofile).stem

    if os.path.exists(opt.outdir):
        print(f">>Dir {opt.outdir} exists. Deleting it.")
        shutil.rmtree(opt.outdir)

    num_frames = video.num_frames()
    if num_frames == 0:
        raise IndexError(f"No frames found in the video file '{opt.videofile}'")

    print(f">>Found {num_frames} frames in the video file '{opt.videofile}'")
    num_digits = len(str(num_frames))
    print(f">>Making subdir '{opt.outdir}' for storing frames")
    os.mkdir(opt.outdir)

    for idx, frame in enumerate(video):
        fname = opt.prefix + str(idx).zfill(num_digits) + ".png"
        cv2.imwrite(os.path.join(opt.outdir, fname), frame)

    print(f">>Finished writing {num_frames} frames to subdir '{opt.outdir}'")

if __name__ == "__main__":
    main()
