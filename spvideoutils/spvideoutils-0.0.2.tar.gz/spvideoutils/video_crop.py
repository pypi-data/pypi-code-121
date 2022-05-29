"""
Crop the video between start and end frame.
"""

import argparse
import sys
import os
import shutil
import cv2
from pathlib import Path

import spvideoutils.video
from spvideoutils import utils


def create_parser():
    """Command line parser."""
    parser = argparse.ArgumentParser(description="Crop the video between 2 frames.")
    parser.add_argument(
        "--start", "-s", default=0, type=int, help="Starting frame idx in video."
    )
    parser.add_argument(
        "--end", "-e", default=-1, type=int, help="Ending frame idx in video. -1:EOF"
    )
    parser.add_argument(
        "--out", "-o", default="crop.mp4", type=str, help="Output cropped video file name."
    )
    parser.add_argument("videofile", type=str, help="Input video mp4 file.")

    return parser


def do_interactive_frame_sel(videofile):
    """"Select start and end frame idx from video."""

    video = spvideoutils.video.Splitter(videofile)

    start_idx = 0
    end_idx = -1
    num_frames = video.num_frames() - 1

    for idx, frame in enumerate(video):
        utils.fprint(frame, f"Frame Idx {idx} of {num_frames}: s=>start, e=>end")

        cv2.imshow("default", frame)
        key_pressed = cv2.waitKey(0) & 0xFF
        if key_pressed == ord("q"):
            break
        elif key_pressed == ord("s"):
            start_idx = idx
            print(f">>Selected start frame_idx {idx}")
        elif key_pressed == ord("e"):
            end_idx = idx
            print(f">>Selected end frame_idx {idx}")

    cv2.destroyAllWindows()
    del video
    return (start_idx, end_idx)


def main():
    """Main program."""
    opt = create_parser().parse_args()

    if opt.end == -1:
        (start_idx, end_idx) = do_interactive_frame_sel(opt.videofile)
    else:
        (start_idx, end_idx) = (arg.start, arg.end)

    if end_idx != -1:
        print(
            f">>Crop the video from frame idx {start_idx} to {end_idx} to '{opt.out}' file"
        )
        in_video = spvideoutils.video.Splitter(opt.videofile)

        out_video = cv2.VideoWriter(
            opt.out,
            cv2.VideoWriter_fourcc(*"mp4v"),
            in_video.fps(),
            (in_video.width(), in_video.height()),
        )

        for idx, frame in enumerate(in_video):
            if idx >= start_idx and idx <= end_idx:
                out_video.write(frame)

        del in_video
        del out_video


if __name__ == "__main__":
    main()
