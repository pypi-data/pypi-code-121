import os
import sys
import json

import bpy
import blend2bam.blender_script_common as common #pylint: disable=import-error,wrong-import-position
from blend2bam.blend2gltf.blender28_script import (
    export_physics,
    fix_image_uri,
    add_actions_to_nla,
    prepare_meshes,
)

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ))
from boterham.helpers import select_obj, duplicate_obj, convert_to_empty


def make_lod(obj, modifier, nodetype='LODNode'):
    print('Auto-LODing', obj.name)
    lod = convert_to_empty(obj)
    steps = int(modifier.name.split('_')[1])
    baseline = modifier.ratio
    step_size = (1-baseline)/steps
    for i in range(steps):
        copy = duplicate_obj(obj)
        for modifier in obj.modifiers:
            if modifier.type == 'DECIMATE' and modifier.name.split('_')[0] == 'LOD':
                modifier.ratio = baseline + (i*step_size)
                bpy.ops.object.modifier_apply(modifier=modifier.name)
        copy.name = lod.name + '_LOD_' + str(i)
        copy.data.name = copy.name
        copy.location = 0,0,0
        copy.rotation_euler = 0,0,0
        copy.parent = lod
    lod['+'+nodetype] = 'None'
    bpy.data.objects.remove(obj, do_unlink=True)

def prepare_modifiers():
    for obj in bpy.data.objects:
        for modifier in obj.modifiers:
            if modifier.type == 'DISPLACE' and modifier.name == 'ShaderTerrainMesh':
                obj['__make_terrain'] = '{},{}'.format(modifier.texture.image.filepath, modifier.strength)
            if modifier.type == 'DECIMATE':
                if modifier.name.split('_')[0] == 'LOD':
                    make_lod(obj, modifier)
                if modifier.name.split('_')[0] == 'FadeLOD':
                    make_lod(obj, modifier, 'FadeLOD')
            if modifier.type == 'NODES':
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(state=True)
                bpy.ops.object.duplicates_make_real(use_base_parent=True, use_hierarchy=True)

def prepare_instancing():
    for obj in bpy.data.objects:
        if obj.is_instancer:
            collection = obj.instance_collection
            if collection:
                library = collection.library
                if library:
                    link = convert_to_empty(obj)
                    path = os.path.splitext(str(library.filepath))[0]+'.bam'
                    link['__linked_file'] = path
                    link['__linked_node'] = collection.name
                    bpy.data.objects.remove(obj, do_unlink=True)

def prepare_wireframe():
    for obj in bpy.data.objects:
        if obj.show_wire:
            color = tuple(obj.color)
            duplicate = duplicate_obj(obj)
            duplicate.show_wire = False
            bpy.context.view_layer.objects.active = duplicate
            select_obj(None)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.delete(type='ONLY_FACE')
            bpy.ops.object.mode_set(mode='OBJECT')
            duplicate.name = 'wireframe_'+obj.name
            duplicate['$set_color'] = '"extra_args":[{}]'.format(list(color))
            duplicate.parent = obj


def export_gltf(settings, src, dst):
    print('Converting .blend file ({}) to .gltf ({})'.format(src, dst))
    dstdir = os.path.dirname(dst)
    os.makedirs(dstdir, exist_ok=True)
    common.make_particles_real()
    add_actions_to_nla()

    print('Preprocessing')
    prepare_wireframe()
    prepare_instancing()
    prepare_modifiers()
    prepare_meshes()

    bpy.ops.export_scene.gltf(
        filepath=dst,
        export_format='GLTF_EMBEDDED' if settings['textures'] == 'embed' else 'GLTF_SEPARATE',
        export_cameras=True,
        export_extras=True,
        export_yup=False,
        export_lights=True,
        export_force_sampling=True,
        export_apply=True,
        export_tangents=True,
        export_animations=settings['animations'] != 'skip',
        use_mesh_edges=True,
        use_mesh_vertices=True,
    )

    with open(dst) as gltf_file:
        gltf_data = json.load(gltf_file)

    #export_physics(gltf_data)
    if settings['textures'] == 'ref':
        fix_image_uri(gltf_data)

    with open(dst, 'w') as gltf_file:
        json.dump(gltf_data, gltf_file, indent=4)


if __name__ == '__main__':
    common.convert_files(export_gltf, 'gltf')
