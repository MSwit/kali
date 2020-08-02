#!/usr/bin/env python3
from threading import Thread, Lock
import threading
from tooling import Tooling
from sequence_number import Sequence_Number
from mitmproxy import http
import json
import sys
import os
import signal
import time
from simple_flow import SimpleFlow
from partial_flow import PartialFlow
from collections import defaultdict
from mitm_logging import log_error
from mitm_logging import log_warning
from sequence import Sequence
import datetime
from mitmproxy.script import concurrent
from mitmproxy import proxy, options
from mitmproxy.tools.dump import DumpMaster
from mitmproxy import ctx

exit(1)


def request(flow: http.HTTPFlow) -> None:
    simple_flow = SimpleFlow.from_flow(flow)

    log_error(json.dumps(simple_flow.request, indent=2))
    try:
        requests = simple_flow.request
        quest_timer_skip_request = [request for request in requests if request.get(
            'kind') == 'quest_timer_skip'][0]
        quest_timer_skip_request['price'] = 10
        log_warning(json.dumps(quest_timer_skip_request))
        log_warning(json.dumps(requests))
        simple_flow.modified_request = requests
        log_warning("-----------------")
        log_error(json.dumps(simple_flow.modified_request, indent=2))
        flow.request.content = json.dumps(
            simple_flow.modified_request).encode('utf-8')

    except Exception as e:
        log_error(str(e))


def response(flow: http.HTTPFlow) -> None:
    simple_flow = SimpleFlow.from_flow(flow)
    log_error(json.dumps(simple_flow.response, indent=2))
