from mitmproxy import http
from mitmproxy import ctx
import json
from mitm_logging import log_error


class SimpleFlow:

    def __init__(self, url, original_request, modified_request, response, flow):
        self.url = url
        self.request = SimpleFlow.get_json_from_unknown(
            original_request)
        self.modified_request = SimpleFlow.get_json_from_unknown(
            modified_request)
        if not self.modified_request:
            self.modified_request = json.loads(
                json.dumps(self.request))
        self.response = SimpleFlow.get_json_from_unknown(response)
        self.flow = flow

    @staticmethod
    def get_json_from_unknown(unknown_object):
        j = unknown_object
        if len(str(j)) == 0:
            return {}
        if not unknown_object:
            return {}
        try:
            if type(j) is str:
                j = json.loads(j)
                if type(j) is str:
                    j = json.dumps(j)
                    raise Exception((j))
        except:
            return {"no_json": j}
        return j

    @staticmethod
    def from_flow(flow: http.HTTPFlow) -> None:
        url = flow.request.pretty_url
        request = SimpleFlow.json_from_http(flow.request)
        response = None
        if flow.response:
            response = SimpleFlow.json_from_http(flow.response)
        simple_flow = SimpleFlow(url, request, None, response, flow.copy())
        return simple_flow

    @staticmethod
    def json_from_http(http_object):
        content = http_object.get_content()
        if len(content) == 0:
            return ""
        try:
            content = content.decode('utf-8')
            return content
        except Exception as e:
            return ""

    def to_json(self):
        return {'url': self.url, 'original_request': self.request,
                'modified_request': self.modified_request, 'response': self.response}

    @staticmethod
    def from_json(json_flow):
        request = json_flow.get('original_request', {})
        if not request:
            request = json_flow.get('request', {})
        modified_request = json_flow.get('modified_request', {})

        return SimpleFlow(json_flow['url'], request, modified_request, json_flow['response'], None)
