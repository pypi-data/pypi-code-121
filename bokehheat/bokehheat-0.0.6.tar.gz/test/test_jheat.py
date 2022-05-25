#####
# title: test_jheat.py
#
# language: python3
# author: bue
# date: 2022-03-10
# license: GPL>=3
#
# description:
#   pytest unit test library for jheat.py
#   + https://docs.pytest.org/
#
#   note:
#   assert actual == expected, message
#   == value equality
#   is reference equality
#   pytest.approx for real values
#####


from bokehheat import jheat
from bokeh import palettes
import numpy as np
import os
import pandas as pd

# generare test data
ls_variable = ['gene_A','gene_B','gene_C','gene_D']
ls_observation = ['sample_A','sample_B','sample_C']
# heat map
a_matrix_map = np.array(range(4*3))
a_matrix_map.shape = (4,3)
df_matrix_map = pd.DataFrame(a_matrix_map, index=ls_variable, columns=ls_observation)

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


### elementar plots ###

class TestJdendro(object):
    ''' test for jheat.jdendro '''

    def test_jdendro(self):
        # const
        dls_result = {
            'left': ['gene_D', 'gene_C', 'gene_B', 'gene_A'],
            'right': ['gene_D', 'gene_C', 'gene_B', 'gene_A'],
            'top': ['sample_C', 'sample_B', 'sample_A'],
            'bottom': ['sample_C', 'sample_B', 'sample_A'],
        }
        # generate jdendro
        for s_root in ['left', 'right', 'top', 'bottom']:
            print(f'process test_cdendro s_root: {s_root} ...')
            r_cophcorre, ls_cat_sorted, s_filename_ext, s_filename_cdt = jheat.jdendro(
                df_matrix = df_matrix_map,
                s_root = s_root,
                s_method = 'single',
                s_metric = 'euclidean',
                b_optimal_ordering = True,
                s_filename = 'jdendrogram_test',
            )
            assert np.all(ls_cat_sorted == dls_result[s_root])
            os.remove(s_filename_cdt)
            os.remove(s_filename_ext)


### heat map plots ###

class TestJheatmap(object):
    ''' test jheat.heatmap '''

    def test_jheatmap(self):
        for tt_axis_annot in [tt_boolecatquant_map, ()]:
            # generate heatmap
            s_filename_ext = jheat.jheatmap(
                df_matrix = df_matrix_map,
                tt_axis_annot = tt_axis_annot,
                s_xcolor = None,
                s_ycolor = None,
                s_filename = 'jheatmap_test',
            )
            assert s_filename_ext == 'jheatmap_test.cdt'
            os.remove(s_filename_ext)

        for s_xcolor in [None, 'sample_boole_color1', 'sample_cat1_color', 'sievert_color']:
            for s_ycolor in [None,'gene_boole_color', 'gene_cat2_color', 'gene_real_color']:
                # generate heatmap
                s_filename_ext = jheat.jheatmap(
                    df_matrix = df_matrix_map,
                    tt_axis_annot = tt_axis_annot,
                    s_xcolor = s_xcolor,
                    s_ycolor = s_ycolor,
                    s_filename = 'jheatmap_test',
                )
                assert s_filename_ext == 'jheatmap_test.cdt'
                os.remove(s_filename_ext)


class TestJclustermap(object):
    ''' test for boehheat.clusterbar '''

    def test_clustermap(self):

        # genrate jclustrermap
        for b_ydendro in [False, True]:
            for b_xdendro in [False, True]:
                print(f'processed test_jclustermap b_ydendro {b_ydendro}, b_xdendro {b_xdendro} ...')
                ls_filename, ls_yaxis, ls_xaxis = jheat.jclustermap(
                    df_matrix = df_matrix_map,
                    tt_axis_annot = (),
                    s_xcolor = None,
                    s_ycolor = None,
                    b_ydendro = b_ydendro,
                    b_xdendro = b_xdendro,
                    #s_method='average',
                    #s_metric='euclidean',
                    b_optimal_ordering = True,  # seaborn clustermap default is False
                    s_filename = 'jclustermap_test',
                )
                print(df_matrix_map.info())
                print(f'ls_yaxis: {ls_yaxis}; ls_xaxis: {ls_xaxis}\n')
                if (b_ydendro == False) and (b_xdendro == False):
                    assert np.all(ls_yaxis == ['gene_A', 'gene_B', 'gene_C', 'gene_D'])
                    assert np.all(ls_xaxis == ['sample_A', 'sample_B', 'sample_C'])
                if (b_ydendro == False) and (b_xdendro == True):
                    assert np.all(ls_yaxis == ['gene_A', 'gene_B', 'gene_C', 'gene_D'])
                    assert np.all(ls_xaxis == ['sample_C', 'sample_B', 'sample_A'])
                if (b_ydendro == True) and (b_xdendro == False):
                    assert np.all(ls_xaxis == ['sample_A', 'sample_B', 'sample_C'])
                    assert np.all(ls_yaxis == ['gene_A', 'gene_B', 'gene_C', 'gene_D'])
                if (b_ydendro == True) and (b_xdendro == True):
                    assert np.all(ls_yaxis == ['gene_A', 'gene_B', 'gene_C', 'gene_D'])
                    assert np.all(ls_xaxis == ['sample_C', 'sample_B', 'sample_A'])
                # delete plot
                for s_file in ls_filename:
                    os.remove(s_file)

