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
        flow.kill()
        return
    try:
        json_content = json.loads(flow.request.get_content())
        if json_content[0]["kind"] == "find_boss_for_siege":
            ctx.log.error(f"Found request to find a new boss!")
            find_boss_for_siege_request_flow = flow.copy()
            ctx.log.error(json.dumps(json_content, indent=2))
            # if not find_boss_for_siege_request_flow:
            #     ctx.log.error("Error, find boss for siege request still none")
            # else:
            #     ctx.log.error("find boss for siege request set")
    except:
        pass


def response(flow: http.HTTPFlow) -> None:
    global do_it
    global find_boss_for_siege_request_flow
    if flow.response.status_code == 400:
        ctx.log.error(flow.response.get_content().decode('utf-8'))
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
                    return
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

                        # automatically decode gzipped responses.

                        request_content = find_boss_for_siege_request_flow.request.get_content().decode("utf-8")
                        request_content = json.loads(request_content)
                        ctx.log.error("This was the original content")
                        ctx.log.error(str(request_content))
                        ctx.log.error("asdf")

                        # element = request_content[0]
                        # ctx.log.error(str(type(request_content)))
                        # return
                        request_content = [content for content in request_content if content.get(
                            'kind', "") == "find_boss_for_siege"][0]
                        # not working?
                        request_content['seq_num'] = request_content['seq_num'] + 2
                        requests = []
                        requests.append(request_content)

                        find_boss_for_siege_request_flow.request.content = json.dumps(
                            requests).encode('utf-8')
                        ctx.log.error("going to send request to find boss:")
                        ctx.log.error(
                            find_boss_for_siege_request_flow.request.get_content().decode("utf-8"))
                        ctx.master.commands.call(
                            "replay.client", [find_boss_for_siege_request_flow])  # Fehler : cannot validate certificate without SNI

                else:
                    ctx.log.error(json.dumps(content, indent=2))
            except Exception as e:
                # ctx.log.error(f"[-] Error: {e}")
                # ctx.log.error(json.dumps(content, indent=2)) s
                ctx.log.error("[-] Ein Fehler ist aufgetreten: " + str(e))
                pass
            return
