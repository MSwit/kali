from mitmproxy import http
from mitmproxy import ctx
import json
import traceback


class SimpleFlow:

    def __init__(self, url, request, response, flow):
        self.url = url
        self.request = request
        self.response = response
        self.flow = flow

    @staticmethod
    def from_flow(flow: http.HTTPFlow) -> None:

        url = flow.request.pretty_url
        request = SimpleFlow.json_from_http(flow.request)
        response = SimpleFlow.json_from_http(flow.response)
        simple_flow = SimpleFlow(url, request, response, flow.copy())

        return simple_flow

    @staticmethod
    def json_from_http(http_object):
        content = http_object.get_content()
        if len(content) == 0:
            return {}

        try:
            content = content.decode('utf-8')
            return content
        except Exception as e:
            return {}

    def to_json(self):
        return {'url': self.url, 'request': self.request, 'response': self.response}

    @staticmethod
    def from_json(json_flow):
        return SimpleFlow(json_flow['url'], json_flow['request'], json_flow['response'], None)
