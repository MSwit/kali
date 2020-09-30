from simple_flow import SimpleFlow
from siege_attack_refiller import SiegeAttackRefiller
import json
# from siege_boss import SiegeBossAttack
from siege_boss import SiegeBossAttack_Finder
from siege_boss import SiegeBoss_Finisher
from siege_boss import TopBossAttack_Finder
import pytest


# def test_must_be_finder():
#     siege_analyser = SiegeBossAttack(
#         must_be_finder=True, current_hp=None, minimum_hp=None, maximum_hp=None, power_attack=False)
#     result = siege_analyser.get_attack_json_for_bosses(
#         SimpleFlow("", None, None, {"sieges": [{"id": "some_boss_id", "top_users": {"finder": "my_id"}}]}, None))

#     assert result != None
#     assert result['siege_id'] == 'some_boss_id'
#     assert result['power_attack'] == False


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


def test_handle_error():
    siege_analyser = SiegeBossAttack_Finder(boss_hp=13, power_attack=True)
    siege_analyser.my_id = "my_fake_id"
    result = siege_analyser.get_attack_json_for_bosses(SimpleFlow("", {"kind": "find_boss_for_siege"}, None, {"error": {"message": "[find_boss_for_siege] Boss siege limit reached!", "action": {
        "kind": "find_boss_for_siege", "sequence_number": 15, "seq_num": 82}, "code": 400, "backend_time": "2020-08-05T17:22:07.888Z"}}, None))
    assert result == None


def test_finisher_attack_normal_sieges_array():

    finisher = SiegeBoss_Finisher(42)
    result = finisher.get_attack_json_for_bosses(
        SimpleFlow("", None, None, {"sieges": [{"id": "some_boss_id", "current_hp": 42}]}, None))

    assert result == {
        "siege_id": "some_boss_id",
        "power_attack": False,
        "autorestore_is_on": True,
        "kind": "boss_siege_attack",
        "sequence_number": -1,
        "seq_num": -1
    }


def test_finisher_attack_second_boss():

    finisher = SiegeBoss_Finisher(42)
    result = finisher.get_attack_json_for_bosses(
        SimpleFlow("", None, None, {"sieges": [{"id": "some_boss_bad_boss_id", "current_hp": 43}, {"id": "some_boss_id", "current_hp": 42}]}, None))

    assert result == {
        "siege_id": "some_boss_id",
        "power_attack": False,
        "autorestore_is_on": True,
        "kind": "boss_siege_attack",
        "sequence_number": -1,
        "seq_num": -1
    }


def test_finsiher_reattack_attacked_boss_with_low_hp():
    finisher = SiegeBoss_Finisher(42)
    result = finisher.get_attack_json_for_bosses(
        SimpleFlow("", None, None, {"boss_siege_attack_result": {
            "status": 200,
            "siege": {"id": "some_boss_id", "current_hp": 42}}}, None))

    assert result == {
        "siege_id": "some_boss_id",
        "power_attack": False,
        "autorestore_is_on": True,
        "kind": "boss_siege_attack",
        "sequence_number": -1,
        "seq_num": -1
    }


def test_finsiher_do_not_finish_twice():
    finisher = SiegeBoss_Finisher(42)
    result = finisher.get_attack_json_for_bosses(
        SimpleFlow("", None, None, {"boss_siege_attack_result": {
            "status": 200,
            "siege": {"id": "some_boss_id", "current_hp": 42}}}, None))

    assert result != None

    result = finisher.get_attack_json_for_bosses(
        SimpleFlow("", None, None, {"boss_siege_attack_result": {
            "status": 200,
            "siege": {"id": "some_boss_id", "current_hp": 41}}}, None))

    assert result == None


def test_finsiher_do_not_attack_boss_with_0_hp():
    finisher = SiegeBoss_Finisher(42)
    simple_flow = SimpleFlow("", None, None, {"boss_siege_attack_result": {
        "status": 200,
        "siege": {"id": "some_boss_id", "current_hp": 0}}}, None)

    result = finisher.get_attack_json_for_bosses(simple_flow)

    assert result == None


@pytest.mark.parametrize("boss_hp,expected", [
    (9, None),
    (10, {
        "siege_id": "some_boss_id",
        "power_attack": False,
        "autorestore_is_on": True,
        "kind": "boss_siege_attack",
        "sequence_number": -1,
        "seq_num": -1
    })])
def test_top_boss_needs_a_minimum_hp(boss_hp, expected):
    finder = TopBossAttack_Finder(10, 0)
    simple_flow = SimpleFlow("", {"kind": "find_boss_for_siege"}, None, {"sieges": [{
        "id": "some_boss_id",
        "current_hp": boss_hp}]}, None)

    result = finder.get_attack_json_for_bosses(simple_flow)
    assert result == expected


def test_top_boss_reattacks():
    finder = TopBossAttack_Finder(10, 1)
    finder.my_id = "my_id"

    simple_flow = SimpleFlow("", {"kind": "find_boss_for_siege"}, None, {"sieges": [{
        "id": "some_boss_id", "current_hp": 10}]}, None)
    result = finder.get_attack_json_for_bosses(simple_flow)

    assert result != None
    simple_flow = SimpleFlow("", None, None, {"boss_siege_attack_result": {
        "siege": {"id": "some_boss_id", "current_hp": 0, "scores": [
            {
                "user_id": "my_id",
                "points": 0, }]}}}, None)

    result = finder.get_attack_json_for_bosses(simple_flow)
    assert result != None  # first retry

    result = finder.get_attack_json_for_bosses(simple_flow)
    assert result == None  # second retry
