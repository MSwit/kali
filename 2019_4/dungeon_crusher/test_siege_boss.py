from simple_flow import SimpleFlow
from siege_attack_refiller import SiegeAttackRefiller
import json
from siege_boss import SiegeBossAttack
from siege_boss import SiegeBossAttack_Finder


def test_must_be_finder():
    siege_analyser = SiegeBossAttack(
        must_be_finder=True, current_hp=None, minimum_hp=None, maximum_hp=None, power_attack=False)
    result = siege_analyser.get_attack_json_for_bosses(
        SimpleFlow("", None, None, {"sieges": [{"id": "some_boss_id", "top_users": {"finder": "my_id"}}]}, None))

    assert result != None
    assert result['siege_id'] == 'some_boss_id'
    assert result['power_attack'] == False


def test_simple_normal_attack():
    siege_analyser = SiegeBossAttack_Finder(boss_hp=13, power_attack=False)
    siege_analyser.my_id = "my_fake_id"
    result = siege_analyser.get_attack_json_for_bosses(
        SimpleFlow("", {"kind": "find_boss_for_siege"}, None, {"sieges": [{"id": "some_boss_id", "current_hp": 13, "top_attack_id": None, "top_users": {"finder": "my_fake_id"}}]}, None))

    assert result == {
        "siege_id": "some_boss_id",
        "power_attack": False,
        "autorestore_is_on": True,
        "kind": "boss_siege_attack",
        "sequence_number": -1,
        "seq_num": -1
    }


def test_simple_power_attack():
    siege_analyser = SiegeBossAttack_Finder(boss_hp=13, power_attack=True)
    siege_analyser.my_id = "my_fake_id"
    result = siege_analyser.get_attack_json_for_bosses(
        SimpleFlow("", {"kind": "find_boss_for_siege"}, None, {"sieges": [{"id": "some_boss_id", "current_hp": 13, "top_attack_id": None, "top_users": {"finder": "my_fake_id"}}]}, None))

    assert result == {
        "siege_id": "some_boss_id",
        "power_attack": True,
        "autorestore_is_on": True,
        "kind": "boss_siege_attack",
        "sequence_number": -1,
        "seq_num": -1
    }


def test_simple_do_not_attack_if_finder_not_me():
    siege_analyser = SiegeBossAttack_Finder(boss_hp=13, power_attack=False)
    siege_analyser.my_id = "my_fake_id"
    result = siege_analyser.get_attack_json_for_bosses(
        SimpleFlow("", {"kind": "find_boss_for_siege"}, None, {"sieges": [{"id": "some_boss_id", "current_hp": 13, "top_attack_id": None, "top_users": {"finder": "some_other_user"}}]}, None))

    assert result == None


def test_simple_do_not_attack_if_hp_not_match():
    siege_analyser = SiegeBossAttack_Finder(boss_hp=13, power_attack=True)
    siege_analyser.my_id = "my_fake_id"
    result = siege_analyser.get_attack_json_for_bosses(
        SimpleFlow("", {"kind": "find_boss_for_siege"}, None, {"sieges": [{"id": "some_boss_id", "current_hp": 12, "top_attack_id": None, "top_users": {"finder": "my_fake_id"}}]}, None))

    assert result == None
