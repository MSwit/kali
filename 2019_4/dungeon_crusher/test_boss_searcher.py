from simple_flow import SimpleFlow
from sequence_number import Sequence_Number
from boss_searcher import BossSearcher
import json

sequence_number_modifier = Sequence_Number()


def test_should_search_returns_false_on_random_flow():
    searcher = BossSearcher(sequence_number_modifier)
    simple_flow = SimpleFlow("", {}, None, {}, None)
    result = searcher.should_search(simple_flow)

    assert result == False


def test_should_search_returns_true_when_there_are_less_than_4_sieges():
    searcher = BossSearcher(sequence_number_modifier)
    simple_flow = SimpleFlow("", {}, None, {'sieges': ['', '', '']}, None)
    result = searcher.should_search(simple_flow)
    assert result == True


def test_do_not_search_when_there_are_queued_searches():
    searcher = BossSearcher(sequence_number_modifier)
    searcher.queued_requests = 1
    simple_flow = SimpleFlow("", {}, None, {'sieges': ['', '']}, None)
    result = searcher.should_search(simple_flow)
    assert result == False


def test_handle_request_reduces_queued_searches():
    searcher = BossSearcher(sequence_number_modifier)
    search_flow = SimpleFlow(
        "", [{'kind': 'find_boss_for_siege'}], None, None, None)
    sieges_flow = SimpleFlow("", {}, None, {'sieges': ['', '']}, None)

    searcher.handle_request(search_flow)
    result = searcher.should_search(sieges_flow)
    assert result == False

    searcher.handle_response(search_flow)
    result = searcher.should_search(sieges_flow)
    assert result == True


def test_dead_boss_should_trigger_search():
    searcher = BossSearcher(sequence_number_modifier)

    simple_flow = SimpleFlow(
        "", {}, None, {'boss_siege_attack_result': {'current_hp': 0}}, None)

    result = searcher.should_search(simple_flow)
    assert result == True
