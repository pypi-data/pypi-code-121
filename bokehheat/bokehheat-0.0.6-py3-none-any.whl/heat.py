####
# title: heat.py
#
# language: python 3.6
# dependencies: bokeh, pandas, scipy
# date: 2018-08
# license: >= GPLv3
# authors: bue, jenny
#
# install:
#    pip3 install bokehheat
#
# load:
#    from bokehheat import heat
#
#    help(heat.cdendro)
#    help(heat.cbar)
#    help(heat.bbar)
#    help(heat.qbar)
#    help(heat.heatmap)
#    help(heat.clustermap)
#
# test run:
#    python3 heat.py
#
# description:
#     A python3 bokeh based categorical dendrogram and heatmap plotting library.
####

# library
#from bokeh.io import show  # bue: used only for development
from bokeh.io import export_png, output_file, reset_output, save  # export_svgs
from bokeh.layouts import layout, row
from bokeh.models import ColorBar, Legend, LegendItem
from bokeh.plotting import figure
from bokeh.transform import linear_cmap
from bokeh.core.validation import silence
from bokeh.core.validation.warnings import FIXED_SIZING_MODE, MISSING_RENDERERS
import json
from matplotlib import cm, colors
import numpy as np
import os
import pandas as pd
import pkg_resources
from scipy.cluster.hierarchy import cophenet, dendrogram, linkage
from scipy.spatial.distance import pdist
import sys

# silence warnings
silence(MISSING_RENDERERS, True)
silence(FIXED_SIZING_MODE, True)

# error handling
#with open("error.json") as f_json:
with open(pkg_resources.resource_filename("bokehheat", "error.json")) as f_json:
    ds_error = json.load(f_json)

# seismic 256 colormap
o_cmap = cm.get_cmap("seismic", 256)
seismic256 = [colors.rgb2hex(o_cmap(i)) for i in range(o_cmap.N)]

# red 256 colormap
o_cmap = cm.get_cmap("Reds", 256)
red256 = [colors.rgb2hex(o_cmap(i)) for i in range(o_cmap.N)]

# functions

# the dendrogram plot
def cdendro(
        df_matrix,
        s_root = 'left',
        s_method = 'single',
        s_metric = 'euclidean',
        b_optimal_ordering = True
    ):
    '''
    input:
        df_matrx: a pandas dataframe where
            the index have to cary the y axis label.
            the column have to cary the x axis label.
            the matrix as such should only cary the z axis values.

        s_root: string. where is the origin of the dendrogram?
            possible values are: left, right, top, bottom.

        s_method:string. detailed description at
            https://docs.scipy.org/doc/scipy/reference/cluster.hierarchy.html
            default single (as in scipy).

        s_metric: string. detailed description at
            https://docs.scipy.org/doc/scipy/reference/cluster.hierarchy.html
            default euclidean.

        b_optimal_ordering: boolean. detailed description at
            https://docs.scipy.org/doc/scipy/reference/cluster.hierarchy.html
            default is True (as in scipy).

    output:
        r_cophcorre: real. cophnetic correlation coefficent. check out
            https://en.wikipedia.org/wiki/Cophenetic

        ls_cat_sorted: list of string with the leaves ordered by
           the applied cluster algorithmen.

        p: bokeh plot object.

    description:
        utilizes scipys pdist, linkage, dendrogram and copdist function
        to generate a bokeh based dendrogram.

        thank you to Jorn Hees who wrote an excellent tutorial about
        hierarchical clustering and dendrograms in scipy and Daniel Russo
        who wrote the only bokeh based dendrogram implementation I was aware of
        at the time I was writing this code.
        + https://joernhees.de/blog/2015/08/26/scipy-hierarchical-clustering-and-dendrogram-tutorial/
        + https://russodanielp.github.io/plotting-a-heatmap-with-a-dendrogram-using-bokeh.html
    '''
    # index as string
    df_matrix.index = df_matrix.index.astype(str)
    df_matrix.columns = df_matrix.columns.astype(str)

    # index or column dendrogram
    if s_root in {'top','bottom'}:
        df_matrix = df_matrix.T

    # distance calculation
    ar_z_linkage = linkage(
        df_matrix,
        method=s_method,
        metric=s_metric,
        optimal_ordering=b_optimal_ordering,
    )
    # cophenetic correlation coefficient calculation
    # bue: how good preserves the clustering the original distance
    r_cophcorre, ar_copdist = cophenet(ar_z_linkage, pdist(df_matrix))
    # categorical leaf layout
    d_dendro = dendrogram(ar_z_linkage, no_plot=True)
    ls_cat_sorted = list(df_matrix.iloc[d_dendro['leaves'],:].index)
    # categorical to number
    d_i2cat = {}
    for i, cat in enumerate(df_matrix.index.values):
        d_i2cat.update({i: cat})
    # linkage number to categorical
    ll_z_linkage = []
    for z_linkage in ar_z_linkage:
        l_z_linkage = list(z_linkage)
        s_cat0 = d_i2cat[int(l_z_linkage[0])]
        s_cat1 = d_i2cat[int(l_z_linkage[1])]
        i_cat0_index = ls_cat_sorted.index(s_cat0)
        i_cat1_index = ls_cat_sorted.index(s_cat1)
        if (i_cat0_index < i_cat1_index):
            d_i2cat.update({len(d_i2cat): s_cat0})
        else:
            d_i2cat.update({len(d_i2cat): s_cat1})
        l_z_linkage[0] = s_cat0
        l_z_linkage[1] = s_cat1
        l_z_linkage[3] = int(l_z_linkage[3])
        ll_z_linkage.append(l_z_linkage)

    # plot categorical
    if s_root in {'right'}:
        p = figure(
            y_range=ls_cat_sorted,
            title=f"cophentic: {round(r_cophcorre,3)}",
        )
        for l_z_linkage in ll_z_linkage:
            p.line(y=[l_z_linkage[0],l_z_linkage[1]], x=[l_z_linkage[2], l_z_linkage[2]], line_color='maroon') # horizontal
            p.line(y=[l_z_linkage[0],l_z_linkage[0]], x=[l_z_linkage[2], 0], line_color='maroon') # vertikal 1
            p.line(y=[l_z_linkage[1],l_z_linkage[1]], x=[l_z_linkage[2], 0], line_color='maroon') # vertikal 2
    elif s_root in {'left'}:
        p = figure(
            y_range=ls_cat_sorted,
            title=f"cophentic: {round(r_cophcorre,3)}"
        )
        for l_z_linkage in ll_z_linkage:
            p.line(y=[l_z_linkage[0],l_z_linkage[1]], x=[-(l_z_linkage[2]), -(l_z_linkage[2])], line_color='maroon') # horizontal
            p.line(y=[l_z_linkage[0],l_z_linkage[0]], x=[-(l_z_linkage[2]), 0], line_color='maroon') # vertikal 1
            p.line(y=[l_z_linkage[1],l_z_linkage[1]], x=[-(l_z_linkage[2]), 0], line_color='maroon') # vertikal 2
    elif s_root in {'top'}:
        p = figure(
            x_range=ls_cat_sorted,
            title=f"cophentic: {round(r_cophcorre,3)}"
        )
        for l_z_linkage in ll_z_linkage:
            p.line(x=[l_z_linkage[0],l_z_linkage[1]], y=[l_z_linkage[2], l_z_linkage[2]], line_color='maroon') # horizontal
            p.line(x=[l_z_linkage[0],l_z_linkage[0]], y=[l_z_linkage[2], 0], line_color='maroon') # vertikal 1
            p.line(x=[l_z_linkage[1],l_z_linkage[1]], y=[l_z_linkage[2], 0], line_color='maroon') # vertikal 2
    elif s_root in {'bottom'}:
        p = figure(
            x_range=ls_cat_sorted,
            title=f"cophentic: {round(r_cophcorre,3)}"
        )
        for l_z_linkage in ll_z_linkage:
            p.line(x=[l_z_linkage[0],l_z_linkage[1]], y=[-(l_z_linkage[2]), -(l_z_linkage[2])], line_color='maroon') # horizontal
            p.line(x=[l_z_linkage[0],l_z_linkage[0]], y=[-(l_z_linkage[2]), 0], line_color='maroon') # vertikal 1
            p.line(x=[l_z_linkage[1],l_z_linkage[1]], y=[-(l_z_linkage[2]), 0], line_color='maroon') # vertikal 2

    # output
    return(r_cophcorre, ls_cat_sorted, p)


# the quantitative barplot
def qbar(df_axis_annot, s_yx, s_z, r_low, r_high, ls_color_palette, s_root):
    """
    input:
        df_axis_annot: pandas dataframe for y or x axis annotation.

        s_yx: string. column label which specifies the column with the
            samples (or variables) labels to be annotated. e.g.: patient_id.

        s_z: string. column label which specifies the column with the
            quantitative annotation. e.g. age_year.

        r_low: quantitative minimum value. the dataset can contain lower values,
            but for color labeling they will be mapped to this minimum value.
            e.g.: 0.

        r_high: quantitative maximum value. the dataset can contain higher values,
            but for color labeling they will be mapped to this maximum value.
            e.g.: 100

        ls_color_palette: a list color strings to specify the color spectrum.
            this variable is compatible with the ordinary bokeh palettes:
            https://bokeh.pydata.org/en/latest/docs/reference/palettes.html

        s_root: string. how should the bar be placed?
          left and right will result in vertical bar, top and bottom will
          result in a horizontal bar.
          possible values are: left, right, top, bottom.

    output:
        p: bokeh plot object.

    description:
        this function will return an interactive bokeh based
        annotation bar plot for a quantitative variable.
    """
    # index as string
    df_axis_annot.columns = df_axis_annot.columns.astype(str)

    # color declaration
    d_zcolormapper = linear_cmap(
        field_name=s_z,
        palette=ls_color_palette,
        low=r_low,
        high=r_high
    )

    # tooltip declaration
    lt_tooltip = [
        (s_yx, f"@{s_yx}"),
        (s_z, f"@{s_z}"),
    ]

    # generate figure
    if (s_root in {"left", "right"}):
        p = figure(
            y_range=df_axis_annot[s_yx],
            x_range=(r_low,r_high),
            title=s_z,
            title_location="right",
            tooltips=lt_tooltip,
        )
        p.hbar(
            source=df_axis_annot,
            y=s_yx,
            right=s_z,
            left=r_low,
            height=0.9,
            color=d_zcolormapper,
        )
        p.yaxis.visible = False
    elif (s_root in {"top", "bottom"}):
        p = figure(
            y_range=(r_low,r_high),
            x_range=df_axis_annot[s_yx],
            title=s_z,
            tooltips=lt_tooltip,
        )
        p.vbar(
            source=df_axis_annot,
            x=s_yx,
            top=s_z,
            bottom=r_low,
            width=0.9,
            color=d_zcolormapper,
        )
        p.xaxis.visible = False
    else:
        sys.exit("Error at bokehheat.qbar: {}".format(
            ds_error["root_unknown"].format(s_root)
        ))
    # result
    return(p)


# the categorical barplot
def cbar(df_axis_annot, s_yx, s_z, s_zcolor, s_root):
    """
    input:
        df_axis_annot: pandas dataframe for y or x axis annotation.

        s_yx: string. column label which specifies the column with the
            samples (or variables) labels to be annotated. e.g.: patient_id.
            BUE 20210519: have to be a string

        s_z: string. column label which specifies the column with the
            quantitative annotation. e.g. age_year.

        s_zcolor: string. column label which specifies the column with the
            color strings related to the categorical annotation.

        s_root: string. how should the bar be placed?
          left and right will result in vertical bar, top and bottom will
          result in a horizontal bar.
          possible values are: left, right, top, bottom.

    output:
        p: bokeh plot object.

    description:
        this function will return an interactive bokeh based
        annotation bar for a categorical variable.
    """
    # index as string
    df_axis_annot.columns = df_axis_annot.columns.astype(str)

    # tooltip declaration
    lt_tooltip = [
        (s_yx, f"@{s_yx}"),
        (s_z, f"@{s_z}"),
    ]
    # generate figure
    if (s_root in {"left", "right"}):
        p = figure(
            y_range=df_axis_annot[s_yx],
            title = s_z,
            title_location="right",
            tooltips = lt_tooltip,
        )
        p.hbar(
            source=df_axis_annot,
            y=s_yx,
            right=1,
            left=0,
            height=0.9,
            color=s_zcolor,
        )
    elif (s_root in {"top", "bottom"}):
        p = figure(
            x_range=df_axis_annot[s_yx],
            title = s_z,
            tooltips = lt_tooltip,
        )
        p.vbar(
            source=df_axis_annot,
            x=s_yx,
            top=1,
            bottom=0,
            width=0.9,
            color=s_zcolor,
        )
    else:
        sys.exit("Error at bokehheat.cbar: {}".format(
            ds_error["root_unknown"].format(s_root)
        ))
    p.xaxis.visible = False
    p.yaxis.visible = False
    # result
    return(p)


# the boolean barplot
def bbar(df_axis_annot, s_yx, s_z, s_true_color, s_false_color, s_root):
    """
    input:
        df_axis_annot: pandas dataframe for y or x axis annotation.

        s_yx: string. column label which specifies the column with the
            samples (or variables) labels to be annotated. e.g.: patient_id.
            BUE 20210519: have to be a string

        s_z: string. column label which specifies the column with the
            boolean annotation.

        s_true_color: string. specifies a color hex or name like 'Black'.

        s_false_color: string. specifies a color hex or name like 'Yellow'.

        s_root: string. how should the bar be placed?
          left and right will result in vertical bar, top and bottom will
          result in a horizontal bar.
          possible values are: left, right, top, bottom.

    output:
        p: bokeh plot object.

    description:
        this function will return an interactive bokeh based
        annotation bar for a boolean variable.
    """
    # handle y and x axis name
    d_color = {True : s_true_color, False : s_false_color}
    df_axis_annot["boolean_color"] = df_axis_annot[s_z].replace(d_color)
    p = cbar(
        df_axis_annot=df_axis_annot,
        s_yx=s_yx,
        s_z=s_z,
        s_zcolor="boolean_color",
        s_root=s_root
    )
    return(p)


# the stacked barplot
def stackedbar(df_matrix, ds_stack_color, b_sum_to_1=True):
    """
    input:
        df_matrix: matrix dataframe.
          the matrix should be in the same xy orientation as the final stackedbar.
          the index should cary the y axis labels.
          the column should cary the x axis labels.
          a doubly stochastic matrix is processed like a left stochatic matrix.
          a matrix with ds_stack_color given for y and x axis label and
          b_sum_to_1 set to False is processed like the columns are the bars.
          + https://en.wikipedia.org/wiki/Stochastic_matrix

        ds_stack_color: dictionary that links
          the y or x or (y and x) axis label to colors.
          https://docs.bokeh.org/en/latest/docs/reference/colors.html

        b_sum_to_1: boolean, if fuction should check, if df_matrix is
          a fractional, maybe stockastic matrix. in other words,
          if all column or all row or all columns and rows sum up to 1.
          if True, the function will trough an error if neither column nor row
          sum up to True.
          default is True.

    output:
        p: bokeh plot object.

    description:
        this function will return a bokeh based, interactive stacked bar plot.
    """
    # index as string
    df_matrix.index = df_matrix.index.astype(str)
    df_matrix.columns = df_matrix.columns.astype(str)

    # handle y and x axis name
    if (df_matrix.index.name == None):
        df_matrix.index.name = "y_axis"
    if (df_matrix.columns.name == None):
        df_matrix.columns.name = "x_axis"
    s_y = df_matrix.index.name
    s_x = df_matrix.columns.name

    # color
    es_key_color = set(ds_stack_color.keys())
    es_y_axis = set(df_matrix.index.values)
    es_x_axis = set(df_matrix.columns.values)
    if (len(es_y_axis.intersection(es_key_color)) == df_matrix.shape[0]):
        b_color_column = True
    else:
        b_color_column = False

    if (len(es_x_axis.intersection(es_key_color)) == df_matrix.shape[1]):
        b_color_row = True
    else:
        b_color_row = False

    # color error
    if (not b_color_column and not b_color_row):
        sys.exit("Error at bokehheat.stackedbar: {}".format(
            ds_error["matrix_color_none"].format(sorted(es_y_axis), sorted(es_x_axis), sorted(ds_stack_color.items()))
        ))

    # sum up to 1
    s_matrix = 'neither column nor row summing to 1'
    # sum over columns
    if all((df_matrix.values.sum(axis=0) < 1.000000001) & (df_matrix.values.sum(axis=0) > 0.999999999)):
        b_sum1_column = True
        s_matrix = 'column summing to 1'
    else:
        b_sum1_column = False
    # sum over row
    if all((df_matrix.values.sum(axis=1) < 1.000000001) & (df_matrix.values.sum(axis=1) > 0.999999999)):
        b_sum1_row = True
        if (b_sum1_column):
            s_matrix = 'column and row summing to 1'
        else:
            s_matrix = 'row summing to 1'
    else:
        b_sum1_row = False


    # !left & !right: no stochastic matrix
    if (b_sum_to_1 and not b_sum1_column and not b_sum1_row):
        sys.exit("Error at bokehheat.stackedbar: {}".format(
            ds_error["matrix_stochastic_none"].format(df_matrix.values.sum(axis=0), df_matrix.values.sum(axis=1))
        ))

    # !left & right: right stochatstic matrix
    elif (b_sum_to_1 and not b_sum1_column and b_sum1_row) \
        or (not b_sum_to_1 and not b_color_column and b_color_row):

        # data
        ls_axis_x = list(df_matrix.columns.values)  # column label
        ls_axis_y = list(df_matrix.index.values)[::-1]  # row label and range
        ls_color_x = [ds_stack_color[s_x] for s_x in ls_axis_x] # column color

        d_matrix = {s_y: ls_axis_y}  # column label
        for s_column in ls_axis_x:
            d_matrix.update({
                s_column:
                list(df_matrix.loc[:,s_column].values)[::-1]
            }) # data per column

        # plot
        lt_tooltip = [
            (f'{s_y}', f"@{s_y}"),
            (f'{s_x}', '@$name $name [fraction]'),
        ]

        p = figure(
            y_range=ls_axis_y,
            tools = "box_zoom,hover,pan,reset",  # have to be set hardcoded
            active_drag = "box_zoom",  # have to be set hardcoded
            tooltips=lt_tooltip,
            title=s_matrix,
            #title_location="right",
        )
        p.hbar_stack(
            ls_axis_x,
            y=s_y,
            height=0.9,
            color=ls_color_x,
            source=d_matrix,
        )

    # (left & !right) | (left & right): left or doubly stochastic matrix
    elif (b_sum_to_1 and b_sum1_column and not b_sum1_row) or (b_sum_to_1 and b_sum1_column and b_sum1_row) \
        or  (not b_sum_to_1 and b_color_column and not b_color_row) or (not b_sum_to_1 and b_color_column and b_color_row):

        # data
        ls_axis_x = list(df_matrix.columns.values)  # column label and range
        ls_axis_y = list(df_matrix.index.values[::-1])  # row label
        ls_color_y = [ds_stack_color[s_y] for s_y in ls_axis_y] # column color

        d_matrix = {s_x: ls_axis_x}  # column label
        for s_row in ls_axis_y:
            d_matrix.update({
                s_row:
                list(df_matrix.loc[s_row,:].values)
            }) # data per row

        # plot
        lt_tooltip = [
            (f'{s_x}', f"@{s_x}"),
            (f'{s_y}', '@$name $name [fraction]'),
        ]

        p = figure(
            x_range=ls_axis_x,
            tools = "box_zoom,hover,pan,reset",  # have to be set hardcoded
            active_drag = "box_zoom",  # have to be set hardcoded
            tooltips=lt_tooltip,
            title=s_matrix,
        )
        p.vbar_stack(
            ls_axis_y,
            x=s_x,
            width=0.9,
            color=ls_color_y,
            source=d_matrix,
        )

    # error case:
    else:
        sys.exit("Error at bokehheat.stackedbar: {}".format(
            ds_error["matrix_else"].format(b_sum_to_1, b_sum1_column, b_sum1_row, b_color_column, b_color_row)
        ))

    # finish up
    p.yaxis.major_label_orientation = "horizontal"
    p.xaxis.major_label_orientation = "vertical"

    # result
    return(p)


# the heatmap
def heatmap(df_matrix, ls_color_palette, r_low, r_high, s_z="value"):
    """
    input:
        df_matrx: a dataframe in same xy orientation as the final heatmap.
          the index should cary the y axis label.
          the column should cary the x axis label.
          the matrix as such should only cary the z axis values.

        ls_color_palette: a list color strings to specify the map`s color spectrum.
            you can use the bokehheat colormaps heat.red256 and heat.seismic256.
            besides this variable is compatible with the ordinary bokeh palettes:
            https://bokeh.pydata.org/en/latest/docs/reference/palettes.html

        r_low: quantitative minimum value. the dataset can contain lower values,
            but for color labeling they will be mapped to this minimum value.
            e.g.: -8.

        r_high: quantitative maximum value. the dataset can contain lower values,
            but for color labeling they will be mapped to this maximum value.
            e.g.: 8.

        s_z: string. label that specifies what the values in the matrix actually
            are. e.g.: 'gene expression [log2]'

    output:
        p: bokeh plot object.

    description:
        this function will return a bokeh based interactive heatmap plot.
        the color are representing the z value.
    """
    # index as string
    df_matrix.index = df_matrix.index.astype(str)
    df_matrix.columns = df_matrix.columns.astype(str)

    # handle y and x axis name
    if (df_matrix.index.name == None):
        df_matrix.index.name = "y_axis"
    if (df_matrix.columns.name == None):
        df_matrix.columns.name = "x_axis"
    s_y = df_matrix.index.name
    s_x = df_matrix.columns.name

    # melt dataframe
    df_tidy = df_matrix.reset_index().melt(
        id_vars=[df_matrix.index.name],
        value_name=s_z
    )
    # color declaration
    d_zcolormapper = linear_cmap(
        field_name=s_z,
        palette=ls_color_palette,
        low=r_low,
        high=r_high
    )
    # tooltip declaration
    lt_tooltip = [
        (s_y, f"@{s_y}"),
        (s_x, f"@{s_x}"),
        (s_z, f"@{s_z}"),
    ]
    # generate figure
    o_colorbar = ColorBar(color_mapper=d_zcolormapper['transform'])
    p = figure(
        y_range=df_matrix.index.values,
        x_range=df_matrix.columns.values,
        tools = "box_zoom,hover,pan,reset",  # have to be set hardcoded
        active_drag = "box_zoom",  # have to be set hardcoded
        tooltips=lt_tooltip,
        title=s_z,
    )
    p.rect(
        source=df_tidy,
        x=s_x,
        y=s_y,
        color=d_zcolormapper,
        width=1,
        height=1,
    )
    p.add_layout(o_colorbar, place='left')
    p.yaxis.major_label_orientation = "horizontal"
    p.xaxis.major_label_orientation = "vertical"

    # out
    return(p)


# the categorical color legend
def cmbarlegend(tt_axis_annot, es_ymatrix, es_xmatrix, i_px, i_height, i_width):
    """
    input:
        tt_axis_annot: axis annotation tuple.
            boolean, categorical, and quantitative axis annotation tuples are possible.
            t_axis_annot_boolean = (df_axis_annot, ls_z, s_true_color, s_false_color)
            t_axis_annot_categorical = (df_axis_annot, ls_z, ls_zcolor)
            t_axis_annot_quantitative = (df_axis_annot, ls_z, lr_low, lr_high, lls_color_palette)

            df_axis_annot: pandas datafarme for y or x axis annotation.
                the df_axis_annot index have to carry df_matrix index or column related labels.
                the df_axis_annot column have to carry all needed s_z and s_zcolor labels.

            ls_z: list of annotation labels which should be turned into annotation bars.

            s_true_color: string. color hex or name for True s_z values. e.g 'Yellow'.

            s_false_color: string. color hex or name for False s_z values. e.g. 'Black'.

            ls_zcolor: list of categorical s_z annotation related color column labels.

            lr_low: list of quantitative s_z annotation related minimum values.

            lr_high: list of quantitative s_z annotation related maximum values.

            lls_color_palette: list of quantitative s_z annotation related color palette lists.

        es_ymatrix: set of df_matrx dataframe index labels.

        es_xmatrix: set of df_matrx dataframe column labels.

        i_px: integer. clustermap pixel unit.

        i_height: integer. i_px * i_height specifies the heatmap height.

        i_width: integer. i_px * i_width specifies the heatmap width.

    output:
        lo_p: list of x axis legend, y axis legend bokeh plot object.

    description:
        this function builds combined legend for all boolean and cathegorical annotation bars.
        specified in tt_axis_annot.
    """
    # set output
    lo_p = [None,None]

    # get color and tags
    ds_ycolor = {}
    ds_xcolor = {}
    for t_axis_annot in tt_axis_annot:

        # check if root is top or right
        es_axis = set(t_axis_annot[0].index)
        b_ok = False
        ls_root = []
        if (len(es_ymatrix.intersection(es_axis)) > 0):
            ls_root.append('right')
            b_ok = True
        if (len(es_xmatrix.intersection(es_axis)) > 0):
            ls_root.append('top')
            b_ok = True
        if not (b_ok):
            sys.exit("Error at bokehheat.cmbarlegend: {}".format(
                ds_error["axis_annot_none"].format(sorted(es_axis), sorted(es_ymatrix), sorted(es_xmatrix))
            ))

        # categorical case
        # t_axis_annot = (df_axis_annot, ls_z, ls_zcolor)
        if (len(t_axis_annot) == 3):

            # extract relevant columns of the dataframe
            for n, s_bz in enumerate(t_axis_annot[1]):
                s_bzcolor = t_axis_annot[2][n]
                df_axis = t_axis_annot[0].loc[:,[s_bz, s_bzcolor]]
                df_axis.drop_duplicates(inplace=True)

                # update x and y dict
                for s_root in ls_root:
                    for i, se_row in df_axis.iterrows():
                        s_tag = str(se_row.loc[s_bz])
                        s_color = str(se_row.loc[s_bzcolor])
                        if (s_root == 'top'):
                            try:
                                es_tag = ds_xcolor[s_color]
                                es_tag.add(s_tag)
                            except KeyError:
                                es_tag = {s_tag}
                            ds_xcolor.update({s_color: es_tag})
                        else:
                            try:
                                es_tag = ds_ycolor[s_color]
                                es_tag.add(s_tag)
                            except KeyError:
                                es_tag = {s_tag}
                            ds_ycolor.update({s_color: es_tag})

        # boolean case
        # t_axis_annot_boolean = (df_axis_annot, ls_z, s_true_color, s_false_color)
        elif (len(t_axis_annot) == 4):

            # update x and y dict
            s_true_color = t_axis_annot[2]
            s_false_color = t_axis_annot[3]
            for s_root in ls_root:
                if (s_root == 'top'):
                    # update true color dict
                    try:
                        es_tag = ds_xcolor[s_true_color]
                        es_tag.add("True")
                    except KeyError:
                        es_tag = {"True"}
                    ds_xcolor.update({s_true_color: es_tag})
                    # update false color dict
                    try:
                        es_tag = ds_xcolor[s_false_color]
                        es_tag.add("False")
                    except KeyError:
                        es_tag = {"False"}
                    ds_xcolor.update({s_false_color: es_tag})

                else:
                    # update true color dict
                    try:
                        es_tag = ds_ycolor[s_true_color]
                        es_tag.add("True")
                    except KeyError:
                        es_tag = {"True"}
                    ds_ycolor.update({s_true_color: es_tag})
                    # update false color dict
                    try:
                        es_tag = ds_ycolor[s_false_color]
                        es_tag.add("False")
                    except KeyError:
                        es_tag = {"False"}
                    ds_ycolor.update({s_false_color: es_tag})

        # quantitative case
        # t_axis_annot = (df_axis_annot, ls_z, lr_low, lr_high, lls_color_palette)
        elif (len(t_axis_annot) == 5):
            pass

        # error case
        else:
            sys.exit("Error at bokehheat.cmbarlegend: {}".format(
                ds_error["axis_annot_invalid"].format(t_axis_annot)
            ))

    # make annotation plot
    print(f"ds_xcolor: {ds_xcolor}")
    if (len(ds_xcolor) > 0):
        p = figure() # title = "x axis color bar legend"
        ds_color = {}
        for s_color, es_legend in ds_xcolor.items():
            ds_color.update({s_color : "; ".join(sorted(es_legend))})
        lo_legend_item = []
        for i, (s_color, s_legend) in enumerate(sorted(ds_color.items(), key=lambda n: n[1])):
            lo_legend_item.append(
                LegendItem(
                    label=s_legend,
                    renderers=[
                        p.line(0, 0, line_color=s_color, line_width=np.ceil(i_px/4))
                    ],
                    index=i,
                ),
            )
        p.add_layout(Legend(items=lo_legend_item))
        p.legend.location = "bottom_left"
        p.height = int(len(ds_color) * np.ceil(i_px/3) + i_px * 1.5)
        p.width = int(np.floor(i_width / 4 * i_px))
        p.toolbar_location = None
        p.axis.visible = False
        p.xgrid.visible = False
        p.ygrid.visible = False
        lo_p[0] = p

    print(f"ds_ycolor: {ds_ycolor}")
    if (len(ds_ycolor) > 0):
        p = figure() # title = "x axis color bar legend"
        ds_color = {}
        for s_color, es_legend in ds_ycolor.items():
            ds_color.update({s_color : "; ".join(sorted(es_legend))})
        lo_legend_item = []
        for i, (s_color, s_legend) in enumerate(sorted(ds_color.items(), key=lambda n: n[1])):
            lo_legend_item.append(
                LegendItem(
                    label=s_legend,
                    renderers=[
                        p.line(0, 0, line_color=s_color, line_width=np.ceil(i_px/4))
                    ],
                    index=i,
                ),
            )
        p.add_layout(Legend(items=lo_legend_item))
        p.legend.location = "bottom_left"
        #p.title_location = "below"
        p.height = i_height * i_px
        p.width = int(np.floor(i_width / 4 * i_px))
        p.toolbar_location = None
        p.axis.visible = False
        p.xgrid.visible = False
        p.ygrid.visible = False
        lo_p[1] = p

    # out
    return(lo_p)


# the clustered heatmap
def clustermap(
        df_matrix,
        ls_color_palette,
        r_low,
        r_high,
        s_z = "value",
        tt_axis_annot = (),
        b_xdendro = False,
        b_ydendro = False,
        s_method = 'average',
        s_metric = 'euclidean',
        b_optimal_ordering = False,
        i_px = 64,
        i_height = 12,
        i_width = 12,
        i_min_border_px = 128,
        s_filename = "clustermap.html",
        s_filetitel = None, #"Bokeh Plot",
    ):
    """
    input:
        df_matrx: a dataframe in same xy orientation as the final heatmap.
            the index have to cary the y axis label.
            the column have to cary the x axis label.
            the matrix as such should only cary the z axis values.

        ls_color_palette: a list color strings to specify the map`s color spectrum.
            you can use the bokehheat colormaps heat.red256 and heat.seismic256.
            beside this variable is compatible with the ordinary bokeh palettes:
            https://bokeh.pydata.org/en/latest/docs/reference/palettes.html

        r_low: quantitative minimum value. the dataset can contain lower values,
            but for color labeling they will be mapped to this minimum value.
            e.g.: -8.

        r_high: quantitative maximum value. the dataset can contain lower values,
            but for color labeling they will be mapped to this maximum value.
            e.g.: 8.

        s_z: string. label that specifies what the values in the matrix actually
            are. e.g.: 'gene expression [log2]'

        tt_axis_annot: axis annotation tuple.
            boolean, categorical and quantitative axis annotation tuples are possible.
            t_axis_annot_boolean = (df_axis_annot, ls_z, s_true_color, s_false_color)
            t_axis_annot_categorical = (df_axis_annot, ls_z, ls_zcolor)
            t_axis_annot_quantitative = (df_axis_annot, ls_z, lr_low, lr_high, lls_color_palette)

            df_axis_annot: pandas datafarme for y or x axis annotation.
                the df_axis_annot index have to carry df_matrix index or column related labels.
                the df_axis_annot column have to carry all needed s_z and s_zcolor labels.

            ls_z: list of annotation labels which should be turned into annotation bars.

            s_true_color: string. color hex or name for True s_z values. e.g 'Yellow'.

            s_false_color: string. color hex or name for False s_z values. e.g. 'Black'.

            ls_zcolor: list of categorical s_z annotation related color column labels.

            lr_low: list of quantitative s_z annotation related minimum values.

            lr_high: list of quantitative s_z annotation related maximum values.

            lls_color_palette: list of quantitative s_z annotation related color palette lists.

        b_ydendro and b_xdendro: boolean, if True the y respective x axis
            get clustered with the specified s_method and s_metiric.
            if False the axis order from the df_matrix is preserved.
            default is False.

        s_method:string. detailed description at
            https://docs.scipy.org/doc/scipy/reference/cluster.hierarchy.html
            default average (as in seaborn).

        s_metric: string. detailed description at
            https://docs.scipy.org/doc/scipy/reference/cluster.hierarchy.html
            default euclidean.

        b_optimal_ordering: boolean. detailed description at
          https://docs.scipy.org/doc/scipy/reference/cluster.hierarchy.html
          default is False (as in seaborn).

        i_px: integer. clustermap pixel unit.
            by default the top dendrogram is 3 times this unit high and 12 times this unit width,
            the right dendrogram is 12 time this unit high and 3 times this unit width,
            the top annotation bars are 1 time this unit high and 12 times this unit width,
            the right annotation bars are 12 time this unit high and 1 time this unit width,
            the heatmap is 12 time this unit high and 12 times this unit width.
            if you need smaller labels increase this unit and make the overall plot
            smaller with your browsers zoom function (Ctrl -).
            if you need bigger labels do the opposite.
            default is 64 pixels.

        i_height: integer. i_px * i_height specifies the heatmap height. default is 12.

        i_width: integer. i_px * i_width specifies the heatmap width. default is 12.

        i_min_border_px: integer. to specify left and bottom plot border padding
            which becomes available for axis labels. default is 128 pixels.

        s_filename: filename of the resulting html or png file.
            default is clustermap.html

        s_filetitel: clustermap plot title.
            this title will be visible as browser tab label and as main label on top of the plot
            default is None.

    output:
        clustermap.html or clustermap.png: resulting file
            with the s_filname attribute specified file name.

        o_layout: clustermap bokeh layout object.

        ls_yaxis: list of string with the leaves the same ordered
            as the heatmap y axis.

        ls_xaxis: list of string with the leaves the same ordered
            as the heatmap x axis.

    description:
        this function will return an interactive bokeh based clustermap related
        html file, bokeh layout object, list of y axis and list x axis labels.
    """
    # index as string
    df_matrix.index = df_matrix.index.astype(str)
    df_matrix.columns = df_matrix.columns.astype(str)
    ls_yaxis = list(df_matrix.index)
    ls_xaxis = list(df_matrix.columns)

    # handle y and x axis name
    if (df_matrix.index.name == None):
        df_matrix.index.name = "y_axis"
    if (df_matrix.columns.name == None):
        df_matrix.columns.name = "x_axis"

    # cluster y and x
    if (b_ydendro):
        r_cophcorre, ls_yaxis, p_ydendro = cdendro(
            df_matrix,
            s_root='right',
            s_method=s_method,
            s_metric=s_metric,
            b_optimal_ordering=b_optimal_ordering,
        )
        p_ydendro.height = i_height * i_px
        p_ydendro.width = 3 * i_px
        p_ydendro.min_border_bottom = i_min_border_px
        p_ydendro.yaxis.visible = False
        p_ydendro.toolbar_location = None
        df_matrix = df_matrix.loc[ls_yaxis,:]
    if (b_xdendro):
        r_cophcorre, ls_xaxis, p_xdendro = cdendro(
            df_matrix,
            s_root='top',
            s_method=s_method,
            s_metric=s_metric,
            b_optimal_ordering=b_optimal_ordering,
        )
        p_xdendro.height = 3 * i_px
        p_xdendro.width = i_width * i_px
        p_xdendro.min_border_left = i_min_border_px
        p_xdendro.xaxis.visible = False
        p_xdendro.toolbar_location = None
        df_matrix = df_matrix.loc[:,ls_xaxis]

    # generate heat map
    p_heatmap = heatmap(
        df_matrix,
        ls_color_palette=ls_color_palette,
        r_low=r_low,
        r_high=r_high,
        s_z=s_z,
    )
    p_heatmap.height = i_height * i_px
    p_heatmap.width = i_width * i_px
    p_heatmap.min_border_left = i_min_border_px
    p_heatmap.min_border_bottom = i_min_border_px
    p_heatmap.toolbar_location="below"

    # link dendrogram
    if (b_ydendro):
        p_ydendro.y_range = p_heatmap.y_range
    if (b_xdendro):
        p_xdendro.x_range = p_heatmap.x_range

    # generate y and axis annotation
    lp_ybar = []
    lp_xbar = []
    es_ymatrix = set(df_matrix.index)
    es_xmatrix = set(df_matrix.columns)
    if (len(es_ymatrix) != df_matrix.shape[0]):
        sys.exit("Error at bokehheat.clustermap: {}".format(
            ds_error["y_axis_unique"].format(list(df_matrix.index))
        ))
    if (len(es_xmatrix) != df_matrix.shape[1]):
        sys.exit("Error at bokehheat.clustermap: {}".format(
            ds_error["x_axis_unique"].format(list(df_matrix.columns))
        ))

    for t_axis_annot in tt_axis_annot:

        # check if root is top or right
        es_axis = set(t_axis_annot[0].index)
        b_ok = False
        ls_root = []
        if (len(es_ymatrix.intersection(es_axis)) > 0):
            ls_root.append('right')
            b_ok = True
        if (len(es_xmatrix.intersection(es_axis)) > 0):
            ls_root.append('top')
            b_ok = True
        if not (b_ok):
            sys.exit("Error at bokehheat.clustermap: {}".format(
                ds_error["axis_annot_none"].format(sorted(es_axis), sorted(es_ymatrix), sorted(es_xmatrix))
            ))

        # categorical
        # t_axis_annot = (df_axis_annot, ls_z, ls_zcolor)
        if (len(t_axis_annot) == 3):
            # extract relevant columns of the dataframe
            for n, s_bz in enumerate(t_axis_annot[1]):
                s_bzcolor = t_axis_annot[2][n]
                df_axis = t_axis_annot[0].loc[:,[s_bz, s_bzcolor]]
                df_axis.index = df_axis.index.astype(str)
                # get df_axis index name
                for s_root in ls_root:
                    # reorder df_axis and include missing values
                    if (s_root == 'top'):
                        df_axis = df_axis.reindex(df_matrix.columns)
                        df_axis = df_axis.loc[df_matrix.columns,:]
                        df_axis.index.name = df_matrix.columns.name
                    else:
                        df_axis = df_axis.reindex(df_matrix.index)
                        df_axis = df_axis.loc[df_matrix.index,:]
                        df_axis.index.name = df_matrix.index.name
                    # call cbar
                    p_bar = cbar(
                        df_axis_annot=df_axis.reset_index(),
                        s_yx=df_axis.index.name,
                        s_z=s_bz,
                        s_zcolor=s_bzcolor,
                        s_root=s_root,
                    )
                    p_bar.toolbar_location = None
                    if (s_root == 'top'):
                        p_bar.x_range = p_heatmap.x_range
                        p_bar.height = i_px
                        p_bar.width = i_width * i_px
                        p_bar.min_border_left = i_min_border_px
                        lp_xbar.insert(0, p_bar)
                    else:
                        p_bar.y_range = p_heatmap.y_range
                        p_bar.height = i_height * i_px
                        p_bar.width = i_px
                        p_bar.min_border_bottom = i_min_border_px
                        lp_ybar.append(p_bar)

        # boolean
        # t_axis_annot_boolean = (df_axis_annot, ls_z, s_true_color, s_false_color)
        elif (len(t_axis_annot) == 4):
            s_true_color = t_axis_annot[2]
            s_false_color = t_axis_annot[3]
            # extract relevant columns of the dataframe
            for n, s_bz in enumerate(t_axis_annot[1]):
                se_axis = t_axis_annot[0].loc[:,s_bz]
                se_axis.index = se_axis.index.astype(str)
                # get se_axis index name
                for s_root in ls_root:
                    # reorder df_axis and include missing values
                    if (s_root == 'top'):
                        se_axis = se_axis.reindex(df_matrix.columns)
                        se_axis = se_axis.loc[df_matrix.columns]
                        se_axis.index.name = df_matrix.columns.name
                    else:
                        se_axis = se_axis.reindex(df_matrix.index)
                        se_axis = se_axis.loc[df_matrix.index]
                        se_axis.index.name = df_matrix.index.name
                    # call bbar
                    p_bar = bbar(
                        df_axis_annot=se_axis.reset_index(),
                        s_yx=se_axis.index.name,
                        s_z=s_bz,
                        s_true_color=t_axis_annot[2],
                        s_false_color=t_axis_annot[3],
                        s_root=s_root,
                    )
                    p_bar.toolbar_location = None
                    if (s_root == 'top'):
                        p_bar.x_range = p_heatmap.x_range
                        p_bar.height = i_px
                        p_bar.width = i_width * i_px
                        p_bar.min_border_left = i_min_border_px
                        lp_xbar.insert(0, p_bar)
                    else:
                        p_bar.y_range = p_heatmap.y_range
                        p_bar.height = i_height * i_px
                        p_bar.width = i_px
                        p_bar.min_border_bottom = i_min_border_px
                        lp_ybar.append(p_bar)

        # quantitative
        # t_axis_annot = (df_axis_annot, ls_z, lr_low, lr_high, lls_color_palette)
        elif (len(t_axis_annot) == 5):
            # extract relevant columns of the dataframe
            for n, s_bz in enumerate(t_axis_annot[1]):
                r_blow = t_axis_annot[2][n]
                r_bhigh = t_axis_annot[3][n]
                ls_bcolor = t_axis_annot[4][n]
                se_axis = t_axis_annot[0].loc[:,s_bz]
                se_axis.index = se_axis.index.astype(str)
                # get se_axis index name
                if (se_axis.index.name == None):
                    se_axis.index.name = "variable"
                for s_root in ls_root:
                    # reorder df_axis and include missing values
                    if (s_root == 'top'):
                        se_axis = se_axis.reindex(df_matrix.columns)
                        se_axis = se_axis.loc[df_matrix.columns]
                    else:
                        se_axis = se_axis.reindex(df_matrix.index)
                        se_axis = se_axis.loc[df_matrix.index]
                    # call qbar
                    p_bar = qbar(
                        df_axis_annot=se_axis.reset_index(),
                        s_yx=se_axis.index.name,
                        s_z=s_bz,
                        r_low=r_blow,
                        r_high=r_bhigh,
                        ls_color_palette=ls_bcolor,
                        s_root=s_root,
                    )
                    p_bar.toolbar_location = None
                    if (s_root == 'top'):
                        p_bar.x_range = p_heatmap.x_range
                        p_bar.height = i_px
                        p_bar.width = i_width * i_px
                        p_bar.min_border_left = i_min_border_px
                        lp_xbar.insert(0, p_bar)
                    else:
                        p_bar.y_range = p_heatmap.y_range
                        p_bar.height = i_height * i_px
                        p_bar.width = i_px
                        p_bar.min_border_bottom = i_min_border_px
                        lp_ybar.append(p_bar)
        # error
        else:
            sys.exit("Error at bokehheat.clustermap: {}".format(
                ds_error["axis_annot_invalid"].format(t_axis_annot)
            ))

    # generate axis annotation legend
    lp_xylegend = cmbarlegend(
        tt_axis_annot=tt_axis_annot,
        es_ymatrix=es_ymatrix,
        es_xmatrix=es_xmatrix,
        i_px=i_px,
        i_height=i_height,
        i_width=i_width,
    )

    ### put output top down together ###
    reset_output()
    output_file(s_filename, title=s_filetitel)
    lp_out = []
    lp_toptop = []
    lp_top = []
    llp_middle = []
    lp_bottom = []
    # check for top axis annotation legend
    if not (lp_xylegend[0] is None):
        #lp_xylegend[0].min_border_left = i_min_border_px
        lp_toptop.append(lp_xylegend[0])
    # set main titel
    if (s_filetitel is None):
        p_title = figure(title = '')
    else:
        p_title = figure(title = s_filetitel)
    p_title.title.text_font_style = "bold"
    p_title.title.text_font_size = "1.5em"
    p_title.title.align = "center"
    #p_title.title_location = "below"
    p_title.height = i_px
    p_title.width = i_width * i_px
    if not (lp_xylegend[0] is None):
        p_title.height = lp_xylegend[0].height
        p_title.width = int(p_heatmap.width - lp_xylegend[0].width)
    p_title.toolbar_location = None
    lp_toptop.append(p_title)
    # check for top dendrogram
    if (b_xdendro):
        lp_top.append(p_xdendro)
    # check for top axis annotation
    for p_xbar in lp_xbar:
        llp_middle.append([p_xbar])
    # all
    lp_bottom.append(p_heatmap)
    # check for right side axis annotation
    for p_ybar in lp_ybar:
        lp_bottom.append(p_ybar)
    # check for right side dendrogram
    if (b_ydendro):
        lp_bottom.append(p_ydendro)
    # check for right side  axis annotation legend
    if not (lp_xylegend[1] is None):
        lp_bottom.append(lp_xylegend[1])
    # kick out toptop row when only None
    if (len(lp_toptop) > 0):
        lp_out.append(lp_toptop)
    # kick out top row when only None
    if (len(lp_top) > 0):
        lp_out.append(lp_top)
    # kick out middle row when no top axis annotation
    if (len(llp_middle) > 0):
        # check for top axis annotation
        for lp_middle in llp_middle:
            lp_out.append(lp_middle)

    # bottom row has always heatmap
    lp_out.append(row(lp_bottom))

    # output
    s_path = '/'.join(s_filename.replace('\\','/').split('/')[:-1])
    if (len(s_path) > 0):
        os.makedirs(s_path, exist_ok=True)
    o_layout = layout(lp_out, sizing_mode='fixed')
    if (s_filename.endswith(".html")):
        save(o_layout)
    elif (s_filename.endswith(".png")):
        export_png(o_layout, filename=s_filename)
    else:
        sys.exit("Error at bokehheat.clustermap: {}".format(
            ds_error["file_type"].format(s_filename.split(".")[-1])
        ))
    return(o_layout, ls_yaxis, ls_xaxis)


# the cluster stacked barplot
def clusterbar(
        df_matrix,
        ds_stack_color,
        b_sum_to_1 = True,
        tt_axis_annot = (),
        b_dendro = False,
        s_method = 'average',
        s_metric = 'euclidean',
        b_optimal_ordering = False,
        i_px = 64,
        i_height = 12,
        i_width = 12,
        i_min_border_px = 128,
        s_filename = "clusterbar.html",
        s_filetitel = None,
    ):
    """
    input:
        df_matrix: matrix dataframe.
          the matrix should be in the same xy orientation as the final stackedbar.
          the index should cary the y axis label.
          the column should cary the x axis label.
          a doubly stochastic matrix is processed like a left stochatic matrix.
          a matrix with ds_stack_color given for y and x axis label and
          b_sum_to_1 set to False is processed like the columns are the bars.

        ds_stack_color: dictionary that links
          the y or x or (y and x) axis label to colors.
          https://docs.bokeh.org/en/latest/docs/reference/colors.html

        b_sum_to_1: boolean, if fuction should check, if df_matrix is
          a fractional, maybe stockastic matrix. in other words,
          if all column or all row or all columns and rows sum up to 1.
          if True, the function will trough an error if neither column nor row
          sum up to 1.
          default is True.

        tt_axis_annot: axis annotation tuple.
            boolean, categorical and quantitative axis annotation tuples are possible.
            t_axis_annot_boolean = (df_axis_annot, ls_z, s_true_color, s_false_color)
            t_axis_annot_categorical = (df_axis_annot, ls_z, ls_zcolor)
            t_axis_annot_quantitative = (df_axis_annot, ls_z, lr_low, lr_high, lls_color_palette)

            df_axis_annot: pandas datafarme for y or x axis annotation.
                the df_axis_annot index have to carry df_matrix index or column related labels.
                the df_axis_annot column have to carry all needed s_z and s_zcolor labels.

            ls_z: list of annotation labels which should be turned into annotation bars.

            s_true_color: string. color hex or name for True s_z values. e.g 'Yellow'.

            s_false_color: string. color hex or name for False s_z values. e.g. 'Black'.

            ls_zcolor: list of categorical s_z annotation related color column labels.

            lr_low: list of quantitative s_z annotation related minimum values.

            lr_high: list of quantitative s_z annotation related maximum values.

            lls_color_palette: list of quantitative s_z annotation related color palette lists.

        b_dendro: boolean, if True, the axis that not sums up to 1.
            get clustered with the specified s_method and s_metiric.
            if both axis sum up to 1, then the x axis get clustered.
            if False the axis order from the df_matrix is preserved.
            default is False.

        s_method:string. detailed description at
            https://docs.scipy.org/doc/scipy/reference/cluster.hierarchy.html
            default average (as in seaborn).

        s_metric: string. detailed description at
            https://docs.scipy.org/doc/scipy/reference/cluster.hierarchy.html
            default euclidean.

        b_optimal_ordering: boolean. detailed description at
            https://docs.scipy.org/doc/scipy/reference/cluster.hierarchy.html
            default is False (as in seaborn).

        i_px: integer. clusterbar pixel unit.
            by default the top dendrogram is 3 times this unit high and 12 times this unit width,
            the right dendrogram is 12 time this unit high and 3 times this unit width,
            the top annotation bars are 1 time this unit high and 12 times this unit width,
            the right annotation bars are 12 time this unit high and 1 time this unit width,
            the stackedbar is 12 time this unit high and 12 times this unit width.
            if you need smaller labels increase this unit and make the overall plot
            smaller with your browsers zoom function (Ctrl -).
            if you need bigger labels do the opposite.
            default is 64 pixels.

        i_height: integer. i_px * i_height specifies the stackedbar height. default is 12.

        i_width: integer. i_px * i_width specifies the stackedbar width. default is 12.

        i_min_border_px: integer. to specify left and bottom plot border padding
            which becomes available for axis labels. default is 128 pixels.

        s_filename: filename of the resulting html or png file.
            default is clusterbar.html

        s_filetitel: clusterbar plot title.
            this title will be visible as browser tab label and as main label on top of the plot
            default is None.

    output:
        clusterbar.html or clusterbar.png: resulting file
            with the s_filname attribute specified file name.

        o_layout: clusterbar bokeh layout object.

        ls_bar_axis: list of string with the leaves the same ordered as the bars.

    description:
        this function will return an interactive bokeh based clusterbar related
        html file, bokeh layout object, list of y axis and list x axis labels.
    """
    # index as string
    df_matrix.index = df_matrix.index.astype(str)
    df_matrix.columns = df_matrix.columns.astype(str)

    ls_yaxis = list(df_matrix.index)
    ls_xaxis = list(df_matrix.columns)

    # handle y and x axis name
    if (df_matrix.index.name == None):
        df_matrix.index.name = "y_axis"
    if (df_matrix.columns.name == None):
        df_matrix.columns.name = "x_axis"

    # bar color orientation
    es_key_color = set(ds_stack_color.keys())
    es_y_axis = set(df_matrix.index.values)
    es_x_axis = set(df_matrix.columns.values)
    if (len(es_y_axis.intersection(es_key_color)) == df_matrix.shape[0]):
        b_color_column = True
    else:
        b_color_column = False
    if (len(es_x_axis.intersection(es_key_color)) == df_matrix.shape[1]):
        b_color_row = True
    else:
        b_color_row = False
    # color error
    if (not b_color_column and not b_color_row):
        sys.exit("Error at bokehheat.clusterbar: {}".format(
            ds_error["matrix_color_none"].format(sorted(es_y_axis), sorted(es_x_axis), sorted(ds_stack_color))
        ))

    # bar sum up to 1 orientation
    if all((df_matrix.values.sum(axis=0) < 1.000000001) & (df_matrix.values.sum(axis=0) > 0.999999999)):
        b_sum1_column = True
    else:
        b_sum1_column = False
    if all((df_matrix.values.sum(axis=1) < 1.000000001) & (df_matrix.values.sum(axis=1) > 0.999999999)):
        b_sum1_row = True
    else:
        b_sum1_row = False
    # sum up to 1 error
    if (b_sum_to_1 and not b_sum1_column and not b_sum1_row):
        sys.exit("Error at bokehheat.clusterbar: {}".format(
            ds_error["matrix_stochastic_none"].format(df_matrix.values.sum(axis=0), df_matrix.values.sum(axis=1))
        ))

    # bar orientation
    b_bar_row = False
    b_bar_column = False
    # !left & right: right stochatstic matrix
    if (b_sum_to_1 and not b_sum1_column and b_sum1_row) \
        or (not b_sum_to_1 and not b_color_column and b_color_row):
        b_bar_row = True
        ls_stack_label = sorted(df_matrix.columns.values)
        s_axis = df_matrix.columns.name
    # (left & !right) | (left & right): left or doubly stochastic matrix
    elif (b_sum_to_1 and b_sum1_column and not b_sum1_row) or  (b_sum_to_1 and b_sum1_column and b_sum1_row) \
        or  (not b_sum_to_1 and b_color_column and not b_color_row) or (not b_sum_to_1 and b_color_column and b_color_row):
        b_bar_column = True
        ls_stack_label = sorted(df_matrix.index.values)
        s_axis = df_matrix.index.name
        if b_bar_row:
            b_bar_row = False
    # error case:
    else:
        sys.exit("Error at bokehheat.clusterbar: {}".format(
            ds_error["matrix_else"].format(b_sum_to_1, b_sum1_column, b_sum1_row, b_color_column, b_color_row)
        ))
    # bar stack color annotation
    ls_stack_color = [ds_stack_color[s_stack] for s_stack in ls_stack_label]
    df_stack_annot = pd.DataFrame([ls_stack_label, ls_stack_color], index=['stack_label','stack_color'], columns=ls_stack_label).T
    df_stack_annot.index.name = s_axis
    t_stack_annot = (df_stack_annot, ['stack_label'], ['stack_color'])


    # cluster y and x
    if (b_bar_row) and (b_dendro):  # y dendrogram for rows
        r_cophcorre, ls_yaxis, p_ydendro = cdendro(
            df_matrix,
            s_root='right',
            s_method=s_method,
            s_metric=s_metric,
            b_optimal_ordering=b_optimal_ordering,
        )
        p_ydendro.height = i_height * i_px
        p_ydendro.width = 3 * i_px
        p_ydendro.min_border_bottom = i_min_border_px
        p_ydendro.yaxis.visible = False
        p_ydendro.toolbar_location = None
        df_matrix = df_matrix.loc[ls_yaxis,:]
    if (b_bar_column) and (b_dendro):  # x dendrogram for columns
        r_cophcorre, ls_xaxis, p_xdendro = cdendro(
            df_matrix,
            s_root='top',
            s_method=s_method,
            s_metric=s_metric,
            b_optimal_ordering=b_optimal_ordering,
        )
        p_xdendro.height = 3 * i_px
        p_xdendro.width = i_width * i_px
        p_xdendro.min_border_left = i_min_border_px
        p_xdendro.xaxis.visible = False
        p_xdendro.toolbar_location = None
        df_matrix = df_matrix.loc[:,ls_xaxis]

    # generate heat stack
    p_stackedbar = stackedbar(
        df_matrix,
        ds_stack_color = ds_stack_color,
        b_sum_to_1 = b_sum_to_1,
    )
    p_stackedbar.height = i_height * i_px
    p_stackedbar.width = i_width * i_px
    p_stackedbar.min_border_left = i_min_border_px
    p_stackedbar.min_border_bottom = i_min_border_px
    p_stackedbar.toolbar_location="below"

    # link dendrogram
    if (b_bar_row) and (b_dendro):
        p_ydendro.y_range = p_stackedbar.y_range
    if (b_bar_column) and (b_dendro):
        p_xdendro.x_range = p_stackedbar.x_range

    # generate y and axis annotation
    lp_ybar = []
    lp_xbar = []
    es_ymatrix = set(df_matrix.index)
    es_xmatrix = set(df_matrix.columns)
    if (len(es_ymatrix) != df_matrix.shape[0]):
        sys.exit("Error at bokehheat.clusterbar: {}".format(
            ds_error["y_axis_unique"].format(list(df_matrix.index))
        ))
    if (len(es_xmatrix) != df_matrix.shape[1]):
        sys.exit("Error at bokehheat.clusterbar: {}".format(
            ds_error["x_axis_unique"].format(list(df_matrix.columns))
        ))

    for t_axis_annot in tt_axis_annot:

        # check if root is top or right
        es_axis = set(t_axis_annot[0].index)
        b_ok = False
        ls_root = []
        if (len(es_ymatrix.intersection(es_axis)) > 0) and (b_sum1_row):
            ls_root.append('right')
            b_ok = True
        if (len(es_xmatrix.intersection(es_axis)) > 0) and (b_sum1_column):
            ls_root.append('top')
            b_ok = True
        if not (b_ok):
            sys.exit("Error at bokehheat.clusterbar: {}".format(
                ds_error["axis_annot_none"].format(sorted(es_axis), sorted(es_ymatrix), sorted(es_xmatrix))
            ))

        # categorical
        # t_axis_annot = (df_axis_annot, ls_z, ls_zcolor)
        if (len(t_axis_annot) == 3):
            # extract relevant columns of the dataframe
            for n, s_bz in enumerate(t_axis_annot[1]):
                s_bzcolor = t_axis_annot[2][n]
                df_axis = t_axis_annot[0].loc[:,[s_bz, s_bzcolor]]
                df_axis.index = df_axis.index.astype(str)
                # get df_axis index name
                for s_root in ls_root:
                    # reorder df_axis and include missing values
                    if (s_root == 'top'):
                        df_axis = df_axis.reindex(df_matrix.columns)
                        df_axis = df_axis.loc[df_matrix.columns,:]
                        df_axis.index.name = df_matrix.columns.name
                    else:
                        df_axis = df_axis.reindex(df_matrix.index)
                        df_axis = df_axis.loc[df_matrix.index,:]
                        df_axis.index.name = df_matrix.index.name
                    # call cbar
                    p_bar = cbar(
                        df_axis_annot=df_axis.reset_index(),
                        s_yx=df_axis.index.name,
                        s_z=s_bz,
                        s_zcolor=s_bzcolor,
                        s_root=s_root,
                    )
                    p_bar.toolbar_location = None
                    if (s_root == 'top'):
                        p_bar.x_range = p_stackedbar.x_range
                        p_bar.height = i_px
                        p_bar.width = i_width * i_px
                        p_bar.min_border_left = i_min_border_px
                        lp_xbar.append(p_bar)
                    else:
                        p_bar.y_range = p_stackedbar.y_range
                        p_bar.height = i_height * i_px
                        p_bar.width = i_px
                        p_bar.min_border_bottom = i_min_border_px
                        lp_ybar.append(p_bar)

        # boolean
        # t_axis_annot_boolean = (df_axis_annot, ls_z, s_true_color, s_false_color)
        elif (len(t_axis_annot) == 4):
            s_true_color = t_axis_annot[2]
            s_false_color = t_axis_annot[3]
            # extract relevant columns of the dataframe
            for n, s_bz in enumerate(t_axis_annot[1]):
                se_axis = t_axis_annot[0].loc[:,s_bz]
                se_axis.index = se_axis.index.astype(str)
                # get se_axis index name
                for s_root in ls_root:
                    # reorder df_axis and include missing values
                    if (s_root == 'top'):
                        se_axis = se_axis.reindex(df_matrix.columns)
                        se_axis = se_axis.loc[df_matrix.columns]
                        se_axis.index.name = df_matrix.columns.name
                    else:
                        se_axis = se_axis.reindex(df_matrix.index)
                        se_axis = se_axis.loc[df_matrix.index]
                        se_axis.index.name = df_matrix.index.name
                    # call bbar
                    p_bar = bbar(
                        df_axis_annot=se_axis.reset_index(),
                        s_yx=se_axis.index.name,
                        s_z=s_bz,
                        s_true_color=t_axis_annot[2],
                        s_false_color=t_axis_annot[3],
                        s_root=s_root,
                    )
                    p_bar.toolbar_location = None
                    if (s_root == 'top'):
                        p_bar.x_range = p_stackedbar.x_range
                        p_bar.height = i_px
                        p_bar.width = i_width * i_px
                        p_bar.min_border_left = i_min_border_px
                        lp_xbar.append(p_bar)
                    else:
                        p_bar.y_range = p_stackedbar.y_range
                        p_bar.height = i_height * i_px
                        p_bar.width = i_px
                        p_bar.min_border_bottom = i_min_border_px
                        lp_ybar.append(p_bar)

        # quantitative
        # t_axis_annot = (df_axis_annot, ls_z, lr_low, lr_high, lls_color_palette)
        elif (len(t_axis_annot) == 5):
            # extract relevant columns of the dataframe
            for n, s_bz in enumerate(t_axis_annot[1]):
                r_blow = t_axis_annot[2][n]
                r_bhigh = t_axis_annot[3][n]
                ls_bcolor = t_axis_annot[4][n]
                se_axis = t_axis_annot[0].loc[:,s_bz]
                se_axis.index = se_axis.index.astype(str)
                # get se_axis index name
                if (se_axis.index.name == None):
                    se_axis.index.name = "variable"
                for s_root in ls_root:
                    # reorder df_axis and include missing values
                    if (s_root == 'top'):
                        se_axis = se_axis.reindex(df_matrix.columns)
                        se_axis = se_axis.loc[df_matrix.columns]
                    else:
                        se_axis = se_axis.reindex(df_matrix.index)
                        se_axis = se_axis.loc[df_matrix.index]
                    # call qbar
                    p_bar = qbar(
                        df_axis_annot=se_axis.reset_index(),
                        s_yx=se_axis.index.name,
                        s_z=s_bz,
                        r_low=r_blow,
                        r_high=r_bhigh,
                        ls_color_palette=ls_bcolor,
                        s_root=s_root,
                    )
                    p_bar.toolbar_location = None
                    if (s_root == 'top'):
                        p_bar.x_range = p_stackedbar.x_range
                        p_bar.height = i_px
                        p_bar.width = i_width * i_px
                        p_bar.min_border_left = i_min_border_px
                        lp_xbar.append(p_bar)
                    else:
                        p_bar.y_range = p_stackedbar.y_range
                        p_bar.height = i_height * i_px
                        p_bar.width = i_px
                        p_bar.min_border_bottom = i_min_border_px
                        lp_ybar.append(p_bar)
        # error
        else:
            sys.exit("Error at bokehheat.clusterbar: {}".format(
                ds_error["axis_annot_invalid"].format(t_axis_annot)
            ))

    # add  stack annotation to axis annotation
    lt_axis_annot = list(tt_axis_annot)
    lt_axis_annot.append(t_stack_annot)

    # generate axis annotation legend
    lp_xylegend = cmbarlegend(
        tt_axis_annot=lt_axis_annot,
        es_ymatrix=es_ymatrix,
        es_xmatrix=es_xmatrix,
        i_px=i_px,
        i_height=i_height,
        i_width=i_width,
    )

    ### put output top down together ###
    reset_output()
    output_file(s_filename, title=s_filetitel)
    lp_out = []
    lp_toptop = []
    lp_top = []
    llp_middle = []
    lp_bottom = []
    # check for top axis annotation legend
    if not (lp_xylegend[0] is None):
        #lp_xylegend[0].min_border_left = i_min_border_px
        lp_toptop.append(lp_xylegend[0])
    # set main titel
    if (s_filetitel is None):
        p_title = figure(title = '')
    else:
        p_title = figure(title = s_filetitel)
    p_title.title.text_font_style = "bold"
    p_title.title.text_font_size = "1.5em"
    p_title.title.align = "center"
    #p_title.title_location = "below"
    p_title.height = i_px
    p_title.width = i_width * i_px
    if not (lp_xylegend[0] is None):
        p_title.height = lp_xylegend[0].height
        p_title.width = int(p_stackedbar.width - lp_xylegend[0].width)
    p_title.toolbar_location = None
    lp_toptop.append(p_title)
    # check for top dendrogram
    if (b_dendro) and (b_bar_column):
        lp_top.append(p_xdendro)
    # check for top axis annotation
    for p_xbar in lp_xbar:
        llp_middle.append([p_xbar])
    # all
    lp_bottom.append(p_stackedbar)
    # check for right side axis annotation
    for p_ybar in lp_ybar:
        lp_bottom.append(p_ybar)
    # check for right side dendrogram
    if (b_dendro) and (b_bar_row):
        lp_bottom.append(p_ydendro)
    # check for right side  axis annotation legend
    if not (lp_xylegend[1] is None):
        lp_bottom.append(lp_xylegend[1])
    # kick out toptop row when only None
    if (len(lp_toptop) > 0):
        lp_out.append(lp_toptop)
    # kick out top row when only None
    if (len(lp_top) > 0):
        lp_out.append(lp_top)
    # kick out middle row when no top axis annotation
    if (len(llp_middle) > 0):
        # check for top axis annotation
        for lp_middle in llp_middle:
            lp_out.append(lp_middle)
    # bottom row has always stackedbar
    lp_out.append(row(lp_bottom))

    # output plot
    s_path = '/'.join(s_filename.replace('\\','/').split('/')[:-1])
    if (len(s_path) > 0):
        os.makedirs(s_path, exist_ok=True)
    o_layout = layout(lp_out, sizing_mode='fixed')
    if (s_filename.endswith(".html")):
        save(o_layout)
    elif (s_filename.endswith(".png")):
        export_png(o_layout, filename=s_filename)
    else:
        sys.exit("Error at bokehheat.clusterbar: {}".format(
            ds_error["file_type"].format(s_root)
        ))
    # output function
    if (b_bar_row):
        ls_bar_axis = ls_yaxis
    else:
        ls_bar_axis = ls_xaxis
    return(o_layout, ls_bar_axis)


'''
if __name__ == '__main__':
    ###
    # test and demo case
    # run:
    #    python3 heat.py
    ###

    # library
    from bokeh.palettes import Reds9,  RdBu11, RdYlBu11, YlGn8, Colorblind8
    import numpy as np
    import pandas as pd

    ### test heatmap ###
    print('\ntest cluster heatmap function ...')

    # prepare some data
    ls_sample = ['sampleA','sampleB','sampleC','sampleD','sampleE','sampleF','sampleG','sampleH']
    ls_variable = ['geneA','geneB','geneC','geneD','geneE','geneF','geneG','geneH', 'geneI']
    ar_z = np.random.randn(9,8)
    df_matrix = pd.DataFrame(ar_z)
    df_matrix.index = ls_variable
    df_matrix.columns = ls_sample
    df_matrix.index.name = 'y'
    df_matrix.columns.name = 'x'

    df_variable = pd.DataFrame({
        'y': ls_variable,
        'genereal': list(np.random.random(9) * 2 - 1),
        'genetype': ['Ligand','Ligand','Ligand','Ligand','Ligand','Ligand','Receptor','Receptor','Receptor'],
        'genetype_color': ['Cyan','Cyan','Cyan','Cyan','Cyan','Cyan','Cornflowerblue','Cornflowerblue','Cornflowerblue'],
        'geneboole': [False, False, False, True, True, True, False, False, False],
    })
    df_variable.index = df_variable.y

    df_sample = pd.DataFrame({
        'x': ls_sample,
        'age_year': list(np.random.randint(0,101, 8)),
        'sampletype': ['LumA','LumA','LumA','LumB','LumB','Basal','Basal','Basal'],
        'sampletype_color': ['Purple','Purple','Purple','Magenta','Magenta','Orange','Orange','Orange'],
        'sampleboole': [False, False, True, True, True, True, False, False],
    })
    df_sample.index = df_sample.x

    t_ycat = (
        df_variable,
        ['genetype'],
        ['genetype_color'],
    )
    t_yboole = (
        df_variable,
        ['geneboole'],
        'Red',  # True
        'Maroon',  # False
    )
    t_yquant = (
        df_variable,
        ['genereal'],
        [-1],
        [1],
        [Colorblind8],
    )
    t_xcat = (
        df_sample,
        ['sampletype'],
        ['sampletype_color'],
    )
    t_xboole = (
        df_sample,
        ['sampleboole'],
        'Red',  # True
        'Maroon',  # False
    )
    t_xquant = (
        df_sample,
        ['age_year'],
        [0],
        [128],
        [YlGn8],
    )
    tt_catboolquant = (t_ycat, t_yboole, t_yquant, t_xquant, t_xboole, t_xcat)
    #tt_catboolquant = (t_ycat, t_yboole, t_yquant)
    #tt_catboolquant = (t_xquant, t_xboole, t_xcat)

    # processing
    #s_file = "theclustermap.html"
    s_file = "theclustermap.png"
    o_clustermap, ls_xaxis, ls_yaxis = clustermap(
        df_matrix = df_matrix,
        ls_color_palette = RdBu11,
        r_low = -3,
        r_high = 3,
        s_z = "log2",
        tt_axis_annot = tt_catboolquant,
        b_ydendro = True,
        b_xdendro = True,
        #s_method='average',
        #s_metric='euclidean',
        #b_optimal_ordering=True,
        i_px = 64,
        i_height = 12,
        i_width = 12,
        s_filename=s_file,
        s_filetitel="the Clustermap",
    )

    # output
    print(f"\ncheck out: {s_file}")
    print(f"y axis is: {ls_yaxis}")
    print(f"x axis is: {ls_xaxis}")


    ## test stackedbar with a fusion of left stochastic matrixes ###
    print('\ntest cluster stackedbar function ...')

    # prepare some data
    # data
    llr_y = [
        # dmso                              # bez235                            # trametinib                        # trametinib_bez235
        [0.000, 0.377, 0.187, 0.197, 0.0] + [0.652, 0.053, 0.000, 0.000, 0.0] + [0.887, 0.251, 0.981, 0.000, 0.0] + [0.360, 0.266, 0.089, 0.263, 0.0],
        [0.558, 0.560, 0.615, 0.512, 0.0] + [0.000, 0.747, 0.000, 0.362, 0.0] + [0.005, 0.679, 0.000, 0.853, 0.0] + [0.201, 0.631, 0.000, 0.136, 0.0],
        [0.211, 0.028, 0.000, 0.285, 0.0] + [0.000, 0.162, 0.000, 0.495, 0.0] + [0.062, 0.051, 0.000, 0.000, 0.0] + [0.153, 0.000, 0.670, 0.315, 0.0],
        [0.225, 0.029, 0.192, 0.000, 0.0] + [0.340, 0.030, 0.992, 0.135, 0.0] + [0.027, 0.000, 0.000, 0.128, 0.0] + [0.218, 0.035, 0.173, 0.218, 0.0],
        [0.006, 0.006, 0.006, 0.006, 1.0] + [0.008, 0.008, 0.008, 0.008, 1.0] + [0.019, 0.019, 0.019, 0.019, 1.0] + [0.068, 0.068, 0.068, 0.068, 1.0],
    ]

    # y-axis
    ls_y = ['basal_y','mesenchymal_y','luminal_y','negative_y','dead_y']

    # y-axis  color
    ls_y_color = ['#ff0000','#008000','#0033cc','#ffd700','#c0c0c0']  # ['red','green','blue','yellow','black']
    ds_y_color = dict(zip(ls_y, ls_y_color))


    # x-axis
    ls_x_treatment = [
        'dmso','dmso','dmso','dmso','dmso',
        'bez235','bez235','bez235','bez235','bez235',
        'trametinib','trametinib','trametinib','trametinib','trametinib',
        'bez235_trametinib','bez235_trametinib','bez235_trametinib','bez235_trametinib','bez235_trametinib',
    ]

    ls_x_diffstate = [
        'basal_x','mesenchymal_x','luminal_x','negative_x','dead_x',  # dmso
        'basal_x','mesenchymal_x','luminal_x','negative_x','dead_x',  # bez235
        'basal_x','mesenchymal_x','luminal_x','negative_x','dead_x',  # trametinib
        'basal_x','mesenchymal_x','luminal_x','negative_x','dead_x',  # bez235_trametinib
    ]

    ls_x = []
    for i in range(len(ls_x_diffstate)):
        s_x = f'{ls_x_treatment[i]}_{ls_x_diffstate[i]}'
        ls_x.append(s_x)

    # x-axis color
    ls_x_treatmnet_color = ['#ff9900'] * 5 + ['#cc9900'] * 5 + ['#996600'] * 5 + ['#663300'] * 5
    ls_x_diffstate_color = ls_y_color * 4

    # pack data matrix
    df_matrix = pd.DataFrame(llr_y, columns=ls_x, index=ls_y)
    df_matrix.index.name = 'y'
    df_matrix.columns.name = 'x'

    # process stackedbar
    #p = stackedbar(df_matrix=df_matrix, ds_stack_color=ds_stack_color, b_sum_to_1=True)
    #show(p)

    # pack annotation
    df_sample = pd.DataFrame({
        'x': ls_x,
        'source_diffstate': ls_x_diffstate,
        'source_diffstate_color': ls_x_diffstate_color,
        'treatment': ls_x_treatment,
        'treatment_color': ls_x_treatmnet_color,
    })
    df_sample.index = df_sample.x

    t_xcat_treatment = (
        df_sample,
        ['treatment'],
        ['treatment_color'],
    )
    t_xcat_diffstate = (
        df_sample,
        ['source_diffstate'],
        ['source_diffstate_color'],
    )
    tt_xcat = (t_xcat_treatment, t_xcat_diffstate,)

    # process clusterbar
    #o_clusterbar, ls_xaxis, ls_yaxis = clusterbar(
    #s_file = 'theclusterbar.html'
    s_file = 'theclusterbar.png'
    o_clusterbar, ls_bar_axis = clusterbar(
        df_matrix = df_matrix,
        ds_stack_color = ds_y_color,
        b_sum_to_1 = True,
        tt_axis_annot = tt_xcat,
        b_dendro = True,
        s_method = 'average',
        s_metric = 'euclidean',
        b_optimal_ordering = True,
        i_px = 64,
        i_height = 12,
        i_width = 12,
        i_min_border_px = 128,
        s_filename = s_file,
        s_filetitel = 'differentation state transition matrix',
    )

    # output
    print(f"\ncheck out: {s_file}")
    print(f"bar axis is: {ls_bar_axis}")
'''
