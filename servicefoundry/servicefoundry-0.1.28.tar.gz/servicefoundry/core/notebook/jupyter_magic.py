from IPython.core.magic import register_cell_magic

from servicefoundry.core.runner.predictor import Predictor
from servicefoundry.internal.util import create_file_from_content


class NotebookSession:
    def __init__(self):
        self.predict = None

    def set_predict(self, file_path):
        if self.predict:
            self.predict.close()
        self.predict = Predictor(file_path)

    def get_predict(self):
        return self.predict


@register_cell_magic
def sfy_load_predict(line, cell):
    global session
    try:
        create_file_from_content("predict.py", cell)
        session.set_predict("predict.py")
        print(
            "Predict script loaded successfully. "
            "Run sfy.get_predictor() to get the runner."
        )
    except ModuleNotFoundError as err:
        msg = f"Failed to register predict script. Caused by: {err}"
        print(msg)
        raise err
    return


try:
    session
except NameError:
    session = NotebookSession()

get_predict = session.get_predict
