from mitmproxy.script import concurrent
from mitmproxy import http
from mitmproxy import ctx
import time
from threading import Lock
import asyncio
import mitmproxy


# https://stackoverflow.com/a/287944/4082686
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

    def http_connect(self, flow: mitmproxy.http.HTTPFlow):
        log_warn(flow.request.pretty_url)
        """
            An HTTP CONNECT request was received. Setting a non 2xx response on
            the flow will return the response to the client abort the
            connection. CONNECT requests and responses do not generate the usual
            HTTP handler events. CONNECT requests are only valid in regular and
            upstream proxy modes.
        """
        pass

    def requestheaders(self, flow: mitmproxy.http.HTTPFlow):
        print(flow.request.pretty_url)
        print(flow.request.pretty_host)
        # log_warn(str(flow.request.pretty_url))

        # exit(1)
        """
            HTTP request headers were successfully read. At this point, the body
            is empty.
        """
        pass

    def responseheaders(self, flow: mitmproxy.http.HTTPFlow):
        # log_warn(flow.request.pretty_url)
        exit(1)
        """
            HTTP response headers were successfully read. At this point, the body
            is empty.
        """
        pass

    def response(self, flow: http.HTTPFlow) -> None:
        log_warn("------------------ RESPONSE starts -------------------")
        lock.release()
        log_warn("------------------ RESPONSE ende -------------------")

    def clientconnect(self, layer: mitmproxy.proxy.protocol.Layer):
        print("clientconnect")
        print(layer)
        print(layer.client_conn.address)
        print(layer.server_conn.address)
        layer.kill()
        """
            A client has connected to mitmproxy. Note that a connection can
            correspond to multiple HTTP requests.
        """
        pass

    def serverconnect(self, conn: mitmproxy.connections.ServerConnection):
        print("serverconnect")
        print(conn)
        """
            Mitmproxy has connected to a server. Note that a connection can
            correspond to multiple requests.
        """


lock = Lock()
# loop = asyncio.new_event_loop()

addons = [
    SomeClass()
]
