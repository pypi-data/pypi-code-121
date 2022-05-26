from servicefoundry.core.notebook.notebook_util import is_notebook
from servicefoundry.internal.predictor import Predictor

from .component import Service, Webapp
from .deploy import deploy, deploy_local
from .login import login
from .logout import logout

load_predictor = Predictor.load_predictor

if is_notebook():
    try:
        import ipywidgets
    except ImportError:
        print("Run `pip install ipywidgets` to use notebook features.")
    from servicefoundry.core.notebook.init import init
    from servicefoundry.core.notebook.jupyter_magic import get_predict
