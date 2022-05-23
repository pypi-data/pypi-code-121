def get_xai_method(state):
    step = state.step
    method = state.xaiMethod
    xaiModifier = state.xaiModifier

    if step in [2, 3, 4] and xaiModifier == "_activation":
        state.xaiPreset = "X Ray"
    elif step == 5:
        state.xaiPreset = "X Ray"
    else:
        state.xaiPreset = "erdc_rainbow_bright"

    if step == 1:
        return f"conv2d{xaiModifier}"
    if step == 2:
        return f"relu{xaiModifier}"
    if step == 3:
        return f"maxpool{xaiModifier}"
    if step == 4:
        return f"dropout{xaiModifier}"
    if step == 5:
        return f"maxpool_activation"

    return method


def is_method_sensitive_to_xy(method):
    if method in [
        "conv2d_activation",
        "relu_activation",
        "maxpool_activation",
        "dropout_activation",
    ]:
        return False
    return True


def add_color(array, lutType, parameters):
    array.update(
        {
            "lutType": lutType,
            "lutOptions": parameters,
        }
    )

    return array


def add_colors(arrays, preset):
    for array in arrays:
        array.update(
            {
                "lutType": "linearColor",
                "lutPreset": preset,
            }
        )
    return arrays


def update_full_pipeline(state, ai_model):
    pipeline = []

    # input
    pipeline.append(
        [
            add_color(ai_model.permeability(), "categoricalColor", state.lutPerm),
            add_color(ai_model.pressure(), "categoricalColor", state.lutPress),
        ]
    )

    # conv2d
    pipeline.append(
        add_colors(
            ai_model.explain("conv2d_activation", (-1, -1)), "erdc_rainbow_bright"
        )
    )

    # relu
    pipeline.append(add_colors(ai_model.explain("relu_activation", (-1, -1)), "X Ray"))

    # maxpool
    pipeline.append(
        add_colors(ai_model.explain("maxpool_activation", (-1, -1)), "X Ray")
    )

    # dense output
    pipeline.append([add_color(ai_model.predict(), "categoricalColor", state.lutPress)])

    state.aiPipeline = pipeline
