import numpy as np
import vtk
from openride.viewer.model_loader import ModelLoader
import vtk.util.numpy_support as vtk_np

from matplotlib import cm
from typing import List



def get_point_actor(x:float, y:float, z:float, color:tuple=(1,1,1), size:int=0.15, alpha:float=1, resolution:int=10) -> vtk.vtkActor:
    source = vtk.vtkSphereSource()
    source.SetThetaResolution(resolution)
    source.SetPhiResolution(resolution)
    source.SetCenter(x, y, z)
    source.SetRadius(size)
    return source_to_actor(source, color, alpha)


BOX_ACTORS_CACHE = {}
def get_box_actor(x:float, y:float, z:float, sx:float, sy:float, sz:float, roll:float, pitch:float, yaw:float, color:tuple=None, alpha:float=1) -> vtk.vtkActor:
    
    # Creating these actors is expansive, so we reuse them if an identical one has already been created.
    args = (color, alpha)
    if args not in BOX_ACTORS_CACHE:
        source = vtk.vtkCubeSource()
        BOX_ACTORS_CACHE[args] = source_to_actor(source, color, alpha)

    actor = vtk.vtkActor()
    actor.ShallowCopy(BOX_ACTORS_CACHE[args])

    actor.SetScale(2 * sx, 2 * sy, 2 * sz)
    rotate_actor(actor, roll, pitch, yaw)
    move_actor(actor, x, y, z)
    return actor


def get_line_actor(vertices:np.ndarray, color:tuple=(1,1,1), alpha:float=1, linewidth:int=2, dashed:bool=False) -> vtk.vtkActor:
    polydata = vtk.vtkPolyData()
    actor = polydata_to_actor(polydata, color, alpha)
    actor.GetProperty().SetLineWidth(linewidth)
    points = vtk.vtkPoints()
    points.SetData(vtk_np.numpy_to_vtk(vertices))
    polydata.SetPoints(points)
    
    lines = vtk.vtkCellArray()
    step = 1 if not dashed else 2
    for i in range(0, vertices.shape[0]-1, step):
        lines.InsertNextCell(2)
        lines.InsertCellPoint(i)
        lines.InsertCellPoint(i+1)
    polydata.SetLines(lines)
    return actor


def get_lines_actor(list_vertices:List[np.ndarray], color:tuple=(1,1,1), alpha:float=1, linewidth:int=2) -> vtk.vtkActor:
    polydata = vtk.vtkPolyData()
    actor = polydata_to_actor(polydata, color, alpha)
    actor.GetProperty().SetLineWidth(linewidth)
    points = vtk.vtkPoints()
    points.SetData(vtk_np.numpy_to_vtk(np.vstack(list_vertices)))
    polydata.SetPoints(points)

    lines = vtk.vtkCellArray()
    i = 0
    for vertices in list_vertices:
        for _ in range(0, vertices.shape[0]-1, 1):
            lines.InsertNextCell(2)
            lines.InsertCellPoint(i)
            lines.InsertCellPoint(i+1)
            i += 1
        i += 1
    polydata.SetLines(lines)
    return actor


def get_polygon_polydata(vertices:np.ndarray) -> vtk.vtkPolyData:

    points = vtk.vtkPoints()
    polygon = vtk.vtkPolygon()
    polygon.GetPointIds().SetNumberOfIds(vertices.shape[0])
    
    for i, p in enumerate(vertices):
        polygon.GetPointIds().SetId(i, i)
        points.InsertNextPoint(p[0], p[1], p[2]) 

    # Add the polygon to a list of polygons
    polygons = vtk.vtkCellArray()
    polygons.InsertNextCell(polygon)

    # Create a PolyData
    polygonPolyData = vtk.vtkPolyData()
    polygonPolyData.SetPoints(points)
    polygonPolyData.SetPolys(polygons)

    pdflt = vtk.vtkTriangleFilter()
    pdflt.SetInputData(polygonPolyData)
    pdflt.Update()
    polygonPolyData = pdflt.GetOutput()

    return polygonPolyData


def get_polygon_actor(vertices:np.ndarray, color:tuple=(1,1,1), alpha:float=1) -> vtk.vtkActor:
    return polydata_to_actor(get_polygon_polydata(vertices), color, alpha)


def get_polygons_actor(vertices_list:List[np.ndarray], color:tuple=(1,1,1), alpha:float=1) -> vtk.vtkActor:

    appendFilter = vtk.vtkAppendPolyData()
    for vertices in vertices_list:
        appendFilter.AddInputData(get_polygon_polydata(vertices))
    appendFilter.Update()

    pdflt = vtk.vtkTriangleFilter()
    pdflt.SetInputData(appendFilter.GetOutput())
    pdflt.Update()
    polygonPolyData = pdflt.GetOutput()

    return polydata_to_actor(polygonPolyData, color, alpha)


def get_point_cloud_actor(vertices:np.ndarray, amplitudes:np.ndarray, color:tuple=None, colormap:str='jet', size:int=10, alpha:float=1, amplitude_max:float=2**16):
    polydata = vtk.vtkPolyData()
    actor = polydata_to_actor(polydata, alpha=alpha)
    actor.GetProperty().SetPointSize(size)
    actor.GetProperty().SetRenderPointsAsSpheres(1)
    points = vtk.vtkPoints()
    cells = vtk.vtkCellArray()
    N = vertices.shape[0]
    points.SetData(vtk_np.numpy_to_vtk(vertices))
    cells_npy = np.vstack([np.ones(N, dtype = np.int64), np.arange(N, dtype = np.int64)]).T.flatten()
    cells.SetCells(N, vtk_np.numpy_to_vtkIdTypeArray(cells_npy))
    polydata.SetPoints(points)
    polydata.SetVerts(cells)

    # Colorize point cloud
    # FIXME: This is slow for large point clouds because of the loop. But a better solution is not trivial.
    if color is None:
        vtkcolors = vtk.vtkUnsignedCharArray()
        vtkcolors.SetNumberOfComponents(3)
        normalized_amplitudes = np.log(1 + np.clip(amplitudes, 0, np.inf)) / np.log(amplitude_max)
        colors = getattr(cm, colormap)(normalized_amplitudes)[:,:3]*255
        for i, p in enumerate(vertices):
            vtkcolors.InsertNextTuple(colors[i])
        polydata.GetCellData().SetScalars(vtkcolors)
    elif isinstance(color, tuple):
        actor.GetProperty().SetColor(*color)
    else:
        # (N,3) rgb color array
        vtkcolors = vtk.vtkUnsignedCharArray()
        vtkcolors.SetNumberOfComponents(3)
        for i, p in enumerate(vertices):
            vtkcolors.InsertNextTuple(color[i]*255)
        polydata.GetCellData().SetScalars(vtkcolors)

    return actor


# Creating these actors is expensive, so we initialize a bunch of them once and reuse them
TEXT_ACTORS_CACHE = [vtk.vtkCaptionActor2D() for _ in range(100)]
def get_text_actor(text:str, x:float, y:float, z:float, fontsize:int=16, _text_actor_index:int=None) -> vtk.vtkCaptionActor2D:

    if _text_actor_index is None:
        actor = vtk.vtkCaptionActor2D()
    else:
        # Because vtkCaptionActor2D are expensive to initialize, we reuse the same actors stored in a list that we expand if needed
        while _text_actor_index >= len(TEXT_ACTORS_CACHE):
            TEXT_ACTORS_CACHE.append(vtk.vtkCaptionActor2D())
        actor = TEXT_ACTORS_CACHE[_text_actor_index]

    actor.SetCaption(text)
    actor.SetAttachmentPoint(x, y, z)
    actor.BorderOff()
    actor.GetTextActor().SetTextScaleModeToNone()
    actor.GetCaptionTextProperty().SetFontSize(fontsize)
    actor.GetCaptionTextProperty().SetShadow(0)
    return actor


def get_cone_actor(x1:float, y1:float, z1:float, x2:float, y2:float, z2:float, color:tuple=(1,1,1), alpha:float=1, headsize:float=1):
    cone_source = vtk.vtkConeSource()
    cone_source.SetHeight(2*headsize)
    cone_source.SetRadius(headsize)
    cone_source.SetCenter(x2, y2, z2)
    cone_source.SetDirection(x2-x1, y2-y1, z2-z1)
    return source_to_actor(cone_source, color, alpha)


MODEL_ACTORS_CACHE = {}
def get_model_actor(loader:ModelLoader, file:str, x:float, y:float, z:float, sx:float, sy:float, sz:float, roll:float, pitch:float, yaw:float, color:tuple=(1,1,1), alpha:float=1) -> vtk.vtkActor:

    # Creating these actors is expansive, so we reuse them if an identical one has already been created.
    args = (file, color, alpha)
    if args not in MODEL_ACTORS_CACHE:
        polydata = loader(file)
        _actor = polydata_to_actor(polydata, color, alpha)
        MODEL_ACTORS_CACHE[args] = (_actor, file)

    actor = vtk.vtkActor()
    actor.ShallowCopy(MODEL_ACTORS_CACHE[args][0])

    x0,x1,y0,y1,z0,z1 = actor.GetBounds()
    actor.SetScale(2*sx/(x1-x0), 2*sy/(y1-y0), 2*sz/(z1-z0))
    rotate_actor(actor, roll, pitch, yaw)
    x0,x1,y0,y1,z0,z1 = actor.GetBounds()
    move_actor(actor, x - (x0 + x1)/2, y - (y0 + y1)/2, z - (z0 + z1)/2)
    
    return actor
            

def mapper_to_actor(mapper:vtk.vtkPolyDataMapper, color:tuple=(1,1,1), alpha:float=1.0) -> vtk.vtkActor:
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(*color)
    actor.GetProperty().SetOpacity(alpha)
    return actor


def source_to_actor(source, color:tuple=(1,1,1), alpha:float=1.0) -> vtk.vtkActor:
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(source.GetOutputPort())
    return mapper_to_actor(mapper, color, alpha)


def polydata_to_actor(polydata, color:tuple=(1,1,1), alpha:float=1.0) -> vtk.vtkActor:
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(polydata)
    return mapper_to_actor(mapper, color, alpha)


def array_to_texture(array:np.ndarray) -> vtk.vtkTexture:
    grid = vtk.vtkImageData()
    grid.SetDimensions(array.shape[0], array.shape[1], 1)
    vtkarr = vtk_np.numpy_to_vtk(array.swapaxes(0,1).reshape((-1, array.shape[-1]), order='F'))
    vtkarr.SetName('Image')
    grid.GetPointData().AddArray(vtkarr)
    grid.GetPointData().SetActiveScalars('Image')
    vtex = vtk.vtkTexture()
    vtex.SetColorModeToDirectScalars()
    vtex.SetInputDataObject(grid)
    return vtex


def move_actor(actor:vtk.vtkActor, x:float, y:float, z:float):
    actor.AddPosition(x, y, z)


def rotate_actor(actor:vtk.vtkActor, roll:float, pitch:float, yaw:float):
    actor.AddOrientation(np.rad2deg(roll), np.rad2deg(pitch), np.rad2deg(yaw))


def set_scale_actor(actor:vtk.vtkActor, sx:float, sy:float, sz:float):
    actor.SetScale(sx, sy, sz)