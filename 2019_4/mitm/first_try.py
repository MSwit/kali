#!/usr/bin/env python3

from mitmproxy import http
from mitmproxy import ctx
import json

do_it = True

find_boss_for_siege_request_flow = None


def request(flow: http.HTTPFlow) -> None:
    global find_boss_for_siege_request_flow
    # pretty_url takes the "Host" header of the request into account, which
    # is useful in transparent mode where we usually only have the IP otherwise.

    url = flow.request.pretty_url
    if not url.startswith("https://soulhunters"):
        flow.response = http.HTTPResponse.make(
            200,  # (optional) status code
            b"Hello World",  # (optional) content
            {"Content-Type": "text/html"}  # (optional) headers
        )
        return
    try:
        json_content = json.loads(flow.request.get_content())
        if json_content[0]["kind"] == "find_boss_for_siege":
            ctx.log.error(f"Found request to find a new boss!")
            find_boss_for_siege_request_flow = flow.copy()
            if not find_boss_for_siege_request_flow:
                ctx.log.error("Error, find boss for siege request still none")
            else:
                ctx.log.error("find boss for siege request set")
    except:
        pass

        # print(flow.request.pr
        # content = flow.request.get_content().decode("utf-8")
        # print(json.dumps(content, indent=2))

        # if flow.request.pretty_url == "http://example.com/path":
        #     flow.response = http.HTTPResponse.make(
        #         200,  # (optional) status code
        #         b"Hello World",  # (optional) content
        #         {"Content-Type": "text/html"}  # (optional) headers
        #     )


def response(flow: http.HTTPFlow) -> None:
    global do_it
    global find_boss_for_siege_request_flow

    url = flow.request.pretty_url

    if not url.startswith("https://soulhunters"):
        return

    if url == "https://soulhunters.beyondmars.io/api/session":
        # ctx.log.error(flow.request.method)
        # ctx.log.error(url)
        if flow.request.method == "PUT":

            content_list = json.loads(flow.request.get_content())
            # ctx.log.error(json.dumps(content, indent=2))
            boss_id = None
            try:
                for content in content_list:
                    if "siege_id" in content:
                        ctx.log.error(json.dumps(content, indent=2))
                        boss_id = content["siege_id"]  # der hier ist doof
                if not boss_id:
                    raise
                # ctx.log.error(boss_id)
                content = json.loads(flow.response.get_content())
                # ctx.log.error(json.dumps(content, indent=2))
                if content["boss_siege_attack_result"]["siege"]["id"] == boss_id:
                    # ctx.log.error("Found the boss which was attacked.")
                    dmg = content["boss_siege_attack_result"]["damage_dealt"]
                    ctx.log.error(f"Damge dealt : {dmg}")
                    # ctx.log.error("1 " + str(do_it))
                    # ctx.log.error("2 " + str(find_boss_for_siege_request_flow))
                    if find_boss_for_siege_request_flow and do_it == True:
                        ctx.log.error(
                            "First time i got a dmg. I would now call another finding for a new boss.")
                        do_it = False
                        # fire track event
                        request_content = find_boss_for_siege_request_flow.request.get_content().decode("utf-8")
                        ctx.log.error(str(len(request_content)))
                        # ctx.log.error(str(request_content))
                        ctx.log.error(json.dumps(request_content, indent=2))
                        ctx.log.error("asdf")

                        ctx.master.commands.call(
                            "replay.client", [find_boss_for_siege_request_flow])

                else:
                    ctx.log.error(json.dumps(content, indent=2))
            except Exception as e:
                # ctx.log.error(f"[-] Error: {e}")
                # ctx.log.error(json.dumps(content, indent=2))
                pass
            return
