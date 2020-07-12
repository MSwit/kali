import json
from mitmproxy import http
from mitmproxy import ctx


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
