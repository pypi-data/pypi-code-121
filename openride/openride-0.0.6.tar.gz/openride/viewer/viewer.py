from openride import BoundingBox, Point, Polyline, Polygon
from openride.core.polyline import Polyline
from openride.viewer import vtk_utils
from openride.viewer.camera import Camera
from openride.viewer.interactor import Interactor
from openride.viewer.hud import Hud
from openride.viewer.model_loader import ModelLoader

from typing import List, Tuple

import vtk



class Viewer:

    def __init__(self, resolution=(1600,900), background:Tuple[float,float,float]=(0.05,0.05,0.1)):

        self.renderer = vtk.vtkRenderer()
        self.renderWindow = vtk.vtkRenderWindow()
        self.renderWindow.AddRenderer(self.renderer)

        self.set_resolution(resolution)
        self.set_background(background)

        self.camera = Camera(self)
        self.interactor = Interactor(self)
        self.hud = Hud(self, position=(50,50))

        self._model_loader = ModelLoader()

        self._actors_to_clear = []
        self._text_actor_index = 0


    def set_resolution(self, resolution:Tuple[int, int]):
        self.renderWindow.SetSize(resolution[0], resolution[1])


    def set_background(self, color=Tuple[float,float,float]):
        self.renderer.SetBackground(*color)
        

    def update(self):
        self.interactor.update()
        self.hud.update()
        self.renderWindow.Render()
        self.__clear_actors()


    def render_actor(self, actor:vtk.vtkActor, persist:bool=False):
        self.renderer.AddActor(actor)
        if not persist: self._actors_to_clear.append(actor)


    def draw_point(self, point:Point, color:tuple=(1,1,1), size:int=0.15, alpha:float=1, resolution:int=10, persist:bool=False):
        actor = vtk_utils.get_point_actor(point.x, point.y, point.z, color, size, alpha, resolution)
        self.render_actor(actor, persist)


    def draw_bounding_box(self, bounding_box:BoundingBox, color:tuple=(1,1,1), alpha:float=1, edge_color:tuple=None, persist:bool=False):

        actor = vtk_utils.get_box_actor(
            bounding_box.position.x, bounding_box.position.y, bounding_box.position.z, 
            bounding_box.size.x, bounding_box.size.y, bounding_box.size.z,
            bounding_box.rotation.roll, bounding_box.rotation.pitch, bounding_box.rotation.yaw,
            color, alpha
        )

        if edge_color is not None:
            actor.GetProperty().SetEdgeVisibility(1)
            actor.GetProperty().SetLineWidth(10)
            actor.GetProperty().SetEdgeColor(*edge_color)

        self.render_actor(actor, persist)


    def draw_model(self, file:str, bounding_box:BoundingBox, color:tuple=(1,1,1), alpha:float=1, persist:bool=False):
        p = bounding_box.position
        s = bounding_box.size
        r = bounding_box.rotation
        actor = vtk_utils.get_model_actor(self._model_loader, file, p.x, p.y, p.z, s.x, s.y, s.z, r.roll, r.pitch, r.yaw, color, alpha)
        self.render_actor(actor, persist)


    def draw_polyline(self, line:Polyline, color:tuple=(1,1,1), alpha:float=1, linewidth:int=2, persist:bool=False):
        actor = vtk_utils.get_line_actor(line.vertices, color, alpha, linewidth)
        self.render_actor(actor, persist)


    def draw_polylines(self, lines:List[Polyline], color:tuple=(1,1,1), alpha:float=1, linewidth:int=2, persist:bool=False):
        actor = vtk_utils.get_lines_actor([line.vertices for line in lines], color=color, alpha=alpha, linewidth=linewidth)
        self.render_actor(actor, persist)


    def draw_polygon(self, polygon:Polygon, color:tuple=(1,1,1), alpha:float=1, persist:bool=False):
        actor = vtk_utils.get_polygon_actor(polygon.vertices, color=color, alpha=alpha)
        self.render_actor(actor, persist)


    def labelize(self, label:str, pos:Point, fontsize:int=16, persist:bool=False):
        if not self.camera.is_in_front(pos): return
        actor = vtk_utils.get_text_actor(label, pos.x, pos.y, pos.z, fontsize, self._text_actor_index)
        self.render_actor(actor, persist)
        self._text_actor_index += 1


    def draw_arrow(self, start:Point, end:Point, color:tuple=(1,1,1), alpha:float=1, linewidth:int=10, headsize:float=1, persist:bool=False):
        self.draw_line(Polyline([start, end]), color=color, alpha=alpha, linewidth=linewidth)
        actor = vtk_utils.get_cone_actor(
            start.x, start.y, start.z,
            end.x, end.y, end.z, 
            color, alpha, headsize,
        )
        self.render_actor(actor, persist)


    def draw_grid(self, origin:Point=Point(), delta:float=5, extent:float=200, alpha:float=1.0, persist:bool=True):
        lines = []

        for s in [0,1]:
            for i in range(int(2*extent/delta)+1):
                points = []
                if s == 0:
                    points.append(Point(-extent, -extent + i * delta) + origin)
                    points.append(Point( extent, -extent + i * delta) + origin)
                else:
                    points.append(Point(-extent + i * delta, -extent) + origin)
                    points.append(Point(-extent + i * delta,  extent) + origin)
                lines.append(Polyline(points))

        self.draw_polylines(lines, color=(0.3,0.3,0.3), alpha=alpha, linewidth=1, persist=persist)


    def __clear_actors(self):
        for actor in self._actors_to_clear:
            self.renderer.RemoveActor(actor)
        self._actors_to_clear = []
        self._text_actor_index = 0


    def close(self):
        del self.renderWindow
        self.interactor._interactor.InvokeEvent("ExitEvent")
