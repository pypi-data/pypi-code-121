import SumoNetVis
import matplotlib.pyplot as plt
import matplotlib
import collections
import typing
from tqdm import tqdm
from pathlib import Path
from lxml import etree
from matplotlib.figure import Figure
from collections import namedtuple
from itertools import groupby
from matplotlib.axes import Axes

from logzero import logger

"""A script to visualize trajectories of vehicles.
The script requires vehroute.xml, net.xml

A script to count #vehicles that traveled an edge.
The scripts input is VehRoute
https://sumo.dlr.de/docs/Simulation/Output/VehRoutes.html
"""


VehicleTypeAndRoute = namedtuple('VehicleTypeAndRoute', ('vehicle_id', 'vehicle_group', 'seq_route'))
VehicleRouteAggregated = namedtuple('VehicleRouteAggregated', ('vehicle_group_name', 'edge_name', 'frequency'))


class RouteVisualizer(object):
    @staticmethod
    def getelements(filename_or_file: Path, tag: str):
        context = iter(etree.iterparse(filename_or_file, events=('start', 'end')))
        _, root = next(context)  # get root element
        for event, elem in context:
            if event == 'end' and elem.tag == tag:
                yield elem
                root.clear()  # preserve memory

    @staticmethod
    def extract_vehicle_group_name(vehicle_id_name: str, split_with: str = '.') -> str:
        """Extract a group name of a vehicle.
        Args:
            vehicle_id_name:
            split_with:
        Returns: a group name of a vehicle
        """
        _ = vehicle_id_name.split(split_with)
        return _[0]

    def extract_route_info(self, path_file: Path, tag: str = 'routes') -> typing.List[VehicleTypeAndRoute]:
        seq_vehicle_type_objects = []
        for elem in self.getelements(str(path_file), tag=tag):
            for vehicle_tree in tqdm(elem.findall('vehicle')):
                vehicle_id = vehicle_tree.attrib['id']
                for route_element in vehicle_tree.findall('route'):
                    route_element: str = route_element.attrib['edges']
                    seq_route_elem = route_element.split()
                    assert len(seq_route_elem) > 0
                    vehicle_group_name = self.extract_vehicle_group_name(vehicle_id)
                    seq_vehicle_type_objects.append(VehicleTypeAndRoute(vehicle_id, vehicle_group_name, seq_route_elem))
                # endfor
            # endfor
        # endfor
        return seq_vehicle_type_objects

    @staticmethod
    def aggregation(seq_vehicle_type_objects: typing.List[VehicleTypeAndRoute]) -> typing.List[VehicleRouteAggregated]:
        """Run sum-aggregation, keys with vehicle-group-name and edge-name.
        Args:
            seq_vehicle_type_objects: [VehicleTypeAndRoute]
        Returns: list of VehicleRouteAggregated. Suitable output for pandas.
        """
        information_aggregated = []
        for group_name, g_obj in groupby(sorted(seq_vehicle_type_objects, key=lambda t: t.vehicle_group),
                                         key=lambda t: t.vehicle_group):
            acc_routes = []
            for v_route_obj in g_obj:
                assert isinstance(v_route_obj, VehicleTypeAndRoute)
                acc_routes += v_route_obj.seq_route
            # end for
            for edge_name, edge_freq in collections.Counter(acc_routes).items():
                information_aggregated.append(VehicleRouteAggregated(group_name, edge_name, edge_freq))
            # end for
        # end for
        return information_aggregated

    @staticmethod
    def set_adjustment_linewidth(target_frequency: int,
                                 max_frequency: int,
                                 max_width: int = 10) -> float:
        """Get ideal line width, considering ratio to the max frequency value.

        Args:
            target_frequency:
            max_frequency:
            max_width:

        Returns: computed line width
        """
        return (target_frequency / max_frequency) * max_width

    def visualize(self,
                  path_vehroute_xml: Path,
                  path_sumo_net: Path,
                  path_output_png: typing.Optional[Path] = None,
                  max_line_width: int = 10,
                  line_color: str = 'auto',
                  ax: Axes = None,
                  f_obj: typing.Optional[Figure] = None,
                  target_vehicle_group: typing.List[str] = None) -> Axes:
        """

        Args:

            path_sumo_net: a XML definition of SUMO network.
            path_vehroute_xml: a XML output of vehroute.
            max_line_width: maximum width of line for rendering traffic.
            line_color:
            ax (optional): matplotlib subplots object
            f_obj (optional): matplotlib file object
            path_output_png (optional): a path to save the png file.
            target_vehicle_routes (optional): a list of vehicle group name that you want to visualize.

        Returns:

        """
        # Plot Sumo Network
        if ax is None:
            fig, ax = plt.subplots()
        # end if

        net = SumoNetVis.Net(str(path_sumo_net))
        net.plot(ax=ax)
        cmap = matplotlib.cm.get_cmap('Spectral')

        target_vehicle_routes = self.extract_route_info(path_vehroute_xml)
        seq_agg_info = self.aggregation(target_vehicle_routes)
        max_frequency = max([agg_obj.frequency for agg_obj in seq_agg_info])
        for route_aggregated_count in seq_agg_info:
            """procedure
            1. get position of routes.
            2. adjustment width of line.
            3. render the line.
            """
            if target_vehicle_group is not None and \
                    route_aggregated_count.vehicle_group_name not in target_vehicle_group:
                continue
            # end if

            assert route_aggregated_count.edge_name in net.edges, \
                f'edge named {route_aggregated_count.edge_name} does not exist in the network.'
            edge_obj = net.edges[route_aggregated_count.edge_name]
            lane_obj = edge_obj.lanes
            for l_obj in lane_obj:
                _line_width = self.set_adjustment_linewidth(target_frequency=route_aggregated_count.frequency,
                                                            max_frequency=max_frequency,
                                                            max_width=max_line_width)
                color = cmap(route_aggregated_count.frequency) if line_color == 'auto' else line_color
                ax.plot(*l_obj.shape.exterior.xy,
                        color=color,
                        label=str(route_aggregated_count.frequency),
                        linewidth=_line_width)
        # Show figure
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
        if f_obj is not None:
            logger.info(f'Saved at {path_output_png}')
            f_obj.savefig(path_output_png)

        return ax



