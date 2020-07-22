from mitmproxy.script import concurrent
from mitmproxy import http
from mitmproxy import ctx
import time
from threading import Lock


class SomeClass:
    @concurrent  # Remove this and see what happens
    def request(self, flow):
        lock.acquire()
        print("handle request: %s%s" % (flow.request.host, flow.request.path))
        time.sleep(5)
        print("start  request: %s%s" % (flow.request.host, flow.request.path))

    # @concurrent
    def response(self, flow: http.HTTPFlow) -> None:
        ctx.log.warn("------------------ RESPONSE starts -------------------")
        ctx.log.warn("------------------ RESPONSE ende -------------------")
        lock.release()


lock = Lock()

addons = [
    SomeClass()
]
