""" Visualization Insitu selection user ajax file
"""

import json
from mimetypes import guess_type

from django.http import HttpResponseBadRequest, HttpResponse
from django.template import loader

import core_explore_tree_app.components.query_ontology.api as query_ontology_api
from core_visualization_insitu_app.components.builds import api as builds_api
from core_visualization_insitu_app.components.insitu_data import api as insitu_data_api
from core_visualization_insitu_app.components.insitu_data import (
    operations as data_operations,
)
from core_visualization_insitu_app.components.layers import api as layers_api
from core_visualization_insitu_app.components.parts import api as parts_api
from core_visualization_insitu_app.components.projects import api as projects_api
from core_visualization_insitu_app.views.user.forms import (
    SelectPartDropDown,
    SelectBuildDropDown,
)


def update_selected_project(request):
    """Update selected project object and update builds, parts and layers forms according to
    project value

    Args:
        request:

    Returns:

    """
    try:
        if request.method == "GET":
            # get the active ontology
            active_ontology = query_ontology_api.get_active()

            # Get the active ontology's ID
            template_id = active_ontology.template.id

            project_name = request.GET.get("project", None)
            project = projects_api.get_project_by_name(project_name)
            projects_api.toggle_project_selection(project.name)

            # Clean Builds and Parts
            builds_api.delete_all_builds()
            parts_api.delete_all_parts()

            # Get the existing builds from the database
            builds_api.set_builds(template_id)
            builds_tuples = builds_api.get_all_builds_names()
            selected_build = builds_api.get_selected_build_name()
            select_build = SelectBuildDropDown(builds_tuples, selected_build)

            # Get the existing parts from the database
            parts_api.set_parts(template_id)
            parts_tuples = parts_api.get_all_parts_names()
            selected_part = parts_api.get_selected_part_name()
            select_part = SelectPartDropDown(parts_tuples, selected_part)

            context_params = {
                "builds": select_build,
                "parts": select_part,
            }

            template = loader.get_template(
                "core_visualization_insitu_app/user/select_insitu_forms.html"
            )
            context = {}
            context.update(request)
            context.update(context_params)

            return HttpResponse(
                json.dumps({"form": template.render(context)}),
                content_type="application/javascript",
            )

        else:
            return HttpResponse(json.dumps({}), "application/javascript")

    except Exception as e:
        return HttpResponseBadRequest(str(e), content_type="application/javascript")


def update_selected_build(request):
    """Update selected build and update parts and layers forms according to
    build value

    Returns:

    """
    try:
        if request.method == "GET":
            # get the active ontology
            active_ontology = query_ontology_api.get_active()

            # Get the active ontology's ID
            template_id = active_ontology.template.id

            # Update selected build
            build_name = request.GET.get("build", None)
            build = builds_api.get_build_by_name(build_name)
            selected_build = builds_api.toggle_build_selection(build.name)

            # Update builds form
            builds_tuples = builds_api.get_all_builds_names()
            select_build = SelectBuildDropDown(builds_tuples, selected_build.name)

            # Clean Parts
            parts_api.delete_all_parts()

            # Get the existing parts from the database
            parts_api.set_parts(template_id)
            parts_tuples = parts_api.get_all_parts_names()
            selected_part = parts_api.get_selected_part_name()
            select_part = SelectPartDropDown(parts_tuples, selected_part)

            context_params = {
                "builds": select_build,
                "parts": select_part,
            }

            template = loader.get_template(
                "core_visualization_insitu_app/user/select_insitu_forms.html"
            )
            context = {}
            context.update(request)
            context.update(context_params)

            return HttpResponse(
                json.dumps({"form": template.render(context)}),
                content_type="application/javascript",
            )

        else:
            return HttpResponse(json.dumps({}), "application/javascript")

    except Exception as e:
        return HttpResponseBadRequest(str(e), content_type="application/javascript")


def update_selected_part(request):
    """Update selected part forms

    Returns:

    """
    try:
        if request.method == "GET":
            # Update selected part
            part_name = request.GET.get("part", None)
            part = parts_api.get_part_by_name(part_name)
            selected_part = parts_api.toggle_part_selection(part.name)

            return HttpResponse(json.dumps({}), content_type="application/javascript")

        else:
            return HttpResponse(json.dumps({}), "application/javascript")

    except Exception as e:
        return HttpResponseBadRequest(str(e), content_type="application/javascript")


def update_selected_layer(request):
    """Update selected layer forms

    Returns:

    """
    try:
        layer_name = request.POST.get("layer", None)
        layer = layers_api.get_layer_by_name(layer_name)
        layers_api.toggle_layer_selection(layer.name)
        return HttpResponse(layer.name)
    except Exception as e:
        return HttpResponseBadRequest(str(e), content_type="application/javascript")


def update_data_information(request):
    """Update the data information including total layers, layer thickness and build location

    Args:
        request:

    Returns:

    """
    try:
        if request.method == "GET":
            # get the active ontology
            active_ontology = query_ontology_api.get_active()

            # Get the active ontology's ID
            template_id = active_ontology.template.id

            # Get insitu_data information
            data_information = data_operations.query_data_information(template_id)

            context_params = {
                "total_layers": data_information["total_layers"],
                "build_location": data_information["build_location"],
                "layer_thickness": data_information["layer_thickness"],
            }

            template = loader.get_template(
                "core_visualization_insitu_app/user/insitu_data_information.html"
            )
            context = {}
            context.update(request)
            context.update(context_params)

            return HttpResponse(
                json.dumps({"form": template.render(context)}),
                content_type="application/javascript",
            )

        else:
            return HttpResponse(json.dumps({}), "application/javascript")

    except Exception as e:
        return HttpResponseBadRequest(str(e), content_type="application/javascript")


def download_image(request):
    """Download the active image of a specific frame tab

    Args:
        request:

    Returns:

    """
    try:
        info_data = request.POST.get("frame_id", None)
        data_name = info_data[:-5]
        tab = int(info_data[-1])

        data_object = insitu_data_api.get_data_by_tab_name(data_name, tab)

        blob_url = data_object.active_image

        image_info = {
            "image_url": blob_url,
            "file_name": data_object.active_image.split("/")[-1],
            "extension": guess_type(data_object.active_image)[0],
        }

        return HttpResponse(json.dumps(image_info), content_type="application/json")

    except Exception as e:
        return HttpResponseBadRequest(str(e), content_type="application/javascript")


def previous_layer(request):
    """Update all tabs from a single frame to the previous layer

    Args:
        request:

    Returns:

    """
    info_data = request.POST.get("frame_id", None)

    data_name = info_data[:-5]
    tab = int(info_data[-1])

    # Layerwise, Meltpool, Build command and XCT windows have at least 1 tab. XCT has only one tab
    data_object_tab1 = insitu_data_api.get_data_by_tab_name(data_name, 1)
    data_objects = [data_object_tab1]

    # Layerwise, Meltpool, and Build command have at least 2 tabs, XCT have only one tab
    if data_name != "xray-computed-tomography":
        data_object_tab2 = insitu_data_api.get_data_by_tab_name(data_name, 2)
        data_objects.append(data_object_tab2)
        # Build command is the only frame with 3 tabs
        if data_name == "build-command":
            data_object_tab3 = insitu_data_api.get_data_by_tab_name(data_name, 3)
            data_objects.append(data_object_tab3)

    # Get the active tab
    data_object = insitu_data_api.get_data_by_tab_name(data_name, tab)

    # if data available
    if data_object.layer_number in data_object.layer_numbers:
        new_layer_number_index = (
            data_object.layer_numbers.index(data_object.layer_number) - 1
        )
        new_layer_number = data_object.layer_numbers[new_layer_number_index]
    # if no data for the current layer
    else:
        temp_layer_numbers = data_object.layer_numbers
        temp_layer_numbers.append(data_object.layer_number)
        temp_layer_numbers.sort()
        new_layer_number_index = temp_layer_numbers.index(data_object.layer_number) - 1
        new_layer_number = temp_layer_numbers[new_layer_number_index]

    layer_information = data_operations.update_layer(data_objects, new_layer_number)
    layer_information["data_name"] = data_name
    layer_information["total_tabs"] = len(data_objects)

    return HttpResponse(json.dumps(layer_information), content_type="application/json")


def access_layer_by_number(request):
    """Update all tabs from a single frame to a specific layer

    Args:
        request:

    Returns:

    """
    info_data = request.POST.get("frame_id", None)
    info_layer_number = request.POST.get("layer_number", None)

    data_name = info_data[:-5]
    tab = int(info_data[-1])

    data_objects = insitu_data_api.get_data_by_name_all_tabs(data_name)

    # Get the active tab
    data_object_active = insitu_data_api.get_data_by_tab_name(data_name, tab)

    total_layers = data_object_active.layer_numbers[-1]

    try:
        info_layer_number = int(info_layer_number)
        if (info_layer_number <= total_layers) and (info_layer_number >= 1):
            layer_information = data_operations.update_layer(
                data_objects, info_layer_number
            )
            layer_information["data_name"] = data_name
            layer_information["total_tabs"] = len(data_objects)

            return HttpResponse(
                json.dumps(layer_information), content_type="application/json"
            )

        return HttpResponse(json.dumps({}), content_type="application/json")

    except Exception as e:
        return HttpResponseBadRequest(str(e), content_type="application/javascript")


def next_layer(request):
    """Update all tabs from a single frame to the next layer

    Args:
        request:

    Returns:

    """
    info_data = request.POST.get("frame_id", None)

    data_name = info_data[:-5]
    tab = int(info_data[-1])

    # Layerwise, Meltpool, Build command and XCT windows have at least 1 tab. XCT has only one tab
    data_object_tab1 = insitu_data_api.get_data_by_tab_name(data_name, 1)
    data_objects = [data_object_tab1]

    # Layerwise, Meltpool, and Build command have at least 2 tabs, XCT have only one tab
    if data_name != "xray-computed-tomography":
        data_object_tab2 = insitu_data_api.get_data_by_tab_name(data_name, 2)
        data_objects.append(data_object_tab2)
        # Build command is the only frame with 3 tabs
        if data_name == "build-command":
            data_object_tab3 = insitu_data_api.get_data_by_tab_name(data_name, 3)
            data_objects.append(data_object_tab3)

    # Get the active tab
    data_object = insitu_data_api.get_data_by_tab_name(data_name, tab)

    # if data available
    if data_object.layer_number in data_object.layer_numbers:
        new_layer_number_index = (
            data_object.layer_numbers.index(data_object.layer_number) + 1
        )

        if new_layer_number_index > (len(data_object.layer_numbers) - 1):
            new_layer_number = data_object.layer_numbers[0]
        else:
            new_layer_number = data_object.layer_numbers[new_layer_number_index]

    # if no data for the current layer
    else:
        temp_layer_numbers = data_object.layer_numbers
        temp_layer_numbers.append(data_object.layer_number)
        temp_layer_numbers.sort()
        new_layer_number_index = temp_layer_numbers.index(data_object.layer_number) + 1

        if new_layer_number_index > (len(temp_layer_numbers) - 1):
            new_layer_number = temp_layer_numbers[0]
        else:
            new_layer_number = temp_layer_numbers[new_layer_number_index]

    layer_information = data_operations.update_layer(data_objects, new_layer_number)
    layer_information["data_name"] = data_name
    layer_information["total_tabs"] = len(data_objects)

    return HttpResponse(json.dumps(layer_information), content_type="application/json")


def get_frames(request):
    """Update all 3 frames insitu active images, layer number, title and total layers

    Args:
        request:

    Returns:

    """
    project = projects_api.get_selected_project_name()
    build = builds_api.get_selected_build_name()
    part = parts_api.get_selected_part_name()

    insitu_objects = insitu_data_api.reset_default_data(project, build, part)
    layer_information = {}

    for insitu_object in insitu_objects:
        data_id = insitu_object.data_name.replace("-", "_")
        window_title = insitu_data_api.get_title(
            insitu_object.images, insitu_object.layer_numbers
        )
        if "xray_computed_tomography" in data_id:
            layer_information[
                data_id + "_title_tab" + str(insitu_object.tab)
            ] = window_title.replace("layer", "slice")
        else:
            layer_information[
                data_id + "_title_tab" + str(insitu_object.tab)
            ] = window_title
        layer_information[
            data_id + "_image_tab" + str(insitu_object.tab)
        ] = insitu_object.active_image
        layer_information[data_id + "_layer"] = insitu_object.layer_number
        layer_information[data_id + "_total_layers"] = insitu_object.layer_numbers[-1]

    return HttpResponse(json.dumps(layer_information), content_type="application/json")


def update_3d_visualization(request):
    """Return the STL document info as a dict

    Args:
        request:

    Returns:

    """
    # get the active ontology
    active_ontology = query_ontology_api.get_active()

    # Get the active ontology's ID
    template_id = active_ontology.template.id

    blob_dict = data_operations.query_stl_document(template_id)

    return HttpResponse(json.dumps(blob_dict), content_type="application/json")
