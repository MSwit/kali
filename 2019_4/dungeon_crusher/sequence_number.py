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


class Sequence_Number:

    def __init__(self):
        self.sequence_number = None
        self.mob_reward_consumed_modifier = 1
        self.seq_num = None
        self.debug = 0

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

            log_error("[+] Setting initial sequence_number and seq_num")
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
        return "\"sequence_number\":" in str(flow.request)

    def check(self, flow: SimpleFlow) -> bool:
        log_error("asdf")
        log_for_error_finding = False
        request = flow.get_request()
        if "dark_ritual_performed" in str(request):
            log_error(request)
            sleep(1)
            log_for_error_finding = True
            # os.kill(os.getpid(), signal.SIGKILL)

        if not self.is_interesting_flow(flow):
            if log_for_error_finding:
                print("uninteresting")
            return True
        if type(flow.request) is dict:
            print(flow.request)

        # self.debug += 1

        json_content_list = json.loads(flow.request)

        # json_content_list = json.loads(flow.request.get_content())
        # ctx.log.error("[-] Original request content: ")
        # ctx.log.error(
        #     f"[-] {json.dumps(Tooling.remove_non_trivial_items_list(json_content_list), indent=2)}")

        updated_content_list = self.generate_updated_json_list(json_content_list)
        if "dark_ritual_performed" in str(json_content_list):
            log_error(updated_content_list[0]['sequence_number'])
            log_error(json_content_list[0]['sequence_number'])
            pass

        if json_content_list != updated_content_list:
            ctx.log.error("[-] request was updated. but it shouldn't.")
            ctx.log.error("[-] Original request content: ")
            ctx.log.error(
                f"[-] {json.dumps(Tooling.remove_non_trivial_items_list(json_content_list), indent=2)}")

            ctx.log.error("[-] Updated request content: ")
            ctx.log.error(
                f"[-]{json.dumps(Tooling.remove_non_trivial_items_list(updated_content_list), indent=2)}")
            return False
        return True

    def try_update_request(self, flow: http.HTTPFlow) -> None:
        try:
            if len(flow.request.get_content()) == 0:
                return
            json_content = json.loads(flow.request.get_content())
            if type(json_content) is list:
                new_json_content = self.generate_updated_json_list(json_content)
            else:
                new_json_content = self.generate_updated_json(json_content)
            flow.request.content = json.dumps(new_json_content).encode('utf-8')
        except:
            pass

    def print_requests(self, flow: http.HTTPFlow) -> None:

        if not Tooling.is_interesting_request(flow):
            return

        content = json.loads(flow.request.get_content())

        for request in content:
            try:
                ctx.log.warn(
                    f"sequence_number: {request['sequence_number']}, 'seq_num' {request['seq_num']}, 'kind': {request['kind']}")
            except:
                ctx.log.warn(json.dumps(content))


this_class = Sequence_Number()


def request(flow: http.HTTPFlow) -> None:
    # log_error(flow.request.pretty_url)

    # ctx.log.warn("-------------------------------------------")
    pass


def response(flow: http.HTTPFlow) -> None:
    simple_flow = SimpleFlow.from_flow(flow)
    log_error(str(simple_flow.get_response()))
    if flow.response.status_code == 400:
        error = simple_flow.get_response().get("error", {})
        if error:
            log_error(str(simple_flow.get_response()))
            message = error['message']
            if "[outside] Wrong action sequence number = " in message:
                correct_seq_num = message.split(" ")[-1]
                correct_seq_num = message.split("!")[0]
                log_error(f"corret seq_num should be {correct_seq_num}")

    this_class.check(simple_flow)
    # pass
