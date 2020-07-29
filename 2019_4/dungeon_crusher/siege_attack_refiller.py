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
from sequence import SequenceHandler
import datetime
from mitmproxy.script import concurrent
from mitmproxy import proxy, options
from mitmproxy.tools.dump import DumpMaster
from mitmproxy import ctx


class SiegeAttackRefiller:

    def __init__(self):
        self.attacks_left = -1

    def handle_request(self, simple_flow: SimpleFlow):
        return simple_flow

    def handle_response(self):
        pass
