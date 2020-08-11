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


class Sieges:

    def __init__(self, sequence_number_modifier):
        self.sequence_number_modifier = sequence_number_modifier
        self.my_id = "a10e9130-7530-4839-9a11-825b99a10895"  # oneplus3t
        self.user = "oneplus"
        self.attacked_bosses = defaultdict(int)
        self.api_session_flow = None
        self.siege_boss_finder = [
            SiegeBossAttack_Finder(13000000, False),
            SiegeBossAttack_Finder(15000000, True),
            SiegeBossAttack_Finder(21000000, True),
            SiegeBossAttack_Finder(30000000, True),
            SiegeBoss_Finisher(3000000)
        ]

    def try_set_session_request(self, simple_flow: SimpleFlow) -> None:
        if "https://soulhunters.beyondmars.io/api/session" in simple_flow.url or "https://gw.soulhunters.beyondmars.io/api/session" in simple_flow.url:  # TODO refactor
            self.api_session_flow = simple_flow.flow.copy()

    def attack_with_json(self, attack_json):
        fake_request = self.api_session_flow.copy()
        request_content = [attack_json]
        fake_request.request.content = json.dumps(  # will update seq_num etc. in request(..)
            request_content).encode('utf-8')
        boss_id = attack_json['siege_id']
        self.attacked_bosses[boss_id] += 1
        log_warning("[#] I will send boss siege attack.")
        time.sleep(0.2)

        ctx.master.commands.call("replay.client", [fake_request])

    def attack(self, boss_id, flow: http.HTTPFlow):
        if not self.api_session_flow:
            log_error(
                "[-] Error: should attack, but there is no template stored yet.")
            return

        try:
            with open(f"{os.path.dirname(os.path.abspath(__file__))}/boss_siege_attack.json", 'r') as f:
                json_content = json.load(f)
            json_content['siege_id'] = boss_id
            fake_request = self.api_session_flow.copy()
            request_content = [json_content]
            fake_request.request.content = json.dumps(  # will update seq_num etc. in request(..)
                request_content).encode('utf-8')

            self.attacked_bosses[boss_id] += 1
            log_warning("[#] I will send boss siege attack.")
            time.sleep(0.5)

            self.pending_attack = True
            ctx.master.commands.call("replay.client", [fake_request])
        except Exception as e:
            tooling.log_stacktrace(e)

    def find_boss_to_attack(self, simple_flow):
        request = simple_flow.request
        response = simple_flow.response

        try:
            log_error(f"[-] Error: {response['error']}")  # TODO move.
            error_msg = response['error']['message']
            if error_msg.startswith("[boss_siege_attack] No attacks left"):
                self.pending_attack = False
            return None
        except:
            pass

        try:
            if type(request) is list and [r for r in request if r.get('kind') == "find_boss_for_siege"]:

                for siege in response['sieges']:
                    boss_id = siege['id']

                    # and siege['current_hp'] == 13000000:
                    if siege['top_users']['finder'] == self.my_id and siege['current_hp'] == 13000000:
                        log_error("[-] WARNING !!!!!!!!!!!!!!!!!!!!!!!!!")
                        log_error("[-] WARNING !!!!!!!!!!!!!!!!!!!!!!!!!")
                        log_error(
                            "[-] Erorr: should be handelet by other code: boss hp == 13mio")
                        log_error("[-] WARNING !!!!!!!!!!!!!!!!!!!!!!!!!")
                        log_error("[-] WARNING !!!!!!!!!!!!!!!!!!!!!!!!!")
                        if siege['top_attack_id'] == None:
                            log_warning("[+] Found normal boss to attack.")
                            return boss_id

                    if siege['top_users']['finder'] == self.my_id and siege['current_hp'] >= 500000000:
                        if siege['top_attack_id'] == None:
                            log_warning("[+] Found top normal boss to attack.")
                            return boss_id
                    if siege['current_hp'] > 220000000:
                        if boss_id not in self.attacked_bosses:
                            log_warning("[+] Found top boss to attack.")
                            return boss_id

            if "boss_siege_attack" in str(request):
                self.pending_attack = False
                siege = response['boss_siege_attack_result']['siege']
                boss_id = None

                my_score_entry = [
                    score for score in siege['scores'] if score['user_id'] == self.my_id][0]
                points = my_score_entry['points']
                if points == 0:
                    boss_id = siege['id']
                    log_error("[-] NO DMG DONE !")
                    if siege['current_hp'] > 220000000:
                        if self.attacked_bosses[boss_id] < 2:
                            return siege['id']
                else:
                    log_error(f"DID DMG: {points}")

            if "https://soulhunters.beyondmars.io/api/boss_sieges/sieges/" in simple_flow.url or "https://gw.soulhunters.beyondmars.io/api/boss_sieges/sieges/" in simple_flow.url:
                pass

            if "https://soulhunters.beyondmars.io/api/boss_sieges/sieges" == simple_flow.url or "https://gw.soulhunters.beyondmars.io/api/boss_sieges/sieges" == simple_flow.url:
                sieges = response['sieges']
                for siege in sieges:
                    boss_id = siege['id']
                    if siege['current_hp'] < 700000:
                        if self.attacked_bosses[boss_id] < 2:
                            log_warning(
                                f"[+] Found boss to attack because of low HP ({siege['current_hp']}).")
                            log_error("[+] Found top boss to reattack.")

                            log_error("[-] WARNING !!!!!!!!!!!!!!!!!!!!!!!!!")
                            log_error("[-] WARNING !!!!!!!!!!!!!!!!!!!!!!!!!")
                            log_error(
                                f"[-] Erorr: should be handelet by other code: boss hp low!. hp == {siege['current_hp'] }")
                            log_error("[-] WARNING !!!!!!!!!!!!!!!!!!!!!!!!!")
                            log_error("[-] WARNING !!!!!!!!!!!!!!!!!!!!!!!!!")
                            return boss_id
            log_error("NO BOSS FOUND !")
        except Exception as e:
            log_error(f"[-] Error: {str(e)}")
            log_error("")

            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            msg = str(exc_type)
            msg += "\n" + str(exc_tb.tb_lineno)
            msg += "\n" + str(fname)
            msg += "\n"
            msg += "\n" + json.dumps(response)
            log_error(msg)
            log_error(f"[-] Error: {str(e)}")

            # os.kill(os.getpid(), signal.SIGKILL)

    def get_attack_json(self, simple_flow: SimpleFlow):
        for finder in self.siege_boss_finder:
            attack_json = finder.get_attack_json_for_bosses(simple_flow)
            if attack_json:
                return attack_json

    def check_response_simple(self, simple_flow):

        attack_json = self.get_attack_json(simple_flow)
        if attack_json:
            self.attack_with_json(attack_json)
            return

        boss_id = self.find_boss_to_attack(simple_flow)
        if boss_id:
            log_error(boss_id)
            self.attack(boss_id, simple_flow.flow)

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

    if simple_flow.status_code == 400:
        error = simple_flow.response.get("error", {})
        if error:
            log_error(json.dumps(simple_flow.response, indent=2))
            message = error['message']
            if "[outside] Wrong action sequence number = " in message:
                correct_seq_num = message.split(" ")[-1]
                correct_seq_num = message.split("!")[0]
                log_error(f"corret seq_num should be {correct_seq_num}")
                exit(1)
            if "Sequence number mismatch" in message:
                log_error(f"corret seq_num should be {message}")
                exit(1)

            if "[find_boss_for_siege] Boss siege limit reached!" in message:
                pass

    this_class.check_response(simple_flow)

    try:
        if should_lock_unlock_flow(simple_flow):
            lock.release()
    except Exception as e:
        Tooling.log_stacktrace(e)


sequence_number_modifier = Sequence_Number()
this_class = Sieges(sequence_number_modifier)


lock = Lock()


boss_searcher = BossSearcher(sequence_number_modifier)
my_addons = [SequenceHandler(),
             SiegeAttackRefiller(),
             siege_refresher.this_class,  # prevent two instances
             boss_searcher]


@concurrent
def request(flow: http.HTTPFlow) -> None:
    simple_flow = SimpleFlow.from_flow(flow)
    if not "soulhunters.beyondmars" in simple_flow.url:
        flow.kill
        return

    [addon.handle_request(simple_flow) for addon in my_addons]
    try:
        # log_warning(
        #     "------------------ REQUEST starts -------------------")
        process_request(simple_flow)

        flow.request.content = json.dumps(
            simple_flow.modified_request).encode('utf-8')
        # log_warning("------------------ REQUEST ends -------------------")
    except Exception as e:
        Tooling.log_stacktrace(e)


def response(flow: http.HTTPFlow) -> None:
    simple_flow = SimpleFlow.from_flow(flow)

    try:
        # log_warning(
        #     "------------------ RESPONSE starts -------------------")
        process_response(simple_flow)
        # log_warning(
        #     "------------------ RESPONSE ende -------------------")
    except Exception as e:
        Tooling.log_stacktrace(e)
    [addon.handle_response(simple_flow) for addon in my_addons]
    pass
