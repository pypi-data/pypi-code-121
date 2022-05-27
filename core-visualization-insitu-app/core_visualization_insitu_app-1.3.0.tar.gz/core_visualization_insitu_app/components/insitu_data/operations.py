"""
InSituData objects operations
"""
import json

import core_explore_tree_app.components.data.query as query_database_api
import core_explore_tree_app.components.query_ontology.api as query_ontology_api
from core_visualization_insitu_app.components.builds import api as builds_api
from core_visualization_insitu_app.components.insitu_data import api as insitu_data_api
from core_visualization_insitu_app.components.parts import api as parts_api
from core_visualization_insitu_app.components.projects import api as projects_api
from core_visualization_insitu_app.utils import dict as utils


def query_data_information(template_id):
    """Query part size from the current selection and return the value

    Args:
        template_id:

    Returns:

    """
    # Get selected build and part for filters
    build = builds_api.get_selected_build_name()
    part_name = parts_api.get_selected_part_name()
    part_id = parts_api.get_selected_part_id()

    # Instantiate storage dict
    data_information = {}

    # Build location
    build_location_path = "dict_content.amBuildDB.amBuild.parts.part.buildLocation"
    query_filter = {"dict_content.amBuildDB.amBuild.parts.part.partName": part_name}
    query_result = query_data(
        build_location_path, query_filter, template_id, is_list=True
    )
    if query_result:
        list_result = utils.get_list_inside_dict(build_location_path, query_result)
        if list_result:
            parsed_result = parse_dict_result(list_result, "buildLocation", part_id)
        else:
            parsed_result = "Unknown"
    else:
        parsed_result = "Unknown"
    data_information["build_location"] = parsed_result

    # Layer thickness
    layer_thickness_path = (
        "dict_content.amBuildDB.amBuild.amProcesses.inProcess.amProcessPlans.amProcessPlan."
        "AMMTProcessPlan.buildSetting.layerThickness"
    )
    query_filter = {"dict_content.amBuildDB.amBuild.generalInfo.buildID": build}
    query_result = query_data(layer_thickness_path, query_filter, template_id)
    if query_result:
        list_result = utils.get_list_inside_dict(layer_thickness_path, query_result)
        if list_result:
            parsed_result = utils.get_dict_path_value_data(
                list_result[0], "layerThickness"
            )
        else:
            parsed_result = "Unknown"
    else:
        parsed_result = "Unknown"

    if parsed_result == "Unknown":
        # Different path for same infos (thanks schema...)
        layer_thickness_path = "dict_content.amBuildDB.amBuild.amProcesses.inProcess.amProcessPlans.amProcessPlan.DeltaProcessPlan.buildSetting.layerThickness"
        query_filter = {"dict_content.amBuildDB.amBuild.generalInfo.buildID": build}
        query_result = query_data(layer_thickness_path, query_filter, template_id)
        if query_result:
            list_result = utils.get_list_inside_dict(layer_thickness_path, query_result)
            if list_result:
                parsed_result = utils.get_dict_path_value_data(
                    list_result[0], "layerThickness"
                )
            else:
                parsed_result = "Unknown"
        else:
            parsed_result = "Unknown"
    data_information["layer_thickness"] = parsed_result

    # Total layers
    layer_thickness = data_information["layer_thickness"]
    if layer_thickness != "Unknown":
        start_height_path = "dict_content.amBuildDB.amBuild.amProcesses.inProcess.amProcessPlans.amProcessPlan.DeltaProcessPlan.buildSetting.startHeight"
        final_height_path = "dict_content.amBuildDB.amBuild.amProcesses.inProcess.amProcessPlans.amProcessPlan.DeltaProcessPlan.buildSetting.finalHeight"
        query_filter = {"dict_content.amBuildDB.amBuild.generalInfo.buildID": build}
        start_height_parsed_result, final_height_parsed_result = calculate_height(
            start_height_path, final_height_path, query_filter, template_id
        )

        # Different path for same infos (thanks schema...)
        if (start_height_parsed_result == "Unknown") and (
            final_height_parsed_result == "Unknown"
        ):
            start_height_path = "dict_content.amBuildDB.amBuild.amProcesses.inProcess.amProcessPlans.amProcessPlan.AMMTProcessPlan.buildSetting.startHeight"
            final_height_path = "dict_content.amBuildDB.amBuild.amProcesses.inProcess.amProcessPlans.amProcessPlan.AMMTProcessPlan.buildSetting.finalHeight"
            start_height_parsed_result, final_height_parsed_result = calculate_height(
                start_height_path, final_height_path, query_filter, template_id
            )

        if (
            (start_height_parsed_result != "Unknown")
            and (final_height_parsed_result != "Unknown")
            and (float(layer_thickness) != 0)
        ):
            total_layers = int(
                (float(final_height_parsed_result) - float(start_height_parsed_result))
                / float(layer_thickness)
            )
        else:
            total_layers = "Unknown"
    else:
        total_layers = "Unknown"

    data_information["total_layers"] = total_layers

    return data_information


def query_data(path, query_filter, template_id, is_list=False):
    """

    Args:
        path:
        query_filter:
        template_id:
        is_list:

    Returns:

    """
    projection = {path: 1}
    data_info = ""

    results = query_database_api.execute_query(
        template_id, [json.dumps(query_filter)], json.dumps(projection)
    )

    if not results:
        return data_info

    return results[0].dict_content


def calculate_height(start_height_path, final_height_path, query_filter, template_id):
    """

    Args:
        start_height_path:
        final_height_path:
        query_filter:
        template_id:

    Returns:

    """
    start_height_query_result = query_data(start_height_path, query_filter, template_id)
    if start_height_query_result:
        list_result = utils.get_list_inside_dict(
            start_height_path, start_height_query_result
        )
        if list_result:
            start_height_parsed_result = utils.get_dict_path_value_data(
                list_result[0], "startHeight"
            )
        else:
            start_height_parsed_result = "Unknown"
    else:
        start_height_parsed_result = "Unknown"

    final_height_query_result = query_data(final_height_path, query_filter, template_id)
    if final_height_query_result:
        list_result = utils.get_list_inside_dict(
            final_height_path, final_height_query_result
        )
        if list_result:
            final_height_parsed_result = utils.get_dict_path_value_data(
                list_result[0], "finalHeight"
            )
        else:
            final_height_parsed_result = "Unknown"
    else:
        final_height_parsed_result = "Unknown"

    return start_height_parsed_result, final_height_parsed_result


def parse_dict_result(list_result, dict_key, part_id="part 1"):
    """

    Args:
        list_result: [{dict_key: {'name1':'value1', 'name2': 'value2', etc.}}]
        dict_key:
        part_id:

    Returns: 'name1: value1, name2: value2, etc.'

    """
    part_number = part_id[5:]  # 'Part_number' or 'Part number' become 'number'
    part_number = int(part_number) - 1  # Minus 1 to get the index
    data_dict = list_result[part_number][dict_key]
    data_info = ""

    for k, v in data_dict.items():
        data_info += str(k) + ": " + str(v) + ", "
    data_info = data_info[:-2]

    if not data_info:
        data_info = "Unknown"

    return data_info


def update_layer(data_objects, new_layer_number):
    """

    Args:
        data_objects: List of insitu data objects
        new_layer_number: int

    Returns:

    """
    title = []
    active_images = []
    tab = []

    # if a layer hasn't data, this is the image displayed
    no_data = "/static/core_visualization_insitu_app/user/img/no_data_layer.jpg"

    for data_object in data_objects:
        # check before if layer_number in layer_numbers, otherwise put no data
        if new_layer_number in data_object.layer_numbers:
            title.append(
                insitu_data_api.get_title(
                    data_object.images,
                    data_object.layer_numbers,
                    layer_number=new_layer_number,
                )
            )
            # images and layer_numbers list match: index image matches with index layer number and so on..
            # so we get layer_number index to know the images_index
            images_index = data_object.layer_numbers.index(new_layer_number)
            active_images.append(data_object.images[images_index])
        else:
            title.append("No data available for this layer")
            active_images.append(no_data)

        tab.append(data_object.tab)
        insitu_data_api.update_data(
            data_object.data_name, tab[-1], new_layer_number, active_images[-1]
        )

    # Same total layers for every tab of the same data_name
    # last layer_numbers element is the last layer
    total_layers = data_objects[0].layer_numbers[-1]

    layer_information = {
        "title": title,
        "image": active_images,
        "layer_number": new_layer_number,
        "total_layers": total_layers,
        "tab": tab,
    }

    return layer_information


def query_images(data_name, tab, template_id, project, build, part):
    """Query all images (all layers) for a single tab from a single frame for a given combination project, build and part

    Args:
        data_name:
        tab:
        template_id:
        project:
        build:
        part:

    Returns:

    """

    # Set the final results
    layers_number = []
    layers_uri = []
    index = 0

    # Instantiate right tab from right frame
    if data_name == "build-command":
        query_name = "BCLayerDataSet"
        zip_name = "dataSetInZip"
        tabs_code = ["PAT", "PWR", "DEN"]

    elif data_name == "melt-pool":
        query_name = "MPMLayerDataSet"
        zip_name = "dataSetInZip"
        tabs_code = ["MPV", "MPA"]

    elif data_name == "layer-wise":
        query_name = "layerWiseDataSet"
        zip_name = "imageSetInZip"
        tabs_code = ["LPV", "LEV"]

    elif data_name == "xray-computed-tomography":
        query_name = "XCTStackImage"
        zip_name = "imageSetInZip"
        tabs_code = ["XCTC"]

    # Query the images
    query_name_path = (
        "dict_content.amMonitoringDataSetDB.inSItuMonitoringItem.dataSet."
        + query_name
        + "."
        + zip_name
        + ".name"
    )
    query_uri_path = (
        "dict_content.amMonitoringDataSetDB.inSItuMonitoringItem.dataSet."
        + query_name
        + "."
        + zip_name
        + ".zipFileLocation.databaseURI"
    )
    build_query_filter = {
        "dict_content.amMonitoringDataSetDB.inSItuMonitoringItem.buildID": build
    }
    part_query_filter = {
        "dict_content.amMonitoringDataSetDB.inSItuMonitoringItem.partID": part
    }
    name_projection = {query_name_path: 1}
    uri_projection = {query_uri_path: 1}

    try:
        blobs_name_results = query_database_api.execute_query(
            template_id,
            [json.dumps(build_query_filter), json.dumps(part_query_filter)],
            json.dumps(name_projection),
        )
    except:
        blobs_name_results = None

    if len(blobs_name_results) > 0:

        for blob_name in blobs_name_results:
            blob_list = utils.get_dict_path_value_data(
                blob_name.dict_content,
                "dict_content.amMonitoringDataSetDB.inSItuMonitoringItem.dataSet."
                + query_name,
            )
            if isinstance(blob_list, list):
                break

        if isinstance(blob_list, list):
            blobs_name = []

            for blob in blob_list:
                blob_name = blob[zip_name]["name"]
                blobs_name.append(blob_name)

            blobs_uri_results = query_database_api.execute_query(
                template_id,
                [json.dumps(build_query_filter), json.dumps(part_query_filter)],
                json.dumps(uri_projection),
            )
            for blob_uri in blobs_uri_results:
                blob_list = utils.get_list_inside_dict(
                    "dict_content.amMonitoringDataSetDB.inSItuMonitoringItem.dataSet."
                    + query_name,
                    blob_uri.dict_content,
                )

                if isinstance(blob_list, list):
                    # Don't confuse the unique zip file (same query) with the multiples images
                    blob_length = len(blob_list[0][query_name])
                    if blob_length > 1:
                        if blob_length > 2:
                            break
                        else:
                            break

            blob_list = blob_list[0][query_name]
            if isinstance(blob_list, list):
                blobs_uri = []
                for blob in blob_list:
                    blob_name = blob[zip_name]["zipFileLocation"]["databaseURI"]
                    # Handle fake urls and put no data image instead
                    if query_name == "BCLayerDataSet":
                        blobs_uri.append(blob_name)
                    else:
                        blob_name_copy = blob_name.split("/")[-2]
                        if "_" not in blob_name_copy:  # fake url is AXXXX_PartY
                            blobs_uri.append(blob_name)
                        else:  # Real one looks like 5e3d7b61a90d0c31f82a0636
                            blobs_uri.append(
                                "/static/core_visualization_insitu_app/user/img/no_data_layer.jpg"
                            )  # No data image

            if tab == 1:
                for blob_name in blobs_name:
                    if tabs_code[0] + "_" in blob_name:
                        layers_number.append(
                            int(blob_name.split("_")[-1][5:])
                        )  # Parse PAT_PartXXXX_LayerXXXX to XXXX the layer number
                        layers_uri.append(blobs_uri[index])
                    index += 1

            if tab == 2:
                for blob_name in blobs_name:
                    if tabs_code[1] + "_" in blob_name:
                        layers_number.append(int(blob_name.split("_")[-1][5:]))
                        layers_uri.append(blobs_uri[index])
                    index += 1

            if tab == 3:
                for blob_name in blobs_name:
                    if tabs_code[2] + "_" in blob_name:
                        layers_number.append(int(blob_name.split("_")[-1][5:]))
                        layers_uri.append(blobs_uri[index])
                    index += 1

    images_data = {
        "images": layers_uri,
        "layers": layers_number,
    }

    return images_data


def query_stl_document(template_id):
    """Query the DB to get the STL document (under a URI) related to the selected project in order to display it in 3D

    Args:
        template_id:

    Returns: Dict with the URI and Filename if there is an existing STL for the project, an empty dict otherwise

    """
    project = projects_api.get_selected_project_name()
    file_location_path = "dict_content.amDesignDB.amDesign.part.digitalModel.tesselation.tesselatedModel.fileLocation"
    file_name_path = "dict_content.amDesignDB.amDesign.part.digitalModel.tesselation.tesselatedModel.fileName"

    query_filter = {"dict_content.amDesignDB.amDesign.projectID": project}
    query_result = query_data(
        file_location_path, query_filter, template_id, is_list=True
    )
    file_location_uri = utils.get_dict_path_value_data(query_result, file_location_path)
    if file_location_uri != "Unknown":
        file_id = file_location_uri.split("/")[-2]
    else:
        file_id = None

    query_result = query_data(file_name_path, query_filter, template_id, is_list=True)
    file_name = utils.get_dict_path_value_data(query_result, file_name_path)

    file_info = {}

    if file_id is not None:
        file_info["file_location_uri"] = file_location_uri
        file_info["file_name"] = file_name

    return file_info


def load_frames(project, build, part):
    """Create insitu_data objects when data are loaded (admin part or daily update). When reaching the user interface,
    no object has to be created and very few queries are needed. The objects created through this process are
    simply retrieved

    Args:
        project:
        build:
        part:

    Returns:

    """
    # get the active ontology
    active_ontology = query_ontology_api.get_active()

    # Get the active ontology's ID
    template_id = active_ontology.template.id

    # Create insitu_data objects
    data = {
        "build-command": [1, 2, 3],
        "melt-pool": [1, 2],
        "layer-wise": [1, 2],
        "xray-computed-tomography": [1],
    }

    for data_name in data.keys():
        for tab in data[data_name]:
            images_data = query_images(
                data_name, tab, template_id, project, build, part
            )
            images = images_data["images"]
            layers = images_data["layers"]
            data_object = insitu_data_api.create_data(
                project, build, part, data_name, tab, images, layers
            )
