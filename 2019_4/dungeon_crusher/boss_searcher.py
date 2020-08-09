#!/usr/bin/env python3

from simple_flow import SimpleFlow
from sequence_number import Sequence_Number
from mitmproxy import http
from mitmproxy import ctx
from mitmproxy.script import concurrent
from mitm_logging import log_error
import json
import time
from threading import Lock


class BossSearcher:

    def __init__(self, sequence_number_modifier):
        self.pending_replay = False
        self.queued_requests = 0
        self.api_session_flow = None
        self.sequence_number_modifier = sequence_number_modifier

    def is_relogin(self, simple_flow: SimpleFlow):  # TODO refactor

        if "https://gw.soulhunters.beyondmars.io/api/session" in simple_flow.url:
            try:
                if simple_flow.request.get('provider', '') == 'android':
                    return True
            except:
                pass
        return False

    def possible_unconsumed_searches(self):

        if self.pending_replay:
            return self.queued_requests + 1
        return self.queued_requests

    def should_search(self,  simple_flow: SimpleFlow) -> bool:
        if self.possible_unconsumed_searches() > 0:
            return False
        try:
            current_boss_hp = simple_flow.response['boss_siege_attack_result']['current_hp']
            if current_boss_hp == 0:
                log_error("[+] Killed a boss. So i can search for another")
                return True
        except Exception as e:
            print(str(e))

        try:
            siege_count = len(simple_flow.response['sieges'])
            log_error(f"[+] current siege count: {siege_count}")
            if siege_count < 4:
                return True
        except Exception as e:
            print(str(e))
            pass
        return False

    def try_set_session_request(self, simple_flow: SimpleFlow) -> None:
        if "https://gw.soulhunters.beyondmars.io/api/session" in simple_flow.url:
            self.api_session_flow = simple_flow.flow.copy()

    def handle_request(self, simple_flow: SimpleFlow) -> None:
        if "find_boss_for_siege" in str(simple_flow.modified_request):
            self.queued_requests += 1
        self.try_set_session_request(simple_flow)

        if self.is_relogin(simple_flow):
            self.queued_requests = 0

    def handle_response(self, simple_flow: SimpleFlow) -> None:
        if "find_boss_for_siege" in str(simple_flow.modified_request):
            self.queued_requests -= 1
            if self.queued_requests < 0:
                raise Exception("[-] queued_requests cant be negative")
        if self.should_search(simple_flow):
            self.try_search_for_boss()

    def try_search_for_boss(self):

        if not self.api_session_flow:
            log_error(
                "[-] no api session flow set, yet. Cant search for new bosses.")
            return
        if not self.sequence_number_modifier.is_ready():  # TODO
            log_error(
                "[-] Sequence number not initialized yet. Cant search for new bosses.")
            return

        search_for_bosses_json = {
            "kind": "find_boss_for_siege", "sequence_number": -1, "seq_num": -1}
        fake_request = self.api_session_flow.copy()
        search_for_bosses_json = [search_for_bosses_json]
        fake_request.request.content = json.dumps(
            search_for_bosses_json).encode('utf-8')

        time.sleep(0.5)

        ctx.master.commands.call("replay.client", [fake_request])
        log_error("[#] I send search for boss request")


sequence_number_modifier = Sequence_Number()
this_class = BossSearcher(sequence_number_modifier)

lock = Lock()


@concurrent
def request(flow: http.HTTPFlow) -> None:
    lock.acquire()
    simple_flow = SimpleFlow.from_flow(flow)
    sequence_number_modifier.try_update_request(simple_flow)
    this_class.handle_request(simple_flow)

    flow.request.content = json.dumps(
        simple_flow.modified_request).encode('utf-8')


def response(flow: http.HTTPFlow) -> None:
    simple_flow = SimpleFlow.from_flow(flow)
    if flow.response.status_code == 400:
        log_error("[-] Error: bad statuscode")
        log_error(json.dumps(simple_flow.response, indent=2))
        exit(1)
    this_class.handle_response(simple_flow)
    lock.release()
