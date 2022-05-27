import cv2
import numpy as np
import os
from fro_AI.utils.data_utils import get_file, get_hash_prefix_from_file_name

base_url = 'http://gz.chuangfeigu.com:8087/fro_AI/models/face_detect/'

configs = {
    'tensorflow': ('opencv_face_detector-21c6147f.pbtxt',
                   'opencv_face_detector_uint8-5c71d752.pb'),
    'caffe': ('deploy-68351da8.prototxt',
              'res10_300x300_ssd_iter_140000_fp16-510ffd24.caffemodel')
}


def load_model(model='caffe', path=None):
    if path is not None:
        model_description = os.path.join(path, configs[model][0])
        model_parameters = os.path.join(path, configs[model][1])
        if not os.path.isfile(model_description):
            raise RuntimeError(f'{model_description} 文件不存在')
        if not os.path.isfile(model_parameters):
            raise RuntimeError(f'{model_parameters} 文件不存在')
    else:
        fname = configs[model][0]
        url = base_url + fname
        hash_prefix = get_hash_prefix_from_file_name(fname)
        model_description = get_file(fname,
                                     url,
                                     hash_prefix=hash_prefix,
                                     cache_subdir='models/face_detect')
        fname = configs[model][1]
        url = base_url + fname
        hash_prefix = get_hash_prefix_from_file_name(fname)
        model_parameters = get_file(fname,
                                    url,
                                    hash_prefix=hash_prefix,
                                    cache_subdir='models/face_detect')

    if model == 'caffe':
        return cv2.dnn.readNetFromCaffe(model_description, model_parameters)
    elif model == 'tensorflow':
        return cv2.dnn.readNetFromTensorflow(model_parameters,
                                             model_description)


class FaceDetector(object):
    def __init__(self, model='caffe', path=None):
        self.net = load_model(model, path)
        try:
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        except:
            pass

    def detect(self, img, overlay=True, threshold=0.5, show_confidence=True):
        """
        检测人脸

        Parameters
        ----------
        img
            BGR格式的图像

        Returns
        -------
        blob
            Network produces output blob with a shape 1x1xNx7 where N is a number of
            detections and an every detection is a vector of values
            [batchId, classId, confidence, left, top, right, bottom]
            see https://github.com/opencv/opencv/blob/f584c6d7239e1d56de0c3bd0232d5ccfaf830084/samples/dnn/object_detection.cpp#L335
        """
        blob = cv2.dnn.blobFromImage(img, 1.0, (300, 300),
                                     (104.0, 177.0, 123.0))
        self.net.setInput(blob)
        detections = self.net.forward()
        if not overlay:
            return detections
        (h, w) = img.shape[:2]
        for i in range(detections.shape[2]):
            # extract the confidence (i.e., probability) associated with the
            # prediction
            confidence = detections[0, 0, i, 2]

            # filter out weak detections by ensuring the `confidence` is
            # greater than the minimum confidence
            if confidence > threshold:
                # compute the (x, y)-coordinates of the bounding box for the
                # object
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                # draw the bounding box of the face along with the associated
                # probability
                y = startY - 10 if startY - 10 > 10 else startY + 10
                cv2.rectangle(img, (startX, startY), (endX, endY), (0, 0, 255),
                              2)
                if show_confidence:
                    text = "{:.2f}%".format(confidence * 100)
                    cv2.putText(img, text, (startX, y),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)
        return detections

    def draw_boxes(self,
                   img,
                   detections,
                   threshold=0.5,
                   show_confidence=False):
        """
        绘制矩形框

        检测结果会直接绘制在原图上

        Parameters
        ----------
        img
            BGR格式的图像
        
        detections
            :py:meth:`detect` 方法返回的结果。

        threshold: float
            检测阈值, detections 中 confidence 大于该值的矩形框才会绘制。
        """
        (h, w) = img.shape[:2]
        for i in range(detections.shape[2]):
            # extract the confidence (i.e., probability) associated with the
            # prediction
            confidence = detections[0, 0, i, 2]

            # filter out weak detections by ensuring the `confidence` is
            # greater than the minimum confidence
            if confidence > threshold:
                # compute the (x, y)-coordinates of the bounding box for the
                # object
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                # draw the bounding box of the face along with the associated
                # probability
                y = startY - 10 if startY - 10 > 10 else startY + 10
                cv2.rectangle(img, (startX, startY), (endX, endY), (0, 0, 255),
                              2)
                if show_confidence:
                    text = "{:.2f}%".format(confidence * 100)
                    cv2.putText(img, text, (startX, y),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)
