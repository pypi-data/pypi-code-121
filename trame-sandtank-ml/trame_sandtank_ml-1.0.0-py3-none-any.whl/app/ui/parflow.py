from trame.widgets import vuetify, trame


def create_control_panel(ctrl):
    with vuetify.VCard(outlined=True, elevation=2, classes="ma-2"):
        with vuetify.VCardTitle(classes="py-1") as title:
            vuetify.VCheckbox(
                v_model=("show_parflow", True),
                on_icon="mdi-water",
                off_icon="mdi-water",
                classes="my-0 py-0",
                dense=True,
                hide_details=True,
            )
            title.add_child("ParFlow")
            vuetify.VSpacer()
            with vuetify.VRow(classes="flex-grow-0", align="center"):
                with vuetify.VBtn(
                    small=True,
                    classes="mx-6",
                    loading=("parflow_running", False),
                    disabled=(
                        "!parflow || parflow_running || pf_bc_left == parflow.bc[0] && pf_bc_right == parflow.bc[1]",
                    ),
                    color="success",
                    click=ctrl.parflow_run,
                ) as btn:
                    vuetify.VIcon("mdi-calculator", left=True)
                    btn.add_child("Run ParFlow")

        vuetify.VDivider(
            v_show=("show_parflow",),
        )
        with vuetify.VRow(
            classes="align-center ma-4 justify-space-between",
            v_if=("parflow", False),
            v_show=("show_parflow",),
        ):
            with vuetify.VRow(classes="align-center flex-grow-0 pa-0"):
                with vuetify.VCol(classes="flex-grow-0 pa-0"):
                    vuetify.VSlider(
                        vertical=True,
                        v_model=("pf_bc_left", 45),
                        classes="px-4",
                        min=0,
                        max=50,
                    )
                    vuetify.VRow(
                        "{{ pf_bc_left }}", classes="subtitle-1 justify-center py-2"
                    )
                with vuetify.VCol(classes="flex-grow-0 pa-0"):
                    trame.XaiHeatMap(
                        classes="elevation-5",
                        style="min-height: 150px;",
                        heatmap=("parflow.permeability",),
                        shape=("parflow.size",),
                        # color_mode=,
                        # color_range=,
                        color_preset="gist_earth",
                    )
                    vuetify.VRow(
                        "Permeability", classes="subtitle-1 justify-center pt-2"
                    )
                with vuetify.VCol(classes="flex-grow-0 pa-0"):
                    vuetify.VSlider(
                        vertical=True,
                        v_model=("pf_bc_right", 6),
                        classes="px-4",
                        min=0,
                        max=50,
                    )
                    vuetify.VRow(
                        "{{ pf_bc_right }}",
                        classes="subtitle-1 justify-center py-2",
                    )

            with vuetify.VCol(
                v_for="field, idx in ['pressure', 'saturation']",
                key="field",
                classes="flex-grow-0 pa-0 mx-2",
            ):
                trame.XaiHeatMap(
                    classes="elevation-5",
                    style="min-height: 150px;",
                    heatmap=("parflow[field]",),
                    shape=("parflow.size",),
                    color_mode="custom",
                    color_range=("parflow.ranges[field]",),
                    color_preset=(
                        "idx === 1 ? 'Spectral_lowBlue' : 'erdc_rainbow_bright'",
                    ),
                )
                vuetify.VRow(
                    "{{ field }}",
                    classes="subtitle-1 justify-center pt-2 text-capitalize",
                )
