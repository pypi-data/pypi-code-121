try:
    import IPython
except ModuleNotFoundError:
    IPython = None

try:
    import pandas as pd
except ModuleNotFoundError:
    pandas = None


def display_dataframe_as_html(df: "pd.DataFrame"):
    """Display mardown"""
    if not IPython:
        return

    # Needs to import here because IPython is optional.
    from IPython.display import HTML
    from IPython.display import display
    display(HTML(df.to_html(escape=False)))


def display_markdown(text: str, **kwargs):
    """Display mardowns"""
    if not IPython:
        return
    # Needs to import here because IPython is optional.
    from IPython.display import Markdown
    from IPython.display import display
    display(Markdown(text.format(**kwargs)))


def display_html(text: str, **kwargs):
    """Display html"""
    if not IPython:
        return
    # Needs to import here because IPython is optional.
    from IPython.display import HTML
    from IPython.display import display
    display(HTML(text.format(**kwargs)))
