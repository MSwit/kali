#!/usr/bin/env python3
from mitmproxy import ctx
from mitmproxy import http
from mitm_logging import log_error
from simple_flow import SimpleFlow
from threading import Thread, Lock
import sys
import time

print(sys.argv)


class ClientReplay:

    def __init__(self):
        self.pending_id = None
        self.lock = Lock()
        self.arena_attack_id = None
        self.rating_boss_id = None

    def replay(self, flow: http.HTTPFlow) -> None:
        if not self.isIdle():
            # can happen when called from thread.
            log_error("[-] There is already another flow pending")
            return
        log_error(
            f"[+] ClientReplay: going to aquire lock for replay flow with id : {flow.id}")
        self.lock.acquire()
        copy = flow.copy()
        self.pending_id = copy.id
        ctx.master.commands.call("replay.client", [copy])
        self.lock.release()

    def reset(self, id_to_reset):
        if self.pending_id == id_to_reset:
            self.pending_id = None
        elif self.arena_attack_id == id_to_reset:
            self.arena_attack_id == None
        elif self.rating_boss_id == id_to_reset:
            self.rating_boss_id = None
        else:
            raise Exception(f"No id: {id_to_reset} to reset !")

    def handle_request(self, simple_flow: SimpleFlow) -> None:
        pass

    def handle_response(self, simple_flow: SimpleFlow) -> None:
        if simple_flow.flow.id == self.pending_id:
            # log_error(f"[+] \t\t REPLAY - seen flow in response -> cleanup. id : {self.pending_id}")
            self.reset(self.pending_id)
            pass

    def isIdle(self):
        return self.pending_id == None
