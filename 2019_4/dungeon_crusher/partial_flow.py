
from mitmproxy import http
from mitm_logging import log_error
from simple_flow import SimpleFlow


class PartialFlow:

    def __init__(self):
        self.url = None
        self.request = None
        self.modified_request = None
        self.response = None

    def set_request(self, flow: SimpleFlow) -> None:
        self.url = flow.url
        self.request = flow.request

    def set_modified_request(self, flow: SimpleFlow) -> None:
        self.modified_request = flow.modified_request

    def set_response(self, flow: SimpleFlow) -> None:
        self.response = flow.response

    def combine(self) -> SimpleFlow:
        if not self.url or self.request == None or self.response == None:
            log_error(
                "[-] Cant combine PartialFlow to Simpleflow. Data missing.")

        return SimpleFlow(self.url, self.request, self.modified_request, self.response, None)

    def is_request_available(self) -> bool:
        return self.request != None

    def reset(self):
        self.url = None
        self.request = None
        self.modified_request = None
        self.response = None
