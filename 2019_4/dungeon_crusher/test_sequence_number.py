
from sequence_number import Sequence_Number


def generate_request(sequence_number, seq_num, kind):
    return {'sequence_number': sequence_number, 'seq_num': seq_num, 'kind': kind}


def test_first_request_issnt_modified():
    request = generate_request(0, 0, "some_kind")
    updater = Sequence_Number()
    updated_request = updater.generate_updated_json(request)
    assert updated_request == request


def test_second_request_gets_updated_seq_num():
    request = generate_request(0, 0, "some_kind")
    updater = Sequence_Number()
    updated_request1 = updater.generate_updated_json(request)
    updated_request2 = updater.generate_updated_json(request)
    assert updated_request2['seq_num'] == 1
    assert updated_request2['sequence_number'] == request['sequence_number']


def test_delete_arrays_from_json():
    content = {"a_property": 12, "b_list_property": [1, 2]}
    modified_content = Sequence_Number.remove_non_trivial_items(content)
    assert modified_content == {"a_property": 12, "b_list_property": []}

    content = {"a_property": 12, "b_dict_property": {'dict_property_a': "17", "dict_property_b_list": [1, 2, 3]}}
    modified_content = Sequence_Number.remove_non_trivial_items(content)
    assert modified_content == {"a_property": 12, "b_dict_property": {}}
