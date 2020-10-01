#!/usr/bin/env python3

from mitmproxy import http
import json
import copy
from simple_flow import SimpleFlow
from mitm_logging import log_error, log_warning
from sequence_number import Sequence_Number
from tooling import Tooling


def process_request(simple_flow: SimpleFlow) -> None:

    if type(simple_flow.request) is list:
        keep_requests = []
        for request in simple_flow.request:

            try:
                if request['kind'] != "pvp_expendable_consumed":
                    keep_requests.append(request)
                else:
                    log_warning("[+] removed pvp_expendable_consumed")
            except:
                pass
        simple_flow.modified_request = keep_requests

    sequence_number_modifier.try_update_request(simple_flow)


def process_response(simple_flow: SimpleFlow) -> None:

    if simple_flow.status_code >= 400:
        error = simple_flow.response.get("error", {})
        if error:
            log_error(json.dumps(simple_flow.response, indent=2))
            message = error['message']

            if "[outside] Wrong action sequence number = " in message:
                correct_seq_num = message.split(" ")[-1]
                correct_seq_num = message.split("!")[0]
                log_error(f"corret seq_num should be {correct_seq_num}")
            if "Sequence number mismatch" in message:
                log_error(f"[-] Error:  {message}")
            if "Session started on other device" in message:
                log_error(f"[-] Error:  {message}")

            if "[find_boss_for_siege] Boss siege limit reached!" in message:
                pass


sequence_number_modifier = Sequence_Number()


def request(flow: http.HTTPFlow) -> None:
    log_error("[+] Processing request.")
    simple_flow = SimpleFlow.from_flow(flow)
    if not "soulhunters.beyondmars" in simple_flow.url:
        flow.kill()
        return

    try:
        log_error("[+] Processing request.")
        process_request(simple_flow)
        flow.request.content = json.dumps(
            simple_flow.modified_request).encode('utf-8')

    except Exception as e:
        Tooling.log_stacktrace(e)


def response(flow: http.HTTPFlow) -> None:

    simple_flow = SimpleFlow.from_flow(flow)

    try:
        log_warning(
            "------------------ RESPONSE starts -------------------")
        process_response(simple_flow)

    except Exception as e:
        Tooling.log_stacktrace(e)

    log_warning(
        "------------------ RESPONSE ende -------------------")
