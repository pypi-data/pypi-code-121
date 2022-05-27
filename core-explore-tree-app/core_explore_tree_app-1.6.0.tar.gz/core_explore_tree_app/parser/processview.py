""" process view
"""
from bson.objectid import ObjectId
from mongoengine.base import BaseList

import core_explore_tree_app.components.data.query as query_api
from core_explore_tree_app.components.navigation.operations import (
    get_navigation_node_by_name,
)
from core_explore_tree_app.utils.xml.projection import get_projection
from core_main_app.components.data.models import Data

my_list = []
my_dict = {}
i = 0
ids_docs_to_query = []
ids_docs_to_querys = []


def retrieve_data_in_path(xml_data_object, data_path):
    """

    Args
        xml_data_object:
        data_path:
    Return:
    """
    data_path_list = data_path.split(".")

    if "dict_content" in data_path_list:
        data_path_list.remove("dict_content")

    xml_data_subobject = xml_data_object

    for data_path_item in data_path_list:
        xml_data_subobject = xml_data_subobject.get(data_path_item)

        if xml_data_subobject is None:
            return None

    return xml_data_subobject


def process_array_type(xml_data_object, json_view_data):
    """Process elements stored in an array

    Args:
        xml_data_object:
        json_view_data:
    Return:
    """
    # Convert path into list and retrieve the array
    xml_data_array = retrieve_data_in_path(xml_data_object, json_view_data["path"])
    data_list = []

    # Conversion to list if there is only one item in it
    if type(xml_data_array) != BaseList:
        xml_data_array = [xml_data_array]

    for xml_data_item in xml_data_array:
        data_list_item = {"name": json_view_data["name"], "items": []}

        for json_view_item in json_view_data["items"]:
            data_list_item_content = {
                "name": json_view_item["name"],
                "value": str(
                    retrieve_data_in_path(xml_data_item, json_view_item["path"])
                ),
            }

            if "is_title_param" in json_view_item:
                data_list_item["name"] = data_list_item["name"].replace(
                    data_list_item_content["name"], data_list_item_content["value"]
                )
            else:
                data_list_item["items"].append(data_list_item_content)

        data_list.append(data_list_item)

    return data_list


def processview(navigation_root_id, document_id, json_content):
    """
    # Function Name: processview(document_id,json_content)
    # Inputs:        document_id - Document ID
    #                json_content - name/path combinations to query
    # Outputs:       Query results page
    # Exceptions:    None
    # Description:   Processes view name/path combination and outputs name/value stored in MongoDB based on document_id

    Parameters:
        navigation_root_id:
        document_id:
        json_content:

    Returns:

    """
    object1 = Data.get_by_id(document_id).dict_content
    tempobject1 = object1

    pviewoutlist = []
    if object1 is None:
        # FIXME error case not working if data is arrayType
        for item in json_content:
            pviewdict = {"name": item["name"], "error": item["path"]}

            pviewoutlist.append(pviewdict)
    else:
        for item in json_content:
            if "type" in item and item["type"] == "array":
                pviewoutlist.append({"items": process_array_type(object1, item)})
            else:
                pathflag = True
                pviewname = item["name"]
                path = item["path"]
                pviewdict = {}
                pathstring = path.split(".")

                if "dict_content" in pathstring:
                    pathstring.remove("dict_content")

                for pstringitem in pathstring:
                    tempobject1 = tempobject1.get(pstringitem)

                    if tempobject1 is None:
                        pathflag = False
                        pviewdict["name"] = pviewname
                        pviewdict["error"] = path

                        my_dict[pviewname] = path
                        my_list.append(my_dict)

                        pviewoutlist.append(pviewdict)
                        break

                if pathflag:
                    pviewdict["name"] = pviewname
                    pviewdict["value"] = tempobject1

                    my_dict[pviewname] = tempobject1

                    if "link" in item:
                        linked_node = get_navigation_node_by_name(
                            navigation_root_id, item["link"]
                        )

                        if linked_node is None:
                            pviewdict["link"] = "error"
                            my_dict["link"] = "error"
                        else:
                            pviewdict["link"] = "%s %s" % (
                                str(linked_node.pk),
                                document_id,
                            )
                            my_dict["link"] = pviewdict["link"]
                    pviewoutlist.append(pviewdict)
                    global i
                    if i == 0:
                        my_list.append(my_dict)
                        i += 1
                    else:
                        for l in my_list:
                            if l != my_dict:
                                my_list.append(my_dict)

                tempobject1 = object1

    return pviewoutlist


def processviewdocidlist(navigation_root_id, document_id, json_content):
    """Processes multiple document_id values using the same json_content view name/path combination and outputs
    name/value stored in MongoDB based on document_id

    Args:
        navigation_root_id:
        document_id:
        json_content:

    Returns:

    """
    totalpviewoutlist = []
    for docid in document_id:
        pviewoutlist = processview(navigation_root_id, docid, json_content)
        totalpviewoutlist.append(pviewoutlist)
    return totalpviewoutlist


def process_cross_query(navigation_root_id, document_id, query, json_content):
    """

    Args:
        navigation_root_id:
        document_id:
        query:
        json_content:
    Return:
    """
    doc_query = {"_id": ObjectId(document_id)}
    doc_projection = {list(query.values())[0]: 1}

    document_list = Data.execute_query(doc_query, []).only(
        list(doc_projection.keys())[0]
    )
    document_projection_value = get_projection(document_list[0])

    cross_query = {list(query.keys())[0]: document_projection_value}
    cross_projection = {"id": 1}

    cross_documents = Data.execute_query(cross_query, []).only(
        list(cross_projection.keys())[0]
    )

    cross_documents_ids = [get_projection(cross_doc) for cross_doc in cross_documents]

    # Gives the crossed documents and their id
    global ids_docs_to_querys
    ids_docs_to_querys = cross_documents_ids

    # FIXME won't work for the case where we need several item from a same document
    cross_document_data = processviewdocidlist(
        navigation_root_id, cross_documents_ids, json_content
    )

    return [content for contents in cross_document_data for content in contents]
