
from mitmproxy import http
from mitm_logging import log_error
from simple_flow import SimpleFlow


class PartialFlow:

    def __init__(self):
        self.url = None
        self.request = None
        self.modified_request = {}
        self.response = None

    def set_request(self, flow: http.HTTPFlow) -> None:
        self.url = flow.request.pretty_url
        self.request = SimpleFlow.json_from_http(flow.request)

    def set_modified_request(self, flow: http.HTTPFlow) -> None:
        self.modified_request = SimpleFlow.json_from_http(flow.request)

    def set_response(self, flow: http.HTTPFlow) -> None:
        self.response = SimpleFlow.json_from_http(flow.response)

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
        self.modified_request = {}
        self.response = None
