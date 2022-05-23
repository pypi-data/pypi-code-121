"""
Module to contain all helper functions
"""
import os
import subprocess


def run_video_download(url, out_path, start_time=0, end_time=None):
    if os.path.exists(out_path):
        return
    vid_download_cmd = None
    if end_time is None:
        vid_download_cmd = 'ffmpeg -i $(youtube-dl -f best -g "{}") -c copy {}'.format(
            url, out_path
        )
    else:
        vid_download_cmd = (
            'ffmpeg -ss {} -i $(youtube-dl -f best -g "{}") -t {} -c copy {}'.format(
                start_time, url, (end_time - start_time), out_path
            )
        )

    video_sub_p = subprocess.Popen(
        vid_download_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf8",
        shell=True,
    )
    stdout, stderr = video_sub_p.communicate()
    # print('------------', vid_download_cmd, stdout, stderr)
    return stdout, stderr
