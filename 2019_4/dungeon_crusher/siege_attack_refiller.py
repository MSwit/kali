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
        self.try_use_max_filler = False

    def handle_request(self, simple_flow: SimpleFlow):
        try:
            ui_based_refills_normal = [
                request for request in simple_flow.modified_request if request['kind'] == 'boss_siege_refill_attack']
            ui_based_refills_max = [
                request for request in simple_flow.modified_request if request['kind'] == 'boss_siege_refill_attacks_max']
            self.attacks_left += len(ui_based_refills_normal)
            self.attacks_left += len(ui_based_refills_max) * 3

            attack_request = [
                request for request in simple_flow.modified_request if request['kind'] == 'boss_siege_attack'][0]

            number_of_needed_refills = 0
            if attack_request['power_attack'] == True:
                number_of_needed_refills = 3
            else:
                number_of_needed_refills = 1

            self.add_refills_to_match(number_of_needed_refills, simple_flow)
        except:
            pass

    def add_refills_to_match(self, number_of_needed_refills: int, simple_flow: SimpleFlow) -> None:
        if number_of_needed_refills == 3 and self.attacks_left == 0 and self.try_use_max_filler:
            simple_flow.modified_request.insert(0,
                                                {"kind": "boss_siege_refill_attacks_max", "sequence_number": -1, "seq_num": -1})
            return
        for i in range(number_of_needed_refills-self.attacks_left):
            simple_flow.modified_request.insert(0,
                                                {"kind": "boss_siege_refill_attack", "sequence_number": -1, "seq_num": -1})

    def handle_response(self, simple_flow: SimpleFlow) -> None:
        try:
            self.attacks_left = simple_flow.response['boss_siege_refill_result']['attacks_left']
        except:
            pass

        # log_error(f"Attacks left should be: {self.attacks_left}.........")
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
