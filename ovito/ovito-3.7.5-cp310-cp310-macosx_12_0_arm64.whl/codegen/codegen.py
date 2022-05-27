import inspect
import numpy
import collections.abc
import io
import ovito
from ovito.nonpublic import ModifierApplication, RefTarget, RenderSettings
from ovito.data import DataObject, Property, ElementType

def format_property_value(value):
    """ Produces a pretty string representation of a Python object or value. """

    # Format small NumPy arrays as Python lists.
    if isinstance(value, numpy.ndarray):
        # Linear arrays of length 4 and shorter.
        if value.ndim == 1 and len(value) <= 4:
            return repr(value.tolist())
        # Matrix arrays of shape (3,4).
        if value.shape == (3,4):
            return repr(value.tolist())

    # Make sure the fully qualified type name is being used.
    t = type(value)
    if t.__name__ != t.__qualname__:
        result = repr(value)
        if result.startswith(t.__name__):
            result = t.__qualname__ + result[len(t.__name__):]
        return result

    # Format floating-point values using a slightly reduced precision to avoid ugly rounding effects (e.g. "0.3799999999999999" instead of "0.38").
    if isinstance(value, float):
        s = "{:.12g}".format(value)
        if not '.' in s and not 'e' in s: s += '.0' # When fixed-point notation is used to format the result, make sure it always includes at least one digit past the decimal point.
        return s

    # In all other cases, fall back to standard formatting using repr() function.
    return repr(value)

def property_value_diff(stream, ref_value, value, include_vis, force_instantiation = False, prefer_oneliner = False, no_direct_assignments = False):
    """ Compares two objects or values of the same type for equality. """

    # NumPy arrays cannot be compared using the == operator. Need to use array_equal() function instead.
    if isinstance(ref_value, numpy.ndarray) and isinstance(value, numpy.ndarray):
        if not numpy.array_equal(ref_value, value) and not no_direct_assignments:
            return [" = {}".format(format_property_value(value))]
        else:
            return []

    # Implement element-wise deep comparison for list-like sequence types.
    if isinstance(ref_value, collections.abc.Sequence) and isinstance(value, collections.abc.Sequence) and not isinstance(ref_value, (tuple, str)):
        result = []
        if len(ref_value) == len(value): 
            for index, (ref_item, item) in enumerate(zip(ref_value, value)):
                for diff in property_value_diff(stream, ref_item, item, include_vis, prefer_oneliner=prefer_oneliner):
                    result.append("[{}]{}".format(index, diff)) 
        elif len(ref_value) < len(value) and isinstance(value[0], RefTarget): 
            for index, (ref_item, item) in enumerate(zip(ref_value, value[:len(ref_value)])):
                for diff in property_value_diff(stream, ref_item, item, include_vis, prefer_oneliner=prefer_oneliner):
                    result.append("[{}]{}".format(index, diff)) 
            for item in value[len(ref_value):]:
                if isinstance(item, RefTarget):
                    statements = generate_object_instantiation(stream, "obj", None, item, include_vis)
                    if isinstance(statements, str):
                        # Generate in-place modifier instantiation:
                        result.append(".append({})".format(statements))
                    else:
                        # Generate code with a temporary variable:
                        result.append("\n".join(statements) + "\n.append(obj)")
                else:
                    result.append(".append({})".format(format_property_value(item)))
        elif not no_direct_assignments:
            result.append(" = {}".format(format_property_value(value)))
        return result

    # Compare two OVITO objects based on their attributes.
    if (ref_value is None or isinstance(ref_value, RefTarget)) and (value is None or isinstance(value, RefTarget)):
        result = []
        if type(ref_value) is not type(value) or force_instantiation:
            result.append(" = {}".format(format_property_value(value)))
        if value is None:
            return result
        only_property_assignments = (len(result) == 1)
        obj_props = get_object_modified_properties(stream, ref_value, value, include_vis)
        for attr_name, attr_value in obj_props.items():
            for diff in attr_value:
                result.append(".{}{}".format(attr_name, diff))
                if not diff.startswith(" = "): only_property_assignments = False

        # If the statements are direct property value assignments, 
        # reformat it as a single constructor call.
        if only_property_assignments:
            arguments = []
            for stat in result[1:]:
                arg = stat[1:]
                if not prefer_oneliner and len(result) > 2:
                    arg = "\n    " + arg
                arguments.append(arg)
            result = [" = {}({})".format(type(value).__qualname__, ", ".join(arguments))]

        return result

    # Use built-in comparison operator otherwise.
    if ref_value != value and not no_direct_assignments:
        return [" = {}".format(format_property_value(value))]

    return []

def generate_object_instantiation(stream, variable_name, ref_obj, obj, include_vis = False, prefer_oneliner = False):
    """ Generates code that instantiates a new object and sets its parameters. """
    assert(isinstance(obj, RefTarget))

    statements = property_value_diff(stream, ref_obj, obj, include_vis, force_instantiation=True, prefer_oneliner=prefer_oneliner)
    if len(statements) == 1:
        # Generate one-liner.
        assert(statements[0].startswith(" = "))
        return statements[0][len(" = "):]
    else:
        src_lines = []
        for stat in statements:
            src_lines.append("{}{}".format(variable_name, stat))
        return src_lines

def get_object_modified_properties(stream, ref_obj, obj, include_vis = False):
    """ Builds a list of properties of the given object which were modified by the user. """ 

    attr_list = {}

    # Unless the caller has already provided it, create a default-initialized object instance of the same type as the input object.
    # It will be used to detect which object parameters were modified by the user.
    if not ref_obj:
        # This object construction may fail with a TypeError if the class does not define a public constructor (e.g. the Property class).
        try:
            ref_obj = type(obj)()
        except TypeError:
            return attr_list
        # Some objects have explicit reference values stored for certain property fields, which can be used to detect changes made by the user.
        obj._copy_initial_parameters_to_object(ref_obj)

    # Iterate over all attributes of the input object.
    for attr_name in obj.__dir__():
        # Determine if the attribute is an object property.
        attr = inspect.getattr_static(obj, attr_name)
        if isinstance(attr, property):
            
            # Skip hidden object attributes which are not documented.
            if not attr.__doc__: continue

            # Get the property value.
            value = getattr(obj, attr_name)
            # Get the corresponding value of the default-initialized reference object.
            ref_value = getattr(ref_obj, attr_name, value)

            # Skip visualization elements unless they should be included and are not disabled.
            if isinstance(value, ovito.vis.DataVis) and include_vis == False:
                continue

            # Skip data objects.
            if isinstance(value, ovito.data.DataObject):
                continue

            # Detect read-only properties. Do not generate statements that directly assign a value to a read-only property.
            is_readonly = (hasattr(attr, "fset") and attr.fset is None)

            # Add attribute to the output list if its value does not exactly match the default value.
            diff = property_value_diff(stream, ref_value, value, include_vis, no_direct_assignments = is_readonly)
            if diff:
                attr_list[attr_name] = diff

    if hasattr(obj, "__codegen__"):
        # Give all classes in the hierarchy the chance to filter or amend the generated statements.
        clazz = type(obj)
        while clazz is not RefTarget:
            if "__codegen__" in clazz.__dict__:
                literal_code = clazz.__codegen__(obj, attr_list)
                if literal_code: stream.write(literal_code)
            clazz = clazz.__bases__[0]

    return attr_list

def is_property_assignment(statement):
    """ Helper function which decides whether a code statement is a value assignment to a property field
        or rather a method call statement. """
    equal_pos = statement.find('=')
    parenthesis_pos = statement.find('(')
    return equal_pos >= 0 and (parenthesis_pos == -1 or parenthesis_pos > equal_pos)

def codegen_modifier(stream, modifier, include_vis, group):
    """ Generates code lines for setting up a modifier and its parameters. """

    # Special handling for PythonScriptModifier:
    if isinstance(modifier, ovito.modifiers.PythonScriptModifier):
        # Do not emit code if Python script modifier is disabled.
        if not modifier.enabled or (not group is None and group.enabled == False):
            stream.write("\n\n# Skipping disabled modifier '{}'".format(modifier.object_title))
            return

        # Simply output the script source code entered by the user. 
        stream.write("\n\n# User-defined modifier '{}':\n".format(modifier.object_title))
        stream.write(modifier.script)
        if not modifier.kwargs:
            stream.write("\npipeline.modifiers.append(modify)")
        else:
            # Pass the values of the user-defined parameters to the modifier function using
            # partial function parameter binding.
            stream.write("\nimport functools")
            kwargs_list = []
            for key,value in modifier.kwargs.items():
                if isinstance(value, RefTarget):
                    statements = generate_object_instantiation(stream, key, type(value)(), value, include_vis, prefer_oneliner=True)
                else:
                    statements = format_property_value(value)
                if isinstance(statements, str):
                    # Generate in-place instantiation:
                    kwargs_list.append("{} = {}".format(key, statements))
                else:
                    # Generate code with a temporary variable:
                    stream.write("\n" + "\n".join(statements))
                    kwargs_list.append("{} = {}".format(key,key))

            if len(kwargs_list) > 2:
                kwargs_list = ["\n    " + arg for arg in kwargs_list]

            stream.write("\npipeline.modifiers.append(functools.partial(modify, {}))".format(", ".join(kwargs_list)))
        return

    # Create a default-initialized modifier instance.
    # It will be used to detect which modifier parameters were modified by the user.
    default_modifier = type(modifier)()

    # Temporarily insert it into a pipeline in order to let the modifier initialize itself based on the current pipeline state.
    modapp = modifier.some_modifier_application
    if modapp:
        default_modapp = default_modifier.create_modifier_application()
        default_modapp.input = modapp.input
        default_modapp.modifier = default_modifier
        default_modifier.initialize_modifier(0, default_modapp)

    if group is None:
        stream.write("\n\n# {}:\n".format(modifier.object_title))
    else:
        stream.write("\n\n# {} - {}:\n".format(group.object_title, modifier.object_title))
    statements = generate_object_instantiation(stream, "mod", default_modifier, modifier, include_vis)
    if isinstance(statements, str):
        # Generate in-place modifier instantiation:
        modifier_statements = "pipeline.modifiers.append({})".format(statements)
    else:
        # Generate code with a temporary variable holding the modifier.
        # The modifier is first constructed and initialized, then inserted into the pipeline. 
        # The list of statements may consist of value assignments to properties of the modifier
        # and calls to methods of the modifier. We place property assignments BEFORE the 
        # insertion of the modifier into the pipeline and method calls AFTER the insertion.
        # This order is required in some cases (e.g. GenerateTrajectoryLinesModifier) so that the
        # modifier has access to the pipeline data when a method is called.
        assignments = [statement for statement in statements if is_property_assignment(statement)]
        method_calls = [statement for statement in statements if not is_property_assignment(statement)]
        all_statements = assignments + ['pipeline.modifiers.append(mod)'] + method_calls
        modifier_statements = "\n".join(all_statements)
    if not group is None and group.enabled == False:
        stream.write("# Leaving this modifier out, because its modifier group is disabled.\n")
        stream.write("if False:\n")
        # Apply correct indentation to the generated statements.
        stream.write("    " + modifier_statements.replace("\n", "\n    "))
    else:
        stream.write(modifier_statements)

def find_object_prefix_recursive(obj, needle, make_mutable = False):
    """ Recursively searches a given object in the object hierarchy of a DataCollection. """  
    if not obj or not isinstance(obj, RefTarget): return None
    if obj is needle: return ""
    for search_pass in (1, 2, 3, 4):
        for attr_name in obj.__dir__():

            # Determine if the attribute is an object property.
            attr = inspect.getattr_static(obj, attr_name)
            if isinstance(attr, property):
                
                # Skip underscore property fields.
                if attr_name.endswith("_"): continue

                # Skip hidden object attributes which are not publicy documented.
                if not attr.__doc__: continue

                try:
                    # Read the current property value (this may raise a KeyError exception).
                    value = getattr(obj, attr_name)

                    # Append '_' suffix to attribute name if property accesses a data object to be modified.
                    # Be careful not to accidentally read the value of the '_' version of the attribute, because this triggers a call to make_mutable()! 
                    if make_mutable and isinstance(value, DataObject) and (attr_name + '_') in obj.__dir__():
                        attr_name = attr_name + '_'

                    if search_pass == 1:
                        if value is needle:
                            # We have found the target in the object hierarchy.
                            return "." + attr_name
                    elif search_pass == 2:
                        if isinstance(value, RefTarget):
                            # Continue with recursive search.
                            path = find_object_prefix_recursive(value, needle, make_mutable)
                            if not path is None:
                                return "." + attr_name + path                            
                    elif search_pass == 3:
                        if isinstance(value, collections.abc.Mapping):
                            # Continue with recursive search.
                            for key in value.keys():
                                if not isinstance(key, str): continue
                                subobj = value[key]
                                if not isinstance(subobj, RefTarget):
                                    if subobj is None: continue
                                    else: break
                                path = find_object_prefix_recursive(subobj, needle, make_mutable)
                                if not path is None:
                                    if make_mutable: key += '_'
                                    return "." + attr_name + "['" + key + "']" + path
                    else:
                        if isinstance(value, collections.abc.Sequence) and not isinstance(value, str):
                            # Continue with recursive search.
                            for index in range(len(value)):
                                subobj = value[index]
                                if not isinstance(subobj, RefTarget): 
                                    if subobj is None: continue
                                    else: break
                                path = find_object_prefix_recursive(subobj, needle, make_mutable)
                                if not path is None:
            
                                    # Special handling of ElementType: Use Property.type_by_id() method.
                                    if isinstance(obj, Property) and isinstance(subobj, ElementType) and attr_name == "types": 
                                        if make_mutable:
                                            return ".type_by_id_({})".format(subobj.id) + path
                                        else:
                                            return ".type_by_id({})".format(subobj.id) + path

                                    return "." + attr_name + "[" + repr(index) + "]" + path

                except KeyError:
                    pass
    return None

def find_visual_element_prefix(pipeline, vis):
    """ Builds the hierarchical Python object expression that references the given visual element in a DataCollection. """  
    if not pipeline.source or not hasattr(pipeline.source, "data"): 
        return None
    return find_object_prefix_recursive(pipeline.source.data, vis)

def codegen_pipeline(pipeline, include_vis):
    """ Generates Python statements for setting up a data pipeline. """

    # Generate script header.
    stream = io.StringIO()
    stream.write("# Boilerplate code generated by OVITO Pro {}\n".format(ovito.version_string))
    stream.write("from ovito.io import *\n")
    stream.write("from ovito.modifiers import *\n")
    stream.write("from ovito.data import *\n")
    stream.write("from ovito.pipeline import *\n")
    if include_vis:
        stream.write("from ovito.vis import *\n")
        stream.write("from ovito.qt_compat import QtCore\n")

    # Generate call to import_file() creating the Pipeline object.
    if isinstance(pipeline.source, ovito.pipeline.FileSource):
        stream.write("\n# Data import:\n")
        # Ask the pipeline's FileSource to compile the list of arguments to be passed to the 
        # import_file() function. 
        filesource_attrs = {}
        pipeline.source.__codegen__(filesource_attrs)
        # Note: FileSource.__codegen__() would normally generate a call to the FileSource.load() method.
        # Here we just take the call argument list and use it to generate a call to import_file() instead. 
        if "load" in filesource_attrs:
            stream.write("pipeline = import_file{}".format(filesource_attrs["load"][0]))
        else:
            stream.write("pipeline = Pipeline(source = FileSource())\n") # Instantiate an empty FileSource if the external file path hasn't been set. 

        # Generate a user-defined modifier function that sets up the data objects in the input
        # data collection of the pipeline. This is needed to replay the manual changes the user has made to these objects in the GUI.
        if hasattr(pipeline.source, "data") and pipeline.source.data: 
            has_data_object_setup = False
            data = pipeline.source.data
            for dataobj in data._get_all_objects_recursive():

                dataobj_props = get_object_modified_properties(stream, None, dataobj)
                if not dataobj_props: continue

                prefix = find_object_prefix_recursive(data, dataobj, make_mutable = True)
                if prefix is None: continue

                for attr_name in sorted(dataobj_props.keys()):
                    attr_diff = dataobj_props[attr_name]
                    for diff in attr_diff:
                        if not has_data_object_setup:
                            has_data_object_setup = True
                            stream.write("\n\n# Manual modifications of the imported data objects:")
                            stream.write("\ndef modify_pipeline_input(frame: int, data: DataCollection):")
                        stream.write("\n    data{}.{}{}".format(prefix, attr_name, diff))
            if has_data_object_setup:
                stream.write("\npipeline.modifiers.append(modify_pipeline_input)")
        
    elif isinstance(pipeline.source, ovito.pipeline.PythonScriptSource):
        # Simply output the script source code entered by the user. 
        stream.write("\n# User-defined pipeline source function:\n")
        stream.write(pipeline.source.script)
        if not pipeline.source.kwargs:
            stream.write("\n# Create a data pipeline with a script-based source object:")
            stream.write("\npipeline = Pipeline(source = PythonScriptSource(function = create))")
        else:
            # Pass the values of the user-defined parameters to the script function using
            # partial function parameter binding.
            stream.write("\nimport functools")
            kwargs_list = []
            for key,value in pipeline.source.kwargs.items():
                if isinstance(value, RefTarget):
                    statements = generate_object_instantiation(stream, key, type(value)(), value, include_vis, prefer_oneliner=True)
                else:
                    statements = format_property_value(value)
                if isinstance(statements, str):
                    # Generate in-place instantiation:
                    kwargs_list.append("{} = {}".format(key, statements))
                else:
                    # Generate code with a temporary variable:
                    stream.write("\n" + "\n".join(statements)) 
                    kwargs_list.append("{} = {}".format(key,key))

            if len(kwargs_list) > 2:
                kwargs_list = ["\n    " + arg for arg in kwargs_list]

            stream.write("\n# Create a data pipeline with a script-based source object:")
            stream.write("\npipeline = Pipeline(source = PythonScriptSource(function = functools.partial(create, {}))".format(", ".join(kwargs_list)))
    else:
        stream.write("\n# The currently selected data pipeline '{}' has a data source of type {}.\n# This program version is not able to generate code for this pipeline source type.".format(pipeline.object_title, type(pipeline.source)))

    # Generate statements for setting up the visual elements of the imported data.
    if include_vis:
        has_visual_element_setup = False
        for vis in pipeline.vis_elements:
            
            prefix = find_visual_element_prefix(pipeline, vis)
            if not prefix: continue

            vis_props = get_object_modified_properties(stream, None, vis, True)
            for attr_name, attr_diff in vis_props.items():
                for diff in attr_diff:
                    if not has_visual_element_setup:
                        has_visual_element_setup = True
                        stream.write("\n\n# Visual element initialization:")
                        stream.write("\ndata = pipeline.compute() # Evaluate new pipeline to gain access to visual elements associated with the imported data objects.")
                    stream.write("\ndata{}.{}{}".format(prefix, attr_name, diff))
        if has_visual_element_setup:
            stream.write("\ndel data # Done accessing input DataCollection of pipeline.")
        stream.write("\npipeline.add_to_scene()")

    # Build list of modifier applications in the pipeline.
    modapps = []
    modapp = pipeline.data_provider
    while isinstance(modapp, ModifierApplication):
        modapps.insert(0, modapp)
        modapp = modapp.input

    # Generate statements for creating the modifiers in the pipeline.
    for modapp in modapps:
        modifier = modapp.modifier

        # Skip hidden modifier types which are not documented.
        if not modifier.__doc__: 
            stream.write("\n\n# Skipping modifier '{}'".format(modifier.object_title))
            continue

        codegen_modifier(stream, modifier, include_vis, modapp.group)

    # Generate statements for setting up the viewport and viewport layout.
    if include_vis and ovito.scene.viewports.active_vp:

        # Generate statement for creating and configuring the Viewport instance(s).
        stream.write("\n\n# Viewport setup:")
        rs = ovito.scene.render_settings
        if not rs.render_all_viewports:
            # Rendering just the active viewport.
            for stat in property_value_diff(stream, None, ovito.scene.viewports.active_vp, True, force_instantiation=True):
                stream.write("\nvp{}".format(stat))
        else:
            # Rendering a viewport layout.
            stream.write("\nviewport_layout = []")
            for vp_rect in ovito.scene.viewports.get_viewport_rectangles():
                stream.write("\n\n# Viewport \"{}\":".format(vp_rect[0].title))
                for stat in property_value_diff(stream, None, vp_rect[0], True, force_instantiation=True):
                    stream.write("\nvp{}".format(stat))
                stream.write("\nviewport_layout.append((vp, {!r}))  # [left,top,width,height]".format(vp_rect[1]))

        # Generate statement for setting up the renderer.
        statements = property_value_diff(stream, None, rs.renderer, True, force_instantiation=True)
        has_renderer = False
        if len(statements) > 1 or statements[0] != " = OpenGLRenderer()":
            has_renderer = True
            stream.write("\n\n# Renderer setup:")
            for stat in statements:
                stream.write("\nrenderer{}".format(stat))

        # Generate call to render_image() or render_anim().
        stream.write("\n\n# Rendering:\n")
        args = []
        args.append("size={!r}".format(rs.size))
        if rs.background_color != (1.0, 1.0, 1.0):
            args.append("background={!r}".format(rs.background_color))
        if has_renderer:
            args.append("renderer=renderer")
        if rs.render_all_viewports:
            args.append("layout=viewport_layout")
        if rs.range == RenderSettings.Range.CurrentFrame:
            args.insert(0, "filename={!r}".format(rs.output_filename if rs.output_filename else 'image.png'))
            if rs.generate_alpha:
                args.append("alpha=True")
            if ovito.scene.anim.current_frame != 0:
                args.append("frame={}".format(ovito.scene.anim.current_frame))
            stream.write("vp.render_image({})".format(", ".join(args)))
        else:
            args.insert(0, "filename={!r}".format(rs.output_filename if rs.output_filename else 'movie.mp4'))
            args.append("fps={!r}".format(ovito.scene.anim.frames_per_second))
            if rs.range == RenderSettings.Range.CustomInterval:
                args.append("range={!r}".format(rs.custom_range))
            if rs.every_nth_frame > 1:
                args.append("every_nth={!r}".format(rs.every_nth_frame))
            stream.write("vp.render_anim({})".format(", ".join(args)))

    src = stream.getvalue()
    stream.close()
    return src

if __name__ == "__main__":
    
    from ovito.io import *
    from ovito.modifiers import *
    from ovito.vis import *
    from ovito.pipeline import *
#    print(codegen_pipeline(ovito.scene.selected_pipeline, True))