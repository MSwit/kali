from sieges import Sieges
from sequence_number import Sequence_Number
from mitmproxy import ctx
from simple_flow import SimpleFlow

my_id = "e786b343-35e8-4f59-9b86-256e188783d7"


def test_get_boss_id():
    # find_boss_to_attack
    response_content = {'sieges': [{'id': "some_good_id", 'top_users': {
        'finder': 'my_good_id'}, 'top_attack_id': None, 'current_hp': 1}]}
    simple_flow = SimpleFlow("some_url", [{'kind': "find_boss_for_siege"}], response_content, None)
    sieges = Sieges(Sequence_Number())
    sieges.my_id = 'my_good_id'
    boss_id = sieges.find_boss_to_attack(simple_flow)

    assert boss_id == "some_good_id"
