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
import siege_refresher
from siege_boss import SiegeBossAttack_Finder
from siege_boss import SiegeBoss_Finisher
from siege_boss import TopBossAttack_Finder
from boss_searcher import BossSearcher
from mob_reward_consumed import MobRewardLogger
import mob_reward_consumed
from boss_config_id_logger import BossConfigIdLogger
import boss_config_id_logger
from client_replay import ClientReplay
from resurect_replayer import ReplayResurrect


class Sieges:

    def __init__(self, sequence_number_modifier, replayer):
        self.sequence_number_modifier = sequence_number_modifier
        self.my_id = "a10e9130-7530-4839-9a11-825b99a10895"  # oneplus3t
        self.user = "oneplus"
        self.attacked_bosses = defaultdict(int)
        self.api_session_flow = None
        self.replayer = replayer
        self.siege_boss_finder = [
            TopBossAttack_Finder(220000001, 4),
            #SiegeBossAttack_Finder(11500000, False),
            #SiegeBossAttack_Finder(12850000, True, False),
            SiegeBossAttack_Finder(9000000, True),
            SiegeBossAttack_Finder(11000000, True),
            SiegeBossAttack_Finder(13000000, True),
            SiegeBossAttack_Finder(12850000, True, False),
            SiegeBossAttack_Finder(15000000, True, False),
            SiegeBossAttack_Finder(17850000, True, False),
            SiegeBossAttack_Finder(18000000, True, False),
            SiegeBossAttack_Finder(21000000, True, False),
            SiegeBossAttack_Finder(25000000, True, False),
            SiegeBossAttack_Finder(25700000, True, False),
            SiegeBossAttack_Finder(30000000, True, False),
            # SiegeBossAttack_Finder(42000000, True),
            # SiegeBossAttack_Finder(54000000, True),
            # SiegeBossAttack_Finder(62000000, True),
            SiegeBoss_Finisher(2500000)
        ]
        self.error = False

    def try_set_session_request(self, simple_flow: SimpleFlow) -> None:
        if "https://soulhunters.beyondmars.io/api/session" in simple_flow.url or "https://gw.soulhunters.beyondmars.io/api/session" in simple_flow.url:  # TODO refactor
            self.api_session_flow = simple_flow.flow.copy()

    def attack_with_json(self, attack_json):
        if self.api_session_flow:
            log_error("                          JUHU api_session_flow was set")
        fake_request = self.api_session_flow.copy()
        request_content = [attack_json]
        fake_request.request.content = json.dumps(  # will update seq_num etc. in request(..)
            request_content).encode('utf-8')
        boss_id = attack_json['siege_id']
        self.attacked_bosses[boss_id] += 1
        log_warning("[#] I will send boss siege attack.")
        self.replayer.replay(fake_request)

    def get_attack_json(self, simple_flow: SimpleFlow):
        for finder in self.siege_boss_finder:
            attack_json = finder.get_attack_json_for_bosses(simple_flow)
            if attack_json:
                return attack_json

    def check_response_simple(self, simple_flow):
        if not self.api_session_flow or not self.replayer.isIdle():
            return
        attack_json = self.get_attack_json(simple_flow)
        if attack_json:
            self.attack_with_json(attack_json)
            return

    def check_response(self, simple_flow: SimpleFlow):
        try:
            self.check_response_simple(simple_flow)
        except Exception as e:
            Tooling.log_stacktrace(e)


def should_lock_unlock_flow(simple_flow: SimpleFlow) -> bool:
    if "https://soulhunters.beyondmars.io/api/clans" in simple_flow.url or "https://gw.soulhunters.beyondmars.io/api/clans" in simple_flow.url:
        return False
    return "https://soulhunters.beyondmars.io" in simple_flow.url or "https://gw.soulhunters.beyondmars.io" in simple_flow.url


def process_request(simple_flow: SimpleFlow) -> None:

    this_class.try_set_session_request(simple_flow)

    if should_lock_unlock_flow(simple_flow):
        lock.acquire()
    else:
        return

    sequence_number_modifier.try_update_request(simple_flow)
    sequence_number_modifier.print_requests(simple_flow)


def process_response(simple_flow: SimpleFlow) -> None:

    if simple_flow.status_code >= 400:
        error = simple_flow.response.get("error", {})
        if error:
            log_error(json.dumps(simple_flow.response, indent=2))
            message = error['message']

            if "[outside] Wrong action sequence number = " in message:
                correct_seq_num = message.split(" ")[-1]
                correct_seq_num = message.split("!")[0]
                log_error(f"corret seq_num should be {correct_seq_num}")
            if "Sequence number mismatch" in message:
                log_error(f"[-] Error:  {message}")
            if "Session started on other device" in message:
                log_error(f"[-] Error:  {message}")

            if "[find_boss_for_siege] Boss siege limit reached!" in message:
                pass
            else:
                this_class.error = True

    this_class.check_response(simple_flow)

    try:
        if should_lock_unlock_flow(simple_flow):
            lock.release()
    except Exception as e:
        Tooling.log_stacktrace(e)


replayer = ClientReplay()
sequence_number_modifier = Sequence_Number()
this_class = Sieges(sequence_number_modifier, replayer)


lock = Lock()

boss_searcher = BossSearcher(sequence_number_modifier, replayer)
refresher = siege_refresher.this_class  # prevent two instances
refresher.replayer = replayer


my_addons = [ReplayResurrect(replayer),
             replayer,
             SequenceHandler(),
             SiegeAttackRefiller(),
             boss_searcher,
             refresher,
             MobRewardLogger(mob_reward_consumed.filename),
             #  BossConfigIdLogger(boss_config_id_logger.filename)
             ]


def should_anaylse_Request(simple_flow):
    return True


@concurrent
def request(flow: http.HTTPFlow) -> None:

    simple_flow = SimpleFlow.from_flow(flow)
    if not "soulhunters.beyondmars" in simple_flow.url:
        # flow.kill()
        return
    if not should_anaylse_Request(simple_flow):
        return
    log_warning(
        "------------------ REQUEST starts -------------------")

    [addon.handle_request(simple_flow) for addon in my_addons]
    try:
        process_request(simple_flow)  # // need to lock befor calling addons

        flow.request.content = json.dumps(
            simple_flow.modified_request).encode('utf-8')
    except Exception as e:
        Tooling.log_stacktrace(e)
    log_warning("------------------ REQUEST ends -------------------")


def response(flow: http.HTTPFlow) -> None:

    log_error("response starts")
    simple_flow = SimpleFlow.from_flow(flow)
    if not should_anaylse_Request(simple_flow):
        return
    # TODO, its bad to handle this addon in a special way.
    replayer.handle_response(simple_flow)
    try:
        log_warning(
            "------------------ RESPONSE starts -------------------")
        process_response(simple_flow)

    except Exception as e:
        Tooling.log_stacktrace(e)
    [addon.handle_response(simple_flow) for addon in my_addons]
    if this_class.error:
        exit(1)
    pass
    log_warning(
        "------------------ RESPONSE ende -------------------")
