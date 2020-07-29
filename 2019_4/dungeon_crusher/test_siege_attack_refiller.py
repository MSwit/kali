from simple_flow import SimpleFlow
from siege_attack_refiller import SiegeAttackRefiller
import json


def test_fill_up_for_power_attack_3_attacks_left():
    siege_attack_refiller = SiegeAttackRefiller()
    siege_attack_refiller.attacks_left = 3
    simple_flow = SimpleFlow("some_url",
                             [{"kind": "boss_siege_attack", "power_attack": True}],
                             None, None, None)

    modified_simple_flow = siege_attack_refiller.handle_request(simple_flow)

    assert len(modified_simple_flow.get_request()) == 1
    assert modified_simple_flow.get_request()
    [0]['kind'] == 'boss_siege_attack'  # unmodified


def test_fill_up_for_power_attack_2_attacks_left():
    siege_attack_refiller = SiegeAttackRefiller()
    siege_attack_refiller.attacks_left = 2
    simple_flow = SimpleFlow("some_url",
                             [{"kind": "boss_siege_attack", "power_attack": True}],
                             None, None, None)

    modified_simple_flow = siege_attack_refiller.handle_request(simple_flow)

    assert len(modified_simple_flow.get_request()) == 2

    assert modified_simple_flow.get_request(
    )[0]['kind'] == 'boss_siege_refill_attack'

    assert modified_simple_flow.get_request(
    )[1]['kind'] == 'boss_siege_attack'


def test_fill_up_for_power_attack_2_attacks_left():
    siege_attack_refiller = SiegeAttackRefiller()
    siege_attack_refiller.attacks_left = 1
    simple_flow = SimpleFlow("some_url",
                             [{"kind": "boss_siege_attack", "power_attack": True}],
                             None, None, None)

    modified_simple_flow = siege_attack_refiller.handle_request(simple_flow)

    assert len(modified_simple_flow.get_request()) == 3

    assert modified_simple_flow.get_request(
    )[0]['kind'] == 'boss_siege_refill_attack'

    assert modified_simple_flow.get_request(
    )[1]['kind'] == 'boss_siege_refill_attack'

    assert modified_simple_flow.get_request(
    )[2]['kind'] == 'boss_siege_attack'
