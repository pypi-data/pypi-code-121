from openride import Point

from typing import Tuple

import numpy as np
import vtk



def spherical_to_cartesian(r, theta, phi) -> Tuple[float, float, float]:
    x = r * np.sin(phi) * np.cos(theta)
    y = r * np.sin(phi) * np.sin(theta)
    z = r * np.cos(phi)
    return x, y, z


def cartesian_to_spherical(x, y, z) -> Tuple[float, float, float]:
    r = (x**2 + y**2 + z**2)**0.5
    theta = np.arctan(y / (x + np.finfo(float).eps))
    if x < 0:
        theta += np.pi
    phi = np.arccos(z / (r + np.finfo(float).eps))
    return r, theta, phi



class Interactor:

    def __init__(self, vtk_viewer):

        self.viewer = vtk_viewer
        
        self._interactor = self.viewer.renderWindow.MakeRenderWindowInteractor()

        # Set an empty style, so this interactor does nothing when we call ProcessEvents() except our callbacks.
        self._interactor.SetInteractorStyle(vtk.vtkInteractorEventRecorder())

        # Callbacks
        self._interactor.AddObserver('MouseMoveEvent',           self.__on_move, 1.0)
        self._interactor.AddObserver('LeftButtonPressEvent',     self.__on_left_click, 1.0)
        self._interactor.AddObserver('MiddleButtonPressEvent',   self.__on_middle_click, 1.0)
        self._interactor.AddObserver('RightButtonPressEvent',    self.__on_right_click, 1.0)
        self._interactor.AddObserver('LeftButtonReleaseEvent',   self.__on_left_release, 1.0)
        self._interactor.AddObserver('MiddleButtonReleaseEvent', self.__on_middle_release, 1.0)
        self._interactor.AddObserver('RightButtonReleaseEvent',  self.__on_right_release, 1.0)
        self._interactor.AddObserver('MouseWheelForwardEvent',   self.__on_scroll_up, 1.0)
        self._interactor.AddObserver('MouseWheelBackwardEvent',  self.__on_scroll_down, 1.0)
        self._interactor.AddObserver('EnterEvent',               self.__on_enter, 1.0)
        self._interactor.AddObserver('LeaveEvent',               self.__on_leave, 1.0)
        self._interactor.AddObserver('ExitEvent',                self.__on_exit, 1.0)
        self._interactor.Initialize()

        self._point_placer = vtk.vtkFocalPlanePointPlacer()

        self.cursor = (0,0)
        self.cursor_is_in_window = True
        self.left_mouse = False
        self.middle_mouse = False
        self.right_mouse = False

    def toggle(self, state:bool):
        if state: self._interactor.Enable()
        else: self._interactor.Disable()

    def update(self):
        self._interactor.ProcessEvents()        

    def __on_enter(self, *args):
        self.cursor_is_in_window = True
    def __on_leave(self, *args):
        self.cursor_is_in_window = False

    def __on_left_click(self, *args):
        self.left_mouse = True
        self.grab_position = self.get_cursor_in_world()
    def __on_left_release(self, *args):
        self.left_mouse = False
    def __on_middle_click(self, *args):
        self.middle_mouse = True
    def __on_middle_release(self, *args):
        self.middle_mouse = False
    def __on_right_click(self, *args):
        self.right_mouse = True
    def __on_right_release(self, *args):
        self.right_mouse = False
    def __on_scroll_up(self, *args):
        self.zoom(1)
    def __on_scroll_down(self, *args):
        self.zoom(-1)
    def __on_exit(self, *args):
        exit()

    def __on_move(self, event, _):
        if not self.cursor_is_in_window: return
        self.cursor = event.GetEventPosition()

        position = self.viewer.camera.get_position()
        focus    = self.viewer.camera.get_focus()


        if self.left_mouse:
            delta = self.get_cursor_in_world() - self.grab_position
            position -= delta
            focus -= delta

        if self.middle_mouse:
            x0, y0 = event.GetLastEventPosition()
            d, horizontal_angle, vertical_angle = self.__get_camera_spherical_coordinates()
            factor = (d / 1400)
            delta_y = self.cursor[1] - y0
            position.z -= factor * delta_y
            focus.z -= factor * delta_y

        if self.right_mouse:
            x0, y0 = event.GetLastEventPosition()
            delta_x = self.cursor[0] - x0
            delta_y = self.cursor[1] - y0
            
            d, horizontal_angle, vertical_angle = self.__get_camera_spherical_coordinates()
            horizontal_angle -= delta_x / 200
            vertical_angle = np.clip(vertical_angle + delta_y / 200, 0.001, np.pi-0.001)
            delta = Point(*spherical_to_cartesian(d, horizontal_angle, vertical_angle))
            position = delta + focus

        self.viewer.camera.set_position(position)
        self.viewer.camera.set_focus(focus)


    def zoom(self, value:float):
        d, horizontal_angle, vertical_angle = self.__get_camera_spherical_coordinates()
        factor = d / 10
        d += value * factor
        delta = Point(*spherical_to_cartesian(d, horizontal_angle, vertical_angle))
        self.viewer.camera.set_position(delta + self.viewer.camera.get_focus())


    def __get_camera_spherical_coordinates(self) -> Tuple[float, float, float]:
        c = self.viewer.camera.get_position() - self.viewer.camera.get_focus()
        return cartesian_to_spherical(c.x, c.y, c.z)


    def get_cursor_in_world(self) -> Point:
        """Returns the intersection between the mouse cursor and the plane z = camera.focus"""
        x, y = self.cursor
        focal_plane_projection = self.__get_cursor_on_focal_plane_projection(x, y)
        return self.__focal_plane_projection_to_z_slice_projection(focal_plane_projection, self.viewer.camera.get_focus().z)


    def __get_cursor_on_focal_plane_projection(self, pixel_x:int, pixel_y:int) -> Point:
        world_position = [0,0,0]
        world_orientation = [0,0,0,0,0,0,0,0,0]
        self._point_placer.ComputeWorldPosition(self.viewer.renderer, (pixel_x, pixel_y), world_position, world_orientation)
        return Point(*world_position)


    def __focal_plane_projection_to_z_slice_projection(self, focal_plane_projection:Point, world_z:float) -> Point:
        cam_position = self.viewer.camera.get_position()
        cam_to_focal_proj = focal_plane_projection - cam_position
        r, theta, phi = cartesian_to_spherical(cam_to_focal_proj.x, cam_to_focal_proj.y, cam_to_focal_proj.z)
        r *= (world_z - cam_position.z) / cam_to_focal_proj.z
        cam_to_focal_proj = Point(*spherical_to_cartesian(r, theta, phi))
        return cam_position + cam_to_focal_proj
