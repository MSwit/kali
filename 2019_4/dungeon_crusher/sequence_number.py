#!/usr/bin/env python3

from mitmproxy import http
from mitmproxy import ctx
import json
from tooling import Tooling
from mitm_logging import log_error
from simple_flow import SimpleFlow
import os
import signal
from time import sleep
from mitm_logging import log_error
from mitm_logging import log_warning


class Sequence_Number:

    def __init__(self):
        self.sequence_number = None
        self.mob_reward_consumed_modifier = 1
        self.seq_num = None
        self.debug = 0

    def is_ready(self):
        return self.seq_num != None

    def generate_updated_json_list(self, json_content_list):
        content = json.loads(json.dumps(json_content_list))
        for i, value in enumerate(json_content_list):
            content[i] = self.generate_updated_json(value)
        return content

    def generate_updated_json(self, json_content):
        content = json.loads(json.dumps(json_content))

        if self.sequence_number == None:
            self.sequence_number = content['sequence_number']
            self.seq_num = content['seq_num']

            log_error(
                f"[+] Setting initial sequence_number: {self.sequence_number} and seq_num: { self.seq_num}")
            return content

        kind = content['kind']
        if kind in "mob_reward_consumed":
            # TODO this is not correct, but ok for now.
            if json_content['level'] >= 122:
                self.mob_reward_consumed_modifier = 2
            self.sequence_number += self.mob_reward_consumed_modifier

        if kind in "battler_reward_chest_consumed":
            self.sequence_number += self.mob_reward_consumed_modifier

        if kind == 'state_updated':
            self.sequence_number += 1

        self.seq_num += 1
        content['seq_num'] = self.seq_num
        content['sequence_number'] = self.sequence_number

        return content

    def is_interesting_flow(self, flow: SimpleFlow) -> bool:
        return "\"sequence_number\":" in str(flow.modified_request)

    def check(self, flow: SimpleFlow) -> bool:
        log_for_error_finding = False
        request = flow.modified_request
        if "dark_ritual_performed" in str(request):
            log_error(request)
            sleep(1)
            log_for_error_finding = True
            # os.kill(os.getpid(), signal.SIGKILL)

        if not self.is_interesting_flow(flow):
            if log_for_error_finding:
                print("uninteresting")
            return True
        if type(flow.modified_request) is dict:
            print(flow.modified_request)

        json_content_list = flow.modified_request
        updated_content_list = self.generate_updated_json_list(
            json_content_list)
        if "dark_ritual_performed" in str(json_content_list):
            log_error(updated_content_list[0]['sequence_number'])
            log_error(json_content_list[0]['sequence_number'])
            pass

        if json_content_list != updated_content_list:
            log_error("[-] request was updated. but it shouldn't.")
            log_error("[-] Original request content: ")
            log_error(
                f"[-] {json.dumps(Tooling.remove_non_trivial_items_list(json_content_list), indent=2)}")

            log_error("[-] Updated request content: ")
            log_error(
                f"[-]{json.dumps(Tooling.remove_non_trivial_items_list(updated_content_list), indent=2)}")
            return False
        return True

    def try_update_request(self, simple_flow: SimpleFlow) -> None:
        log_error(json.dumps(simple_flow.modified_request))
        try:
            if not simple_flow.modified_request:
                return
            if self.try_handle_relogin(simple_flow):
                return

            json_content = simple_flow.modified_request
            if type(json_content) is list:
                new_json_content = self.generate_updated_json_list(
                    json_content)
            else:
                new_json_content = self.generate_updated_json(json_content)
            simple_flow.modified_request = new_json_content
        except:
            pass

    def print_requests(self, simple_flow: SimpleFlow) -> None:

        if not Tooling.is_interesting_request(simple_flow):
            return

        for request in simple_flow.modified_request:
            try:
                log_warning(
                    f"sequence_number: {request['sequence_number']}, 'seq_num' {request['seq_num']}, 'kind': {request['kind']}")
            except:
                log_warning(json.dumps(simple_flow.modified_request))

    def is_relogin(self, simple_flow: SimpleFlow):

        if "https://soulhunters.beyondmars.io/api/session" in simple_flow.url:
            try:
                if simple_flow.get_request().get('provider', '') == 'android':
                    return True
            except:
                pass
        return False

    def try_handle_relogin(self, simple_flow: SimpleFlow):
        if self.is_relogin(simple_flow):
            log_warning("Detect relogin")
            self.seq_num = None
            self.sequence_number = None
            return True

        return False


this_class = Sequence_Number()


def request(flow: http.HTTPFlow) -> None:
    # log_error(flow.request.pretty_url)

    # log_warning("-------------------------------------------")
    pass


def response(flow: http.HTTPFlow) -> None:
    simple_flow = SimpleFlow.from_flow(flow)
    log_error(str(simple_flow.response))
    if flow.response.status_code == 400:
        error = simple_flow.response.get("error", {})
        if error:
            log_error(str(simple_flow.response))
            message = error['message']
            if "[outside] Wrong action sequence number = " in message:
                correct_seq_num = message.split(" ")[-1]
                correct_seq_num = message.split("!")[0]
                log_error(f"corret seq_num should be {correct_seq_num}")

    this_class.check(simple_flow)
    # pass
