#!/usr/bin/env python3

import os
import signal
import json
from mitmproxy import http
from mitmproxy import ctx
from simple_flow import SimpleFlow


class sequence:

    def __init__(self):
        self.flows = []

    def append(self, flow: SimpleFlow):
        self.flows.append(flow)

    @staticmethod
    def from_file(path_to_file):
        pass

    def to_file(self, path_to_file):
        json_content = []
        for flow in self.flows:
            json_content.append(flow.to_json())
        with open(path_to_file, 'w') as f:
            json.dump(json_content, f)


file_to_store = "test.json"
if os.path.exists(file_to_store):
    print(f"file {file_to_store} already exists.")
    os.kill(os.getpid(), signal.SIGKILL)

this_class = sequence()


def response(flow: http.HTTPFlow) -> None:
    try:
        simple_flow = SimpleFlow.from_flow(flow)
        this_class.append(simple_flow)
        this_class.to_file(file_to_store)
    except Exception as e:

        ctx.log.error(str(flow.request.get_content()))
        ctx.log.error(str(flow.response.get_content()))
        ctx.log.error("")
        ctx.log.error(str(e))
        exit(0)
