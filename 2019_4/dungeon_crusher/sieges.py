#!/usr/bin/env python3

from mitmproxy import http
from mitmproxy import ctx
import json


class Boss_find:

    @staticmethod
    def should_attack(width):
        return False


class Siege:

    def __init__(self):
        self.last_sequence_number = None
        self.last_seq_num = None
        self.error = False
        self.my_id = "e786b343-35e8-4f59-9b86-256e188783d7"

    def find_boss_for_siege(self, flow):
        json_content_list = json.loads(flow.request.get_content())
        found_boss_request = False

        for json_content in json_content_list:

            if json_content.get('kind') == 'find_boss_for_siege':
                ctx.log.error(f"[#] Info (find_boss_for_siege): {json_content}")
                json_content_response = json.loads(flow.response.get_content())
                found_boss_request = True
                try:
                    sieges = [siege for siege in json_content_response['sieges'] if siege['top_attack_id'] is None and siege['top_users']['finder'] == self.my_id]
                    ctx.log.warn("###### 1")

                    if len(sieges) > 1:
                        ctx.log.warn("###### 2")
                        ctx.log.warn(f"There is more than one possible boss to attack, that shouldnt be so!")    
                        ctx.log.warn(json.dumps(sieges, indent=2))    
                        return
                    if len(sieges) == 0:
                        ctx.log.warn("###### 3: No possible siege found.")
                        return
                    sieges = sieges[0]
                    ctx.log.warn("###### 3")
                    boss_id = sieges['id']
                    ctx.log.warn(f"There is a boss that could be attacked: id : {boss_id}")
                except Exception as e:
                    ctx.log.error(f"[-] An Error occured: {str(e)}")




        # if found_boss_request:
        #     json_content = json.loads(flow.response.get_content())
        #     ctx.log.error(json.dumps(json_content, indent=2))
        #     sieges = json_content['sieges']


    def siege_attack(self, flow):
        json_content_list = json.loads(flow.request.get_content())
        found_attack_request = False

        for json_content in json_content_list:
            ctx.log.error(f"[#] Info (siege_attack): {json_content}")


            try:
                if json_content.get('kind') == 'boss_siege_attack':
                    found_attack_request = True
                    json_content = json.loads(flow.response.get_content())
                    scores = json_content['boss_siege_attack_result']['siege']['scores']
                    my_scores = [score for score in scores if score['user_id'] == self.my_id][0]
                    ctx.log.error(f"Found Siege Attack: My Damage was: {my_scores['points']}")
            except Exception as e:
                ctx.log.error(f"[-] An Error occured: {str(e)}")

        if found_attack_request:
            # json_content = json.loads(flow.response.get_content())
            # ctx.log.error(json.dumps(json_content, indent=2))
            # exit(1)
            pass
            

    def check_response(self, flow: http.HTTPFlow):
        url = flow.request.pretty_url

        try:
            if not url.startswith("https://soulhunters"):
                return
            if len(flow.request.get_content()) == 0:
                return

            json_content = json.loads(flow.request.get_content())

            if type(json_content) is not list:
                return

            json_content_list = json_content
            self.find_boss_for_siege(flow)  # TODO get new Boss_id?
            # self.siege_attack(flow)

        except Exception as e:
            ctx.log.warn("#########")
            ctx.log.error(json.dumps(json.loads(
                flow.response.get_content()), indent=2))
            ctx.log.error(f"[-] An Error occured: {str(e)}")

            import sys
            import os
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ctx.log.error(f"{exc_type}, {fname}, {exc_tb.tb_lineno}")
            
            # exit(1)


this_class = Siege()


# def request(flow: http.HTTPFlow) -> None:
#     this_class.check_response(flow)


def response(flow: http.HTTPFlow) -> None:
    this_class.check_response(flow)
