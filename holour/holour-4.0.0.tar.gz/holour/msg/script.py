

class Script:

    def __init__(self, filename: str, path: str, _type: str = ''):
        self._type = 'script'
        self.filename = filename
        self.path = path

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Script):
            return other.filename == self.filename and other.path == self.path
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __repr__(self):
        return f"Script<filename={self.filename}, path={self.path}>"


class WaypointConfig:

    def __init__(self, show_waypoints: bool, show_current_waypoint: bool, _type: str = ''):
        self._type = 'waypoint_config'
        self.show_waypoints = show_waypoints
        self.show_current_waypoint = show_current_waypoint

    def __eq__(self, other: object) -> bool:
        if isinstance(other, WaypointConfig):
            return other.show_waypoints == self.show_waypoints \
                   and other.show_current_waypoint == self.show_current_waypoint
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __repr__(self):
        return f"WaypointConfig<" \
               f"show_waypoints={self.show_waypoints}, show_current_waypoint={self.show_current_waypoint}>"
