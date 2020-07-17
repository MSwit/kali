from threading import Thread, Lock
from tooling import Tooling
from sequence_number import Sequence_Number
from mitmproxy import http
from mitmproxy import ctx
import json
import os
import time
from simple_flow import SimpleFlow
from collections import defaultdict
# import mitm_logging


# class User:
#     def __self__(self, id):
#         self.id = id


# class OnePlus(User):

#     def __self__(self, id):
#         super(id)

#     def get_good_boss_id(self, siege)


class Sieges:

    def __init__(self, sequence_number_modifier):
        self.sequence_number_modifier = sequence_number_modifier
        # self.my_id = "e786b343-35e8-4f59-9b86-256e188783d7" # nexus
        # self.user = "nexus"

        self.my_id = "a10e9130-7530-4839-9a11-825b99a10895"  # oneplus3t
        self.user = "oneplus"
        self.attacked_bosses = defaultdict(int)
        self.api_session_flow = None

    # def is_interesting_response(self, simple_flow):
    #     url = simple_flow.url
    #     if not url.startswith("https://soulhunters"):
    #         return False

    #     if "boss_config_id" not in str(simple_flow.response):
    #         return False
    #     return True

    # def get_good_boss_id(self, siege):

    #     if self.my_id == "e786b343-35e8-4f59-9b86-256e188783d7":
    #         return self.get_good_boss_id_nexus(siege)
    #     elif self.my_id == "a10e9130-7530-4839-9a11-825b99a10895":
    #         return self.get_good_boss_id_oneplus3t(siege)

    # def get_good_boss_id_nexus(self, siege):

    #     boss_id = siege['id']

    #     if boss_id in self.attacked_bosses:
    #         return  # TODO, we will attack big bosses multiple times later on.

    #     if siege['top_users']['finder'] == self.my_id:
    #         if siege['top_attack_id'] == None:
    #             if siege['current_hp'] < 3000000:

    #                 return siege['id']

    # def get_good_boss_id_oneplus3t(self, siege):
    #     ctx.log.warn(str(siege))
    #     boss_id = siege['id']
    #     try:
    #         if siege['top_users']['finder'] == self.my_id:
    #             if siege['top_attack_id'] == None:
    #                 return siege['id']
    #         if siege['current_hp'] > 200000000:  # TODO
    #             my_scores = [score for score in siege['scores'] if score['user_id'] == self.my_id]
    #             if my_scores:
    #                 points = my_scores['points']
    #                 if points > 0:
    #                     ctx.log.warn(f"Already did dmg to boss: {points}")
    #                 else:
    #                     return boss_id
    #     except Exception as e:
    #         ctx.log.error(str(e))

    #     return None

    #     if boss_id in self.attacked_bosses:
    #         return  # TODO, we will attack big bosses multiple times later on.

    #     if siege['top_users']['finder'] == self.my_id:
    #         if siege['top_attack_id'] == None:
    #             return siege['id']

    # def find_boss_id_to_attack(self, simple_flow):
    #     if "find_boss_..." in simple_flow.request:
    #         pass

    #     return None
        # try:
        #     return self.get_good_boss_id(json_content)
        # except:
        #     pass

        # for siege in json_content['sieges']:
        #     ctx.log.error(str(siege))
        #     boss_id = self.get_good_boss_id(siege)

        #     if boss_id:
        #         return boss_id
        # return None

    def attack(self, boss_id, flow: http.HTTPFlow):
        try:
            with open(f"{os.path.dirname(os.path.abspath(__file__))}/boss_siege_attack.json", 'r') as f:
                json_content = json.load(f)
            json_content['siege_id'] = boss_id
            fake_request = flow.copy()
            request_content = [json_content]
            fake_request.request.content = json.dumps(  # will update seq_num etc. in request(..)
                request_content).encode('utf-8')

            self.attacked_bosses[boss_id] += 1
            ctx.log.warn("[#] I will send boss siege attack.")

            time.sleep(1.5)

            ctx.master.commands.call("replay.client", [fake_request])
        except Exception as e:
            import traceback

            ctx.log.error(f"[-] an error Occured: {e}")
            trace = traceback.format_stack()
            ctx.log.error(str(trace))
            ctx.log.error(str(e.__traceback__))
            import sys
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ctx.log.error(str(exc_type))
            ctx.log.error(str(fname))
            ctx.log.error(str(exc_tb.tb_lineno))

    def find_boss_to_attack(self, simple_flow):

        request = simple_flow.request
        response = simple_flow.response
        # ctx.log.warn("[+] will search for boss to attack")
        # ctx.log.error(json.dumps(request, indent=2))
        # ctx.log.error(str(request))
        # if type(request) is list and [r for r in request if r.get('kind') == "find_boss_for_siege"]:
        #     ctx.log.error("find_boss_for_siege is in request")
        # else:
        #     ctx.log.error(json.dumps(request))
        try:

            if type(request) is list and [r for r in request if r.get('kind') == "find_boss_for_siege"]:
                # ctx.log.error("find_boss_for_siege is in request")
                for siege in response['sieges']:
                    boss_id = siege['id']
                    if siege['top_users']['finder'] == self.my_id:
                        if siege['top_attack_id'] == None:
                            # self.attacked_bosses[boss_id] += 1
                            ctx.log.warn("[+] Found normal boss to attack.")
                            return boss_id

                    if siege['current_hp'] > 110000000:
                        if boss_id not in self.attacked_bosses:
                            # self.attacked_bosses[boss_id] += 1
                            ctx.log.warn("[+] Found top boss to attack.")
                            return boss_id

            if "boss_siege_attack" in str(request):
                siege = response['boss_siege_attack_result']['siege']
                boss_id = None
                # we wont reattack small bosses.

                my_score_entry = [
                    score for score in siege['scores'] if score['user_id'] == self.my_id][0]
                points = my_score_entry['points']
                if points == 0:
                    boss_id = siege['id']
                    ctx.log.error("[-] NO DMG DONE !")
                    if siege['current_hp'] > 110000000:
                        if self.attacked_bosses[boss_id] < 2:
                            # self.attacked_bosses[boss_id] += 1
                            ctx.log.warn("[+] Found top boss to reattack.")
                            boss_id = siege['id']
                else:
                    ctx.log.error(f"DID DMG: {points}")
                self.try_refill()

            ctx.log.warn("[+] no Boss found to attack.")
        except Exception as e:
            ctx.log.warn(f"[-] Error: {str(e)}")
            import sys
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ctx.log.error(str(exc_type))
            ctx.log.error(str(fname))
            ctx.log.error(str(exc_tb.tb_lineno))
            ctx.log.error(json.dumps(response))
            ctx.log.warn(f"[-] Error: {str(e)}")

    def try_refill(self):
        if not self.api_session_flow:
            ctx.log.error("[-] could not send refill request. No 'api/session' flow available")
            return
        attack_refill_json = {"kind": "boss_siege_refill_attack", "sequence_number": 11, "seq_num": 21}
        fake_request = self.api_session_flow.copy()
        attack_refill_json = [attack_refill_json, attack_refill_json]
        fake_request.request.content = json.dumps(  # will update seq_num etc. in request(..)
            attack_refill_json).encode('utf-8')

        time.sleep(2)

        ctx.log.warn("[#] I will send refill request")
        time.sleep(1.5)
        # ctx.log.error(fake_request.request.get_content().decode('utf-8'))
        ctx.master.commands.call("replay.client", [fake_request])

    def check_response_simple(self, simple_flow):
        boss_id = self.find_boss_to_attack(simple_flow)
        if boss_id:
            ctx.log.error(boss_id)
            self.attack(boss_id, simple_flow.flow)

    def check_response(self, flow: http.HTTPFlow):
        try:
            simple_flow = SimpleFlow.from_flow(flow)
            self.check_response_simple(simple_flow)
        except Exception as e:
            import traceback

            ctx.log.error(f"[-] an error Occured: {e}")
            trace = traceback.format_stack()
            ctx.log.error(str(trace))
            ctx.log.error(str(e.__traceback__))
            import sys
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ctx.log.error(str(exc_type))
            ctx.log.error(str(fname))
            ctx.log.error(str(exc_tb.tb_lineno))


sequence_number_modifier = Sequence_Number()
this_class = Sieges(sequence_number_modifier)


mutex = Lock()


def request(flow: http.HTTPFlow) -> None:
    ctx.log.warn("------------------ request starts -------------------")
    try:
        if "\"sequence_number\"" in flow.request.get_content().decode('utf-8'):
            ctx.log.error("[+] will aquire lock for:")
            ctx.log.error(flow.request.get_content().decode('utf-8'))

            mutex.acquire()
            # ctx.log.error("[+] lock aquired:")
    except:
        pass

    if flow.request.pretty_url == "https://soulhunters.beyondmars.io/api/session":
        this_class.api_session_flow = flow
        # ctx.log.error(f"Session flow set!")
    else:
        # ctx.log.error(f"Wrong url: {flow.request.pretty_url}")
        pass

    # ctx.log.warn("----------------------------------------")
    sequence_number_modifier.try_update_request(flow)
    sequence_number_modifier.print_requests(flow)
    # try:
    #     if "boss_siege_refill_attack" in flow.request.get_content().decode('utf-8'):
    #         ctx.log.error("boss_siege_refill_attack request:")
    #         ctx.log.error(flow.request.get_content().decode('utf-8'))

    # except:
    #     pass
    # ctx.log.warn("------------after update------------")
    # sequence_number_modifier.print_requests(flow)

    # mutex.release()
    ctx.log.error("------------------ request ends -------------------")


def response(flow: http.HTTPFlow) -> None:
    ctx.log.warn("------------------ RESPONSE starts -------------------")
    try:
        if "boss_siege_refill_attack" in flow.request.get_content().decode('utf-8'):
            # Die antwort kommt asynchron? bzw. immer dnn, wenn ich keinen dmg gemacht habe, kommt keine antwort?
            # ctx.log.error("boss_siege_refill_attack response:")
            # ctx.log.error(flow.response.get_content().decode('utf-8'))
            pass

    except:
        pass

    if flow.response.status_code == 400:
        ctx.log.error("[-] Bad statuscode")
        ctx.log.error(str(flow.request.get_content()))
        ctx.log.error(str(flow.response.get_content()))

    this_class.check_response(flow)

    # # return
    # # if "find_boss_for" in str(flow.request.get_content()):
    # #     ctx.log.error(flow.response.get_content().decode('utf-8'))
    # if flow.response.status_code == 400:
    #     ctx.log.error(f"[-] An Error occured: Bad Statuscode:")
    #     ctx.log.error(json.dumps(json.loads(flow.request.get_content()), indent=2))
    #     ctx.log.error(json.dumps(json.loads(flow.response.get_content()), indent=2))
    try:
        if "\"sequence_number\"" in flow.request.get_content().decode('utf-8'):
            ctx.log.error("[+] Lock released!")
            mutex.release()
    except:
        pass
    ctx.log.error("------------------ RESPONSE ends -------------------")


# aktueller stand...
# mofified_sieges_2_onePlus_2_should_found_boss_but_didnt.bak

# oneplus3t findet 20-30 mio boss nicht.


# request: "find_boss_for_siege"
# response: {\"sieges\":[{\"id\":\"95eaef8a-2761-4950-aad2-44421601ece4\",\"current_hp\":17680159,\"expires_at....
# => attack big boss.


# request: https://soulhunters.beyondmars.io/api/boss_sieges/sieges/505600d3-8ce4-4488-bc6c-0c12166db877
# response: "{\"id\":\"505600d3-8ce4-4488-bc6c-0c12166db877\",\"current_hp\":1971309952,\"expires_at\":\"2020-07-14T16:18:07.288Z\", ... scores: [....]

# "[{\"kind\": \"boss_siege_refill_attack\", \"sequence_number\": 2, \"seq_num\": 3}, {\"siege_id\": \"505600d3-8ce4-4488-bc6c-0c12166db877\", \"power_attack\": false, \"autorestore_is_on\": false, \"kind\": \"boss_siege_attack\"
# {\"boss_siege_refill_result\":{\"attacks_left\":0,\"refill_at\":\"2020-07-14T16:45:44.971Z\",\"updated_at\":\"..Z\"},\"boss_siege_attack_result\":{\"status\":200,\"siege\":{\"expires_at\":\"...\",\"
#  current_hp\":1655268692,\"id\":\"505600d3-8ce4-4488-bc6c-0c12166db877\",\"created_at\":\"..\",\"updated_at\":\"..\",\"private\":false,\"total_users\":34,\"top_users\":{\"mvp\":\"3bfeb99d-566e-4491-ac39-21b5f3931acd\",\"finder\":\"e66e5ce2-f994-4bac-b4a1-71c87fc0835c\",\"last_hit\":\"f08f6b49-e1b8-4142-90c4-81a9b7741120\"},\"top_attack_id\":\"ab72aaa2-a1ef-442f-94c7-d9259f2e3b0b\",\"boss_config_id\":216125,
# \"scores\": [....]
