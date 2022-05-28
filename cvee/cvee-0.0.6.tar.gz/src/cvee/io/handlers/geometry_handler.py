import numpy as np

from cvee.io.handlers.base import BaseFileHandler

try:
    import trimesh
except:
    pass


# TODO: write test cases
class GeometryHandler(BaseFileHandler):
    def load_from_fileobj(self, file, **kwargs):
        mesh = trimesh.load(file)
        if isinstance(mesh, trimesh.points.PointCloud):
            return np.asarray(mesh.vertices)
        else:
            return np.asarray(mesh.vertices), np.asarray(mesh.faces)

    def save_to_fileobj(self, file, obj, **kwargs):
        if isinstance(obj, dict):
            if "faces" in obj and "vertices" in obj:
                _ = trimesh.Trimesh(vertices=obj["vertices"], faces=obj["faces"]).export(file)
            elif "faces" not in obj and "vertices" in obj:
                _ = trimesh.Trimesh(vertices=obj["vertices"]).export(file)
            else:
                raise RuntimeError("Dict obj should contain key 'vertices'")
        elif isinstance(obj, list) or isinstance(obj, tuple):
            if len(obj) == 2:
                _ = trimesh.Trimesh(vertices=obj[0], faces=obj[1]).export(file)
            elif len(obj) == 1:
                _ = trimesh.Trimesh(vertices=obj[0]).export(file)
            else:
                raise RuntimeError("Obj should not be empty")
        elif isinstance(obj, trimesh.Trimesh):
            _ = obj.export(file)
        elif isinstance(obj, np.ndarray):
            _ = trimesh.Trimesh(vertices=obj).export(file)
        else:
            raise TypeError(f"Not supported type: {type(obj)}")

    def load_from_path(self, filepath, **kwargs):
        mesh = trimesh.load(filepath)
        if isinstance(mesh, trimesh.points.PointCloud):
            return np.asarray(mesh.vertices)
        else:
            return np.asarray(mesh.vertices), np.asarray(mesh.faces)

    def save_to_path(self, filepath, obj, **kwargs):
        if isinstance(obj, dict):
            if "faces" in obj and "vertices" in obj:
                _ = trimesh.Trimesh(vertices=obj["vertices"], faces=obj["faces"]).export(filepath)
            elif "faces" not in obj and "vertices" in obj:
                _ = trimesh.Trimesh(vertices=obj["vertices"]).export(filepath)
            else:
                raise RuntimeError("Dict obj should contain key vertices")
        elif isinstance(obj, list) or isinstance(obj, tuple):
            if len(obj) == 2:
                _ = trimesh.Trimesh(vertices=obj[0], faces=obj[1]).export(filepath)
            elif len(obj) == 1:
                _ = trimesh.Trimesh(vertices=obj[0]).export(filepath)
            else:
                raise RuntimeError("Obj should not be empty")
        elif isinstance(obj, trimesh.Trimesh):
            _ = obj.export(filepath)
        elif isinstance(obj, np.ndarray):
            _ = trimesh.Trimesh(vertices=obj).export(filepath)
        else:
            raise TypeError(f"Not supported type: {type(obj)}")
