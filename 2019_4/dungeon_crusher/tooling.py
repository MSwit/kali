import json
from mitmproxy import http
from mitmproxy import ctx
from mitm_logging import log_error
import traceback
import sys
import os
from simple_flow import SimpleFlow


class Tooling:

    @staticmethod
    def copy(json_content):
        return json.loads(json.dumps(json_content))

    @staticmethod
    def remove_non_trivial_items_list(orginal_json_list):
        return [Tooling.remove_non_trivial_items(orginal_json) for orginal_json in orginal_json_list]

    @staticmethod
    def remove_non_trivial_items(orginal_json):
        content = Tooling.copy(orginal_json)
        for i, key in enumerate(orginal_json):
            _type = type(orginal_json[key])
            if _type is list:
                content[key] = []
            elif _type is dict:
                content[key] = {}
            elif key == "state":
                content[key] = {}
        return content

    @staticmethod
    def is_interesting_request(simple_flow: SimpleFlow) -> bool:

        if not simple_flow.url.startswith("https://soulhunters"):
            return False
        if not simple_flow.get_modified_request():
            return False

        json_content = simple_flow.get_modified_request()

        if type(json_content) is not list:
            return False
        return True

    @staticmethod
    def log_stacktrace(exception):

        log_error(f"[-] an error Occured: {exception}")
        trace = traceback.format_stack()
        log_error(str(trace))
        log_error("---")
        # log_error(str(exception.__traceback__))
        # log_error("---")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        for entry in os.path.split(exc_tb.tb_frame.f_code.co_filename):
            # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            log_error(str(exc_type))
            # log_error("---")
            # log_error(str(fname) + " asdfasf")
            # log_error("---")
            log_error(str(exc_tb.tb_lineno))
            # log_error("------")
            # log_error(type(entry))
            log_error("entry: " + str(entry))
