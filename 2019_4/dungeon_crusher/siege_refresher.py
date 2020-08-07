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
        self.refresh_timer()

    def handle_request(self, simple_flow: SimpleFlow) -> None:
        pass

    def handle_response(self, simple_flow: SimpleFlow) -> None:
        log_error("[+] SiegeRefresher:handle_response called")

        if simple_flow.url == "https://soulhunters.beyondmars.io/api/boss_sieges/sieges" or simple_flow.url == "https://gw.soulhunters.beyondmars.io/api/boss_sieges/sieges":
            self.update_flow = simple_flow.flow.copy()
            self.update_flow.request.content = json.dumps({}).encode('utf-8')

        try:
            sieges = simple_flow.response['sieges']
            log_error(f"[+] Current siege count: {len(sieges)}.........")
            self.refresh_timer()
        except:
            pass

    def refresh_timer(self):
        if self.refresh_thread:
            self.refresh_thread.cancel()
        self.refresh_thread = Timer(5, self.replay_siege_update_flow)
        self.refresh_thread.start()

    def replay_siege_update_flow(self):
        if self.update_flow:
            log_warning(
                f"last siege refresh is very old. Going to generate a request")
            ctx.master.commands.call(
                "replay.client", [self.update_flow.copy()])
        else:
            log_error(
                "[-] could not replay siege refresher. No basic flow available")
        self.refresh_timer()


this_class = SiegeRefresher()


def response(flow: http.HTTPFlow) -> None:
    try:
        simple_flow = SimpleFlow.from_flow(flow)

        this_class.handle_response(simple_flow)

    except Exception as e:
        Tooling.log_stacktrace(e)
