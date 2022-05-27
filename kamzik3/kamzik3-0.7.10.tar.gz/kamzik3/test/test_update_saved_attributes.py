import h5py
from pathlib import Path
import yaml

import kamzik3.snippets.update_saved_attributes as upd

here = Path(__file__).parent
h5file = here.parent / "example" / "saved_attributes.h5"
yml_file = here.parent / "example" / "saved_attributes_example.yml"
existing_config = {
    "/Default/Detector": [
        {
            "index": 0,
            "Color": "None",
            "Time": "None",
            "Comment": "None",
            "Z ['Position'][mm]": "None",
            "Y ['Position'][mm]": "None",
            "X ['Position'][mm]": "None",
        },
        {
            "index": 1,
            "Color": "#fff",
            "Time": "31-05-2021 12:05:59",
            "Comment": "test",
            "Z ['Position'][mm]": "1.0000000000000002",
            "Y ['Position'][mm]": "1.0",
            "X ['Position'][mm]": "1.0",
        },
    ],
    "/Default/Sample": [
        {
            "index": 0,
            "Color": "None",
            "Time": "None",
            "Comment": "None",
            "X ['Position'][mm]": "None",
            "Y ['Position'][mm]": "None",
            "Z ['Position'][mm]": "None",
        },
        {
            "index": 1,
            "Color": "#fff",
            "Time": "31-05-2021 12:05:59",
            "Comment": "test",
            "X ['Position'][mm]": "1.0",
            "Y ['Position'][mm]": "1.0",
            "Z ['Position'][mm]": "1.0000000000000002",
        },
    ],
}

new_config = {
    "groups": ["Default", "Lab099"],
    "motors": {
        "Detector": ["Z ['Position'][mm]", "Y ['Position'][mm]", "X ['Position'][mm]"],
        "Sample": ["X ['Position'][mm]", "Y ['Position'][mm]", "Z ['Position'][mm]"],
        "Chiller": ["Ika ['Temperature'][degC]", "Ika ['Velocity'][rpm]"],
    },
}

inverted_config = {
    "groups": ["Default", "Lab099"],
    "motors": {
        "Sample": ["X ['Position'][mm]", "Y ['Position'][mm]", "Z ['Position'][mm]"],
        "Chiller": ["Ika ['Temperature'][degC]", "Ika ['Velocity'][rpm]"],
        "Detector": ["Z ['Position'][mm]", "Y ['Position'][mm]", "X ['Position'][mm]"],
    },
}


def test_get_existing_config_ok():
    config = upd.get_existing_config(filename=h5file)
    assert "/Default/Detector" in config
    assert "/Default/Sample" in config
    assert config["/Default/Detector"][0].get("index") == 0
    assert config["/Default/Detector"][0].get("Color") == "None"


def test_get_yaml_config_ok():
    new_conf = upd.get_yaml_config(filename=yml_file)
    assert "/Default/Detector" in new_conf
    assert "/Default/Sample" in new_conf
    assert new_conf["/Default/Detector"].get("Comment") == "None"
    assert new_conf["/Default/Sample"].get("Color") == "None"
    assert new_conf["/Default/Sample"].get("X ['Position'][mm]") == "None"


def test_check_config_no_group():
    with yml_file.open(mode="r", encoding="utf-8") as config_file:
        new_conf = yaml.load(config_file, Loader=yaml.SafeLoader)
    del new_conf["groups"]
    result = upd.check_config(new_conf)
    assert set(result.keys()) == {"/Default/Detector", "/Default/Sample"}
    assert set(result["/Default/Detector"]) == {
        "Color",
        "Time",
        "Comment",
        "X ['Position'][mm]",
        "Y ['Position'][mm]",
        "Z ['Position'][mm]",
    }


def test_save_existing_config_path_ok(tmp_path):
    filename = tmp_path / "existing_config.yml"
    upd.save_existing_model(config=existing_config, path=filename)
    assert filename.is_file()
    with filename.open(mode="r", encoding="utf-8") as file:
        conf = yaml.load(file, Loader=yaml.SafeLoader)
    assert set(conf.keys()) == {"groups", "motors"}
    assert conf["groups"] == ["Default"]
    assert set(conf["motors"].keys()) == {"Detector", "Sample"}
    assert set(conf["motors"]["Sample"]) == {
        "Z ['Position'][mm]",
        "Y ['Position'][mm]",
        "X ['Position'][mm]",
    }


def test_generate_saved_attributes_groups_none(tmp_path):
    new_h5file = tmp_path / "saved_attributes_updated.h5"
    assert upd.generate_saved_attributes(path=new_h5file, groups=None) is False


def test_generate_saved_attributes_groups_no_record(tmp_path):
    new_h5file = tmp_path / "saved_attributes_updated.h5"
    assert (
        upd.generate_saved_attributes(
            path=new_h5file, groups=upd.check_config(new_config)
        )
        is True
    )
    assert new_h5file.is_file()


def test_generate_saved_attributes_groups_records(tmp_path):
    new_h5file = tmp_path / "saved_attributes_updated.h5"
    assert (
        upd.generate_saved_attributes(path=new_h5file, groups=existing_config) is True
    )
    assert new_h5file.is_file()


def test_generate_config_yaml_none():
    assert (
        upd.generate_config(yaml_config=None, h5_config=existing_config)
        is existing_config
    )


def test_generate_config_no_existing_config():
    new_conf = upd.check_config(new_config)
    assert upd.generate_config(yaml_config=new_conf, h5_config=None) is new_conf


def test_generate_config_ok():
    final_config = upd.generate_config(
        yaml_config=upd.check_config(new_config), h5_config=existing_config
    )
    assert "/Default/Chiller" in final_config
    assert final_config["/Default/Detector"][1].get("Time") == "31-05-2021 12:05:59"
    assert final_config["/Default/Chiller"][1].get("Time") == "None"
    assert len(final_config["/Default/Detector"]) == 2
    assert final_config["/Lab099/Detector"][0].get("Z ['Position'][mm]") == "None"
    assert len(final_config["/Lab099/Detector"]) == 1


def test_generate_config_invert_keys():
    final_config = upd.generate_config(
        yaml_config=upd.check_config(inverted_config), h5_config=existing_config
    )
    assert "/Default/Chiller" in final_config
    assert final_config["/Default/Detector"][1].get("Time") == "31-05-2021 12:05:59"
    assert final_config["/Default/Chiller"][1].get("Time") == "None"
    assert len(final_config["/Default/Detector"]) == 2
    assert final_config["/Lab099/Detector"][0].get("Z ['Position'][mm]") == "None"
    assert len(final_config["/Lab099/Detector"]) == 1


def test_generate_saved_attributes_inverted_config(tmp_path):
    new_h5file = tmp_path / "saved_attributes_updated.h5"
    final_config = upd.generate_config(
        yaml_config=upd.check_config(inverted_config), h5_config=existing_config
    )
    assert upd.generate_saved_attributes(path=new_h5file, groups=final_config) is True
    assert new_h5file.is_file()
    saved_config = upd.get_existing_config(filename=new_h5file)
    assert "/Lab099/Detector" in saved_config
    assert saved_config["/Default/Sample"][1].get("Time") == "31-05-2021 12:05:59"
    assert saved_config["/Default/Chiller"][1].get("Time") == "None"
    assert len(saved_config["/Default/Detector"]) == 2
    assert saved_config["/Lab099/Sample"][0].get("Z ['Position'][mm]") == "None"
    assert len(saved_config["/Lab099/Chiller"]) == 1
