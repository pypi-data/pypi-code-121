from azureml.automl.dnn.vision.object_detection_yolo.models.yolo_wrapper import YoloV5Wrapper
from azureml.automl.dnn.vision.object_detection.common.constants import ModelNames


class TestYoloWrapper:
    def test_yolo_wrapper_create(self):
        settings = {'device': 'cpu', 'model_size': 'small'}

        model_wrapper = YoloV5Wrapper(
            model_name=ModelNames.YOLO_V5, number_of_classes=4, specs=settings)
        assert model_wrapper is not None
