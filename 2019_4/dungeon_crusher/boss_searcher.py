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
from client_replay import ClientReplay


class BossSearcher:

    def __init__(self, sequence_number_modifier, replayer):
        self.api_session_flow = None
        self.replayer = replayer
        self.sequence_number_modifier = sequence_number_modifier

    def is_relogin(self, simple_flow: SimpleFlow):  # TODO refactor

        if "https://gw.soulhunters.beyondmars.io/api/session" in simple_flow.url:
            try:
                if simple_flow.request.get('provider', '') == 'android':
                    return True
            except:
                pass
        return False

    def should_search(self,  simple_flow: SimpleFlow) -> bool:

        try:
            current_boss_hp = simple_flow.response['boss_siege_attack_result']['current_hp']
            if current_boss_hp == 0:
                log_error("[+] Killed a boss. So i can search for another")
                return True
        except Exception as e:
            pass

        try:
            siege_count = len(simple_flow.response['sieges'])
            log_error(f"[+] current siege count: {siege_count}")
            if siege_count < 4:
                return True
        except Exception as e:
            pass
        return False

    def try_set_session_request(self, simple_flow: SimpleFlow) -> None:
        if "https://gw.soulhunters.beyondmars.io/api/session" in simple_flow.url:
            self.api_session_flow = simple_flow.flow.copy()

    def handle_request(self, simple_flow: SimpleFlow) -> None:
        self.try_set_session_request(simple_flow)

    def handle_response(self, simple_flow: SimpleFlow) -> None:
        log_error(
            f"[++++++++++] boss_searcher. replayer is idle? : {self.replayer.isIdle()}")
        if self.replayer.isIdle() and self.should_search(simple_flow):
            log_error(f"replayer is idle? : {self.replayer.isIdle() }")
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

        # time.sleep(0.5)

        log_error("[+] \tI send search for boss request")
        # log_error(
        #     "[+] boss_searcher: because of many errors, i will check the state of the replayer again:")
        log_error(f"replayer is idle? : {self.replayer.isIdle() }")
        self.replayer.replay(fake_request)


sequence_number_modifier = Sequence_Number()
replayer = ClientReplay()
this_class = BossSearcher(sequence_number_modifier, replayer)

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
