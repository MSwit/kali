#!/usr/bin/env python3

from mitmproxy import http
from mitmproxy import ctx
import json
import copy


class Sequence_Number:

    def __init__(self):
        self.sequence_number = None
        self.seq_num = None

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
            return content

        kind = content['kind']
        if kind == 'state_updated':
            self.sequence_number += 1

        self.seq_num += 1
        content['seq_num'] = self.seq_num
        content['sequence_number'] = self.sequence_number

        return content

    def check(self, flow: http.HTTPFlow) -> None:
        if not self.is_interesting_request(flow):
            return
        json_content_list = json.loads(flow.request.get_content())

        updated_content_list = self.generate_updated_json_list(json_content_list)
        if json_content_list != updated_content_list:
            ctx.log.error("[-] request was updated. but it shouldn't.")
            ctx.log.error("[-] Original request content: ")
            ctx.log.error(
                f"[-] {json.dumps(Sequence_Number.remove_non_trivial_items_list(json_content_list), indent=2)}")

            ctx.log.error("[-] Updated request content: ")
            ctx.log.error(
                f"[-]{json.dumps(Sequence_Number.remove_non_trivial_items_list(updated_content_list), indent=2)}")

    @staticmethod
    def remove_non_trivial_items_list(orginal_json_list):
        return [Sequence_Number.remove_non_trivial_items(orginal_json) for orginal_json in orginal_json_list]

    @staticmethod
    def remove_non_trivial_items(orginal_json):
        content = copy.copy(orginal_json)
        for i, key in enumerate(orginal_json):
            _type = type(orginal_json[key])
            if _type is list:
                content[key] = []
            elif _type is dict:
                content[key] = {}
            elif key == "state":
                content[key] = {}
        return content

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
