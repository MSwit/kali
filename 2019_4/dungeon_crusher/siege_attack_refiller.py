#!/usr/bin/env python3
from threading import Thread, Lock
import threading
from tooling import Tooling
from sequence_number import Sequence_Number
from mitmproxy import http
import json
import sys
import os
import signal
import time
from simple_flow import SimpleFlow
from partial_flow import PartialFlow
from collections import defaultdict
from sequence import SequenceHandler
import datetime
from mitmproxy.script import concurrent
from mitmproxy import proxy, options
from mitmproxy.tools.dump import DumpMaster
from mitmproxy import ctx
from mitm_logging import log_error
from mitm_logging import log_warning


class SiegeAttackRefiller:

    def __init__(self):
        self.attacks_left = 0

    def handle_request(self, simple_flow: SimpleFlow):
        try:

            attack_request = [
                request for request in simple_flow.modified_request if request['kind'] == 'boss_siege_attack'][0]
            if attack_request['power_attack'] == True:
                if self.attacks_left == 3:
                    pass
                if self.attacks_left == 2:
                    simple_flow.modified_request.insert(0,
                                                        {"kind": "boss_siege_refill_attack", "sequence_number": -1, "seq_num": -1})
                if self.attacks_left == 1:
                    simple_flow.modified_request.insert(0,
                                                        {"kind": "boss_siege_refill_attack", "sequence_number": -1, "seq_num": -1})
                    simple_flow.modified_request.insert(0,
                                                        {"kind": "boss_siege_refill_attack", "sequence_number": -1, "seq_num": -1})
                if self.attacks_left == 0:
                    simple_flow.modified_request.insert(0,
                                                        {"kind": "boss_siege_refill_attacks_max", "sequence_number": -1, "seq_num": -1})

                    # simple_flow.modified_request.insert(0,
                    #                                     {"kind": "boss_siege_refill_attack", "sequence_number": -1, "seq_num": -1})
                    # simple_flow.modified_request.insert(0,
                    #                                     {"kind": "boss_siege_refill_attack", "sequence_number": -1, "seq_num": -1})
                    # simple_flow.modified_request.insert(0,
                    #                                     {"kind": "boss_siege_refill_attack", "sequence_number": -1, "seq_num": -1})
            else:
                if self.attacks_left == 0:

                    simple_flow.modified_request.insert(0,
                                                        {"kind": "boss_siege_refill_attacks_max", "sequence_number": -1, "seq_num": -1})

                    log_error("going to add refill action")

                    # TODO
                    # handle : [-] Error: {'message': 'Failed to consume 56:1 - only 0 items available!', 'action': {'kind': 'boss_siege_refill_attacks_max', 'sequence_number': 16, 'seq_num': 35}, 'code': 400, 'backend_time': '2020-08-04T12:46:24.566Z'}

        except:
            pass

    def handle_response(self, simple_flow: SimpleFlow) -> None:
        try:
            self.attacks_left = simple_flow.response['boss_siege_refill_result']['attacks_left']
        except:
            pass

        log_error(f"Attacks left should be: {self.attacks_left}.........")
        response = simple_flow.response
        try:
            error_msg = response['error']['message']
            if error_msg.startswith("[boss_siege_attack] No attacks left"):
                log_error("Setting inital attacks to '0'.")
                self.attacks_left = 0
            else:
                log_error(error_msg)
        except:
            pass
