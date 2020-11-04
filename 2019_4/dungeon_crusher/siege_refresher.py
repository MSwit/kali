#!/usr/bin/env python3

from mitmproxy import http
from mitmproxy import ctx
import json
from tooling import Tooling
from mitm_logging import log_error
from simple_flow import SimpleFlow
import os
from mitm_logging import log_error
from mitm_logging import log_warning
from threading import Timer


class SiegeRefresher:

    def __init__(self):
        self.update_flow = None
        self.refresh_thread = None
        self.replayer = None

    def handle_request(self, simple_flow: SimpleFlow) -> None:
        pass

    def handle_response(self, simple_flow: SimpleFlow) -> None:
        # log_error("[+] SiegeRefresher:handle_response called")

        if simple_flow.url == "https://soulhunters.beyondmars.io/api/boss_sieges/sieges" or simple_flow.url == "https://gw.soulhunters.beyondmars.io/api/boss_sieges/sieges":
            self.update_flow = simple_flow.flow.copy()
            self.update_flow.request.content = json.dumps({}).encode('utf-8')

        # else:
        #     log_error(json.dumps(simple_flow.modified_request, indent=2))

        try:
            sieges = simple_flow.response['sieges']
            log_error(
                f"[+] Detect Current siege count: {len(sieges)}........., re-schedule timer")
            self.refresh_timer()
        except:
            pass

    def refresh_timer(self):
        if self.refresh_thread:
            self.refresh_thread.cancel()
        self.refresh_thread = Timer(2, self.replay_siege_update_flow)
        self.refresh_thread.start()

    def replay_siege_update_flow(self):
        if self.update_flow:
            if self.replayer.isIdle():
                log_error(
                    f"last siege refresh is very old. Going to generate a request")
                # This can cause race conditions.
                self.replayer.replay(self.update_flow)

            else:
                log_error(
                    "[+] cant refresh sieges. Replayer issnt idle.")
        else:
            pass
        self.refresh_timer()


this_class = SiegeRefresher()


def response(flow: http.HTTPFlow) -> None:
    try:
        simple_flow = SimpleFlow.from_flow(flow)

        this_class.handle_response(simple_flow)

    except Exception as e:
        Tooling.log_stacktrace(e)
