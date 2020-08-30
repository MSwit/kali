#!/usr/bin/env python3

from mitmproxy import http
from mitmproxy import ctx
import json
from tooling import Tooling
from mitm_logging import log_error
from simple_flow import SimpleFlow
import os
from time import sleep
from mitm_logging import log_error
from mitm_logging import log_warning
import datetime
from shutil import copyfile


class BossConfigIdLogger:

    def __init__(self, log_file):
        self.log_file = log_file
        self.set_initial_content()

    def set_initial_content(self):
        try:
            with open(self.log_file, 'r') as f:
                self.content = json.load(f)
        except:
            self.content = []

    def append_siege_info(self, siege_info):
        self.content.append(siege_info)
        with open(self.log_file, 'w') as f:
            json.dump(self.content, f)

    def handle_request(self, simple_flow: SimpleFlow):
        pass

    def handle_response(self, simple_flow: SimpleFlow) -> None:
        sieges = []
        if "boss_siege_attack"in str(simple_flow.request):
            pass
            siege = simple_flow.response['boss_siege_attack_result']['siege']
            sieges = [siege]

        try:
            sieges = simple_flow.response['sieges']
        except:
            pass

        for siege in sieges:
            siege_info = BossConfigIdLogger.parse_siege_info(siege)
            self.append_siege_info(siege_info)

    @staticmethod
    def parse_siege_info(siege):
        boss_id = siege['id']
        current_hp = siege['current_hp']
        created_at = siege['created_at']
        boss_config_id = siege['boss_config_id']

        return {
            "boss_id": boss_id,
            "current_hp": current_hp,
            "created_at": created_at,
            "boss_config_id": boss_config_id,
        }


filename = "boss_config_id_logger.json"
if os.path.exists(filename):
    backup = os.path.splitext(filename)[0] + "_" + datetime.datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S") + ".json"
    copyfile(filename, backup)

this_class = BossConfigIdLogger(filename)


def request(flow: http.HTTPFlow) -> None:
    log_error("----------- request starts")

    simple_flow = SimpleFlow.from_flow(flow)
    this_class.handle_request(simple_flow)
    log_error("----------- request ends")
