from mitmproxy import http
from mitmproxy import ctx

from mitm_logging import log_error
from mitm_logging import log_warning


def process_request(flow: http.HTTPFlow) -> None:
    url = flow.request.pretty_url
    log_error(f"Url : {url}")
    if "maik" in url:
        fake_request = flow.copy()
        fake_request.request.url = "http://localhost:3001/fake_request"
        ctx.master.commands.call("replay.client", [fake_request])


def process_response(flow: http.HTTPFlow) -> None:
    log_error(f"Url : {flow.request.pretty_url}")


def request(flow: http.HTTPFlow) -> None:

    ctx.log.warn("------------------ REQUEST starts -------------------")
    process_request(flow)
    ctx.log.warn("------------------ REQUEST ends -------------------")


def response(flow: http.HTTPFlow) -> None:
    ctx.log.warn("------------------ RESPONSE starts -------------------")
    process_response(flow)
    ctx.log.warn("------------------ RESPONSE ende -------------------")
