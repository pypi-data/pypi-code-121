#!/usr/bin/python
# encoding=utf-8
from loguru import logger

from monitors.page.classifier import SVMClassifier
from monitors.page.cutter import VideoCutter
from monitors.page.reporter import Reporter


def cut(video_path, data_home):
    """

    :param video_path: demo.mp4
    :param data_home: ./cut_result
    :return:
    """

    # --- cut ---
    cutter = VideoCutter()
    res = cutter.cut(video_path, block=6)
    stable, unstable = res.get_range(threshold=0.97, offset=3)

    res.pick_and_save(
        stable,
        20,
        to_dir=data_home,
        meaningful_name=True
    )


def train(data_home, model_file='model.pkl'):
    """

    :param model_file:
    :param data_home:
    :return:
    """

    cl = SVMClassifier()

    cl.load(data_home)
    cl.train()
    cl.save_model(model_path=model_file, overwrite=True)


def predict(video_path, model_file, report_path='report.html'):
    """
    :param report_path:
    :param video_path: demo.mp4
    :param model_file: model.pkl
    :return:
    """
    logger.info('------------ Start analyzing video！------------- ')

    cutter = VideoCutter()
    res = cutter.cut(video_path)
    stable, _ = res.get_range()

    cl = SVMClassifier()
    cl.load_model(model_file)

    classify_result = cl.classify(
        video_path,
        stable,
    )

    r = Reporter()
    r.draw(
        classify_result,
        report_path=report_path,
        cut_result=res,
    )
    return classify_result.to_dict()
