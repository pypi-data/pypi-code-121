#####
# title: test_heat.py
#
# language: python3
# author: bue
# date: 2022-03-10
# license: GPL>=3
#
# description:
#   pytest unit test library for heat.py
#   + https://docs.pytest.org/
#
#   note:
#   assert actual == expected, message
#   == value equality
#   is reference equality
#   pytest.approx for real values
#####


from bokehheat import heat
from bokeh import palettes
import numpy as np
import os
import pandas as pd

# generare test data
ls_variable = ['gene_A','gene_B','gene_C','gene_D']
ls_observation = ['sample_A','sample_B','sample_C']
# stacked bar
a_matrix_bar = np.array([[1/10, 1/10, 3/10], [2/10, 1/10, 2/10], [3/10, 3/10, 2/10], [4/10, 5/10, 3/10]])
df_matrix_bar = pd.DataFrame(a_matrix_bar, index=ls_variable, columns=ls_observation)
# heat map
a_matrix_map = np.array(range(4*3))
a_matrix_map.shape = (4,3)
df_matrix_map = pd.DataFrame(a_matrix_map, index=ls_variable, columns=ls_observation)

ds_stack_color = {
    # gene
    'gene_A': 'Cyan',
    'gene_B': 'Blue',
    'gene_C': 'Navy',
    'gene_D': 'Purple',
}


# generate some gene annotation
df_variable = pd.DataFrame({
    'y': ls_variable,
    'gene_real': [-0.3, 0, +0.3, +0.6],
    'gene_cat': ['Ligand','Ligand','Receptor','Receptor'],
    'gene_cat_color': ['Cyan','Cyan','Cornflowerblue','Cornflowerblue'],
    'gene_boole': [False, False, False, True],
})
df_variable.set_index('y', inplace=True)


# generate some sample annotation
df_observation = pd.DataFrame({
    'x': ls_observation,
    'age_year': [1,2,3],
    'sievert': [3,2,1],
    'sample_cat1': ['LumA','LumB','Basal'],
    'sample_cat1_color': ['Purple','Magenta','Orange'],
    'sample_cat2': ['Primary','Primary','Metastasis'],
    'sample_cat2_color': ['Brown','Brown','Black'],
    'sample_boole1': [False, False, True],
    'sample_boole2': [False, True, True],
})
df_observation.set_index('x', inplace=True)

# generate annotation bars
t_yboole = (df_variable, ['gene_boole'],'Red','Maroon')  # data, boolen columns, True color, False color
t_ycat = (df_variable, ['gene_cat'], ['gene_cat_color'])  # data, categorical columns, categorical colors
t_yquant = (df_variable, ['gene_real'], [-1], [1], [palettes.YlGn8[::-1]])  # data, real columns, min values, max values, real colormaps

t_xboole = (df_observation, ['sample_boole1','sample_boole2'],'Red','Maroon')  # data, boolen column, True color, False color
t_xcat = (df_observation, ['sample_cat1','sample_cat2'], ['sample_cat1_color','sample_cat2_color'])  # data, categorical columns, categorical colors
t_xquant = (df_observation, ['age_year','sievert'], [0,0], [4,4], [palettes.YlGn8,palettes.Cividis8])  # data, real columns, min values, max values, real colormaps

tt_boolecatquant_map = (t_yboole, t_ycat, t_yquant, t_xquant, t_xcat, t_xboole)
tt_boolecatquant_bar = (t_xquant, t_xcat, t_xboole)


### elementar plots ###

class TestCdendro(object):
    ''' test for heat.cdendro '''

    def test_cdendro(self):
        # const
        dls_result = {
            'left': ['gene_D', 'gene_C', 'gene_B', 'gene_A'],
            'right': ['gene_D', 'gene_C', 'gene_B', 'gene_A'],
            'top': ['sample_C', 'sample_B', 'sample_A'],
            'bottom': ['sample_C', 'sample_B', 'sample_A'],
        }
        # generate cdendro
        for s_root in ['left', 'right', 'top', 'bottom']:
            print(f'process test_cdendro s_root: {s_root} ...')
            r_cophcorre, ls_cat_sorted, p = heat.cdendro(
                df_matrix = df_matrix_map,
                s_root = s_root,
                s_method = 'single',
                s_metric = 'euclidean',
                b_optimal_ordering = True,
            )
            assert np.all(ls_cat_sorted == dls_result[s_root])


class TestQbar(object):
    ''' test for heat.qbar '''

    def test_qbar(self):
        # generate qbar
        for s_root in ['left', 'right', 'top', 'bottom']:
            print(f'process test_qbar s_root: {s_root} ...')
            p = heat.qbar(
                df_axis_annot = df_variable.reset_index(),
                s_yx = 'y',
                s_z = 'gene_real',
                r_low = -1,
                r_high = 1,
                ls_color_palette = palettes.YlGn8[::-1],
                s_root = s_root,
            )
            assert str(type(p)) == "<class 'bokeh.plotting.figure.Figure'>"


class TestCbar(object):
    ''' test for heat.cbar '''

    def test_cbar(self):
        # generate cbar
        for s_root in ['left', 'right', 'top', 'bottom']:
            print(f'process test_cbar s_root: {s_root} ...')
            p = heat.cbar(
                df_axis_annot = df_variable.reset_index(),
                s_yx = 'y',
                s_z = 'gene_cat',
                s_zcolor = 'gene_cat_color',
                s_root = s_root,
            )
            assert str(type(p)) == "<class 'bokeh.plotting.figure.Figure'>"


class TestBbar(object):
    ''' test heat.bbar '''

    def test_bbar(self):
        # generate bbar
        for s_root in ['left', 'right', 'top', 'bottom']:
            print(f'process test_bbar s_root: {s_root} ...')
            p= heat.bbar(
                df_axis_annot = df_variable.reset_index(),
                s_yx = 'y',
                s_z = 'gene_boole',
                s_true_color = 'yellow',
                s_false_color = 'black',
                s_root = s_root,
            )
            assert str(type(p)) == "<class 'bokeh.plotting.figure.Figure'>"


class TestCmbarlegend(object):
    ''' test heat.cmbarlegend '''

    def test_cmbarlegend(self):
        # generate cmbarlegend
        lp_xylegend = heat.cmbarlegend(
            tt_axis_annot = tt_boolecatquant_map,
            es_ymatrix = set(df_matrix_map.index),
            es_xmatrix = set(df_matrix_map.columns),
            i_px = 64,
            i_height = 12,
            i_width = 12,
        )
        assert str(type(lp_xylegend[0])) == "<class 'bokeh.plotting.figure.Figure'>"
        assert str(type(lp_xylegend[1])) == "<class 'bokeh.plotting.figure.Figure'>"

    def test_cmbarlegend(self):
        # generate cmbarlegend
        lp_xylegend = heat.cmbarlegend(
            tt_axis_annot = tt_boolecatquant_bar,
            es_ymatrix = set(df_matrix_bar.index),
            es_xmatrix = set(df_matrix_bar.columns),
            i_px = 64,
            i_height = 12,
            i_width = 12,
        )
        assert str(type(lp_xylegend[0])) == "<class 'bokeh.plotting.figure.Figure'>"
        assert str(type(lp_xylegend[1])) == "<class 'NoneType'>"



### heat map plots ###

class TestHeatmap(object):
    ''' test heat.heatmap '''

    def test_heatmap(self):
        # generate heatmap
        p = heat.heatmap(
            df_matrix = df_matrix_map,
            ls_color_palette = heat.seismic256,
            r_low = 0,
            r_high = 10,
            #s_z = "value",
        )
        assert str(type(p)) == "<class 'bokeh.plotting.figure.Figure'>"


class TestClustermap(object):
    ''' test for boehheat.clusterbar '''

    def test_clustermap(self):

        # genrate clustrermap
        #for s_ext in ['html','png']:
        for s_ext in ['html']:
            for tt_axis_annot in [tt_boolecatquant_map, ()]:
                for b_ydendro in [True, False]:
                    for b_xdendro in [True, False]:
                        s_file = 'clustermap_test.html'  # or 'theclustermap.png'
                        o_clustermap, ls_yaxis, ls_xaxis = heat.clustermap(
                            df_matrix = df_matrix_map,
                            ls_color_palette = heat.seismic256,
                            r_low = 0,
                            r_high = 10,
                            s_z = 'raw',
                            tt_axis_annot = tt_axis_annot,
                            b_ydendro = b_ydendro,
                            b_xdendro = b_xdendro,
                            #s_method='average',
                            #s_metric='euclidean',
                            b_optimal_ordering=True,  # seaborn clustermap default is False
                            #i_px = 64,
                            #i_height = 12,
                            #i_width = 12,
                            #i_min_border_px = 128,
                            s_filename = s_file,
                            s_filetitel = 'test cluster map',
                        )
                        print(f'processed test_clustermap s_ext {s_ext}, tt_axis_annot, b_ydendro {b_ydendro}, b_xdendro {b_xdendro} ...')
                        print(f'ls_yaxis: {ls_yaxis}; ls_xaxis: {ls_xaxis}\n')
                        if (b_ydendro == False) and (b_xdendro == False):
                            assert np.all(ls_yaxis == ['gene_A', 'gene_B', 'gene_C', 'gene_D'])
                            assert np.all(ls_xaxis == ['sample_A', 'sample_B', 'sample_C'])
                        if (b_ydendro == False) and (b_xdendro == True):
                            assert np.all(ls_yaxis == ['gene_A', 'gene_B', 'gene_C', 'gene_D'])
                            assert np.all(ls_xaxis == ['sample_C', 'sample_B', 'sample_A'])
                        if (b_ydendro == True) and (b_xdendro == False):
                            assert np.all(ls_yaxis == ['gene_A', 'gene_B', 'gene_C', 'gene_D'])
                            assert np.all(ls_xaxis == ['sample_A', 'sample_B', 'sample_C'])
                        if (b_ydendro == True) and (b_xdendro == True):
                            assert np.all(ls_yaxis == ['gene_A', 'gene_B', 'gene_C', 'gene_D'])
                            assert np.all(ls_xaxis == ['sample_C', 'sample_B', 'sample_A'])
                        # delete plot
                        os.remove(s_file)


### stack bar plots ####

class TestStackedbar(object):
    ''' test heat.stackedbar '''

    def test_stackedbar(self):
        # generate stackbar
        for df_matrix_input in [df_matrix_bar, df_matrix_bar.T]:
            # stochastic matrix
            p = heat.stackedbar(
                df_matrix = df_matrix_input,
                ds_stack_color = ds_stack_color,
                b_sum_to_1 = True,
            )
            assert str(type(p)) == "<class 'bokeh.plotting.figure.Figure'>"
            # non stochastic matrix
            for i_factor in [0,2]:
                p = heat.stackedbar(
                    df_matrix = df_matrix_input * i_factor,
                    ds_stack_color = ds_stack_color,
                    b_sum_to_1 = False,
                )
                assert str(type(p)) == "<class 'bokeh.plotting.figure.Figure'>"


class TestClusterbar(object):
    ''' test for boehheat.clusterbar '''

    def test_clusterbar(self):
        # generate clusterbar
        #for s_ext in ['html','png']:
        for s_ext in ['html']:
            s_file = f'clusterbar_test.{s_ext}'  # or 'theclusterbar.png'
            for tt_axis_annot in [tt_boolecatquant_bar, ()]:
                for b_dendro in [True, False]:
                    o_clusterbar, ls_axis = heat.clusterbar(
                        df_matrix = df_matrix_bar,
                        ds_stack_color = ds_stack_color,
                        b_sum_to_1 = True,
                        tt_axis_annot = tt_axis_annot,
                        b_dendro = b_dendro,
                        #s_method = 'average',
                        #s_metric = 'euclidean',
                        b_optimal_ordering = True,
                        #i_px = 64,
                        #i_height = 12,
                        #i_width = 12,
                        #i_min_border_px = 128,
                        s_filename = s_file,
                        s_filetitel = 'test cluster bar',
                    )
                    if b_dendro:
                        assert np.all(ls_axis == ['sample_C', 'sample_A', 'sample_B'])
                    else:
                        assert np.all(ls_axis == ['sample_A', 'sample_B', 'sample_C'])
                    # delete plot
                    os.remove(s_file)

