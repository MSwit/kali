from tooling import Tooling


def test_delete_arrays_from_json():
    content = {"a_property": 12, "b_list_property": [1, 2]}
    updated_content = Tooling.remove_non_trivial_items(content)
    assert updated_content == {"a_property": 12, "b_list_property": []}

    content = {"a_property": 12, "b_dict_property": {'dict_property_a': "17", "dict_property_b_list": [1, 2, 3]}}
    updated_content = Tooling.remove_non_trivial_items(content)
    assert updated_content == {"a_property": 12, "b_dict_property": {}}
