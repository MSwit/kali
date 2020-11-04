#!/usr/bin/env python3
from threading import Thread, Lock
from simple_flow import SimpleFlow
import mitm_logging
from mitmproxy.script import concurrent
from mitmproxy import http
import json


class SingleFlowGate:
    def __init__(self):
        self.lock = Lock()
        self.locked_flow = None
        self.pending_flows_count = 0
        self.logging = False

    def should_lock(self, simple_flow: SimpleFlow) -> bool:
        if "https://soulhunters.beyondmars.io/api/clans" in simple_flow.url or "https://gw.soulhunters.beyondmars.io/api/clans" in simple_flow.url:
            return False

        if "sequence_number" in str(simple_flow.modified_request) and "seq_num" in str(simple_flow.modified_request):
            # // issue with quests ! But maybe only siege quests which causes errors all the time.
            return True
        # if "https://soulhunters.beyondmars.io" in simple_flow.url or "https://gw.soulhunters.beyondmars.io" in simple_flow.url:
        #     return True
        return False

    def handle_request(self, simple_flow: SimpleFlow) -> None:
        if self.should_lock(simple_flow):
            self.pending_flows_count += 1

            self.log_error(
                f"[+] want to aquire lock. Currently there are {self.pending_flows_count} in the queue")
            self.lock.acquire()

            self.pending_flows_count -= 1
            self.locked_flow = simple_flow

    def handle_response(self, simple_flow: SimpleFlow) -> None:
        if self.should_lock(simple_flow):
            if self.locked_flow.flow_id == simple_flow.flow_id:
                self.log_error(
                    f"[+] going to release one flow.")
                self.lock.release()
            else:
                self.log_error(
                    "[-] want to release the lock, but the flow issnt the same.", force=True)
                self.log_error(
                    f"response flow id == {simple_flow.flow.id}", force=True)
                self.log_error(
                    f"locked flow id == {self.locked_flow.flow.id}", force=True)
                exit(1)

    def log_error(self, msg: str, force: bool = False) -> None:
        if self.logging:
            mitm_logging.log_error(msg)
