import bpy

def select_obj(obj=None, append=False):
    if not append:
        bpy.ops.object.select_all(action='DESELECT')
    if obj:
        obj.select_set(state=True)

def duplicate_obj(obj, select=True):
    if obj:
        copy = obj.copy()
        if obj.data:
            copy.data = obj.data.copy()
        if obj.animation_data:
            copy.animation_data.action = obj.animation_data.action.copy()
        bpy.context.scene.collection.objects.link(copy)
    if select:
        select_obj(obj)
    return copy

def convert_to_empty(obj):
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='CURSOR')
    empty = bpy.context.object
    name = obj.name
    obj.name = 'None'
    empty.name = name
    empty.parent = obj.parent
    empty.location = obj.location
    empty.rotation_euler = obj.rotation_euler
    empty.scale = obj.scale
    return empty
