import pathlib
import typing
from typing import Optional, Tuple, List, Dict

import matplotlib.patches
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import geopandas
import numpy


import SumoNetVis
from matplotlib.figure import Figure
from shapely.geometry import Point
from adjustText import adjust_text


from sumo_output_parsers.definition_parser.detectors_det_parser import DetectorDefinitionParser, \
    DetectorPositions, LanePosition
from sumo_output_parsers.logger_unit import logger


class DetectorPositionVisualizer(object):
    def __init__(self,
                 path_sumo_net: pathlib.Path,
                 path_sumo_detector: pathlib.Path):
        self.path_sumo_net = path_sumo_net
        self.detector_parsers = DetectorDefinitionParser(path_sumo_detector)
        self.arrowprops_dict_default = {
            'arrowstyle': '->',
            'color': 'yellow'
        }

    @staticmethod
    def clean_up_detector_id(detector_id: str) -> bool:
        if ':' in detector_id:
            return False
        else:
            return True

    @staticmethod
    def _collect_lane_info(sumo_net: SumoNetVis.Net) -> Dict[str, LanePosition]:
        """Collect lane information from net.xml file.

        Args:
            sumo_net:

        Returns: {lane-id: LanePosition}
        """
        lane_def = {}
        for e in sumo_net.edges.values():
            if e.function == 'internal':
                continue
            # end if
            for l_obj in e.lanes:
                lane_id = l_obj.id
                edge_id = e.id
                incoming_connection = [c_obj.from_lane.id for c_obj in l_obj.incoming_connections
                                       if c_obj.from_lane is not None and c_obj.from_edge.function != 'internal']
                outgoing_connection = [c_obj.to_lane.id for c_obj in l_obj.outgoing_connections
                                       if c_obj.to_lane is not None and c_obj.from_edge.function != 'internal']
                lane_def_obj = LanePosition(
                    lane_id=lane_id,
                    lane_number=l_obj.index,
                    edge_id=edge_id,
                    lane_from=incoming_connection,
                    lane_to=outgoing_connection,
                    lane_position_xy=l_obj.shape,
                    speed=l_obj.speed,
                    sumo_net_vis_lane_obj=l_obj
                )
                lane_def[lane_id] = lane_def_obj
            # end for
        # end for
        return lane_def

    @staticmethod
    def __decide_detector_position(net_obj: SumoNetVis.Net,
                                   detector_definition: DetectorPositions,
                                   lane2lane_def: Dict[str, LanePosition]) -> Tuple[Point, str]:
        """Decide a detector position 'left-hand' or 'right-hand' on a lane.
        The algorithm is that
        if all incoming-lanes have smaller x position, the detector position is 'right-hand'
        if all incoming-lanes have bigger x positions, then the detector position is 'left-hand'.
        else 'unknown', then returns center of the lane.
        """
        edge_id = detector_definition.lane_object.edge_id
        incoming_junction_shape = net_obj.edges[edge_id].from_junction
        outgoing_junction_shape = net_obj.edges[edge_id].to_junction

        lane_shape = ''  # left-right contain diagonal shapes. top-bottom are only when an angle is at 90 degrees
        edge_end = ''  # left, right, top, bottom

        diff_x_pos = abs(
            outgoing_junction_shape.shape.centroid.bounds[0] - incoming_junction_shape.shape.centroid.bounds[0])
        diff_y_pos = abs(
            outgoing_junction_shape.shape.centroid.bounds[1] - incoming_junction_shape.shape.centroid.bounds[1])
        # left-right or top-down is based on which has bigger difference value.
        if diff_x_pos > diff_y_pos:
            if outgoing_junction_shape.shape.centroid.bounds[0] > incoming_junction_shape.shape.centroid.bounds[0]:
                # bounds are a tuple of (x-left, y-bottom, x-right, y-top)
                lane_shape = 'left-right'
                edge_end = 'right'
            elif outgoing_junction_shape.shape.centroid.bounds[0] < incoming_junction_shape.shape.centroid.bounds[0]:
                lane_shape = 'left-right'
                edge_end = 'left'
        else:
            if outgoing_junction_shape.shape.centroid.bounds[1] < incoming_junction_shape.shape.centroid.bounds[1]:
                lane_shape = 'top-down'
                edge_end = 'down'
            if outgoing_junction_shape.shape.centroid.bounds[1] > incoming_junction_shape.shape.centroid.bounds[1]:
                lane_shape = 'top-down'
                edge_end = 'top'

        incoming_lanes = detector_definition.lane_object.lane_from
        positions_incoming = [lane2lane_def[l_id].lane_position_xy.bounds for l_id in incoming_lanes
                              if detector_definition.lane_object.sumo_net_vis_lane_obj.parentEdge.id != lane2lane_def[l_id].sumo_net_vis_lane_obj.parentEdge.id]

        positions_outgoing = [lane2lane_def[l_id].lane_position_xy.bounds
                              for l_id in detector_definition.lane_object.lane_to
                              if detector_definition.lane_object.sumo_net_vis_lane_obj.parentEdge.id != \
                              lane2lane_def[l_id].sumo_net_vis_lane_obj.parentEdge.id]

        xy_current_lane_bound = detector_definition.lane_object.lane_position_xy.bounds
        xy_right_most_current = (xy_current_lane_bound[2], xy_current_lane_bound[3])

        detector_top = numpy.mean([
            [xy_current_lane_bound[0], xy_current_lane_bound[3]],
            [xy_current_lane_bound[2], xy_current_lane_bound[3]]], axis=0)
        detector_down = numpy.mean([
            [xy_current_lane_bound[0], xy_current_lane_bound[1]],
            [xy_current_lane_bound[2], xy_current_lane_bound[1]]], axis=0)
        detector_left = numpy.mean([
            [xy_current_lane_bound[0], xy_current_lane_bound[1]],
            [xy_current_lane_bound[0], xy_current_lane_bound[3]]], axis=0)
        detector_right = numpy.mean([
            [xy_current_lane_bound[2], xy_current_lane_bound[1]],
            [xy_current_lane_bound[2], xy_current_lane_bound[3]]], axis=0)

        if lane_shape == 'left-right':
            if edge_end == 'right':
                return Point(*detector_right), 'right'
            else:
                return Point(*detector_left), 'left'
        else:
            if edge_end == 'top':
                return Point(*detector_top), 'top'
            else:
                return Point(*detector_down), 'down'

    def _collect_detector_info(self) -> Tuple[List[DetectorPositions], SumoNetVis.Net]:
        # get definition of detectors
        detector_definitions = self.detector_parsers.xml2definitions()
        # self.net.plot(ax=ax)
        net = SumoNetVis.Net(self.path_sumo_net.__str__())
        # mapping of lane-id into lane position
        lane2lane_def = self._collect_lane_info(net)
        # update detector object with lane positions
        for detector_def in detector_definitions:
            assert detector_def.lane_id in lane2lane_def, \
                f"key {detector_def.lane_id} does not exist in net.xml definition."
            detector_def.lane_object = lane2lane_def[detector_def.lane_id]
            # decide detector position based on incoming lane information
            det_position, det_position_type = self.__decide_detector_position(net, detector_def, lane2lane_def)

            detector_def.detector_position_xy = det_position
            detector_def.detector_position_type = det_position_type
        # end for
        return detector_definitions, net

    def get_detector_df(self,
                        detector_definitions: Optional[List[DetectorPositions]] = None,
                        position_visualization: str = 'left') -> geopandas.GeoDataFrame:
        """Generate a `GeoDataFrame` of detectors.
        """
        assert position_visualization in ('left', 'right', 'center')
        if detector_definitions is None:
            detector_definitions, sumo_net = self._collect_detector_info()
        # end if
        d = {
            'detector-id': [d.detector_id for d in detector_definitions],
            'geometry': [detector_def.detector_position_xy for detector_def in detector_definitions],
            'lane-id': [d.lane_id for d in detector_definitions],
            'detector-position-type': [d.detector_position_type for d in detector_definitions]
        }
        df = geopandas.GeoDataFrame(d)
        return df

    @staticmethod
    def _get_lanes_positions(sumo_net: SumoNetVis.Net) -> geopandas.GeoDataFrame:
        """Generate a `GeoDataFrame` of lanes.

        Returns: GeoPandas object
        """
        # records of [lane-id, detector-poly]
        d = {
            'lane-id': [l.id for e in sumo_net.edges.values() for l in e.lanes if l.shape.is_empty is False],
            'geometry': [l.shape for e in sumo_net.edges.values() for l in e.lanes if l.shape.is_empty is False]
        }

        gdf = geopandas.GeoDataFrame(d)
        return gdf

    def visualize_interactive(self,
                              path_save_html: pathlib.Path,
                              width: int = 600,
                              height: int = 500):
        """Visualization with interactive functions thank to hvplot.

        Args:
            path_save_html: path to save the generated html.
            width: size of plot.
            height: size of plot.

        Returns:
            `holoviews.core.overlay.Overlay`
        """
        from bokeh.resources import INLINE
        import hvplot.pandas  # noqa
        import holoviews

        assert path_save_html.parent.exists()
        detector_definitions, sumo_net = self._collect_detector_info()
        sumo_net_df = self._get_lanes_positions(sumo_net)
        detector_df = self.get_detector_df(detector_definitions)

        plot = sumo_net_df.hvplot(width=width, height=height, hover_cols='lane-id', legend=False) * \
               detector_df.hvplot(color='orange', hover_cols=['detector-id', 'lane-id', 'detector-position-type'])
        hvplot.save(plot, path_save_html, resources=INLINE)
        logger.info(f'saved at {path_save_html}')
        return plot

    def visualize(self,
                  target_detector_ids: Optional[Dict[str, typing.Optional[str]]] = None,
                  position_visualization: str = 'left',
                  is_detector_name: bool = True,
                  path_save_png: Optional[pathlib.Path] = None,
                  ax: Optional[Axes] = None,
                  fig_obj: Optional[Figure] = None,
                  text_color: str = 'red',
                  arrowprops_dict: typing.Dict[str, str] = None
                  ) -> Axes:
        """Visualization of detector positions.
        Currently, the detector position is not exact but approximation.
        The visualization shows only lane where a detector stands.

        Args:
            target_detector_ids: a list of detector-id and color of dot. Ex, [{'detector-id': 'red'}]. The color is a color-code of Matplotlib. Leave the color None if you do not specify a color.
            path_save_png: path to save png file.
            position_visualization: 'left', 'right', 'center'. The option on a lane to render a detector.
            is_detector_name: render detector name if True else nothing.
            ax: matplotlib Axes object
            fig_obj: matplotlib Figure object
            text_color: text colors of detector-ids if is_detector_name is True
            arrowprops_dict: arguments to arrowprops if is_detector_name is True
        Returns:
            ax: matplotlib layer object
        """
        assert position_visualization in ('left', 'right', 'center')
        detector_definitions, sumo_net = self._collect_detector_info()
        # visualizations
        if ax is None:
            fig_obj, ax = plt.subplots()
        # end if
        # self.net.plot(ax=ax)
        sumo_net.plot(ax=ax)

        if target_detector_ids is not None:
            d_ids = target_detector_ids.keys()
            detector_definitions = [d_obj for d_obj in detector_definitions if d_obj.detector_id in d_ids]
        # end if
        # update detector object with lane positions
        array_text = []
        for detector_def in detector_definitions:
            point_position: Point = detector_def.detector_position_xy

            if target_detector_ids:
                color_code = target_detector_ids[detector_def.detector_id]
            else:
                color_code = numpy.random.rand(3, )
            # end if
            ax.scatter(point_position.x, point_position.y, c=color_code)
            if is_detector_name:
                plt_text_obj = plt.text(point_position.x,
                                        point_position.y,
                                        s=detector_def.detector_id,
                                        ha='center',
                                        va='center',
                                        color=text_color)
                array_text.append(plt_text_obj)
            # end if
        # end for
        if is_detector_name:
            if arrowprops_dict is not None:
                __arrow_dict = arrowprops_dict
            else:
                __arrow_dict = self.arrowprops_dict_default
            # end if
            adjust_text(array_text, arrowprops=__arrow_dict)

        if path_save_png is not None:
            fig_obj.savefig(path_save_png.__str__(), bbox_inches='tight')
            logger.info(f'saved at {path_save_png}')
        # end if

        return ax
