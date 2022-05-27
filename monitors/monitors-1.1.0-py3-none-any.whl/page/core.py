#!/usr/bin/python
# encoding=utf-8

"""Can only be modified by the administrator. Only Core pipeline are provided..
"""
import os
import shutil

from loguru import logger
from monitors.dynamic import predict
from monitors.page.reporter import gen_report
from monitors.page.toolbox import copyfile, find_all_cases


def engine(original_path, video_path, format_video_path, monitors_report_path, model_path, summary_report_path,
           width=888,
           height=1920, device_name='Xiaomi9 Android 10'):
    """

    :param summary_report_path:
    :param model_path:
    :param monitors_report_path:
    :param format_video_path:
    :param video_path:
    :param height: video resolution
    :param width: video resolution
    :param original_path: first-hand video path
    :param device_name: device name
    :return:
    """
    if len(list(find_all_cases(base=original_path, types='files', mark='.mp4'))) == 0:
        logger.warning(f'{original_path} No video files to analyze !')
        return

    if os.path.isdir(video_path):
        shutil.rmtree(video_path)
        shutil.rmtree(format_video_path)
        os.makedirs(video_path)
        os.makedirs(format_video_path)

    target_size = (width, height)

    [copyfile(srcfile, video_path + '/') for srcfile in
     [i for i in find_all_cases(base=original_path, types='files', mark='.mp4')]]

    for video in find_all_cases(base=video_path, mark='mp4', types='files'):
        logger.info(video)
        cmd = f'ffmpeg -i {video} -r 60 {format_video_path + "/" + video.split(".")[0].split("/")[-1]}.mp4'
        os.system(cmd)
    detail = []
    report_results = [{'devices': device_name, 'result': detail}]

    for case in find_all_cases(base=format_video_path, mark='mp4', types='files'):
        case_name = case.split(".")[0].split("/")[-1]
        result_dict = predict(video_path=case, model_file=model_path + f'/{case_name}.h5', target_size=target_size,
                              report_path=monitors_report_path + f'/{case_name}.html')
        start = result_dict['0'][-1]
        logger.info(start)

        if isinstance(start, list):
            start = str(start[-1]).replace('>', '').split('timestamp=')[1]
        else:
            start = str(start).replace('>', '').split('timestamp=')[1]
        logger.info(start)

        end = result_dict['2'][0]
        logger.info(end)

        if isinstance(end, list):
            end = str(end[0]).replace('>', '').split('timestamp=')[1]
        else:
            end = str(end).replace('>', '').split('timestamp=')[1]
        logger.info(end)

        cost = float(end) - float(start)
        logger.info(round(cost * 1000))
        detail.append({'name': case_name, 'cost': round(cost * 1000)})

    gen_report(results=report_results, report_path=summary_report_path)
    logger.info('end of prediction！')
