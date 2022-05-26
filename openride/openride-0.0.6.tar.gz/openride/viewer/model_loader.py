import vtk

from abc import ABC, abstractclassmethod



class BaseModelLoader(ABC):

    @abstractclassmethod
    def __call__(self, file:str) -> vtk.vtkPolyData:
        """Loads files into vtk.vtkPolyData instances"""



class STLLoader(BaseModelLoader):

    def __init__(self):
        self._loaded_files = {}

    def __call__(self, file:str, n_polygons:int=100000) -> vtk.vtkPolyData:
        """Loads .stl files into vtk.vtkPolyData instances"""
        if file not in self._loaded_files:
            reader = vtk.vtkSTLReader()
            reader.SetFileName(file)
            reader.Update()
            polydata = reader.GetOutput()

            decimate = vtk.vtkQuadricDecimation()
            decimate.SetInputData(polydata)
            decimate.SetTargetReduction(1.0 - n_polygons / polydata.GetNumberOfPolys())
            decimate.Update()
    
            self._loaded_files[file] = decimate.GetOutput()

        return self._loaded_files[file]


class OBJLoader(BaseModelLoader):

    def __init__(self):
        self._loaded_files = {}

    def __call__(self, file:str, n_polygons:int=100000) -> vtk.vtkPolyData:
        """Loads .stl files into vtk.vtkPolyData instances"""
        if file not in self._loaded_files:
            reader = vtk.vtkOBJReader()
            reader.SetFileName(file)
            reader.Update()
            polydata = reader.GetOutput()

            decimate = vtk.vtkQuadricDecimation()
            decimate.SetInputData(polydata)
            decimate.SetTargetReduction(1.0 - n_polygons / polydata.GetNumberOfPolys())
            decimate.Update()
    
            self._loaded_files[file] = decimate.GetOutput()

        return self._loaded_files[file]


class ModelLoader(BaseModelLoader):

    def __init__(self):
        self.loaders = {
            'stl': STLLoader(),
            'obj': OBJLoader(),
        }

    def __call__(self, file:str) -> vtk.vtkPolyData:
        loader = self.loaders.get(file.split('.')[-1])
        if loader is None:
            raise NotImplementedError
        else:
            return loader(file)