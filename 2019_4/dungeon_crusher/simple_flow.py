from mitmproxy import http
from mitmproxy import ctx
import json
from mitm_logging import log_error


class SimpleFlow:

    def __init__(self, url, original_request, modified_request, response, flow):
        self.url = url
        self.original_request = original_request
        self.modified_request = modified_request
        self.response = response
        self.flow = flow

    def get_request(self):
        return SimpleFlow.get_json_from_unknown(self.original_request)

    def get_mofied_request(self):
        return SimpleFlow.get_json_from_unknown(self.modified_request)

    def get_response(self):
        return SimpleFlow.get_json_from_unknown(self.response)

    @staticmethod
    def get_json_from_unknown(unknown_object):
        j = unknown_object
        if len(str(j)) == 0:
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
        return {'url': self.url, 'original_request': self.get_request(), 'modified_request': self.get_mofied_request(), 'response': self.get_response()}

    @staticmethod
    def from_json(json_flow):
        request = json_flow.get('original_request', {})
        if not request:
            request = json_flow.get('request', {})
        modified_request = json_flow.get('modified_request', {})

        return SimpleFlow(json_flow['url'], request, modified_request, json_flow['response'], None)
