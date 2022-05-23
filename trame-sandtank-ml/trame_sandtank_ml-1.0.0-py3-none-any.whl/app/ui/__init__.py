from trame.app import get_server, dev
from trame.ui.vuetify import VAppLayout
from trame.widgets import vuetify
from . import parflow, ai, xai


def _reload():
    dev.reload(parflow, ai, xai)


def initialize(server):
    state, ctrl = server.state, server.controller

    state.trame__title = "Sandtank ML"

    server.controller.on_server_reload.add(_reload)

    with VAppLayout(server) as layout:
        with vuetify.VContainer(fluid=True, classes="pa-0") as container:
            parflow.create_control_panel(ctrl)
            ai.create_control_panel(ctrl)
            xai.create_control_panel(ctrl)
