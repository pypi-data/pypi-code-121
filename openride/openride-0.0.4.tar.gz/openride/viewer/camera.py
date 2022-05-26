from openride import Point

import numpy as np
import vtk



class Camera:

    def __init__(self, viewer):
        self.viewer = viewer
        self._camera = viewer.renderer.GetActiveCamera()
        self._camera.SetClippingRange(0.1, 100000)
        self._camera.SetViewUp(0,0,1)
        self.__add_lights()
        self.set_focus(Point(1))


    def __add_lights(self):
        self._light = vtk.vtkLight()
        self._light.SetPosition(0,0,1)
        self._light.SetFocalPoint(0,0,0)
        self.viewer.renderer.AddLight(self._light)
        self.viewer.renderer.AddLight(self._light.ShallowClone())


    def set_position(self, position:Point):
        self._camera.SetPosition(position.x, position.y, position.z)
        self._light.SetPosition(position.x, position.y, position.z)

    
    def set_focus(self, focus:Point):
        self._camera.SetFocalPoint(focus.x, focus.y, focus.z)
        self._light.SetFocalPoint(focus.x, focus.y, focus.z)


    def get_position(self) -> Point:
        return Point(*self._camera.GetPosition())

    
    def get_focus(self) -> Point:
        return Point(*self._camera.GetFocalPoint())


    def is_in_front(self, point:Point) -> bool:
        v1 = np.array([point.x-self.position.x, point.y-self.position.y, point.z-self.position.z])
        v2 = np.array([self.focus.x-self.position.x, self.focus.y-self.position.y, self.focus.z-self.position.z])
        return np.dot(v1, v2) >= 0