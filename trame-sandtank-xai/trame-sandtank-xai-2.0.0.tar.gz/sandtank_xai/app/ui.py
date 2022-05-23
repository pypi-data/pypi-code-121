from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, html
from sandtank_xai import html as xai


def initialize(server):
    server.state.trame__title = "SandTank ML - XAI"
    with SinglePageLayout(server) as layout:
        layout.title.set_text("SandTank ML - XAI")

        with layout.icon as icon:
            icon.click = "step = ''"
            vuetify.VIcon("mdi-wizard-hat")

        with layout.toolbar:
            vuetify.VSpacer()
            vuetify.VSelect(
                v_model=("mode", "initial"),
                items=(
                    "modes",
                    [
                        {"value": "initial", "text": "Initial condition"},
                        {"value": "wet-wet", "text": "Wet"},
                        {"value": "wet-dry", "text": "Wet to Dry"},
                        {"value": "dry-wet", "text": "Dry to Wet"},
                        {"value": "dry-dry", "text": "Dry"},
                    ],
                ),
                style="width: 50px;",
                label="Scenario",
                dense=True,
                hide_details=True,
            )
            with html.Div(
                style="position: relative; width: calc(100% - 500px); height: 64px; overflow: hidden;"
            ):
                with vuetify.VStepper(
                    v_model=("step", 0),
                    style="position: absolute; width: 100%; top: 50%; transform: translateY(-50%); background-color: transparent",
                ):
                    with vuetify.VStepperHeader():
                        with vuetify.Template(v_for="label, idx in steps"):
                            vuetify.VDivider(
                                v_if=("!!idx",),
                                key=("`${idx}-div`",),
                            )
                            vuetify.VStepperStep(
                                "{{ label }}",
                                editable=True,
                                step=("idx + 1",),
                                key=("idx",),
                            )
            vuetify.VProgressLinear(
                indeterminate=True,
                absolute=True,
                bottom=True,
                active=("trame__busy",),
            )

        # Main content
        with layout.content:
            with vuetify.VContainer(
                fluid=True,
                classes="align-start",
                v_if=("aiInputPerm && step > 0",),
            ):
                with vuetify.VRow(
                    classes="ma-3", justify="space-between", align="center"
                ):
                    xai.XaiImageOverlay(
                        style="height: 225px",
                        id="perm",
                        data=("aiInputPerm", None),
                        color_map=("lutPerm | categoricalColor",),
                        overlay=("(xaiOutputs || []).length === 2 && xaiOutputs[0]",),
                        pointer_location=(
                            "(xaiModifier === '_conductance' || step > 4) && xaiHover",
                        ),
                        weights=("weightsInputs?.[0]",),
                        crop=("[xaiHover, 3]",),
                    )
                    html.Div("+", classes="title mb-8 mt-n8")
                    xai.XaiImageOverlay(
                        style="height: 225px",
                        id="press",
                        data=("aiInputPress", None),
                        color_map=("lutPress | categoricalColor",),
                        overlay=("(xaiOutputs || []).length === 2 && xaiOutputs[1]",),
                        pointer_location=(
                            "(xaiModifier === '_conductance' || step > 4) && xaiHover",
                        ),
                        weights=("weightsInputs?.[1]",),
                        crop=("[xaiHover, 3]",),
                    )
                    html.Div("=", classes="title mb-8 mt-n8")
                    xai.XaiImageOverlay(
                        style="height: 225px",
                        id="out-press",
                        data=("aiOutputPress", None),
                        color_map=("lutPress | categoricalColor",),
                        pointer_location=(
                            "(xaiModifier === '_conductance' || step > 4) && xaiHover",
                        ),
                        show_ij=True,
                        hover="(xaiModifier === '_conductance' || (step > 4)) && set('xaiHover', $event)",
                        exit="xaiHover = null",
                    )

                vuetify.VDivider(classes="mt-8")

                with vuetify.VStepper(value=("step", 0)):
                    with vuetify.VStepperItems():
                        with vuetify.VStepperContent(step="1", classes="py-0"):
                            with vuetify.VRow(
                                classes="py-4 ma-0",
                                justify="space-between",
                                align_content="center",
                            ):
                                html.Div(
                                    "Convolution 2D",
                                    classes="subtitle-1 font-weight-medium",
                                )
                                with vuetify.VBtnToggle(
                                    v_model=("xaiModifier", "_activation"),
                                    dense=True,
                                    mandatory=True,
                                ):
                                    with vuetify.VBtn(small=True, value="_conductance"):
                                        vuetify.VIcon("mdi-map-search-outline")
                                    with vuetify.VBtn(small=True, value="_activation"):
                                        vuetify.VIcon("mdi-map-outline")

                        with vuetify.VStepperContent(step="2", classes="py-0"):
                            with vuetify.VRow(
                                classes="py-4 ma-0",
                                justify="space-between",
                                align_content="center",
                            ):
                                html.Div(
                                    "Relu (Activation function)",
                                    classes="subtitle-1 font-weight-medium",
                                )
                                with vuetify.VBtnToggle(
                                    v_model=("xaiModifier", "_activation"),
                                    dense=True,
                                    mandatory=True,
                                ):
                                    with vuetify.VBtn(small=True, value="_conductance"):
                                        vuetify.VIcon("mdi-map-search-outline")
                                    with vuetify.VBtn(small=True, value="_activation"):
                                        vuetify.VIcon("mdi-map-outline")

                        with vuetify.VStepperContent(step="3", classes="py-0"):
                            with vuetify.VRow(
                                classes="py-4 ma-0",
                                justify="space-between",
                                align_content="center",
                            ):
                                html.Div(
                                    "Max Pool (Sub-sample in 2D)",
                                    classes="subtitle-1 font-weight-medium",
                                )
                                with vuetify.VBtnToggle(
                                    v_model=("xaiModifier", "_activation"),
                                    dense=True,
                                    mandatory=True,
                                ):
                                    with vuetify.VBtn(small=True, value="_conductance"):
                                        vuetify.VIcon("mdi-map-search-outline")
                                    with vuetify.VBtn(small=True, value="_activation"):
                                        vuetify.VIcon("mdi-map-outline")

                        with vuetify.VStepperContent(step="4", classes="py-0"):
                            with vuetify.VRow(
                                classes="py-4 ma-0",
                                justify="space-between",
                                align_content="center",
                            ):
                                html.Div(
                                    "Drop Out: Randomly blank-out 50% of the input to prevent memorization (Only ON during training)",
                                    classes="subtitle-1 font-weight-medium",
                                )
                                with vuetify.VBtnToggle(
                                    v_model=("xaiModifier", "_activation"),
                                    dense=True,
                                    mandatory=True,
                                ):
                                    with vuetify.VBtn(small=True, value="_conductance"):
                                        vuetify.VIcon("mdi-map-search-outline")
                                    with vuetify.VBtn(small=True, value="_activation"):
                                        vuetify.VIcon("mdi-map-outline")

                        with vuetify.VStepperContent(step="5", classes="py-0"):
                            with vuetify.VRow(
                                classes="py-4 ma-0",
                                justify="space-between",
                                align_content="center",
                            ):
                                html.Div(
                                    "Overlay weights of the Dense layer onto its input (MaxPool)",
                                    classes="subtitle-1 font-weight-medium",
                                )

                        with vuetify.VStepperContent(step="6", classes="py-0"):
                            with vuetify.VRow(
                                classes="py-4 ma-0",
                                justify="space-between",
                                align_content="center",
                            ):
                                html.Div(
                                    "Overlay output and see which part of the input trigger the selected XAI method",
                                    classes="subtitle-1 font-weight-medium",
                                )
                                vuetify.VSelect(
                                    classes="pt-0 mt-0",
                                    style="max-width: 300px;",
                                    v_model=("xaiMethod", "Saliency"),
                                    items=(
                                        "xaiMethods",
                                        [
                                            "GradientShap",
                                            "DeepLift",
                                            "IntegratedGradients",
                                            "Saliency",
                                            "SlidingWindow",
                                            "RISE",
                                        ],
                                    ),
                                    dense=True,
                                    hide_details=True,
                                )

                vuetify.VDivider(classes="mb-4")
                with vuetify.VRow(
                    v_if=("xaiOutputs", None), classes="justify-space-between mx-4 py-4"
                ):
                    with xai.XaiImageOverlay(
                        style="min-height: 250px",
                        v_for=("array, idx in xaiOutputs",),
                        key="idx",
                        id=("`opaque-xai-${xaiModifier}-${step}-${idx}`",),
                        data=("array",),
                        color_map=(
                            "[`o-xai-${xaiModifier}-${step}-${idx}`, xaiPreset, array.range] | linearColor",
                        ),
                        overlay=("weightsOutputs[idx]",),
                        pointer_location=(
                            "step === 1 && idx === xaiOutputSelected && xaiHover",
                        ),
                        show_ij=("idx === xaiOutputSelected",),
                        enter="step < 3 && set('xaiOutputSelected', idx)",
                        hover="step < 3 && set('xaiHover', $event)",
                        exit="xaiOutputSelected = -1",
                        scale=("3 * 102 / array.size[0]",),
                    ):
                        with vuetify.VRow(classes="py-1"):
                            html.Img(
                                src=(
                                    "`o-xai-${xaiModifier}-${step}-${idx}` | imageSrc",
                                ),
                                style="width: 100%; height: 15px",
                                __properties=["src"],
                            )
                        with vuetify.VRow():
                            html.Div("{{ array.range[0].toFixed(4) }}")
                            vuetify.VSpacer()
                            html.Div("{{ array.range[1].toFixed(4) }}")

            xai.XaiFullPipeline(
                v_else=True,
                # __properties=["v_else"],
                pipeline=("aiPipeline", []),
                labels=(
                    "['Inputs', 'Convolution 2D', 'Relu', 'Max Pool', 'Dense / Output']",
                ),
                click="$event && ($event < 4) && set('step', $event)",
            )

        # Footer
        # layout.footer.hide()
