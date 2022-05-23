from visiongraph.model.geometry.BoundingBox2D import BoundingBox2D
from visiongraph.result.spatial.ObjectDetectionResult import ObjectDetectionResult

FACE_DETECTION_ID = 0
FACE_DETECTION_LABEL = "face"


class FaceDetectionResult(ObjectDetectionResult):
    def __init__(self, score: float, bounding_box: BoundingBox2D):
        super().__init__(FACE_DETECTION_ID, FACE_DETECTION_LABEL, score, bounding_box)
