#!/usr/bin/env python3

from mitmproxy import http
from mitmproxy import ctx
import json
from tooling import Tooling
from mitm_logging import log_error
from simple_flow import SimpleFlow
import os
import signal
from time import sleep
from mitm_logging import log_error
from mitm_logging import log_warning
from datetime import datetime


class SiegeRefresher:

    def __init__(self):
        self.last_update = datetime.now()
        self.update_flow = None

    def handle_request(self, simple_flow: SimpleFlow) -> None:
        pass

    def handle_response(self, simple_flow: SimpleFlow) -> None:

        if simple_flow.url == "https://soulhunters.beyondmars.io/api/boss_sieges/sieges":
            self.update_flow = simple_flow.flow.copy()
            self.update_flow.request.content = json.dumps({}).encode('utf-8')

        now = datetime.now()
        try:
            # log_error("asdfasdf")
            sieges = simple_flow.response['sieges']
            log_error(f"Current siege count: {len(sieges)}.........")
            self.last_update = now

        except:
            if "sieges" in (str(simple_flow.response)):
                log_error(json.dumps(simple_flow.response))
            pass

        seconds_since_last_update = (now - self.last_update).total_seconds()
        if seconds_since_last_update > 3:
            if self.update_flow:
                self.last_update = now
                log_warning(
                    f"last siege refresh is very old {seconds_since_last_update} seconds. Going to generate a request")

                ctx.master.commands.call(
                    "replay.client", [self.update_flow.copy()])


this_class = SiegeRefresher()


def response(flow: http.HTTPFlow) -> None:
    try:
        simple_flow = SimpleFlow.from_flow(flow)

        this_class.handle_response(simple_flow)

    except Exception as e:
        Tooling.log_stacktrace(e)
