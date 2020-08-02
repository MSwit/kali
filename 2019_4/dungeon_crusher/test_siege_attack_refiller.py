from simple_flow import SimpleFlow
from siege_attack_refiller import SiegeAttackRefiller
import json


def test_fill_up_for_power_attack_3_attacks_left():
    siege_attack_refiller = SiegeAttackRefiller()
    siege_attack_refiller.attacks_left = 3
    simple_flow = SimpleFlow("some_url",
                             [{"kind": "boss_siege_attack", "power_attack": True}],
                             None, None, None)

    siege_attack_refiller.handle_request(simple_flow)
    modified_request = simple_flow.get_modified_request()
    assert len(modified_request) == 1
    assert modified_request[0]['kind'] == 'boss_siege_attack'  # unmodified


def test_fill_up_for_power_attack_2_attacks_left():
    siege_attack_refiller = SiegeAttackRefiller()
    siege_attack_refiller.attacks_left = 2
    simple_flow = SimpleFlow("some_url",
                             [{"kind": "boss_siege_attack", "power_attack": True}],
                             None, None, None)

    siege_attack_refiller.handle_request(simple_flow)

    modified_request = simple_flow.get_modified_request()
    assert len(modified_request) == 2
    assert modified_request[0]['kind'] == 'boss_siege_refill_attack'
    assert modified_request[1]['kind'] == 'boss_siege_attack'


def test_fill_up_for_power_attack_1_attacks_left():
    siege_attack_refiller = SiegeAttackRefiller()
    siege_attack_refiller.attacks_left = 1
    simple_flow = SimpleFlow("some_url",
                             [{"kind": "boss_siege_attack", "power_attack": True}],
                             None, None, None)

    siege_attack_refiller.handle_request(simple_flow)

    modified_request = simple_flow.get_modified_request()
    assert len(modified_request) == 3
    assert modified_request[0]['kind'] == 'boss_siege_refill_attack'
    assert modified_request[1]['kind'] == 'boss_siege_refill_attack'
    assert modified_request[2]['kind'] == 'boss_siege_attack'


def test_fill_up_for_power_attack_0_attacks_left():
    siege_attack_refiller = SiegeAttackRefiller()
    siege_attack_refiller.attacks_left = 0
    simple_flow = SimpleFlow("some_url",
                             [{"kind": "boss_siege_attack", "power_attack": True}],
                             None, None, None)

    siege_attack_refiller.handle_request(simple_flow)

    modified_request = simple_flow.get_modified_request()
    assert len(modified_request) == 2
    assert modified_request[0]['kind'] == 'boss_siege_refill_attacks_max'
    assert modified_request[1]['kind'] == 'boss_siege_attack'


def test_fill_up_for_normal_attack_0_attacks_left():
    siege_attack_refiller = SiegeAttackRefiller()
    siege_attack_refiller.attacks_left = 0
    simple_flow = SimpleFlow("some_url",
                             [{"kind": "boss_siege_attack", "power_attack": False}],
                             None, None, None)

    siege_attack_refiller.handle_request(simple_flow)

    modified_request = simple_flow.get_modified_request()
    assert len(modified_request) == 2
    assert modified_request[0]['kind'] == 'boss_siege_refill_attacks_max'
    assert modified_request[1]['kind'] == 'boss_siege_attack'


def test_read_normal_refill_response():
    siege_attack_refiller = SiegeAttackRefiller()
    siege_attack_refiller.attacks_left = -1
    simple_flow = SimpleFlow("", {"kind": "boss_siege_refill_attack"},
                             None, {"boss_siege_refill_result": {"attacks_left": 2, }}, flow=None)

    siege_attack_refiller.handle_response(simple_flow)
    assert siege_attack_refiller.attacks_left == 2


def test_no_attacks_left_response():
    siege_attack_refiller = SiegeAttackRefiller()
    simple_flow = SimpleFlow("", None,
                             None, {"error": {"message": "[boss_siege_attack] No attacks left!", }}, flow=None)

    siege_attack_refiller.handle_response(simple_flow)
    assert siege_attack_refiller.attacks_left == 0
