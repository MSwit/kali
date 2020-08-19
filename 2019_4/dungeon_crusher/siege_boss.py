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


class SiegeBossAttack_Finder:

    def __init__(self, boss_hp, power_attack: bool, has_to_be_finder: bool = True):
        self.my_id = "a10e9130-7530-4839-9a11-825b99a10895"
        self.boss_hp = boss_hp
        self.power_attack = power_attack
        self.has_to_be_finder = has_to_be_finder

    def get_attack_json_for_bosses(self, simple_flow: SimpleFlow):
        if not "find_boss_for_siege" in str(simple_flow.request):
            return None
        try:
            error_msg = simple_flow.response["error"]["message"]
            return None
        except:
            pass

        sieges = simple_flow.response['sieges']
        for siege in sieges:
            if (siege['top_users']['finder'] == self.my_id or not self.has_to_be_finder) and siege['current_hp'] == self.boss_hp:
                if siege['top_attack_id'] == None:
                    return self.get_attack_json_for_boss_id(siege['id'])

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


class SiegeBoss_Finisher:
    def __init__(self, maximal_boss_hp):
        self.my_id = "a10e9130-7530-4839-9a11-825b99a10895"
        self.maximal_boss_hp = maximal_boss_hp
        self.attacked_bosses = defaultdict(int)

    def get_attack_json_for_bosses(self, simple_flow: SimpleFlow):
        sieges = []
        try:
            sieges = simple_flow.response['sieges']
        except:
            pass

        try:
            sieges = [simple_flow.response['boss_siege_attack_result']['siege']]
        except:
            pass

        for siege in sieges:
            if siege['current_hp'] <= self.maximal_boss_hp and siege['current_hp'] > 0:
                boss_id = siege['id']
                if self.attacked_bosses[boss_id] == 0:  # currently not attacked
                    self.attacked_bosses[boss_id] += 1
                    log_error(
                        f"[+] SiegeBossFinisher: get_attack_json_for_bosses: current_boss_hp == {siege['current_hp']}")
                    return self.get_attack_json_for_boss_id(boss_id)
                else:
                    log_error("[-] WARNING !!!!!!!!!!!!!!!!!!!!!!!!!")
                    log_error("[-] WARNING !!!!!!!!!!!!!!!!!!!!!!!!!")
                    log_error(f"Attacks: {self.attacked_bosses[boss_id]}")
                    log_error(f"[-] Did not finished Boss with id {boss_id}")
                    log_error(f"Current Boss hp : {siege['current_hp']}")
                    log_error(json.dumps(siege, indent=2))
                    log_error("[-] WARNING !!!!!!!!!!!!!!!!!!!!!!!!!")
                    log_error("[-] WARNING !!!!!!!!!!!!!!!!!!!!!!!!!")

        return None

    def get_attack_json_for_boss_id(self, boss_id):
        return {
            "siege_id": boss_id,
            "power_attack": False,
            "autorestore_is_on": True,
            "kind": "boss_siege_attack",
            "sequence_number": -1,
            "seq_num": -1
        }


class TopBossAttack_Finder():

    def __init__(self, minimum_hp, max_attack_count):
        self.my_id = "a10e9130-7530-4839-9a11-825b99a10895"
        self.minimum_hp = minimum_hp
        self.max_attack_count = max_attack_count
        self.attacked_bosses = defaultdict(int)

    def get_attack_json_for_bosses(self, simple_flow: SimpleFlow):
        sieges = []

        if "find_boss_for_siege" in str(simple_flow.request):
            try:
                sieges = simple_flow.response['sieges']
            except:
                pass
            for siege in sieges:
                if siege['current_hp'] >= self.minimum_hp:
                    boss_id = siege['id']
                    self.attacked_bosses[boss_id] += 1
                    return self.get_attack_json_for_boss_id(boss_id)

        try:
            siege = simple_flow.response['boss_siege_attack_result']['siege']
        except:
            return None
        my_score_entry = [
            score for score in siege['scores'] if score['user_id'] == self.my_id][0]
        points = my_score_entry['points']
        boss_id = siege['id']
        if points == 0 and self.attacked_bosses[boss_id] <= self.max_attack_count:
            self.attacked_bosses[boss_id] += 1
            return self.get_attack_json_for_boss_id(boss_id)
        return None

    def get_attack_json_for_boss_id(self, boss_id):
        return {
            "siege_id": boss_id,
            "power_attack": False,
            "autorestore_is_on": True,
            "kind": "boss_siege_attack",
            "sequence_number": -1,
            "seq_num": -1
        }
