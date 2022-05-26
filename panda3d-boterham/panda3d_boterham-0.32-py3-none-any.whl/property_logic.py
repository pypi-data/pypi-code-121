import sys
import json
import panda3d.core


def geom_to_collision_polygons(root, keep=True):
    for c in root.findAllMatches('**/+GeomNode'):
        geomNode = c.node()
        for g in range(geomNode.getNumGeoms()):
            geom = geomNode.getGeom(g).decompose()
            vdata = geom.getVertexData()
            vreader = panda3d.core.GeomVertexReader(vdata, 'vertex')
            cChild = panda3d.core.CollisionNode('{}'.format(c.getName()))
            for p in range(geom.getNumPrimitives()):
                prim = geom.getPrimitive(p)
                for p2 in range(prim.getNumPrimitives()):
                    s = prim.getPrimitiveStart(p2)
                    e = prim.getPrimitiveEnd(p2)
                    v = []
                    for vi in range (s, e):
                        vreader.setRow(prim.getVertex(vi))
                        v.append (vreader.getData3f())
                    colPoly = panda3d.core.CollisionPolygon(*v)
                    cChild.addSolid(colPoly)
            c.parent.attachNewNode(cChild)
            if not keep:
                c.detach_node()

def nodepath_to_collision_polygons(root):
    for nodepath in root.find_all_matches("**/=geom_to_collision_polygon"):
        geom_to_collision_polygons(nodepath)

def set_collision_shapes(nodepath):
    def get_pos_hpr_scale(np):
        return np.get_pos(), np.get_hpr(), np.get_scale()

    def add_shape(nodepath, shape, shape_np):
        nodepath.node().add_solid(shape)
        shape_np.detach_node()

    for shape_np in nodepath.find_all_matches('**/=+CollisionSphere'):
        pos, hpr, scale = get_pos_hpr_scale(shape_np)
        shape = panda3d.core.CollisionSphere(pos[0], pos[1], pos[2], scale[2])
        add_shape(nodepath, shape, shape_np)
    for shape_np in nodepath.find_all_matches('**/=+CollisionInvSphere'):
        pos, hpr, scale = get_pos_hpr_scale(shape_np)
        shape = panda3d.core.CollisionInvSphere(pos[0], pos[1], pos[2], scale[2])
        add_shape(nodepath, shape, shape_np)
    for shape_np in nodepath.find_all_matches('**/=+CollisionCapsule'):
        pos, hpr, scale = get_pos_hpr_scale(shape_np)
        shape = panda3d.core.CollisionCapsule(
            pos[0]-(scale[0]/2), pos[1]-(scale[1]/2), pos[2]-(scale[2]/2),
            pos[0]+(scale[0]/2), pos[1]+(scale[1]/2), pos[2]+(scale[2]/2),
            (scale[0]+scale[1])/2
        )
        add_shape(nodepath, shape, shape_np)
    for shape_np in nodepath.find_all_matches('**/=+CollisionPlane'):
        pos, hpr, scale = get_pos_hpr_scale(shape_np)
        shape = panda3d.core.CollisionPlane(pos, (0,0,1))
        add_shape(nodepath, shape, shape_np)
    for shape_np in nodepath.find_all_matches('**/=+CollisionRay'):
        pos, hpr, scale = get_pos_hpr_scale(shape_np)
        shape = panda3d.core.CollisionRay(*pos, hpr)
        add_shape(nodepath, shape, shape_np)
    for shape_np in nodepath.find_all_matches('**/=+CollisionLine'):
        pos, hpr, scale = get_pos_hpr_scale(shape_np)
        shape = panda3d.core.CollisionLine(*pos, hpr)
        add_shape(nodepath, shape, shape_np)
    for shape_np in nodepath.find_all_matches('**/=+CollisionSegment'):
        pos, hpr, scale = get_pos_hpr_scale(shape_np)
        to_pos = shape.get_pos(shape_np, scale[2])
        shape = panda3d.core.CollisionSegment(pos, to_pos)
        add_shape(nodepath, shape, shape_np)
    for shape_np in nodepath.find_all_matches('**/=+CollisionBox'):
        pos, hpr, scale = get_pos_hpr_scale(shape_np)
        shape = panda3d.core.CollisionBox(pos, *scale)
        add_shape(nodepath, shape, shape_np)
    for shape_np in nodepath.find_all_matches('**/=+CollisionPolygon'):
        geom_to_collision_polygons(shape_np, keep=False)
        shape_np.show()

def set_collisions(root):
    nodepath_to_collision_polygons(root)
    set_collision_shapes(root)

def set_lod_switches(nodepath):
    furthest = 1024
    step_size = furthest/len(nodepath.get_children())
    into, outto = furthest, furthest-step_size
    for c, child in enumerate(nodepath.get_children()):
        nodepath.node().add_switch(into, outto)
        into = outto
        outto /= 2
    furthest_out = nodepath.node().get_out(0)
    nodepath.node().set_switch(0, furthest**4, furthest_out)

def read_args(root, value_raw):
    if value_raw == "None" or value_raw == '1' or value_raw == '1.0':
        return []
    extra_args = []
    try:
        value_json = json.loads('{'+value_raw+'}')
    except json.decoder.JSONDecodeError:
        print('error, json cant decode:', value_raw)
        sys.exit(1)

    if 'extra_args' in value_json:
        if type(value_json['extra_args']) == list:
            for arg in value_json['extra_args']:
                if type(arg) == str:
                    if arg[0] == '@':
                        found = root.find(arg[1:])
                        if found:
                            arg = found
                        else:
                            print('could not find {}'.format(arg))
                            sys.exit(1)
                if type(arg) == list:
                    arg = tuple(arg)
                extra_args.append(arg)
        else:
            print('extra_args of {} is not a list'.format(tag))
            sys.exit(1)
    return extra_args

def tags_as_nodepath_function(root, nodetype=panda3d.core.NodePath('nodepath')):
    funcs = dir(nodetype)
    custom_sort = [
        'wrt_reparent_to',
        'reparent_to',
        'flatten_strong',
    ]
    custom_sort.reverse()
    for s in custom_sort:
        funcs.remove(s)
        funcs.insert(0, s)

    for func in funcs:
        tag = '${}'.format(func)
        for nodepath in root.find_all_matches("**/="+tag):
            print(' Running NodePath function:',tag, nodepath)
            value_raw = nodepath.get_tag(tag)
            extra_args = read_args(root, value_raw)
            function = getattr(nodepath, func)
            function(*extra_args)
            nodepath.clear_tag(tag)
            nodepath.clear_python_tag(tag)

def tags_as_node_function(root, nodetype=panda3d.core.PandaNode('pandanode')):
    funcs = dir(nodetype)
    funcs.sort(key=lambda s: len(s))
    for func in funcs:
        tag = '$node().{}'.format(func)
        for nodepath in root.find_all_matches("**/="+tag):
            value_raw = nodepath.get_tag(tag)
            extra_args = read_args(root, value_raw)
            function = getattr(nodepath.node(), func)
            function(*extra_args)
            nodepath.clear_tag(tag)
            nodepath.clear_python_tag(tag)

def tags_as_class(root):
    panda_nodes = [
        "PandaNode", "DataNode", "MouseRecorder", "AnalogNode", "ButtonNode", "DialNode", "TrackerNode",
        "VirtualMouse", "MouseAndKeyboard", "MouseInterfaceNode", "DriveInterface,MouseSubregion",
        "Trackball", "ButtonThrower", "MouseWatcher", "Transform2SG", "InputDeviceNode", "LightNode",
        "AmbientLight", "CallbackNode", "ComputeNode", "LensNode", "Camera", "LightLensNode",
        "DirectionalLight", "PointLight", "SphereLight", "RectangleLight", "Spotlight", "LODNode",
        "FadeLODNode", "SelectiveChildNode", "SequenceNode", "SwitchNode", "UvScrollNode", "Fog",
        "GeomNode", "ModelNode", "ModelRoot", "PlaneNode", "PolylightNode", "PortalNode", "OccluderNode",
        "TextNode", "FrameRateMeter", "SceneGraphAnalyzerMeter", "RigidBodyCombiner",
        "ShaderTerrainMesh", "AnimBundleNode", "PartBundleNode", "Character", "CollisionNode",
        "CollisionVisualizer", "ParametricCurve", "PiecewiseCurve", "NurbsCurve", "HermiteCurve",
        "CubicCurveseg", "RopeNode", "SheetNode", "PGItem", "PGButton", "PGEntry", "PGVirtualFrame",
        "PGScrollFrame", "PGSliderBar", "PGWaitBar", "PGTop"
    ]

    for panda_node in panda_nodes:
        tag = '+{}'.format(panda_node)
        for nodepath in root.find_all_matches("**/="+tag):
            print(' Turn to PandaNode:',tag, nodepath)
            value_raw = nodepath.get_tag(tag)
            extra_args = read_args(root, value_raw)
            panda_node_class = getattr(panda3d.core, panda_node)
            new_node = panda_node_class(nodepath.name)
            new_nodepath = nodepath.parent.attach_new_node(new_node)
            new_nodepath.set_transform(nodepath.get_transform())
            nodepath.clear_tag(tag)
            nodepath.clear_python_tag(tag)
            for key in nodepath.get_python_tag_keys():
                new_nodepath.set_python_tag(key, nodepath.get_python_tag(key))
            for key in nodepath.get_tag_keys():
                new_nodepath.set_tag(key, nodepath.get_tag(key))
            for child in nodepath.get_children():
                child.reparent_to(new_nodepath)
            nodepath.detach_node()
            nodepath = new_nodepath
            tags_as_node_function(root, nodetype=new_node)

            if panda_node == 'LODNode' or panda_node == 'FadeLODNode':
                set_lod_switches(nodepath)
            if panda_node == 'CollisionNode':
                set_collision_shapes(nodepath)


def evaluate_property_logic(root):
    tags_as_class(root)
    tags_as_nodepath_function(root)
    set_collisions(root)

