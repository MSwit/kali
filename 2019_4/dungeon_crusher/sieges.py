from tooling import Tooling
from sequence_number import Sequence_Number
from mitmproxy import http
from mitmproxy import ctx
import json
import os


class Sieges:

    def __init__(self, sequence_number_modifier):
        self.sequence_number_modifier = sequence_number_modifier
        self.my_id = "e786b343-35e8-4f59-9b86-256e188783d7"
        self.attacked_bosses = []

    def is_interesting_response(self, flow: http.HTTPFlow):
        url = flow.request.pretty_url
        if not url.startswith("https://soulhunters"):
            return False

        if "boss_config_id" not in str(flow.response.get_content()):
            return False
        return True

    def get_good_boss_id(self, siege):

        boss_id = siege['id']

        if boss_id in self.attacked_bosses:
            return  # TODO, we will attack big bosses multiple times later on.

        if siege['top_users']['finder'] == self.my_id:
            if siege['top_attack_id'] == None:
                if siege['current_hp'] < 3000000:

                    return siege['id']

    def find_boss_id_to_attack(self, json_content):
        try:
            return self.get_good_boss_id(json_content)
        except:
            pass

        for siege in json_content['sieges']:
            ctx.log.error(str(siege))
            boss_id = self.get_good_boss_id(siege)

            if boss_id:
                return boss_id
        return None

    def attack(self, boss_id, flow: http.HTTPFlow):
        with open(f"{os.path.dirname(os.path.abspath(__file__))}/boss_siege_attack.json", 'r') as f:
            json_content = json.load(f)
        json_content['siege_id'] = boss_id
        fake_request = flow.copy()
        request_content = [json_content]
        fake_request.request.content = json.dumps(  # will update seq_num etc. in request(..)
            request_content).encode('utf-8')

        self.attacked_bosses.append(boss_id)

        ctx.log.warn("[#] I will send boss siege attack.")
        ctx.master.commands.call("replay.client", [fake_request])

    def check_response(self, flow: http.HTTPFlow):
        if len(flow.response.get_content()) == 0:
            return
        content = flow.response.get_content().decode('utf-8')
        if "error" in content:
            ctx.log.error(content)

        ctx.log.error(str(flow.response.get_content().decode('utf-8')))
        if not self.is_interesting_response(flow):
            return
        try:
            if "boss_config_id" not in str(flow.response.get_content()):
                return
        except:
            pass
        if 'boss_siege_attack_result' in flow.response.get_content().decode('utf-8'):
            return

        json_content = json.loads(flow.response.get_content().decode('utf-8'))

        boss_id = self.find_boss_id_to_attack(json_content)
        if not boss_id:
            ctx.log.warn("[+] no Boss found to attack.")
        else:
            self.attack(boss_id, flow)


sequence_number_modifier = Sequence_Number()
this_class = Sieges(sequence_number_modifier)


def request(flow: http.HTTPFlow) -> None:
    ctx.log.warn("----------------------------------------")
    sequence_number_modifier.print_requests(flow)
    sequence_number_modifier.try_update_request(flow)
    ctx.log.warn("------------after update------------")
    sequence_number_modifier.print_requests(flow)


def response(flow: http.HTTPFlow) -> None:

    this_class.check_response(flow)
    # return
    # if "find_boss_for" in str(flow.request.get_content()):
    #     ctx.log.error(flow.response.get_content().decode('utf-8'))
    if flow.response.status_code == 400:
        ctx.log.error(f"[-] An Error occured: Bad Statuscode:")
        ctx.log.error(json.dumps(json.loads(flow.request.get_content()), indent=2))
        ctx.log.error(json.dumps(json.loads(flow.response.get_content()), indent=2))

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
