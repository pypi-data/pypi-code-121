import re

import boto3.docs.docstring
import boto3.exceptions
import boto3.session


__func_alias__ = {"type_": "type"}


def parse(hub, session: "boto3.session.Session", service: str):
    plugins = {}

    # Create the boto client that will be parsed for capabilities
    client = session.client(
        service_name=service,
        region_name=hub.OPT.pop_create.region,
        api_version=hub.OPT.pop_create.api_version,
    )
    operations = {}
    for op in client.meta.method_to_api_mapping:
        try:
            verb, resource = op.split("_", maxsplit=1)
            if re.match(rf"\w+[^aoius]s$", resource):
                resource = hub.tool.format.inflect.singular(resource)
            if resource not in operations:
                operations[resource] = {}
            operations[resource][verb] = op
        except ValueError:
            ...

    # Get resources if we can for this object
    resources = {}
    try:
        service_resource = session.resource(
            service_name=service,
            region_name=hub.OPT.pop_create.region,
            api_version=hub.OPT.pop_create.api_version,
        )
        for sub_resource in service_resource.meta.resource_model.subresources:
            resources[hub.tool.format.case.snake(sub_resource.name)] = (
                sub_resource.name,
                [],
            )
            resources[hub.tool.format.case.snake(sub_resource.name)][1].extend(
                [
                    f"hub.tool.boto3.resource.exec(resource, {action.name}, *args, **kwargs)"
                    for action in sub_resource.resource.model.actions
                ]
            )
    except boto3.exceptions.ResourceNotExistsError:
        ...

    clean_service = hub.tool.format.keyword.unclash(service).replace("-", "_")
    if clean_service != service.replace("-", "_"):
        plugin_docstring = hub.tool.format.html.parse(
            client._service_model.documentation
        )
        plugins[f"{clean_service}.init"] = {
            "imports": [],
            "functions": {},
            "doc": "\n".join(hub.tool.format.wrap.wrap(plugin_docstring, width=120)),
            "sub_alias": [service.replace("-", "_"), clean_service],
        }

    # Create a state for everything that has a create/delete/describe function
    for resource, functions in operations.items():
        other_calls = [
            f"hub.exec.boto3.client.{clean_service}.{op}" for op in functions.values()
        ]
        get_resource_call = ""

        if not resource:
            continue
        # Get resource and describe func
        if resource not in resources:
            # Prefer using the client first
            for func_name in hub.pop_create.aws.template.DESCRIBE_FUNCTIONS:
                if func_name in functions:
                    describe_function_call = f"await hub.exec.boto3.client.{clean_service}.{functions[func_name]}(resource_id)"
                    break
            else:
                hub.log.info(
                    f"Cannot determine how to describe {clean_service}.{resource}: {list(functions.keys())}"
                )
                continue
        else:
            # If the client wasn't complete, try to use a resource
            r = resources[resource]
            get_resource_call = f'resource = hub.tool.boto3.resource.create(ctx, "{clean_service}", "{r[0]}", resource_id)'
            other_calls.append(get_resource_call)
            describe_function_call = "await hub.tool.boto3.resource.describe(resource)"
            other_calls.extend(r[1])

        # Get create function
        for func_name in hub.pop_create.aws.template.CREATE_FUNCTIONS:
            if func_name in functions:
                create_function = functions[func_name]
                break
        else:
            hub.log.info(
                f"Cannot determine how to create {clean_service}.{resource}: {list(functions.keys())}"
            )
            continue

        # Get delete function
        for func_name in hub.pop_create.aws.template.DELETE_FUNCTIONS:
            if func_name in functions:
                delete_function = functions[func_name]
                break
        else:
            hub.log.info(
                f"Cannot determine how to delete {clean_service}.{resource}: {list(functions.keys())}"
            )
            continue

        # Get list function
        for func_name in functions:
            if client.can_paginate(functions[func_name]):
                list_function = functions[func_name]
                break
        else:
            hub.log.info(
                f"Cannot determine how to describe {clean_service}.{resource}: {list(functions.keys())}"
            )
            continue

        clean_resource = hub.tool.format.keyword.unclash(resource)
        plugin_key = f"{clean_service}.{clean_resource}".replace("-", "_")
        plugins[plugin_key] = {
            "imports": [
                "import copy",
                "from typing import *",
                "__contracts__ = ['resource']",
            ],
            "functions": {},
            "doc": str(client.__doc__),
        }
        if clean_resource != resource:
            plugins[plugin_key]["virtualname"] = resource

        plugins[plugin_key]["doc"] = "\n".join(other_calls)
        shared_function_data = {
            "delete_function": f"hub.exec.boto3.client.{clean_service}.{delete_function}",
            "create_function": f"hub.exec.boto3.client.{clean_service}.{create_function}",
            "list_function": f"hub.exec.boto3.client.{clean_service}.{list_function}",
            "waiter_call": "",
            "resource_function_call": get_resource_call,
            "describe_function_call": describe_function_call,
            "list_item": "TODO",
            "resource_id": "TODOs",
            "service_name": clean_service,
            "resource": resource,
            "has_client_token": False,
            "is_idempotent": False,
            "tag_method": "TODO, unify the way resources are tagged",
        }
        for state_function, op_name in zip(
            ("present", "absent", "describe"),
            (create_function, delete_function, list_function),
        ):
            func_definition = hub.pop_create.aws.function.parse(
                client, service, op_name
            )
            func_definition["hardcoded"].update(shared_function_data)
            func_definition["hardcoded"].update(
                {
                    "has_client_token": func_definition["params"].pop(
                        "ClientToken", None
                    ),
                    "is_idempotent": func_definition["params"].pop(
                        "ClientToken", "idempotent" in func_definition["doc"].lower()
                    ),
                }
            )

            # Normalize the name parameter
            if "Name" in func_definition["params"]:
                name = func_definition["params"].pop("Name")
            elif "name" in func_definition["params"]:
                name = func_definition["params"].pop("name")
            else:
                name = hub.pop_create.aws.template.NAME_PARAMETER.copy()
                if func_definition["hardcoded"]["is_idempotent"]:
                    name["doc"] = "The name of the state"

            resource_id_parameter = (
                hub.pop_create.aws.template.RESOURCE_ID_PARAMETER.copy()
            )
            if state_function == "absent":
                # resource_id parameter is required for absent() function
                resource_id_parameter["required"] = True
            # Create a new param list the puts "name" first in the ordered dict
            func_definition["params"] = dict(
                Name=name,
                resource_id=resource_id_parameter,
                **func_definition["params"],
            )
            plugins[plugin_key]["functions"][state_function] = func_definition

        # TODO this is where stuff needs to happen
        plugins[plugin_key]["functions"]["describe"]["hardcoded"]["present_params"] = [
            {k: "TODO"} for k in plugins[plugin_key]["functions"]["present"]["params"]
        ]

    return plugins
