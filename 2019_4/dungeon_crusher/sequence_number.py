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
        json_content_list = json.load(flow.request.get_content())


this_class = Sequence_Number()


def request(flow: http.HTTPFlow) -> None:
    this_class.check(flow)

    ctx.log.warn("-------------------------------------------")
