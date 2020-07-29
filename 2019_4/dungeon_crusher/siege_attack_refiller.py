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
from mitm_logging import log_error
from mitm_logging import log_warning
from sequence import SequenceHandler
import datetime
from mitmproxy.script import concurrent
from mitmproxy import proxy, options
from mitmproxy.tools.dump import DumpMaster
from mitmproxy import ctx


class SiegeAttackRefiller:

    def __init__(self):
        self.attacks_left = -1

    def handle_request(self, simple_flow: SimpleFlow):

        attack_request = simple_flow.get_request()[0]
        if attack_request['power_attack'] == True:
            if self.attacks_left == 3:
                pass
            if self.attacks_left == 2:
                request = simple_flow.get_request().insert(0,
                                                           {"kind": "boss_siege_refill_attack", "sequence_number": -1, "seq_num": -1})
                simple_flow.request = request
            if self.attacks_left == 1:
                request = simple_flow.get_request().insert(0,
                                                           {"kind": "boss_siege_refill_attack", "sequence_number": -1, "seq_num": -1})
                request = simple_flow.get_request().insert(0,
                                                           {"kind": "boss_siege_refill_attack", "sequence_number": -1, "seq_num": -1})
                simple_flow.request = request

            if self.attacks_left == 0:
                request = simple_flow.get_request().insert(0,
                                                           {"kind": "boss_siege_refill_attacks_max", "sequence_number": -1, "seq_num": -1})

                simple_flow.request = request
        else:
            if self.attacks_left == 0:
                request = simple_flow.get_request().insert(0,
                                                           {"kind": "boss_siege_refill_attacks_max", "sequence_number": -1, "seq_num": -1})

                simple_flow.request = request

        return simple_flow

    def handle_response(self):
        pass
