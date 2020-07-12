#!/usr/bin/env python3

from mitmproxy import http
from mitmproxy import ctx
import json
import copy


def update_json_list(json_content_list) -> None:
    content = json.loads(json.dumps(json_content_list))
    for i, value in enumerate(json_content_list):
        print(value)
        content[i] = update_json(value)
    return content


def update_json(json_content) -> json:
    if json_content.get('kind') != 'pvp_finished':
        return json_content

    content = json.loads(json.dumps(json_content))
    if content['result'] == 1:
        content['result'] = 0

    return content


def update_request(flow: http.HTTPFlow) -> None:

    json_content_list = json.loads(flow.request.get_content())

    updated_content_list = update_json_list(json_content_list)

    if json_content_list != updated_content_list:
        ctx.log.error(str(json_content_list))
        ctx.log.error(str(updated_content_list))

    flow.request.set_content(json.dumps(updated_content_list).encode('utf-8'))

    pass


def is_interesting_request(flow: http.HTTPFlow):

    url = flow.request.pretty_url
    if not url.startswith("https://soulhunters"):
        ctx.log.error(f"uninteresting {url}")
        return False
    if len(flow.request.get_content()) == 0:
        return False

    json_content = json.loads(flow.request.get_content())

    if type(json_content) is not list:
        return False
    return True


def request(flow: http.HTTPFlow) -> None:
    if not is_interesting_request(flow):
        return
    original_request = flow.request.get_content().decode("utf-8")
    update_request(flow)
    updated_request = flow.request.get_content().decode("utf-8")
    if "pvp_finished" in original_request:
        ctx.log.error(str(original_request))
        ctx.log.error(str(updated_request))


def response(flow: http.HTTPFlow) -> None:
    if "pvp_finished" not in str(flow.request.get_content()):
        return
    flow.kill()
