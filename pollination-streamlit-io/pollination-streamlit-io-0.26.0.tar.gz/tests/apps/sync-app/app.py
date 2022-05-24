import json
import streamlit as st
import pathlib
from streamlit_vtkjs import st_vtkjs

from ladybug_geometry.geometry3d.mesh import Mesh3D
from ladybug_geometry.geometry3d.polyline import Polyline3D 
from ladybug_geometry.geometry3d.line import LineSegment3D 
from ladybug_geometry.geometry3d.pointvector import Point3D
from ladybug_geometry.geometry3d.face import Face3D
from ladybug_geometry.geometry3d.polyface import Polyface3D

from ladybug_vtk.fromgeometry import (
    from_line3d, 
    from_mesh3d, 
    from_point3d, 
    from_polyface3d, 
    from_polyline3d,
    from_face3d
)
from ladybug_vtk.model import Model
from ladybug_vtk.model_dataset import ModelDataSet

from pollination_streamlit_io import (button,
    special)

def get_polydata(value):
    polydata = []
    lbt_data = []
    if not isinstance(value, list):
        value = [value]
    for el in value:
        if el['type'] == 'Mesh3D':
            mesh = Mesh3D.from_dict(el)
            print(mesh)
            polydata.append(from_mesh3d(mesh))
            lbt_data.append(mesh)
        if el['type'] == 'Polyline3D':
            pln = Polyline3D.from_dict(el)
            print(pln)
            polydata.append(from_polyline3d(pln))
            lbt_data.append(pln)
        if el['type'] == 'LineSegment3D':
            crv = LineSegment3D.from_dict(el)
            print(crv)
            polydata.append(from_line3d(crv))
            lbt_data.append(crv)
        if el['type'] == 'Point3D':
            pt = Point3D.from_dict(el)
            print(pt)
            polydata.append(from_point3d(pt))
            lbt_data.append(pt)
        if el['type'] == 'Polyface3D':
            pli = Polyface3D.from_dict(el)
            print(pli)
            polydata.extend(from_polyface3d(pli))
            lbt_data.append(pli)
        if el['type'] == 'Face3D':
            face = Face3D.from_dict(el)
            print(face)
            polydata.append(from_face3d(face))
            lbt_data.append(face)
    
    dataSet = ModelDataSet('test', polydata)
    model = Model(dataSet)
    test = model.to_vtkjs('.', './geometry')
    return pathlib.Path(test), lbt_data

def run_viewer(value, key):
    file, ltb_data = get_polydata(value)
    dict_data = [_.to_dict() for _ in ltb_data]
    st_vtkjs(file.read_bytes(), True, key)
    return dict_data

def run_model_viewer(value, key):
    file, ltb_data = get_polydata(value)
    dict_data = [_.to_dict() for _ in ltb_data]
    st_vtkjs(file.read_bytes(), True, key)
    return dict_data

# get the platform from the query uri
query = st.experimental_get_query_params()
platform = special.get_host()

if platform == 'rhino':
    # special controls
    st.subheader('Pollination Token for Sync')
    po_token = special.sync(key="my-po-sync")
    st.write(po_token)

    # common controls
    # first sync button.get
    st.subheader('Pollination, Get Geometry Button')
    geometry = button.get(key='0001',
        sync_token=po_token)
    if geometry:
        # st.json(geometry)
        dict_data = run_viewer(geometry, 
            key="my-super-viewer")
    
    # second sync button.get
    st.subheader('Pollination, Get Geometry Button')
    geometry = button.get(key='0002',
        sync_token=po_token)
    if geometry:
        # st.json(geometry)
        dict_data = run_viewer(geometry,
        key="my-super-viewer-2")

if platform == 'sketchup':
    # special controls
    st.subheader('Pollination Token for Sync')
    po_token = special.sync(key="my-po-sync")
    st.write(po_token)
    # common controls
    # first sync button.get
    st.subheader('Geometry, Get Geometry Button')
    geometry = button.get(key='0001',
        sync_token=po_token,
        platform='sketchup')
    if geometry:
        # st.json(geometry)
        dict_data = run_viewer(geometry, 
            key="my-super-viewer")
    
    # second sync button.get
    st.subheader('Geometry, Get Geometry Button')
    geometry = button.get(key='0002',
        sync_token=po_token,
        platform='sketchup')
    if geometry:
        # st.json(geometry)
        dict_data = run_viewer(geometry, 
            key="my-super-viewer-2")

    # model button.get
    st.subheader('Pollination, Get Geometry Button')
    model = button.get(key='0003',
        is_pollination_model=True,
        platform='sketchup')
    if model:
        st.json(model)