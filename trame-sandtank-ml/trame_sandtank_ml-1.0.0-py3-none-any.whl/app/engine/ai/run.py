from trame.assets.remote import GoogleDriveFile
from .ml import load_ml_model

MODEL = None
MODEL_FILE = GoogleDriveFile(
    local_path="./refs/trained-model",
    google_id="1AL2KlhfH_ZcQJM8wWSb9pG9M_jxgcn50",
    local_base=__file__,
)


def get_model():
    global MODEL
    if MODEL is None:
        MODEL = load_ml_model("RegressionPressure", MODEL_FILE.path)

    return MODEL


def ai_run(left=25, right=25):
    model = get_model()
    model.set_bc(left, right)
    return {**model.predict(), "bc": (left, right)}
