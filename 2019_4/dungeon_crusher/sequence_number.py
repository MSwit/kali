#!/usr/bin/env python3

from mitmproxy import http
from mitmproxy import ctx
import json


class Sequence_Number:

    def __init__(self):
        self.last_sequence_number = None
        self.last_seq_num = None

    def generate_updated_json_list(self, json_content_list):
        for i, value in enumerate(json_content_list):
            json_content_list[i] = self.update(value)

    def generate_updated_json(self, json_content):
        import copy
        content = copy.copy(json_content)

        if self.last_sequence_number == None:
            self.last_sequence_number = content['sequence_number']
            self.last_seq_num = content['seq_num']
            return content
        self.last_seq_num += 1
        content['seq_num'] = self.last_seq_num

        return content

    def check(self, flow: http.HTTPFlow) -> None:
        if not self.is_interesting_request(flow):
            return
        json_content_list = json.loads(flow.request.get_content())

    def is_interesting_request(self, flow: http.HTTPFlow):
        url = flow.request.pretty_url
        if not url.startswith("https://soulhunters"):
            return False
        if len(flow.request.get_content()) == 0:
            return False

        json_content = json.loads(flow.request.get_content())

        if type(json_content) is not list:
            return False
        return True


this_class = Sequence_Number()


def request(flow: http.HTTPFlow) -> None:
    this_class.check(flow)

    ctx.log.warn("-------------------------------------------")
