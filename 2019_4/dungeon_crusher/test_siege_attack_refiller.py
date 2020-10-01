from simple_flow import SimpleFlow
from siege_attack_refiller import SiegeAttackRefiller
import json
oss_siege_attack'


def test_read_normal_refill_response():
    siege_attack_refiller = SiegeAttackRefiller()
    siege_attack_refiller.attacks_left = -1
    simple_flow = SimpleFlow("", [{"kind": "boss_siege_refill_attack"}],
                             None, {"boss_siege_refill_result": {"attacks_left": 2, }}, flow=None)

    siege_attack_refiller.handle_response(simple_flow)
    assert siege_attack_refiller.attacks_left == 2


def test_no_attacks_left_response():
    siege_attack_refiller = SiegeAttackRefiller()
    siege_attack_refiller.attacks_left == 1
    simple_flow = SimpleFlow("", None,
                             None, {"error": {"message": "[boss_siege_attack] No attacks left!", }}, flow=None)

    siege_attack_refiller.handle_response(simple_flow)
    assert siege_attack_refiller.attacks_left == 0


def test_use_ui_based_refiller_normal_with_normal_attack():
    siege_attack_refiller = SiegeAttackRefiller()
    siege_attack_refiller.attacks_left = 0
    simple_flow = SimpleFlow("some_url",
                             [{"kind": "other_request"}, {"kind": "boss_siege_refill_attack"}, {
                                 "kind": "boss_siege_attack", "power_attack": False}],
                             None, None, None)

    siege_attack_refiller.handle_request(simple_flow)

    modified_request = simple_flow.modified_request
    assert len(modified_request) == 3
    assert modified_request[0]['kind'] == 'other_request'
    assert modified_request[1]['kind'] == 'boss_siege_refill_attack'
    assert modified_request[2]['kind'] == 'boss_siege_attack'


def test_use_ui_based_refiller_normal_with_power_attack():
    siege_attack_refiller = SiegeAttackRefiller()
    siege_attack_refiller.attacks_left = 0
    simple_flow = SimpleFlow("some_url",
                             [{"kind": "other_request"}, {"kind": "boss_siege_refill_attack"}, {
                                 "kind": "boss_siege_attack", "power_attack": True}],
                             None, None, None)

    siege_attack_refiller.handle_request(simple_flow)

    modified_request = simple_flow.modified_request
    assert len(modified_request) == 5
    assert modified_request[0]['kind'] == 'boss_siege_refill_attack'
    assert modified_request[1]['kind'] == 'boss_siege_refill_attack'
    assert modified_request[2]['kind'] == 'other_request'
    assert modified_request[3]['kind'] == 'boss_siege_refill_attack'
    assert modified_request[4]['kind'] == 'boss_siege_attack'


def test_prefere_max_filler():
    siege_attack_refiller = SiegeAttackRefiller()
    siege_attack_refiller.try_use_max_filler = True
    simple_flow = SimpleFlow("some_url",
                             [{"kind": "other_request"},  {
                                 "kind": "boss_siege_attack", "power_attack": True}],
                             None, None, None)

    siege_attack_refiller.handle_request(simple_flow)

    modified_request = simple_flow.modified_request
    assert len(modified_request) == 3
    assert modified_request[0]['kind'] == 'boss_siege_refill_attacks_max'
    assert modified_request[1]['kind'] == 'other_request'
    assert modified_request[2]['kind'] == 'boss_siege_attack'
