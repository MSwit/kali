#!/usr/bin/env python3

import os
import signal
import json
from mitmproxy import http
from mitmproxy import ctx
from simple_flow import SimpleFlow
from mitm_logging import log_warning
from mitm_logging import log_error
from partial_flow import PartialFlow
import datetime
import tooling


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


class SequenceHandler:

    def __init__(self):
        self.sequence_filename = datetime.datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S") + ".json"
        self.partial_flow = PartialFlow()
        self.sequence = Sequence()

    def handle_request(self, simple_flow: SimpleFlow) -> None:
        self.partial_flow.set_request(simple_flow)

    def handle_response(self, flow: SimpleFlow) -> None:
        if self.partial_flow.is_request_available:
            self.partial_flow.set_modified_request(flow)
            self.partial_flow.set_response(flow)
            simple_flow = self.partial_flow.combine()

            self.sequence.append(simple_flow)
            self.sequence.to_file(self.sequence_filename)


this_class = SequenceHandler()


def response(flow: http.HTTPFlow) -> None:
    try:
        simple_flow = SimpleFlow.from_flow(flow)
        this_class.handle_request(simple_flow)
        this_class.handle_response(simple_flow)
        controll_sequence = Sequence.from_file(this_class.sequence_filename)
        if json.dumps(this_class.sequence.to_json()) != json.dumps(controll_sequence.to_json()):
            ctx.log.error(
                "[-] Error. Reloaded sequence is not equal the original stored one.")
            exit(0)
    except Exception as e:
        tooling.Tooling.log_stacktrace(e)

        exit(0)
