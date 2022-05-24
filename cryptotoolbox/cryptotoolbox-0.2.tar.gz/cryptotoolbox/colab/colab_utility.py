from __future__ import print_function

def init_napoleon_colab():
    import os
    stream = os.popen('pip install dropbox')
    output = stream.read()
    print(output)

    stream = os.popen('pip install plotly==4.7.1')
    output = stream.read()
    print(output)

    stream = os.popen('pip install dash == 1.13.3')
    output = stream.read()
    print(output)

    from napoleontoolbox.signal import signal_utility
    from napoleontoolbox.analyzer import minutely_market, hourly_market, market
    from datetime import datetime
    import pandas as pd

    from ipywidgets import interact, interactive, fixed, interact_manual
    import ipywidgets as widgets
    from napoleontoolbox.utility import metrics

    from pathlib import Path

    import matplotlib.pyplot as plt


    import plotly.offline as py
    py.init_notebook_mode(connected=True)
    import plotly.graph_objs as go
    import plotly
    from plotly.offline import iplot



    def configure_plotly_browser_state():
      import IPython
      display(IPython.core.display.HTML('''
            <script src="/static/components/requirejs/require.js"></script>
            <script>
              requirejs.config({
                paths: {
                  base: '/static/base',
                  plotly: 'https://cdn.plot.ly/plotly-latest.min.js?noext',
                },
              });
            </script>
            '''))
    import IPython

    configure_plotly_browser_state()
    IPython.get_ipython().events.register('pre_run_cell', configure_plotly_browser_state)


