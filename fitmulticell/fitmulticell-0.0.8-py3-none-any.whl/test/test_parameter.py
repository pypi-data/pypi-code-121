import os

import fitmulticell as fmc


def test_parameter_overwrite():
    file = os.path.normpath(os.getcwd() + os.sep)
    # file = os.getcwd()
    file_ = str(file + '/doc/example/models' + '/Demo_CellMotility.xml')
    par_map = {
        'motion_strength': './Global/Constant[@symbol="motion_strength"]',
        'noise_level': './Global/Constant[@symbol="noise_level"]',
    }
    model = fmc.model.MorpheusModel(
        file_,
        par_map=par_map,
        executable="morpheus",
        show_stdout=False,
        show_stderr=True,
        raise_on_error=False,
    )
    pars = {'motion_strength': 10}

    model.write_modified_model_file(file_=file_, pars=pars)
    param_val = model.get_par_value_form_xml_file(
        file_=file_, param="motion_strength"
    )
    assert param_val == "10"


def test_parameter_scale():
    file = os.path.normpath(os.getcwd() + os.sep)
    # file = os.getcwd()
    file_ = str(file + '/doc/example/models' + '/Demo_CellMotility.xml')
    par_map = {
        'motion_strength': './Global/Constant[@symbol="motion_strength"]',
        'noise_level': './Global/Constant[@symbol="noise_level"]',
    }
    pars = {'motion_strength': 1, 'noise_level': 2}
    pars_scale = {'motion_strength': "log2", 'noise_level': "log10"}

    model = fmc.model.MorpheusModel(
        file_,
        par_map=par_map,
        executable="morpheus",
        show_stdout=False,
        show_stderr=True,
        raise_on_error=False,
        par_scale=pars_scale,
    )

    model.write_modified_model_file(file_=file_, pars=pars)
    param_val_1 = model.get_par_value_form_xml_file(
        file_=file_, param="motion_strength"
    )
    param_val_2 = model.get_par_value_form_xml_file(
        file_=file_, param="noise_level"
    )

    assert float(param_val_1) == 2.0 ** (pars['motion_strength'])
    assert float(param_val_2) == 10.0 ** (pars['noise_level'])
