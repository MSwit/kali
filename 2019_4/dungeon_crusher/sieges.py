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


class Sieges:

    def __init__(self, sequence_number_modifier):
        self.sequence_number_modifier = sequence_number_modifier
        # self.my_id = "e786b343-35e8-4f59-9b86-256e188783d7" # nexus
        # self.user = "nexus"

        self.my_id = "a10e9130-7530-4839-9a11-825b99a10895"  # oneplus3t
        self.user = "oneplus"
        self.attacked_bosses = defaultdict(int)
        self.api_session_flow = None
        self.peding_attack = False

    def try_set_session_request(self, flow):
        if "https://soulhunters.beyondmars.io/api/session" in flow.request.pretty_url:  # TODO refactor
            self.api_session_flow = flow.copy()

    def attack(self, boss_id, flow: http.HTTPFlow):
        if not self.api_session_flow:
            log_error(
                "[-] Error: should attack, but there is no template stored yet.")
            return
        if self.peding_attack == True:
            log_error(
                "[-] Error: should attack, but there is another attack performing")
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

            self.peding_attack = True
            ctx.master.commands.call("replay.client", [fake_request])
        except Exception as e:
            import traceback

            log_error(f"[-] an error Occured: {e}")
            trace = traceback.format_stack()
            log_error(str(trace))
            log_error(str(e.__traceback__))
            import sys
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            log_error(str(exc_type))
            log_error(str(fname))
            log_error(str(exc_tb.tb_lineno))

    def is_search_for_boss_available(self, simple_flow):
        try:
            sieges = simple_flow.get_response()['sieges']
            if len(sieges) < 4:
                if self.peding_attack == False:
                    return True
        except:
            pass
        return False

    def find_boss_to_attack(self, simple_flow):
        request = simple_flow.get_request()
        response = simple_flow.get_response()

        try:
            log_error(f"[-] Error: {response['error']}")  # TODO move.
            return None
        except:
            pass

        try:
            if type(request) is list and [r for r in request if r.get('kind') == "find_boss_for_siege"]:

                for siege in response['sieges']:
                    boss_id = siege['id']
                    if siege['top_users']['finder'] == self.my_id:
                        if siege['top_attack_id'] == None:
                            log_warning("[+] Found normal boss to attack.")
                            return boss_id

                    if siege['current_hp'] > 120000000:
                        if boss_id not in self.attacked_bosses:
                            log_warning("[+] Found top boss to attack.")
                            return boss_id

            if "boss_siege_attack" in str(request):
                self.peding_attack = False
                siege = response['boss_siege_attack_result']['siege']
                boss_id = None

                my_score_entry = [
                    score for score in siege['scores'] if score['user_id'] == self.my_id][0]
                points = my_score_entry['points']
                if points == 0:
                    boss_id = siege['id']
                    log_error("[-] NO DMG DONE !")
                    if siege['current_hp'] > 120000000:
                        if self.attacked_bosses[boss_id] < 2:
                            log_error("[+] Found top boss to reattack.")
                            return siege['id']
                else:
                    log_error(f"DID DMG: {points}")

            if "https://soulhunters.beyondmars.io/api/boss_sieges/sieges" in simple_flow.url:
                for siege in response['sieges']:
                    boss_id = siege['id']
                    if siege['current_hp'] < 700000:
                        if self.attacked_bosses[boss_id] < 2:
                            log_warning(
                                f"[+] Found boss to attack because of low HP ({siege['current_hp']}).")
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

    def try_refill(self):
        if not self.api_session_flow:
            log_error(
                "[-] could not send refill request. No 'api/session' flow available")
            return
        attack_refill_json = {
            "kind": "boss_siege_refill_attack", "sequence_number": 11, "seq_num": 21}
        fake_request = self.api_session_flow.copy()
        attack_refill_json = [attack_refill_json]
        fake_request.request.content = json.dumps(  # will update seq_num etc. in request(..)
            attack_refill_json).encode('utf-8')

        time.sleep(0.5)

        # log_error("[#] I will send refill request")
        time.sleep(0.5)

        ctx.master.commands.call("replay.client", [fake_request])

    def check_response_simple(self, simple_flow):

        boss_id = self.find_boss_to_attack(simple_flow)
        if boss_id:
            log_error(boss_id)

            self.try_refill()
            self.attack(boss_id, simple_flow.flow)
        else:
            available = self.is_search_for_boss_available(simple_flow)
            if available:
                self.try_search_for_boss()

    def try_search_for_boss(self):

        if not self.api_session_flow:
            log_error(
                "[-] no api session flow set, yet. Cant search for new bosses.")
            return
        if not self.sequence_number_modifier.is_ready():
            log_error(
                "[-] Sequence number not initialized yet. Cant search for new bosses.")
            return

        search_for_bosses_json = {
            "kind": "find_boss_for_siege", "sequence_number": -1, "seq_num": -1}
        fake_request = self.api_session_flow.copy()
        search_for_bosses_json = [search_for_bosses_json]
        fake_request.request.content = json.dumps(  # will update seq_num etc. in request(..)
            search_for_bosses_json).encode('utf-8')

        time.sleep(0.5)

        ctx.master.commands.call("replay.client", [fake_request])
        log_error("[#] I send search for boss request")

    def check_response(self, flow: http.HTTPFlow):
        try:
            simple_flow = SimpleFlow.from_flow(flow)
            self.check_response_simple(simple_flow)
        except Exception as e:
            Tooling.log_stacktrace(e)


def should_lock_unlock_flow(flow: http.HTTPFlow) -> bool:
    if "https://soulhunters.beyondmars.io/api/clans" in flow.request.pretty_url:
        return False
    return "https://soulhunters.beyondmars.io" in flow.request.pretty_url


def process_request(flow: http.HTTPFlow) -> None:
    log_error("1")
    this_class.try_set_session_request(flow)
    log_error("2")
    if should_lock_unlock_flow(flow):
        lock.acquire()
        log_error("3")

        log_error(SimpleFlow.from_flow(flow).url)
        log_error("4")
        log_error(SimpleFlow.from_flow(flow).get_request())
        log_error("5")

        log_error("6")
    else:
        return

    sequence_number_modifier.try_update_request(flow)
    sequence_number_modifier.print_requests(flow)


def process_response(flow: http.HTTPFlow) -> None:

    simple_flow = SimpleFlow.from_flow(flow)

    if flow.response.status_code == 400:
        if flow.response.status_code == 400:
            error = simple_flow.get_response().get("error", {})
            if error:
                log_error(str(simple_flow.get_response()))
                message = error['message']
                if "[outside] Wrong action sequence number = " in message:
                    correct_seq_num = message.split(" ")[-1]
                    correct_seq_num = message.split("!")[0]
                    log_error(f"corret seq_num should be {correct_seq_num}")

    this_class.check_response(flow)

    try:
        if should_lock_unlock_flow(flow):
            lock.release()
    except Exception as e:
        Tooling.log_stacktrace(e)


sequence_number_modifier = Sequence_Number()
this_class = Sieges(sequence_number_modifier)


lock = Lock()


my_addons = [SequenceHandler()]
@concurrent
def request(flow: http.HTTPFlow) -> None:
    [addon.handle_request(SimpleFlow.from_flow(flow)) for addon in my_addons]
    try:
        # log_warning(
        #     "------------------ REQUEST starts -------------------")
        process_request(flow)
        # log_warning("------------------ REQUEST ends -------------------")
    except Exception as e:
        Tooling.log_stacktrace(e)


def response(flow: http.HTTPFlow) -> None:
    try:
        # log_warning(
        #     "------------------ RESPONSE starts -------------------")
        process_response(flow)
        # log_warning(
        #     "------------------ RESPONSE ende -------------------")
    except Exception as e:
        Tooling.log_stacktrace(e)
    [addon.handle_response(SimpleFlow.from_flow(flow)) for addon in my_addons]
