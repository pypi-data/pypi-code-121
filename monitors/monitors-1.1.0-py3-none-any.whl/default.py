#!/usr/bin/python
# encoding=utf-8

from monitors.page.cutter import VideoCutter
from monitors.page.classifier import SVMClassifier
from monitors.page.reporter import Reporter
from monitors.page.video import VideoObject
from loguru import logger


def predict(video_path, report_path):
    """

    :param video_path:
    :param report_path:'index.html'
    :return:
    """
    logger.info('------------ Start analyzing video！------------- ')
    video = VideoObject(video_path)
    video.load_frames()

    # --- cutter ---
    cutter = VideoCutter()
    res = cutter.cut(video)
    stable, unstable = res.get_range()
    data_home = res.pick_and_save(stable, 5)

    # --- classify ---
    cl = SVMClassifier()
    cl.load(data_home)
    cl.train()
    classify_result = cl.classify(video, stable)

    # --- draw ---
    r = Reporter()
    r.draw(classify_result, report_path=report_path)
    return classify_result.to_dict()
