#!/usr/bin/python
# encoding=utf-8
from loguru import logger

from monitors.page.cutter import VideoCutter
from monitors.page.classifier.keras import KerasClassifier
from monitors.page.reporter import Reporter
from monitors.page.video import VideoObject


def cut(video_path, data_home):
    """

    :param video_path: test.mp4
    :param data_home: ./dataset
    :return:
    """

    video = VideoObject(video_path)
    video.load_frames()

    cutter = VideoCutter()
    res = cutter.cut(video, block=6)
    stable, unstable = res.get_range(threshold=0.97, offset=3)

    # save dataset
    res.pick_and_save(stable, 10, to_dir=data_home, meaningful_name=True)
    print(f"data saved to {data_home}")


def train(data_home, loop: int, target_size: tuple, model_file='keras_model.h5'):
    """

    :param model_file:
    :param target_size: (888,1920)
    :param loop: 训练循环次数
    :param data_home: data_home = "./dataset"
    :return:
    """

    cl = KerasClassifier(
        epochs=loop,
        target_size=target_size,
    )
    cl.train(data_home)
    cl.save_model(model_path=model_file, overwrite=True)


def predict(video_path, model_file, target_size: tuple, report_path='report.html'):
    """

    :param report_path:
    :param target_size: (888,1920)
    :param video_path: test.mp4
    :param model_file: ./keras_model.h5
    :return:
    """
    logger.info('------------ Start analyzing video！------------- ')

    video = VideoObject(video_path)
    video.load_frames()

    # --- cutter ---
    cutter = VideoCutter()
    res = cutter.cut(video)
    stable, unstable = res.get_range()

    # --- classifier ---
    cl = KerasClassifier(
        target_size=target_size
    )

    cl.load_model(model_file)

    classify_result = cl.classify(video, stable, keep_data=True)
    result_dict = classify_result.to_dict()

    # --- draw ---
    r = Reporter()
    r.draw(classify_result, report_path=report_path)
    return result_dict
