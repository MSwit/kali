from mitmproxy.script import concurrent
from mitmproxy import http
from mitmproxy import ctx
import time
from threading import Lock
import asyncio


# https: // stackoverflow.com/a/287944/4082686
def log_warn(text):
    print("\033[94m" + text + "\033[0m")


class SomeClass:
    @concurrent  # Remove this and see what happens
    def request(self, flow):
        # asyncio.set_event_loop(loop)
        log_warn("------------------ request starts -------------------")
        lock.acquire()
        log_warn("handle request: %s%s" %
                 (flow.request.host, flow.request.path))
        # time.sleep(5)
        print("start  request: %s%s" % (flow.request.host, flow.request.path))
        log_warn("------------------ request ende -------------------")

    def response(self, flow: http.HTTPFlow) -> None:
        log_warn("------------------ RESPONSE starts -------------------")
        lock.release()
        log_warn("------------------ RESPONSE ende -------------------")


lock = Lock()
# loop = asyncio.new_event_loop()

addons = [
    SomeClass()
]
