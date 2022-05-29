"""
Captures the video from the camera to a file.
"""

import argparse
import sys
import os

import cv2
from spvideoutils import camera
from spvideoutils import utils

def create_parser():
    """Create command line parser for arguments."""
    parser = argparse.ArgumentParser(
        description="Capture video from camera to mp4 file."
    )
    parser.add_argument(
        "--index", "-i", default=0, type=int, help="Camera index on this mc."
    )
    parser.add_argument(
        "--time", "-t", default=4, type=int, help="Seconds to capture the video"
    )
    parser.add_argument("outfile", type=str, help="Output mp4 file to store the video.")
    return parser


def next_gui_state(gui_state, key_pressed):
    next_state = gui_state
    if key_pressed == ord('q'):
        next_state = "QUIT"
    elif key_pressed == ord('s'):
        next_state = "VIDEO"
    return next_state

def main():
    """Main program."""
    opt = create_parser().parse_args()

    print(f">>Opening camera at index={opt.index} to store to '{opt.outfile}' file for time={opt.time}")
    cam = camera.Camera(opt.index)
    gui_state = "LIVE"

    while True:
        frame = cam.read_frame()
        utils.fprint(frame, f"{gui_state}: Press s to save to {opt.outfile} for {opt.time} secs")
        cv2.imshow("default", frame)
        key_pressed = cv2.waitKey(1) & 0xff
        gui_state = next_gui_state(gui_state, key_pressed)

        if gui_state != "LIVE":
            break

    cv2.destroyAllWindows()
    if gui_state == "VIDEO":
        print(f">>Starting to capture video to {opt.outfile} for {opt.time} secs.")
        cam.take_video(opt.outfile, time_secs=opt.time)
        out_size = round(os.path.getsize(opt.outfile) / (10**6), 1)
        print("\n")
        print(f">>Created {opt.outfile} with size of {out_size} MBytes")
    del cam


if __name__ == "__main__":
    main()
