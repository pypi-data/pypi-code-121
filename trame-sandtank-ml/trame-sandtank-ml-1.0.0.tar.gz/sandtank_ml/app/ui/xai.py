from trame.widgets import vuetify, trame


def create_control_panel(ctrl):
    with vuetify.VCard(outlined=True, elevation=2, classes="ma-2"):
        with vuetify.VCardTitle(classes="py-1") as title:
            vuetify.VCheckbox(
                v_model=("show_xai", True),
                on_icon="mdi-head-snowflake-outline",
                off_icon="mdi-head-snowflake-outline",
                classes="my-0 py-0",
                dense=True,
                hide_details=True,
            )
            title.add_child("XAI")
            vuetify.VSpacer()
            with vuetify.VRow(classes="flex-grow-0", align="center"):
                with vuetify.VBtn(
                    small=True,
                    classes="mx-6",
                    loading=("xai_running", False),
                    disabled=("xai_running || !ai",),
                    color="success",
                    click=ctrl.xai_run,
                ) as btn:
                    vuetify.VIcon("mdi-calculator", left=True)
                    btn.add_child("Run XAI method")

        vuetify.VDivider(v_show="show_xai")
        with vuetify.VRow(
            classes="align-center ma-4 justify-space-between",
            v_if=("xai", False),
            v_show="show_xai",
        ):
            with vuetify.VCol(classes="flex-grow-0 pa-0 mx-2"):
                trame.XaiHeatMap(
                    style="min-height: 150px;",
                    heatmap=("xai.values",),
                    shape=("xai.size",),
                    color_mode="custom",
                    color_range=("[-1, 1]",),
                    color_preset="BuRd",
                )
                vuetify.VRow(
                    "Saliency Map",
                    classes="subtitle-1 justify-center pt-2 text-capitalize",
                )
