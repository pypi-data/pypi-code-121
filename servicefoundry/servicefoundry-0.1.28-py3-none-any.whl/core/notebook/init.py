from typing import List

from ipywidgets import Box, Button, Layout, widgets

from servicefoundry.internal.clients.service_foundry_client import (
    ServiceFoundryServiceClient,
)
from servicefoundry.internal.exceptions import (
    BadRequestException,
    ConfigurationException,
)
from servicefoundry.internal.session_factory import get_session
from servicefoundry.internal.template.sf_template import SfTemplate
from servicefoundry.internal.template.template_parameters import (
    FILE_PATH,
    NUMBER,
    OPTIONS,
    STRING,
    WORKSPACE,
    TemplateParameter,
)

style = {"description_width": "350px"}


def init():
    try:
        get_session()
    except BadRequestException:
        return "Please login using login() function before using init."
    tfs_client = ServiceFoundryServiceClient.get_client()
    templates = tfs_client.get_templates_list()
    template_choices = [("Select a template.", None)]
    for t in templates:
        template_choices.append((f'{t["id"]} - {t["description"]}', t["id"]))

    items_layout = Layout(width="auto")
    items = []

    template_dropdown = widgets.Dropdown(
        options=template_choices,
        description="Template:",
        layout=items_layout,
        style=style,
    )
    items.append(template_dropdown)
    box_layout = Layout(
        display="flex", flex_flow="column", align_items="stretch", width="100%"
    )
    box = Box(children=items, layout=box_layout)
    output = widgets.Output()

    def _on_change(change):
        if (
            change["name"] is not None
            and change["name"] == "value"
            and (change["new"] != change["old"])
        ):
            template = change["new"]
            if template is not None:
                template_dropdown.disabled = True
                output.append_stdout(f"You have selected template: {template}\n")
                sf_template = SfTemplate.get_template(f"truefoundry.com/v1/{template}")
                items.extend(
                    _get_form_item(sf_template, items_layout, tfs_client, output)
                )
                box.children = items

    template_dropdown.observe(_on_change)
    return box


# Return form items with click button
def _get_form_item(sf_template: SfTemplate, layout, tfs_client, output):
    items, fetchers = _get_items(sf_template.parameters, layout, tfs_client)
    button = Button(description="Initialize", tooltip="Initialize", layout=layout)

    def on_button_clicked(_):
        try:
            parameter_values = {}
            for fetcher in fetchers:
                key, value = fetcher()
                parameter_values[key] = value
            project_folder = sf_template.generate_project(parameter_values)
            output.append_stdout(
                f"New project is initialized in directory {project_folder}.\n"
            )
            output.append_stdout(
                f"Use sfn.deploy(project_folder='{project_folder}', local=True) to run locally.\n"
            )
        except ConfigurationException as err:
            output.append_stderr(f"{err.message}\n")
            return
        button.disabled = True

    button.on_click(on_button_clicked)
    items.append(button)
    items.append(output)
    return items


def _input_fetcher(param, item):
    def fetcher():
        value = item.value
        if param.kind == NUMBER:
            if value.isnumeric():
                value = int(value)
            else:
                msg = f"Answer of {param.prompt} should be integer."
                raise ConfigurationException(msg)
        return param.id, value

    return fetcher


def _dropdown_fetcher(param, item):
    def fetcher():
        value = item.value
        return param.id, value

    return fetcher


def _get_items(parameters: List[TemplateParameter], layout, tfs_client):
    items = []
    fetchers = []
    for param in parameters:
        kind = param.kind
        if kind in [STRING, NUMBER, FILE_PATH]:
            item = widgets.Text(
                value=str(param.default),
                placeholder=str(param.default),
                description=param.prompt,
                disabled=False,
                layout=layout,
                style=style,
            )
            fetcher = _input_fetcher(param, item)

        elif kind == WORKSPACE:
            item = widgets.Dropdown(
                options=param.get_workspaces(tfs_client),
                description=param.prompt,
                layout=layout,
                style=style,
            )
            fetcher = _dropdown_fetcher(param, item)
        elif kind == OPTIONS:
            item = widgets.Dropdown(
                options=param.options,
                description=param.prompt,
                layout=layout,
                style=style,
            )
            fetcher = _dropdown_fetcher(param, item)
        else:
            raise RuntimeError(f"Unhandled template parameter kind {kind}")
        items.append(item)
        fetchers.append(fetcher)
    return items, fetchers
