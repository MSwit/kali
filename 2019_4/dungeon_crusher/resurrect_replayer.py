#!/usr/bin/env python3
from mitmproxy import ctx
from mitmproxy import http
from mitm_logging import log_error
from simple_flow import SimpleFlow
from threading import Thread, Lock
import sys
import time
from threading import Timer


class ReplayResurrect:

    def __init__(self, replayer):
        self.last_pending_id = None
        self.replayer = replayer
        self.refresh_thread = None
        self.resurect_count = 0

    def handle_request(self, simple_flow: SimpleFlow) -> None:
        if self.resurect_count > 0:
            log_error(f"[-] Resurection count: {self.resurect_count}")
        self.refresh_timer()

    def handle_response(self, simple_flow: SimpleFlow) -> None:
        pass

    def refresh_timer(self):
        if self.refresh_thread:
            self.refresh_thread.cancel()
        self.last_pending_id = self.replayer.pending_id

        self.refresh_thread = Timer(10, self.try_resurrect)
        self.refresh_thread.start()

    def try_resurrect(self):
        if not self.replayer.isIdle():
            log_error("[-] Something went wrong. Try to resurrect the replayer")
            self.replayer.reset(self.replayer.pending_id)
            self.resurect_count += 1

        self.refresh_timer()
