
import os
from sequence_number import Sequence_Number
from sequence import Sequence
from simple_flow import SimpleFlow


test_data_path = os.path.dirname(os.path.realpath(__file__)) + "/testdata"


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


def test_dark_ritual_performed_resets_numbers():
    print(test_data_path)
    sequence = Sequence.from_file(
        f'{test_data_path}/unmodified_flow__dark_ritual_performed.json')

    sequence_sumber_modifier = Sequence_Number()

    for flow in sequence.flows:
        assert sequence_sumber_modifier.check(flow) == True
