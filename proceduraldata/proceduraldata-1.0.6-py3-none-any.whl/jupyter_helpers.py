'''
Joonas Govenius, 2019-2022

Helper functions related to interacting with Jupyter.
'''

from pdata._metadata import __version__

def get_notebook_name():
  """
  Return the full path of the Jupyter notebook, if this runs within Jupyter.
  Otherwise returns None.

  From https://github.com/jupyter/notebook/issues/1000#issuecomment-359875246
  """
  import json
  import os.path
  import re
  import ipykernel
  import requests

  from requests.compat import urljoin

  from notebook.notebookapp import list_running_servers

  try:
    kernel_id = re.search('kernel-(.*).json',
                            ipykernel.connect.get_connection_file()).group(1)
  except RuntimeError:
    return None
      
  servers = list_running_servers()
  for ss in servers:
    response = requests.get(urljoin(ss['url'], 'api/sessions'),
                            params={'token': ss.get('token', '')})
    for nn in json.loads(response.text):
      if nn['kernel']['id'] == kernel_id:
        relative_path = nn['notebook']['path']
        return os.path.join(ss['notebook_dir'], relative_path)


def save_notebook():
  """
  Saves the Jupyter notebook, if this runs from Jupyter.

  Based on https://stackoverflow.com/questions/44961557/how-can-i-save-a-jupyter-notebook-ipython-notebook-programmatically?rq=1
  """
  from IPython.display import Javascript
  from IPython.core.display import display
  import time

  display(Javascript('''
    require(["base/js/namespace"],function(Jupyter) {
        Jupyter.notebook.save_checkpoint();
    });
    '''))

  # We should wait until the save has actually been completed.
  # TODO: This is not the best way...
  time.sleep(1.)
