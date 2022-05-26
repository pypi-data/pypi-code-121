import os
from .terrain import make_terrain


def boterham_load_model(filename):
    root = loader.load_model(filename)
    # Load links
    # TODO: Make recursive
    loaded = {}
    for child in root.find_all_matches('**/=__linked_file'):
        path = child.get_tag('__linked_file')
        path = os.path.dirname('./'+filename)+path
        nodename = child.get_tag('__linked_node')
        if path in loaded:
            file = loaded[path]
        else:
            file = loaded[path] = loader.load_model(path)
        node = file.find('**/'+nodename)
        instance = node.copy_to(child.parent)
        instance.set_transform(child.get_transform())
        child.detach_node()

    # Setup heightmap
    for child in root.find_all_matches('**/=__make_terrain'):
        filepath, height = child.get_tag('__make_terrain').split(',')
        terrain_root = make_terrain(filepath, int(float(height)))
        terrain_root.wrt_reparent_to(child.parent)
        terrain_root.set_pos(terrain_root, child.get_pos())
        child.detach_node()
    return root
