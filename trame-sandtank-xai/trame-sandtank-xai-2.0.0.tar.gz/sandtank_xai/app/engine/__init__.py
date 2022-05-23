from .xai.ml import RegressionPressure
from .xai import get_xai_method, is_method_sensitive_to_xy, update_full_pipeline
from .xai.colors import lutPerm, lutPress

from trame.assets.remote import GoogleDriveFile

# -----------------------------------------------------------------------------
# Global values
# -----------------------------------------------------------------------------

AI_MODEL = None


BC_MODES = {
    "initial": [25, 25],
    "wet-wet": [45, 45],
    "wet-dry": [45, 5],
    "dry-wet": [5, 45],
    "dry-dry": [5, 5],
    "drew-drew": [10, 10],
}

# -----------------------------------------------------------------------------
# Engine initialization
# -----------------------------------------------------------------------------


def initialize(server):
    global AI_MODEL
    state, ctrl = server.state, server.controller

    # Init some shared state vars
    state.setdefault("path_to_model", None)
    state.update(
        {
            "steps": ["Conv 2D", "Relu", "Max Pool", "Drop-out", "Dense", "XAI"],
            # XAI methods
            "xaiPreset": "erdc_rainbow_bright",
            "xaiHover": None,
            "xaiOutputSelected": -1,
            # Weights
            "weightsInputs": None,
            "weightsOutputs": [],
            # LookupTables configurations
            "lutPerm": lutPerm,
            "lutPress": lutPress,
        }
    )

    @state.change("mode")
    def update_ai(mode, **kwargs):
        if AI_MODEL is None:
            return

        left, right = BC_MODES[mode]
        AI_MODEL.set_bc(left, right)
        state.aiInputPerm = AI_MODEL.permeability()
        state.aiInputPress = AI_MODEL.pressure()
        state.aiOutputPress = AI_MODEL.predict()
        xai()
        update_full_pipeline(state, AI_MODEL)

    @state.change("xaiHover", "mode", "xaiMethod", "step", "xaiModifier")
    def xai(**kwargs):
        ij, step = state.xaiHover, state.step
        # prev_result = app.get('xaiOutputs')
        method = get_xai_method(state)
        xy_dep = is_method_sensitive_to_xy(method)
        if xy_dep and ij:
            xy = (ij["i"], ij["j"])
            state.xaiOutputs = AI_MODEL.explain(method, xy)
        elif not xy_dep:
            # print('b')
            # if prev_result is None:
            #   print(' => in')
            state.xaiOutputs = AI_MODEL.explain(method, (-1, -1))
        else:
            state.xaiOutputs = None

        if step == 5 and ij:
            state.weightsOutputs = AI_MODEL.get_dense_weights(**ij)
        else:
            state.weightsOutputs = []

    @state.change("xaiOutputSelected")
    def update_active_weights(step, xaiOutputSelected, **kwargs):
        idx = xaiOutputSelected

        if step in [1, 2, 3]:
            state.weightsInputs = AI_MODEL.get_weights(idx)
        else:
            state.weightsInputs = None

    @ctrl.add("on_server_ready")
    def load_model(path_to_model, mode, **kwargs):
        print("xai engine initialize", path_to_model, mode)
        global AI_MODEL
        if path_to_model:
            AI_MODEL = RegressionPressure(path_to_model)
        else:
            remote_model = GoogleDriveFile(
                local_path="./refs/default-trained-model.out",
                google_id="1AL2KlhfH_ZcQJM8wWSb9pG9M_jxgcn50",
                local_base=__file__,
            )
            AI_MODEL = RegressionPressure(remote_model.path)
        update_ai(mode)
