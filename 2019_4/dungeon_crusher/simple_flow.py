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
        try:
            url = flow.request.pretty_url
            request = SimpleFlow.json_from_http(flow.request)
            response = SimpleFlow.json_from_http(flow.response)

            simple_flow = SimpleFlow(url, request, response, flow.copy())
            pass
        except Exception as e:
            ctx.log.error(str(e))
            ctx.log.error(traceback.format_exc())

        return simple_flow

    @staticmethod
    def json_from_http(http_object):
        try:
            content = http_object.get_content()
            if len(content) == 0:
                return {}

            content = json.loads(content.decode('utf-8'))
            return content
        except Exception as e:
            ctx.log.error(str(e))
            ctx.log.error(traceback.format_exc())
