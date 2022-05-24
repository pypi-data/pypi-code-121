from utf_queue_client.models.base_model import LegacyBaseModel as BaseModel
import pytest


def test_base_model():

    test_dict = {
        "key1": "value1",
        "key2": 2,
        "key3": {"subkey1": "subvalue1"},
        "key4": ["apple", "orange"],
        "key5": [{"nested_dict_key": 1}, ["nested_list_val1", "nested_list_val2"]],
    }
    dot_dict_1 = BaseModel.convert_dict_to_model(test_dict)

    def check_values(dot_dict: BaseModel):
        assert dot_dict.key1 == "value1"
        assert dot_dict.key2 == 2
        assert dot_dict.key3.subkey1 == "subvalue1"
        assert len(dot_dict.key4) == 2
        assert dot_dict.key4[0] == "apple" and dot_dict.key4[1] == "orange"
        assert len(dot_dict.key5) == 2
        assert isinstance(dot_dict.key5[0], BaseModel)
        assert dot_dict.key5[0].nested_dict_key == 1
        assert isinstance(dot_dict.key5[1], list)
        assert len(dot_dict.key5[1]) == 2
        assert dot_dict.key5[1][0] == "nested_list_val1"
        assert dot_dict.key5[1][1] == "nested_list_val2"

    check_values(dot_dict_1)
    dot_dict_copy = dot_dict_1.copy()
    check_values(dot_dict_copy)
    assert dot_dict_1 == dot_dict_copy

    # test that apply returns true when a value is changed
    apply_from = {"key1": "newvalue1", "new_key": "newvalue2"}
    assert dot_dict_1.apply(apply_from)
    assert dot_dict_1.key1 == "newvalue1"
    assert dot_dict_1 != dot_dict_copy
    assert not hasattr(dot_dict_1, "new_key")
    # nothing changed so apply returns False
    assert not dot_dict_1.apply(apply_from)

    # apply should raise valueError if a type is changed
    apply_from = {"key1": 2}
    with pytest.raises(ValueError):
        dot_dict_1.apply(apply_from)
