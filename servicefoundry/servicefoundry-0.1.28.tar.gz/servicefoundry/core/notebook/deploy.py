from IPython.core.display import display
from ipywidgets import Output, widgets

from servicefoundry.core.deploy import _deploy_local
from servicefoundry.core.notebook.notebook_callback import NotebookOutputCallBack

thread = None


def deploy_local(project_folder=""):
    global thread
    output_callback = NotebookOutputCallBack()
    output_callback.start_panel()
    if thread is not None and thread.is_alive():
        output_callback.print_line("Stopping the old process.")
        thread.stop()
        thread.join()
        output_callback.print_line("Old process stopped.")

    thread = _deploy_local(project_folder, output_callback)
