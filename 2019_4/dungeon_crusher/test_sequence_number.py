
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
    updated_content = Sequence_Number.remove_non_trivial_items(content)
    assert updated_content == {"a_property": 12, "b_list_property": []}

    content = {"a_property": 12, "b_dict_property": {'dict_property_a': "17", "dict_property_b_list": [1, 2, 3]}}
    updated_content = Sequence_Number.remove_non_trivial_items(content)
    assert updated_content == {"a_property": 12, "b_dict_property": {}}


def test_update_sequence_number():
    updater = Sequence_Number()

    initial_request = generate_request(0, 0, "some_kind")
    updater.generate_updated_json(initial_request)
    request = generate_request(1, 1, "state_updated")
    updated_content = updater.generate_updated_json(request)
    assert updated_content['seq_num'] == 1
    assert updated_content['sequence_number'] == 1


def test_lvl_122_increases_mob_reward_consumed_modifier():
    updater = Sequence_Number()

    initial_request = generate_request(0, 0, "some_kind")
    updater.generate_updated_json(initial_request)
    request = generate_request(1, 1, "mob_reward_consumed")
    request["level"] = 121

    updated_content = updater.generate_updated_json(request)
    assert updated_content['sequence_number'] == 1

    updated_content = updater.generate_updated_json(request)
    assert updated_content['sequence_number'] == 2  # +1

    request['level'] = 122
    updated_content = updater.generate_updated_json(request)
    assert updated_content['sequence_number'] == 4  # +2


def test_battler_reward_chest_consumed_increase_by_1_or_2():
    updater = Sequence_Number()

    initial_request = generate_request(0, 0, "some_kind")
    updater.generate_updated_json(initial_request)

    mob_request = generate_request(1, 1, "mob_reward_consumed")
    mob_request["level"] = 121
    updated_content = updater.generate_updated_json(mob_request)
    assert updated_content['sequence_number'] == 1

    chest_reward = generate_request(0, 0, "battler_reward_chest_consumed")
    updated_content = updater.generate_updated_json(chest_reward)
    assert updated_content['sequence_number'] == 2  # +1

    mob_request['level'] = 122
    updated_content = updater.generate_updated_json(mob_request)
    assert updated_content['sequence_number'] == 4  # +2

    updated_content = updater.generate_updated_json(chest_reward)
    assert updated_content['sequence_number'] == 6  # +2
