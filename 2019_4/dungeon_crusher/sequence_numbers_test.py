#!/usr/bin/env python3

from mitmproxy import http
from mitmproxy import ctx
import json


do_it = True

find_boss_for_siege_request_flow = None
sequence_numbers = {}
current_kind = ""


last_sequence_number = None
last_seq_num = None
error = False

mob_reward_consumed_modifier = 1


def update_seq_numbers(json_content):
    return json_content
    content = json.loads(json.dumps(json_content))
    if "sequence_number" in content:
        sequence_number = content['sequence_number']
        if "seq_num" in content:
            seq_num = content['seq_num']

            max_seq_num = sequence_numbers.get(str(sequence_number))
            if max_seq_num > seq_num:
                seq_num = max_seq_num + 1
            sequence_numbers[str(sequence_number)] = seq_num
            content['seq_num'] = seq_num
    return content


def request(flow: http.HTTPFlow) -> None:
    global find_boss_for_siege_request_flow
    global sequence_numbers

    global last_sequence_number
    global last_seq_num
    global error
    global mob_reward_consumed_modifier

    url = flow.request.pretty_url
    if not url.startswith("https://soulhunters"):
        # flow.kill()
        return

    try:
        ctx.log.error("------- request --------")
        if len(flow.request.get_content()) == 0:
            ctx.log.error(
                f" Request without a body. Content length = 0. Method was {flow.request.method}")
            return
        json_content_list = json.loads(flow.request.get_content())

        if type(json_content_list) is dict:
            ctx.log.error(
                "This request has a dict as content: So it seems unintersting")
            ctx.log.error(json.dumps(json_content_list, indent=2))
            return

        ctx.log.error(
            f"there are {len(json_content_list)} array elements in this request.\n")
        for json_content in json_content_list:

            ctx.log.error(str(json_content))

            try:
                sequence_number = json_content['sequence_number']
                seq_num = json_content['seq_num']
                kind = json_content['kind']
                if last_sequence_number is not None and last_seq_num is not None:

                    expected_sequence_number = last_sequence_number
                    expected_seq_num = last_seq_num + 1
                    ctx.log.error(f"Kind : {kind}")
                    if kind in "primal_mob_consumed" and mob_reward_consumed_modifier == 1:
                        # Das wird nicht stimmen, aber erstmal besser als nix.
                        if json_content['level'] >= 122:
                            mob_reward_consumed_modifier = 2

                    if kind in "mob_reward_consumed":
                        ctx.log.error(
                            "mob_reward_consumed detected; increasing sequence_number")

                        level = json_content['level']
                        expected_sequence_number = last_sequence_number + mob_reward_consumed_modifier

                    if kind in 'state_updated':
                        ctx.log.error(
                            "state_updated detected; increasing sequence_number")
                        expected_sequence_number = last_sequence_number + 1

                    if sequence_number != expected_sequence_number:
                        ctx.log.error(
                            "[-] Error: expected sequence_number wrong.")
                        ctx.log.error(
                            f"[-]  expected : {expected_sequence_number}, but was {sequence_number}")
                        error = True

                    if seq_num != expected_seq_num:
                        ctx.log.error("[-] Error: expected seq_num wrong.")
                        ctx.log.error(
                            f"[-]  expected : {expected_seq_num}, but was {seq_num}")
                        error = True

                    if error:
                        ctx.log.warn("[-] Es ist ein Fehler aufgetreten.")
                        # exit(1)
                ctx.log.error(
                    f"setting sequence_number: {sequence_number} and seq_num: {seq_num}")
                last_sequence_number = sequence_number
                last_seq_num = seq_num

            except Exception as e:
                ctx.log.error("Error during printing seq numbers \n" + str(e))

    except Exception as e:
        ctx.log.error(f"[-] Error: {str(e)}")
        content = json.loads(flow.request.get_content())
        ctx.log.error(str(type(content)))
        ctx.log.error(f"[-] {json.dumps(content,indent=2)}")

        error = True
    if error:
        ctx.log.warn("[-] Es ist ein Fehler aufgetreten.")


def response(flow: http.HTTPFlow) -> None:
    pass
    # ctx.log.error("------------ resonse -------------")
