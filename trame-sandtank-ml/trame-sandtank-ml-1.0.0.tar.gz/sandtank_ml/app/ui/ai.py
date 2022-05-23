from trame.widgets import vuetify, trame


def create_control_panel(ctrl):
    with vuetify.VCard(outlined=True, elevation=2, classes="ma-2"):
        with vuetify.VCardTitle(classes="py-1") as title:
            vuetify.VCheckbox(
                v_model=("show_ai", True),
                on_icon="mdi-brain",
                off_icon="mdi-brain",
                classes="my-0 py-0",
                dense=True,
                hide_details=True,
            )
            title.add_child("Machine Learning")
            vuetify.VSpacer()
            with vuetify.VRow(classes="flex-grow-0", align="center"):
                with vuetify.VBtn(
                    small=True,
                    classes="mx-6",
                    loading=("ai_running", False),
                    disabled=(
                        "ai_running || (ai && pf_bc_left == ai.bc[0] && pf_bc_right == ai.bc[1])",
                    ),
                    color="success",
                    click=ctrl.ai_run,
                ) as btn:
                    vuetify.VIcon("mdi-calculator", left=True)
                    btn.add_child("Run AI model")

        vuetify.VDivider(v_show="show_ai")
        with vuetify.VRow(
            classes="align-center ma-4 justify-space-between",
            v_if=("ai", False),
            v_show="show_ai",
        ):
            with vuetify.VCol(classes="flex-grow-0 pa-0 mx-2"):
                trame.XaiHeatMap(
                    classes="elevation-5",
                    style="min-height: 150px;",
                    heatmap=("ai.input_perm",),
                    shape=("ai.size",),
                    color_mode="custom",
                    color_range=("[-1, 1]",),
                    # color_preset=,
                )
                vuetify.VRow(
                    "Input permeability",
                    classes="subtitle-1 justify-center pt-2 text-capitalize",
                )
            with vuetify.VCol(classes="flex-grow-0 pa-0 mx-2"):
                trame.XaiHeatMap(
                    classes="elevation-5",
                    style="min-height: 150px;",
                    heatmap=("ai.input_pressure",),
                    shape=("ai.size",),
                    color_mode="custom",
                    color_range=("[-1, 1]",),
                    # color_preset=,
                )
                vuetify.VRow(
                    "Input pressure",
                    classes="subtitle-1 justify-center pt-2 text-capitalize",
                )
            with vuetify.VCol(classes="flex-grow-0 pa-0 mx-2"):
                trame.XaiHeatMap(
                    classes="elevation-5",
                    style="min-height: 150px;",
                    heatmap=("ai.values",),
                    shape=("ai.size",),
                    color_mode="custom",
                    color_range=("pf_ai_range", [-1, 0]),
                    # color_preset=,
                )
                vuetify.VRow(
                    "Predicted Pressure",
                    classes="subtitle-1 justify-center pt-2 text-capitalize",
                )
