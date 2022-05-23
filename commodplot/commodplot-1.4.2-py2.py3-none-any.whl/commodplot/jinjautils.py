import base64
import logging
import os
from datetime import datetime

import plotly as pl
from jinja2 import PackageLoader, FileSystemLoader, Environment
from plotly import graph_objects as go

# margin to use in HTML charts - make charts bigger but leave space for title
narrow_margin = {"l": 2, "r": 2, "t": 30, "b": 10}


def convert_dict_plotly_fig_png(d):
    """
    Given a dict (that might be passed to jinja), convert all plotly figures png
    """
    for k, v in d.items():
        if isinstance(d[k], go.Figure):
            d[k] = plpng(d[k])
        if isinstance(d[k], dict):
            convert_dict_plotly_fig_png(d[k])

    return d


def plpng(fig):
    """
    Given a plotly figure, return it as a png
    """
    image = base64.b64encode(pl.io.to_image(fig)).decode("ascii")
    res = f'<img src="data:image/png;base64,{image}">'
    return res


def convert_dict_plotly_fig_html_div(d):
    """
    Given a dict (that might be passed to jinja), convert all plotly figures of html divs
    """
    for k, v in d.items():
        if isinstance(d[k], go.Figure):
            d[k] = plhtml(d[k])
        if isinstance(d[k], dict):
            convert_dict_plotly_fig_html_div(d[k])

    return d


def plhtml(fig, margin=narrow_margin, **kwargs):
    """
    Given a plotly figure, return it as a div
    """
    if fig is not None:
        fig.update_layout(margin=margin)

        fig.update_xaxes(automargin=True)
        fig.update_yaxes(automargin=True)
        return pl.offline.plot(fig, include_plotlyjs=False, output_type="div")

    return ""


def render_html(
    data,
    template,
    package_loader_name=None,
    template_globals=None,
    plotly_image_conv_func=convert_dict_plotly_fig_html_div,
    filename: str = None,
):
    """
    Using a Jinja2 template, render html file and return as string
    :param data: dict of jinja parameters to include in rendered html
    :param template: absolute location of template file
    :param package_loader_name: if using PackageLoader instead of FileLoader specify package name
    :return:
    """
    data = plotly_image_conv_func(data)

    tdirname, tfilename = os.path.split(os.path.abspath(template))
    if package_loader_name:
        loader = PackageLoader(package_loader_name, "templates")
    else:
        loader = FileSystemLoader(tdirname)
    env = Environment(loader=loader)
    env.finalize = jinja_finalize
    template = env.get_template(tfilename)
    if template_globals:
        for template_global in template_globals:
            template.globals[template_global] = template_globals[template_global]

    output = template.render(
        pagetitle=data["name"], last_gen_time=datetime.now(), data=data
    )

    if filename:
        render_html_to_file(filename, output)

    return output


def render_html_to_file(filename: str, output: str):
    """
    Using a Jinja2 template, render a html file and save to disk
    :param data: dict of jinja parameters to include in rendered html
    :param template: absolute location of template file
    :param filename: location of where rendered html file should be output
    :param package_loader_name: if using PackageLoader instead of FileLoader specify package name
    :return:
    """
    logging.info("Writing html to {}".format(filename))

    with open(filename, "w", encoding="utf8") as fh:
        fh.write(output)

    return filename


def jinja_finalize(value):
    """
    Finalize for jinja which makes empty entries show as blank rather than none
    and converts plotly charts to html divs
    :param value:
    :return:
    """
    if value is None:
        return ""
    if isinstance(value, go.Figure):
        return plhtml(value)
    return value
