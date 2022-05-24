#!/usr/bin/env python3

import cv2
import json
import logging
import numpy as np
import os
import re
from typing import List, Union, Tuple


# def interpolate_latlon(lat_start_stop: tuple, long_start_stop: tuple, n_steps: int):
#     lat_inter = np.interp(x=np.linspace(0, n_steps), list(lat_start_stop), [1, 2])
#     return lat_inter


def interpolate(start, stop, steps):
    step_size = (stop - start) / steps
    out_vals = [start + i * step_size for i in range(steps)]
    return out_vals


def interpolate_latlon(latlon_start: tuple, latlon_stop: tuple, steps: int) -> Tuple[list, list]:
    latitudes = interpolate(latlon_start[0], latlon_stop[0], steps)
    longitudes = interpolate(latlon_start[1], latlon_stop[1], steps)
    return latitudes, longitudes


def create_srt(fpath_video: str, fpath_subs: str = None) -> None:
    """
    Creates an .srt file in the same place where the video file is located.
    :param fpath_video:
    :return: None.
    """
    if fpath_subs is None:
        fpath_subs = remove_extension(fpath_video) + ".srt"
    command = ["ffmpeg", "-i", fpath_video, fpath_subs]
    os.system(' '.join(command))


def get_latlong_from_srt(frame_string) -> Tuple[float, float, Tuple[str, str]]:
    """

    :param frame_string:
    :return: latitude, longitude, hemispheres
    """
    pattern = re.compile(r"GPS \((-?[\d]+\.[\d]+), (-?[\d]+\.[\d]+), [\d]+\),")  # GPS (14.2823, 36.0614, 15),
    matches = pattern.search(frame_string)
    longitude, latitude = float(matches.group(1)), float(matches.group(2))
    north_south = "N" if latitude >= 0 else "S"
    east_west = "E" if longitude >= 0 else "W"
    assert -90 <= latitude <= 90 and -180 <= longitude <= 180, f"Lat/Long {latitude} {longitude} contains invalid values."
    return latitude, longitude, (north_south, east_west)


def get_srt_second(frame_string) -> int:
    """
    Starts at 1 (not zero-indexing!)
    :param frame_string:
    :return:
    """
    pattern = re.compile(r"^[\n]?([\d]+)\n")
    match = pattern.search(frame_string).group()
    logging.debug(f"Match: {match}")
    return int(match)


def get_filename_only(fpath):
    fname = os.path.split(fpath)[-1].split('.')[0]
    return fname


def remove_extension(fpath: str):
    fpath_out = '.'.join(fpath.split('.')[:-1])
    return fpath_out


def create_frames_output_dir(fpath_video, frame_interval) -> str:
    video_name = get_filename_only(fpath_video)
    output_dir = os.path.join(os.path.split(fpath_video)[0], f"{video_name}_{frame_interval}_frame_interval")
    try:
        os.makedirs(output_dir)
    except FileExistsError:
        print("[ WARNING ] Output directory already exists.\nPress [Enter] to continue regardless, at the risk of overwriting files.")
        input()
    finally:
        return output_dir


def get_current_second(frame_number: int, fps: Union[float, int]) -> int:
    return frame_number // fps


def get_framerate(fpath_video: str) -> Union[float, int]:
    vid = cv2.VideoCapture(fpath_video)
    fps = vid.get(cv2.CAP_PROP_FPS)
    return np.round(fps, 1)


def get_total_frame_count(fpath_video) -> int:
    vid = cv2.VideoCapture(fpath_video)
    framecount = vid.get(cv2.CAP_PROP_FRAME_COUNT)
    return int(framecount)


def load_raw_srt(fpath_srt) -> List[str]:
    with open(fpath_srt, 'r') as f:
        sub_raw = f.read()
    subs = sub_raw.split("\n\n")  # Split them into one subtitle string per second.
    subs = [sub.strip() for sub in subs if sub.strip()]  # remove empty entries and leading/training \n
    return subs


def read_srt(fpath_srt) -> dict:
    """

    :param fpath_srt:
    :return:
    """
    subs = load_raw_srt(fpath_srt)
    subs_dict = {}
    for i, content in enumerate(subs):
        logging.debug(content)
        second = get_srt_second(content)
        lat, long, hemispheres = get_latlong_from_srt(content)
        logging.debug(f"i:{i}, second: {second}")
        assert i + 1 == second
        subs_dict[i] = {"latitude": lat,
                        "longitude": long,
                        "hemispheres_lat_long": hemispheres
                        }
    return subs_dict


def extract_video_frames(fpath_video: str, frame_interval: int, output_dir=None, subtitle_file="",
                         show_progress=True, retrieve_GPS_coordinates=False):

    if not subtitle_file:
        subtitle_file = remove_extension(fpath_video) + ".srt"

    if not os.path.exists(subtitle_file):
        print(f"[ Warning ] Did not find subtitle file {subtitle_file}. Continuing regardless.")

    # Initial setup and checks
    if not os.path.exists(fpath_video):
        raise FileNotFoundError(f"Video file not found: {fpath_video}")
    video_name = os.path.split(fpath_video)[-1].split('.')[0].replace(' ', '_')
    logging.info(f"Video name: {video_name}")
    total_frames = get_total_frame_count(fpath_video)
    if output_dir is None:
        output_dir = create_frames_output_dir(fpath_video, frame_interval)

    # Open video
    video = cv2.VideoCapture(fpath_video)
    if not video.isOpened():
        raise IOError("Cannot open video")

    # Extract frames
    current_frame = 0
    processed_frames = 0
    while video.isOpened():
        frame_retrieved, frame = video.read()
        if frame_retrieved:
            # Check if frame should be exported
            if current_frame % frame_interval == 0:
                if show_progress:
                    msg_params = {"perc": current_frame / total_frames * 100, "frame": current_frame}
                    print("{perc:05.2f} % completed. Processing frame {frame}".format(**msg_params))
                # Save frame
                # ToDo: find the second of the image and merge GPS coordinates into the image
                logging.debug(f"Output dir: {output_dir}")
                logging.debug(f"Output dir: {video_name}")
                logging.debug(f"Output dir: {current_frame}")

                fpath_frame_out = os.path.join(output_dir, f"{video_name}_frame_{current_frame}.tif")
                cv2.imwrite(fpath_frame_out, frame)
                processed_frames += 1
            current_frame += 1
        else:  # If no frame received, i.e. end of video.
            print(f"Reached end of video. Exported {processed_frames} frames.")
            break
    video.release()
    print("Done")


if __name__ == "__main__":

    loglevel = logging.DEBUG
    logformat = "[%(levelname)s]\t%(funcName)15s: %(message)s"
    logging.basicConfig(level=loglevel, format=logformat)
    logging.disable()

    # fpath_video = "/media/findux/DATA/Documents/Malta_II/surveys/2022-05-03_Ramla/DJI_0154-002.MOV"
    # fpath_subs = "/media/findux/DATA/Documents/Malta_II/surveys/2022-05-03_Ramla/DJI_0154-002.srt"
    # frame_interval = 50
    # subs = read_srt(fpath_subs)
    # [print(v["latitude"], v["longitude"]) for k, v in subs.items()]
    # latlong_start = get_latlong_from_srt(load_raw_srt(fpath_subs)[80])
    # latlong_stop = get_latlong_from_srt(load_raw_srt(fpath_subs)[81])
    # print(latlong_start, latlong_stop)

    # fpath_messina = "/media/findux/DATA/Documents/Malta_II/surveys/Messina/DJI/DJI_0003.mp4"
    #create_srt(fpath_messina)

    # test_string = "abcde asda GPS (-1400.2823, 36.0614, 15), asölkjdal"
    # coords = get_latlong_from_srt(test_string)
    # print(coords)

    fpath_vid = "/media/findux/DATA/Documents/Malta_II/surveys/2022-05-03_Ramla/DJI_0153-003.MOV"
    fpath_vid = "/media/findux/DATA/Documents/Malta_II/surveys/2022-05-03_Ramla/DJI_0154-002.MOV"
    fpath_vid = "/media/findux/DATA/Documents/Malta_II/surveys/Messina/DJI_0003.mp4"
    extract_video_frames(fpath_vid, 12, show_progress=True)