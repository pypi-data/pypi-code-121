"""
# voxel.py
# this module creates a voxel array from an stl
"""

from numpy import hstack, newaxis
from stl.mesh import Mesh
from stltovoxel import convert_meshes


def import_stl_as_voxels(input_file_path, parallel):
    """imports an stl file into a voxel array

    Args:
        input_file_path (str): path to stl file

    Returns:
        nDArray[int8]: a set of voxels in a 3D array,
                          0 and 1 indicate air and block respectively
    """
    meshes = []
    mesh_obj = Mesh.from_file(input_file_path)
    org_mesh = hstack((
        mesh_obj.v0[:, newaxis],
        mesh_obj.v1[:, newaxis],
        mesh_obj.v2[:, newaxis]
    ))
    meshes.append(org_mesh)
    vol = convert_meshes(meshes, resolution=100, parallel=parallel)[0]
    return vol


def import_text_as_voxels(input_text, parallel):
    """imports an stl file into a voxel array

    Args:
        input_text (str): stl text

    Returns:
        nDArray[int8]: a set of voxels in a 3D array,
                          0 and 1 indicate air and block respectively
    """
    meshes = []
    mesh_obj = Mesh.from_file(None, fh=input_text)
    org_mesh = hstack((
        mesh_obj.v0[:, newaxis],
        mesh_obj.v1[:, newaxis],
        mesh_obj.v2[:, newaxis]
    ))
    meshes.append(org_mesh)
    vol = convert_meshes(meshes, resolution=100, parallel=parallel)[0]
    return vol
