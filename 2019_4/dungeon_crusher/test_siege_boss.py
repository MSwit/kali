from simple_flow import SimpleFlow
from siege_attack_refiller import SiegeAttackRefiller
import json
from siege_boss import SiegeBossAttack


def test_must_be_finder():
    siege_analyser = SiegeBossAttack(
        must_be_finder=True, current_hp=None, minimum_hp=None, maximum_hp=None, power_attack=False)
    result = siege_analyser.get_attack_json_for_bosses(
        SimpleFlow("", None, None, {"sieges": [{"id": "some_boss_id", "top_users": {"finder": "my_id"}}]}, None))

    assert result != None
    assert result['siege_id'] == 'some_boss_id'
    assert result['power_attack'] == False
