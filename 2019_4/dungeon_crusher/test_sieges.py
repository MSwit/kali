from sieges import Sieges
from sequence_number import Sequence_Number
from mitmproxy import ctx

my_id = "e786b343-35e8-4f59-9b86-256e188783d7"


def test_get_boss_id():

    content = {'id': "some_good_id", 'top_users': {
        'finder': 'e786b343-35e8-4f59-9b86-256e188783d7'}, 'top_attack_id': None, 'current_hp': 1}
    boss_id = Sieges(Sequence_Number()).get_good_boss_id(content)

    assert boss_id == "some_good_id"
