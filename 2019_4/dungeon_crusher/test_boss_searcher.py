from simple_flow import SimpleFlow
from sequence_number import Sequence_Number
from boss_searcher import BossSearcher
import json
from client_replay import ClientReplay
import pytest


class FakeFlow():

    def __init__(self):
        self.request = FakeRequest()
        # self.id = "1"

    def copy(self):
        return self


class FakeRequest:
    def __init__(self):
        self.content = {}


class FakeReplayer():

    def __init__(self):
        self.is_idle = True
        self.replay_calls = 0

    def isIdle(self):
        return self.is_idle

    def replay(self, flow):
        self.replay_calls += 1


sequence_number_modifier = Sequence_Number()
sequence_number_modifier.seq_num = 0
sequence_number_modifier.sequence_number = 0
replayer = FakeReplayer()
searcher = BossSearcher(sequence_number_modifier, replayer)
searcher.api_session_flow = FakeFlow()


def teardown_function():

    replayer.replay_calls = 0
    searcher = BossSearcher(sequence_number_modifier, replayer)
    replayer.is_idle = True


def test_do_not_search_on_random_flows():
    simple_flow = SimpleFlow("", {}, None, {}, None)
    searcher.handle_response(simple_flow)
    assert replayer.replay_calls == 0


def test_search_if_there_are_less_than_4_sieges():
    simple_flow = SimpleFlow("", {}, None, {'sieges': ['', '', '']}, None)

    searcher.handle_response(simple_flow)
    assert replayer.replay_calls == 1


def test_do_not_search_if_there_are__4_sieges():
    simple_flow = SimpleFlow("", {}, None, {'sieges': ['', '', '', '']}, None)

    searcher.handle_response(simple_flow)
    assert replayer.replay_calls == 0


def test_do_not_search_when_there_are_queued_searches():
    simple_flow = SimpleFlow("", {}, None, {'sieges': ['', '', '']}, None)

    replayer.is_idle = False
    searcher.handle_response(simple_flow)
    assert replayer.replay_calls == 0

    replayer.is_idle = True
    searcher.handle_response(simple_flow)
    assert replayer.replay_calls == 1


def test_dead_boss_should_trigger_search():

    simple_flow = SimpleFlow(
        "", {}, None, {'boss_siege_attack_result': {'current_hp': 0}}, None)

    searcher.handle_response(simple_flow)
    assert replayer.replay_calls == 1
