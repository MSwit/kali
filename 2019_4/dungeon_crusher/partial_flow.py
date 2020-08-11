
from mitmproxy import http
from mitm_logging import log_error
from simple_flow import SimpleFlow


class PartialFlow:

    def __init__(self):
        self.url = None
        self.request = None
        self.modified_request = None
        self.response = None
        self.status_code = None

    def set_request(self, flow: SimpleFlow) -> None:
        self.url = flow.url
        self.request = flow.request

    def set_modified_request(self, flow: SimpleFlow) -> None:
        self.modified_request = flow.modified_request

    def set_response(self, flow: SimpleFlow) -> None:
        self.status_code = flow.status_code
        self.response = flow.response

    def combine(self) -> SimpleFlow:
        if not self.url or self.request == None or self.response == None:
            log_error(
                "[-] Cant combine PartialFlow to Simpleflow. Data missing.")
            # exit(1)
        simple_flow = SimpleFlow(
            self.url, self.request, self.modified_request, self.response, None)
        simple_flow.status_code = self.status_code
        return simple_flow

    def is_request_available(self) -> bool:
        return self.request != None

    def reset(self):
        self.url = None
        self.request = None
        self.modified_request = None
        self.response = None
