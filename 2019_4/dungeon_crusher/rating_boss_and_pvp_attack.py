#!/usr/bin/env python3

from mitmproxy import http
import json
import copy
from simple_flow import SimpleFlow
from mitm_logging import log_error, log_warning


def update_json_list(json_content_list) -> None:
    content = json.loads(json.dumps(json_content_list))
    for i, value in enumerate(json_content_list):
        content[i] = update_json(value)
    return content


def update_json(json_content) -> json:
    if json_content.get('kind') != 'rating_boss_finished' and json_content.get('kind') != 'pvp_finished':
        return json_content

    content = json.loads(json.dumps(json_content))
    if content['result'] == 1:
        log_warning("[+] found rating boss or pvp loss. Will update to win")
        log_warning(str(content))
        content['result'] = 0

    return content


def update_request(simple_flow: SimpleFlow) -> None:
    # // hier

    json_content_list = simple_flow.request
    updated_content_list = update_json_list(json_content_list)
    if json_content_list != updated_content_list:
        log_error(str(json_content_list))
        log_error(str(updated_content_list))

    simple_flow.modified_request = updated_content_list


def is_interesting_request(simple_flow: SimpleFlow):
    return "rating_boss_finished" in str(simple_flow.request) or 'pvp_finished' in str(simple_flow.request)


def request(flow: http.HTTPFlow) -> None:
    simple_flow = SimpleFlow.from_flow(flow)
    if not is_interesting_request(simple_flow):
        log_error("uninsteresting")
        log_error(json.dumps(simple_flow.request, indent=2))

        return
    update_request(simple_flow)

    flow.request.set_content(json.dumps(
        simple_flow.modified_request).encode('utf-8'))


def response(flow: http.HTTPFlow) -> None:
    try:
        response = json.loads(flow.response.get_content().decode('utf-8'))
        error = response['error']
        code = error['code']
        if code == 400:
            log_error("[-] Error: Bad status code.")
            log_error(json.dumps(response, indent=2))
    except:
        pass

    simple_flow = SimpleFlow.from_flow(flow)
    if "rating_boss_finished" in str(simple_flow.request):
        flow.kill()
        exit(1)


# Error:
# 192.168.178.23:46251: clientconnect
#   [+] found rating boss or pvp loss. Will update to win
#   {'boss_id': 700, 'result': 1, 'signature': 610870973, 'kind': 'rating_boss_finished', 'sequence_number': 10, 'seq_num': 9}
#   [{'boss_id': 700, 'result': 1, 'signature': 610870973, 'kind': 'rating_boss_finished', 'sequence_number': 10, 'seq_num': 9}, {'quest_id': 107, 'progress': 64, 'kind': 'quest_progress', 'sequence_number': 10, 'seq_num': 10}]
#   [{'boss_id': 700, 'result': 0, 'signature': 610870973, 'kind': 'rating_boss_finished', 'sequence_number': 10, 'seq_num': 9}, {'quest_id': 107, 'progress': 64, 'kind': 'quest_progress', 'sequence_number': 10, 'seq_num': 10}]
#   [-] Error: Bad status code.
#   {
#   "error": {
#     "message": "[outside] Wrong action sequence number = 9 <> 11!",
#     "action": {
#       "boss_id": 700,
#       "result": 0,
#       "signature": 610870973,
#       "kind": "rating_boss_finished",
#       "sequence_number": 10,
#       "seq_num": 9
#     },
#     "code": 400,
#     "backend_time": "2020-09-04T18:14:42.273Z"
#   }
# }


# Arena kiste
#   [
#   {
#     "hero_id": 2104,
#     "new_rarity": 160,
#     "kind": "hero_hidden_rarity_upgraded",
#     "sequence_number": 9,
#     "seq_num": 50
#   }
# ]

# [
#   {
#     "level": 3353,
#     "consumed_loot": [
#       {
#         "config_id": 105090,
#         "amount": 1
#       }
#     ],
#     "kind": "mob_reward_consumed",
#     "sequence_number": 15,
#     "seq_num": 20
#   },
#   {
#     "level": 3354,
#     "consumed_loot": [
#       {
#         "config_id": 100520,
#         "amount": 1
#       }
#     ],
#     "kind": "mob_reward_consumed",
#     "sequence_number": 17,
#     "seq_num": 21
#   },
#   {
#     "level": 3355,
#     "consumed_loot": [
#       {
#         "config_id": 21,
#         "amount": 550648
#       }
#     ],
