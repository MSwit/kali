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
from sequence import SequenceHandler
import datetime
from shutil import copyfile


class MobRewardLogger:

    def __init__(self, log_file):
        self.log_file = log_file
        self.set_initial_content()

    def set_initial_content(self):
        try:
            with open(self.log_file, 'r') as f:
                self.content = json.load(f)
        except:
            self.content = []

    def append_requests(self, requests):
        self.content.append(requests)
        with open(self.log_file, 'w') as f:
            json.dump(self.content, f)

    def handle_request(self, simple_flow: SimpleFlow):

        if type(simple_flow.request) is list:
            mob_reward_consumed_requests = [
                request for request in simple_flow.request if request.get('kind') == "mob_reward_consumed"]

            if mob_reward_consumed_requests:
                self.append_requests(mob_reward_consumed_requests)

    def handle_response(self, simple_flow: SimpleFlow) -> None:
        pass


filename = "mob_reward_logger.json"
if os.path.exists(filename):
    backup = os.path.splitext(filename)[0] + "_" + datetime.datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S") + ".json"
    copyfile(filename, backup)

this_class = MobRewardLogger(filename)


def request(flow: http.HTTPFlow) -> None:
    log_error("----------- request starts")

    simple_flow = SimpleFlow.from_flow(flow)
    this_class.handle_request(simple_flow)
    log_error("----------- request ends")
