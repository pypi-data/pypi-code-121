import dataclasses
from typing import Tuple, List, Optional
from pathlib import Path
from collections import namedtuple

from SumoNetVis.Net import _Lane
from shapely.geometry import Polygon, Point

from sumo_output_parsers.logger_unit import logger
from sumo_output_parsers.models.parser import ParserClass


@dataclasses.dataclass
class LanePosition(object):
    lane_id: str
    lane_number: int
    edge_id: str
    lane_from: Optional[List[str]]
    lane_to: Optional[List[str]]
    lane_position_xy: Optional[Polygon] = None
    speed: Optional[float] = None
    sumo_net_vis_lane_obj: Optional[_Lane] = None


@dataclasses.dataclass
class DetectorPositions(object):
    """
    """
    detector_id: str
    lane_id: str
    detector_position_from_end: float
    detector_position_xy: Optional[Point] = None
    lane_object: Optional[LanePosition] = None
    detector_position_type: Optional[str] = None


class DetectorDefinitionParser(ParserClass):
    def __init__(self,
                 path_detectors_det: Path):
        super().__init__(path_detectors_det)
        self.key_attribute_name = 'e1Detector'

    def xml2matrix(self, target_element: str):
        raise NotImplementedError()

    def xml2definitions(self) -> List[DetectorPositions]:
        detectors = []
        for elem in self.getelements(str(self.path_file), self.key_attribute_name):
            position_def = DetectorPositions(
                detector_id=elem.attrib['id'],
                lane_id=elem.attrib['lane'],
                detector_position_from_end=elem.attrib['pos'])
            detectors.append(position_def)
        # end for
        return detectors
