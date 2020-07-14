import traceback
from mitmproxy import http
from mitmproxy import ctx


def log_error(object_to_be_logged):

    trace = traceback.format_stack()
    if "mitmdump" in str(trace):
        ctx.log.error(object_to_be_logged)
    else:
        print(object_to_be_logged)
