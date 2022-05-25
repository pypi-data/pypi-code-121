import os
import plotly.io as pio
from plotly.io._base_renderers import IFrameRenderer
from logzero import logger
from uuid import uuid4
import ipynb_path


class MyIFrameRenderer(IFrameRenderer):
    """Custom renderer for `iframe` and `iframe_connected`, in which HTML file
    names of plots are unique and thus kept forever.
    """

    def __init__(self,
                 config=None,
                 auto_play=False,
                 post_script=None,
                 animation_opts=None,
                 include_plotlyjs=True,
                 html_directory="iframe_figures"):
        super().__init__(config,
                         auto_play,
                         post_script,
                         animation_opts,
                         include_plotlyjs,
                         html_directory)

        nb_path = ipynb_path.get()
        self.root_dir, nb_name = os.path.split(nb_path)
        self.html_directory = f"{nb_name}.iframe_figures"
        abs_html_directory = f"{nb_path}.iframe_figures"
        try:
            os.makedirs(abs_html_directory)
        except OSError as error:
            if not os.path.isdir(abs_html_directory):
                raise error

    def to_mimebundle(self, fig_dict):
        from plotly.io import write_html

        # Make iframe size slightly larger than figure size to avoid
        # having iframe have its own scroll bar.
        iframe_buffer = 20
        layout = fig_dict.get("layout", {})

        if layout.get("width", False):
            iframe_width = str(layout["width"] + iframe_buffer) + "px"
        else:
            iframe_width = "100%"

        if layout.get("height", False):
            iframe_height = layout["height"] + iframe_buffer
        else:
            iframe_height = str(525 + iframe_buffer) + "px"

        # Build filename using ipython cell number
        filename = self.build_filename()

        write_html(
            fig_dict,
            filename,
            config=self.config,
            auto_play=self.auto_play,
            include_plotlyjs=self.include_plotlyjs,
            include_mathjax="cdn",
            auto_open=False,
            post_script=self.post_script,
            animation_opts=self.animation_opts,
            default_width="100%",
            default_height=525,
            validate=False,
        )

        # Build IFrame
        iframe_html = """\
<iframe
sandbox="allow-scripts allow-downloads"
scrolling="no"
width="{width}"
height="{height}"
src="{src}"
frameborder="0"
allowfullscreen
></iframe>
""".format(
            width=iframe_width,
            height=iframe_height,
            src=self.build_url()
        )

        return {"text/html": iframe_html}

    def build_filename(self):
        self.out_fname = f"{self.html_directory}/{uuid4()}.html"
        logger.debug(f"{self.out_fname}")
        # NOTE: Always make a plot at the Notebook's directory
        cwd = os.getcwd()
        rel = os.path.relpath(
            os.path.commonprefix([self.root_dir, cwd]), cwd)
        return f"{rel}/{self.out_fname}"

    def build_url(self):
        # NOTE: Path for iframe must be a relative path from the root dir
        return self.out_fname


def _set_custom_iframe_renderers() -> None:
    pio.renderers["iframe"] = MyIFrameRenderer(config=pio._renderers.config,
                                               include_plotlyjs=True)
    pio.renderers["iframe_connected"] = MyIFrameRenderer(config=pio._renderers.config,
                                                         include_plotlyjs="cdn")
