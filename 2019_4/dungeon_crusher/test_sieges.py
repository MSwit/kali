import os
from sieges import Sieges
from sequence_number import Sequence_Number
from mitmproxy import ctx
from simple_flow import SimpleFlow
from sequence import Sequence
my_id = "e786b343-35e8-4f59-9b86-256e188783d7"
test_data_path = os.path.dirname(os.path.realpath(__file__)) + "/testdata"


def test_get_boss_id():
    # find_boss_to_attack
    response_content = {'sieges': [{'id': "some_good_id", 'top_users': {
        'finder': 'my_good_id'}, 'top_attack_id': None, 'current_hp': 1}]}
    simple_flow = SimpleFlow(
        "some_url", [{'kind': "find_boss_for_siege"}], None, response_content, None)
    sieges = Sieges(Sequence_Number())
    sieges.my_id = 'my_good_id'
    boss_id = sieges.find_boss_to_attack(simple_flow)

    assert boss_id == "some_good_id"


def test_should_attack_top_boss_twice():
    request_content = [{'kind': 'boss_siege_attack'}]
    response_content = {
        'boss_siege_attack_result': {'siege':
                                     {
                                         "id": "some_boss_id",
                                         "top_users": {
                                             "finder": "some_other_id"
                                         },
                                         "top_attack_id": "some_other_id",
                                         "current_hp": 200000000,
                                         "scores": [{"user_id": "my_good_id", "points": 0}]
                                     }
                                     }}

    simple_flow = SimpleFlow(
        "some_url", request_content, None, response_content, None)
    sieges = Sieges(Sequence_Number())
    sieges.my_id = 'my_good_id'
    sieges.attacked_bosses['some_boss_id'] = 1
    boss_id = sieges.find_boss_to_attack(simple_flow)
    assert boss_id == "some_boss_id"

    sieges.attacked_bosses['some_boss_id'] = 2
    boss_id = sieges.find_boss_to_attack(simple_flow)
    assert boss_id == None  # already attacked two times.


def test_should_found_boss():

    print(test_data_path)
    sequence = Sequence.from_file(f'{test_data_path}/siege_modified_004.json')

    sieges = Sieges(Sequence_Number())

    flow = [flow for flow in sequence.flows if "find_boss_for_siege" in str(
        flow.get_request())][0]
    boss_id = sieges.find_boss_to_attack(flow)
    assert boss_id == "b6759a52-e042-4a7e-876f-4154958f8e48"
