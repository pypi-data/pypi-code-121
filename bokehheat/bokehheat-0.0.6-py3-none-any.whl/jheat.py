###
# title: jheat.py
#
# language: python 3.7
# dependencies: matplotlib, pandas, scipy
# date: 2019-02
# license: >= GPLv3
# authors: bue, jenny
#
# install:
#    pip3 install bokehheat
#
# load:
#    from bokehheat import heat
#
#    help(heat.jdendro)
#    help(heat.jheatmap)
#    help(heat.jclustermap)
#
# test run:
#    python3 jheat.py
#
# description:
#     A python3 bokeh based categorical dendrogram and heatmap plotting library.
###

# library
import csv
import json
from matplotlib import colors
import numpy as np
import os
import pandas as pd
import pkg_resources
from scipy.cluster.hierarchy import cophenet, dendrogram, linkage
from scipy.spatial.distance import pdist
import sys

# error handling
with open(pkg_resources.resource_filename("bokehheat", "error.json")) as f_json:
    ds_error = json.load(f_json)


# functions
# the jtreeview dendro
def jdendro(
        df_matrix,
        s_root = 'left',
        s_method = 'single',
        s_metric = 'euclidean',
        b_optimal_ordering = True,
        s_filename="jdendrogram",
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

        s_filename: string. file name without extension.
            default jdendrogram.

    output:
        r_cophcorre: real. cophnetic correlation coefficent. check out
            https://en.wikipedia.org/wiki/Cophenetic

        ls_cat_sorted: list of string with the leaves ordered by
           the applied cluster algorithmen.

        s_filename_ext: jtree compatible dendrogram gtr or atr file and filename.
            cophnetic correlation coefficent is integrated in filename. check out
            https://en.wikipedia.org/wiki/Cophenetic

        s_filename_cdt: jtree compatible heatmap cdt file and filename.

    description:
        utilizes scipys pdist, linkage, dendrogram and copdist function
        to generate a javatreeview compatible dendrogram gtr or atr file and filename.

        thank you to Jorn Hees who wrote an excellent tutorial about
        hierarchical clustering and dendrograms in scipy and Daniel Russo
        who wrote the only bokeh based dendrogram implementation I was aware of
        at the time I was writing this code.
        + https://joernhees.de/blog/2015/08/26/scipy-hierarchical-clustering-and-dendrogram-tutorial/
        + https://russodanielp.github.io/plotting-a-heatmap-with-a-dendrogram-using-bokeh.html
    '''
    # index or column dendrogram
    if (s_root in {"left","right"}):
        s_ext = "gtr"
    elif s_root in {'top','bottom'}:
        df_matrix = df_matrix.T
        s_ext = "atr"
    else:
        sys.exit("Error at bokehheat.jdendro: {}".format(
            ds_error["root_unknown_j"].format(t_axis_annot)
        ))

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

    # distance trafo
    ar_z_distance = -2 *  ar_z_linkage[:,2] / ar_z_linkage[:,2].max() + 1

    # linkage number to nodes and clusters
    ls_node = list(df_matrix.index)
    ll_z_linkage = [["NODEID","LEFT","RIGHT","CORRELATION","NODECOLOR"],]
    for i_node, ar_z_linkage_row in enumerate(ar_z_linkage):
        s_node = f"NODE{i_node}X"
        ls_node.append(s_node)
        l_z_linkage = list(ar_z_linkage_row)
        s_cluster0 = ls_node[int(l_z_linkage[0])]
        s_cluster1 = ls_node[int(l_z_linkage[1])]
        r_distance = ar_z_distance[i_node]
        s_hexcolor = colors.to_hex(d_dendro["color_list"][i_node])
        l_z_linkage = [s_node, s_cluster0, s_cluster1, r_distance, s_hexcolor]
        ll_z_linkage.append(l_z_linkage)

    # write to file
    s_filename_ext = f"{s_filename}.{s_ext}"
    with open(s_filename_ext, "w") as f_csv:
        o_writer = csv.writer(f_csv, delimiter="\t")
        o_writer.writerows(ll_z_linkage)

    # generate tree sky if jdendro not was called form jclustermap
    s_filename_cdt = f"{s_filename}.cdt"
    if not os.path.isfile(s_filename_cdt):
        if (s_ext == "gtr"):
            ll_tree_sky = [["GID","NAME","UNIQUEID", f"coph_{round(r_cophcorre, 3)}"],]
            for s_leave in ls_cat_sorted:
                ll_tree_sky.append([s_leave,s_leave,s_leave,0])

        else: # s_ext == atr
            ll_tree_sky = [
                ["GID","NAME","UNIQUEID"] + ls_cat_sorted,
                ["AID","",""] + ls_cat_sorted,
                [f"coph_{round(r_cophcorre, 3)}"] * 3 + [0] * len(ls_cat_sorted),
            ]

        # write to file
        with open(s_filename_cdt, "w") as f_csv:
            o_writer = csv.writer(f_csv, delimiter="\t")
            o_writer.writerows(ll_tree_sky)

    # output
    return(r_cophcorre, ls_cat_sorted, s_filename_ext, s_filename_cdt)



# the heatmap
def jheatmap(
        df_matrix,
        tt_axis_annot = (),
        s_xcolor = None,
        s_ycolor = None,
        s_filename = "jheatmap",
    ):
    """
    input:
        df_matrx: a dataframe in same xy orientation as the final heatmap.
          the index should cary the y axis label.
          the column should cary the x axis label.
          the matrix as such should only cary the z axis values.

        tt_axis_annot: axis annotation tuple.
            categorical and quantitative axis annotation tuples are possible.
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

        s_y/xcolor: string. specifies column label for which y/x axis heatmap label should be colored.
            in javatreeview heatmap only one annotation bar per axis can be colored.

        s_filename: string. file name without extension.
            default jheatmap.

    output:
        s_filename_ext: jtree compatible heatmap cdt file and filename.

    description:
        this function will return a javatreeview compatible heatmap cdt file.
        the color are representing the z value.
    """
    # handle input
    es_index = set(df_matrix.index)
    es_column = set(df_matrix.columns)

    # basic transformastion
    df_manipu = df_matrix.copy()
    df_manipu.columns.name = None
    df_manipu.insert(0, "NAME", df_matrix.index)
    df_manipu.insert(1, "UNIQUEID", df_matrix.index)
    df_manipu.insert(2,"GWEIGHT", 1)
    df_manipu = df_manipu.T
    df_manipu.insert(0, "AID", df_manipu.index)
    df_manipu.insert(1, "EWEIGHT", 1)
    df_manipu = df_manipu.T
    df_manipu.loc[["AID","EWEIGHT"], ["NAME","UNIQUEID","GWEIGHT"]] = np.nan

    # additional annotation
    for t_axis_annot in tt_axis_annot:

        # extract relevant columns of the dataframe
        for n, s_bz in enumerate(t_axis_annot[1]):

            # get data column
            df_axis = t_axis_annot[0].loc[:,[s_bz]]
            es_axis = set(df_axis.index)

            # orientation
            s_weight = "GWEIGHT"
            if (es_axis == es_column):
                s_weight = "EWEIGHT"
                df_manipu = df_manipu.T

            # merge to output
            ls_column = list(df_manipu.columns)
            i_weight = ls_column.index(s_weight)
            ls_column.insert(i_weight, s_bz)
            df_manipu =  pd.merge(df_manipu, df_axis, left_index=True, right_index=True, how="left") #.replace({np.nan: None})
            df_manipu = df_manipu.reindex(ls_column, axis=1)

            # deal with color
            if (s_bz in {s_ycolor, s_xcolor}):

                # categorical
                # t_axis_annot = (df_axis_annot, ls_z, ls_zcolor)
                if (len(t_axis_annot) == 3):
                    # hex color trafo
                    s_bzcolor = t_axis_annot[2][n]
                    df_color = t_axis_annot[0].loc[:,[s_bzcolor]]
                    df_color.columns = ["FGCOLOR"]
                    d_hex = {}
                    [d_hex.update({s_color: colors.to_hex(s_color)}) for s_color in df_color.FGCOLOR]
                    df_color.replace(d_hex, inplace=True)

                # boolean
                # t_axis_annot_boolean = (df_axis_annot, ls_z, s_true_color, s_false_color)
                elif (len(t_axis_annot) == 4):
                    # hex color trafo
                    s_true_color = t_axis_annot[2]
                    s_false_color = t_axis_annot[3]
                    df_color = t_axis_annot[0].loc[:,[s_bz]]
                    df_color.columns = ["FGCOLOR"]
                    df_color.replace({True: s_true_color, False: s_false_color}, inplace=True)
                    d_hex = {}
                    [d_hex.update({s_color: colors.to_hex(s_color)}) for s_color in df_color.FGCOLOR]
                    df_color.replace(d_hex, inplace=True)

                # quantitative
                # t_axis_annot = (df_axis_annot, ls_z, lr_low, lr_high, lls_color_palette)
                elif (len(t_axis_annot) == 5):
                    # hex color trafo
                    r_low = t_axis_annot[2][n]
                    r_high = t_axis_annot[3][n]
                    ls_color = t_axis_annot[4][n]
                    df_color = t_axis_annot[0].loc[:,[s_bz]]
                    o_cmap = colors.LinearSegmentedColormap.from_list("pwn_cmap", ls_color)
                    df_color["FGCOLOR"] = [colors.to_hex(o_cmap((r_color - r_low) / (r_high - r_low))) for r_color in df_color.loc[:,s_bz]]
                    df_color.drop(s_bz, axis=1, inplace=True)

                # error
                else:
                    sys.exit("Error at bokehheat.jheatmap: {}".format(
                    ds_error["axis_annot_invalid"].format(t_axis_annot)
                ))

                # merge color to output
                ls_column = list(df_manipu.columns)
                i_weight = ls_column.index(s_weight)
                ls_column.insert(i_weight, "FGCOLOR")
                df_manipu =  pd.merge(df_manipu, df_color, left_index=True, right_index=True, how="left") #.replace({np.nan: None})
                df_manipu = df_manipu.reindex(ls_column, axis=1)

            # orientation
            if (es_axis == es_column):
                df_manipu = df_manipu.T

    # set index name and write to file
    df_manipu.index.name = "GID"
    s_filename_ext = f"{s_filename}.cdt"
    df_manipu.to_csv(s_filename_ext, sep="\t")

    # output
    return(s_filename_ext)



# the cluster heatmap
def jclustermap(
        df_matrix,
        tt_axis_annot = (),
        s_xcolor = None,
        s_ycolor = None,
        b_xdendro = False,
        b_ydendro = False,
        s_method = 'average',
        s_metric = 'euclidean',
        b_optimal_ordering = False,
        s_filename = "jclustermap",
    ):
    """
    input:
        df_matrx: a dataframe in same xy orientation as the final heatmap.
            the index have to cary the y axis label.
            the column have to cary the x axis label.
            the matrix as such should only cary the z axis values.

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

        b_ydendro and b_xdendro: boolean, if True the y respective x axis
            get clustered with the specified s_method and s_metiric.
            if False the axis order from the df_matrix is preserved.
            default is False.

        s_y/xcolor: string. specifies column label for which y/x axis heatmap label should be colored.
            in javatreeview heatmap only one annotation bar per axis can be colored.

        s_method:string. detailed description at
            https://docs.scipy.org/doc/scipy/reference/cluster.hierarchy.html
            default average (as in seaborn).

        s_metric: string. detailed description at
            https://docs.scipy.org/doc/scipy/reference/cluster.hierarchy.html
            default euclidean.

        b_optimal_ordering: boolean. detailed description at
          https://docs.scipy.org/doc/scipy/reference/cluster.hierarchy.html
          default is False (as in seaborn).

        s_filename: filename of the resulting files, without file extension.
            default is jclustermap,

    output:
        ls_filename: jtree compatible cdt heatmap and  gtr, atr dendrogram files
            and filename list.

        ls_yaxis: list of string with the leaves the same ordered
            as the heatmap y axis.

        ls_xaxis: list of string with the leaves the same ordered
            as the heatmap x axis.

    description:
        this function will javatreeview compatible cdt heatmap and gtr, atr dendrogram files
        and a list of ordered y axis x axis labels.
    """

    ls_filename = []
    ls_yaxis = list(df_matrix.index)
    ls_xaxis = list(df_matrix.columns)

    # cluster y and x
    if (b_ydendro):
        r_cophcorre, ls_yaxis, s_ydendro_file, s_cdt_file, = jdendro(
            df_matrix,
            s_root='right',
            s_method=s_method,
            s_metric=s_metric,
            b_optimal_ordering=b_optimal_ordering,
            s_filename=s_filename,
        )
        ls_filename.append(s_ydendro_file)
        os.remove(s_cdt_file)

    if (b_xdendro):
        r_cophcorre, ls_xaxis, s_xdendro_file, s_cdt_file = jdendro(
            df_matrix,
            s_root='top',
            s_method=s_method,
            s_metric=s_metric,
            b_optimal_ordering=b_optimal_ordering,
            s_filename=s_filename,
        )
        ls_filename.append(s_xdendro_file)
        os.remove(s_cdt_file)

    # generate heat map
    df_matrix = df_matrix.loc[ls_yaxis, ls_xaxis]
    s_heatmap_file = jheatmap(
        df_matrix,
        tt_axis_annot=tt_axis_annot,
        s_xcolor=s_xcolor,
        s_ycolor=s_ycolor,
        s_filename=s_filename,
    )
    ls_filename.append(s_heatmap_file)

    # output
    return(ls_filename, ls_yaxis, ls_xaxis)  #o_layout replaced by ls_file

"""
if __name__ == '__main__':
    ###
    # test and demo case
    # run:
    #    python3 jheat.py
    ###

    # library
    from bokeh.palettes import Reds9, RdBu11, RdYlBu11, YlGn8, Colorblind8
    import numpy as np
    import pandas as pd

    # prepare some data
    ls_sample = ['sampleA','sampleB','sampleC','sampleD','sampleE','sampleF','sampleG','sampleH']
    ls_variable = ['geneA','geneB','geneC','geneD','geneE','geneF','geneG','geneH', 'geneI']
    ar_z = np.random.rand(9,8) * 2 -1
    df_matrix = pd.DataFrame(ar_z, index=ls_variable, columns=ls_sample)
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

    #'''
    t_out = jdendro(
        df_matrix=df_matrix,
        s_root = 'left',
        s_method = 'single',
        s_metric = 'euclidean',
        b_optimal_ordering = True,
        s_filename = "jdendro_gtr",
    )
    print(f"{t_out}\n")
    #'''

    #'''
    t_out = jdendro(
        df_matrix=df_matrix,
        s_root = 'top',
        s_method = 'single',
        s_metric = 'euclidean',
        b_optimal_ordering = True,
        s_filename = "jdendro_atr",
    )
    print(f"{t_out}\n")
    #'''

    #'''
    s_out =  jheatmap(
        df_matrix=df_matrix,
        tt_axis_annot = tt_catboolquant,
        s_xcolor = "age_year",
        s_ycolor = "geneboole",
        s_filename = "jheatmap",
    )
    print(f"{s_out}\n")
    #'''

    #'''
    t_out = jclustermap(
        df_matrix=df_matrix,
        tt_axis_annot = tt_catboolquant,
        s_xcolor = "age_year",
        s_ycolor = "genetype",
        b_xdendro = True,
        b_ydendro = True,
        s_filename = "jclustermap",
    )
    print(f"{t_out}\t")
    #'''
"""
