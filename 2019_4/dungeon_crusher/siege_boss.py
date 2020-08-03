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
from siege_attack_refiller import SiegeAttackRefiller
from siege_refresher import SiegeRefresher


class SiegeBossAttack:

    # def __init__(self):
    def __init__(self, must_be_finder: bool, current_hp, minimum_hp, maximum_hp, power_attack: bool):
        self.my_id = "my_id"
        self.must_be_finder = must_be_finder
        self.power_attack = power_attack
        pass

    def get_attack_json_for_bosses(self, simple_flow: SimpleFlow):
        sieges = simple_flow.response['sieges']
        for siege in sieges:
            attack_json = self.get_attack_json_for_boss(siege)
            if attack_json:

                return attack_json
        return None

    def get_attack_json_for_boss(self, siege):
        try:
            if self.must_be_finder:
                if siege['top_users']['finder'] == self.my_id:
                    return self.get_attack_json_for_boss_id(siege['id'])
        except:
            pass
        return None

    def get_attack_json_for_boss_id(self, boss_id):
        return {
            "siege_id": boss_id,
            "power_attack": self.power_attack,
            "autorestore_is_on": True,
            "kind": "boss_siege_attack",
            "sequence_number": -1,
            "seq_num": -1
        }