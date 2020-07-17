#!/usr/bin/env python3

import os
import signal
import json
from mitmproxy import http
from mitmproxy import ctx
from simple_flow import SimpleFlow


class Sequence:

    def __init__(self):
        self.flows = []

    def append(self, flow: SimpleFlow):
        self.flows.append(flow)

    @staticmethod
    def from_file(path_to_file):
        with open(path_to_file, 'r') as f:
            json_content = json.load(f)

        sequence = Sequence()
        for json_flow in json_content['flows']:
            sequence.flows.append(SimpleFlow.from_json(json_flow))
        return sequence

    def to_file(self, path_to_file):
        with open(path_to_file, 'w') as f:
            json.dump(self.to_json(), f)

    def to_json(self):
        flows = []
        for flow in self.flows:
            flows.append(flow.to_json())
        return {'flows': flows}


file_to_store = "test.json"
if os.path.exists(file_to_store):
    print(f"file {file_to_store} already exists.")
    os.kill(os.getpid(), signal.SIGKILL)

this_class = Sequence()


def response(flow: http.HTTPFlow) -> None:
    try:
        simple_flow = SimpleFlow.from_flow(flow)
        this_class.append(simple_flow)
        this_class.to_file(file_to_store)
        controll_sequence = Sequence.from_file(file_to_store)

        if json.dumps(this_class.to_json()) != json.dumps(controll_sequence.to_json()):
            ctx.log.error("[-] Error. Reloaded sequence is not equal the original stored one.")
            exit(0)
    except Exception as e:

        ctx.log.error(str(flow.request.get_content()))
        ctx.log.error(str(flow.response.get_content()))
        ctx.log.error("")
        ctx.log.error(str(e))
        exit(0)
