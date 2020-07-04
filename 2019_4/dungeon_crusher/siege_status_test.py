#!/usr/bin/env python3

from mitmproxy import http
from mitmproxy import ctx
import json


def request(flow: http.HTTPFlow) -> None:
    pass


def response(flow: http.HTTPFlow) -> None:

    try:

        content = flow.response.get_content().decode('utf-8')
        json_content = json.loads(content)
        try:
            sieges = json_content['sieges']  # will throw
        except:
            return

        ctx.log.info(f"{json.dumps(json_content, indent=2)}")
        ctx.log.warn(f"{len(sieges)} sieges are currently available")
        if len(json_content['sieges']) == 4:
            # TODO remove a not interesting one. TODO or even more.
            ctx.log.warn(f"Detect 4 sieges. Lets remove the first.")
            ctx.log.error("going to kick the 1th siege")
            json_content['sieges'] = json_content['sieges'][1:]
            flow.response.content = json.dumps(json_content).encode('utf-8')

    except Exception as e:
        ctx.log.error(f"[-] An Error occured: {str(e)}")
        import sys
        import os
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        ctx.log.error(f"{exc_type}, {fname}, {exc_tb.tb_lineno}")
        # exit(1)
        pass
