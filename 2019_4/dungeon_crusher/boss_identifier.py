from simple_flow import SimpleFlow
from client_replay import ClientReplay
from mitm_logging import log_error
from mitm_logging import log_warning
from sequence import SequenceHandler
from sequence_number import Sequence_Number
from client_replay import ClientReplay
from mitmproxy import http
import json


class Boss():
    def __init__(self):
        self.id = None
        self.curren_hp = None
        self.max_known_hp = None
        self.my_attacks = []
        self.other_dmg = None
        self.am_i_the_finder = False


class KnownBosses():

    def __init__(self):

        self.bosses = []


class BossDetailAnalyzer:
    def __init__(self,  known_bosses):
        self.known_bosses = known_bosses

    def handle_refresh_or_find(self,  simple_flow: SimpleFlow):

        pass

    def handle_handle_attack(self,  simple_flow: SimpleFlow):
        pass

    def handle_detail_view(self,  simple_flow: SimpleFlow):
        #          https://gw.soulhunters.beyondmars.io/api/boss_sieges/sieges/0d0b129b-974f-43c2-82ee-3a9262039299
        #   {
        #   "id": "0d0b129b-974f-43c2-82ee-3a9262039299",
        #   "current_hp": 0,
        #   "expires_at": "2020-10-27T19:42:07.127Z",
        #   "created_at": "2020-10-27T19:12:07.128Z",
        #   "updated_at": "2020-10-27T19:12:32.306Z",
        #   "private": false,
        #   "total_users": 7,
        #   "top_users": {
        #     "mvp": "7daca59d-2573-4ab2-b16f-a664cd0e1b47",
        #     "finder": "c9f3eb73-0f69-4468-9d51-8944a689492c",
        #     "last_hit": "7daca59d-2573-4ab2-b16f-a664cd0e1b47"
        #   },
        #   "top_attack_id": "e38f5f95-fc40-45c4-b8d3-d67c87a11ac9",
        #   "boss_config_id": 16436,
        #   "scores": [
        pass

    def handle_request(self, simple_flow: SimpleFlow) -> None:
        pass

    def handle_response(self, simple_flow: SimpleFlow) -> None:
        log_error(simple_flow.url)
        if "https://gw.soulhunters.beyondmars.io/api/boss_sieges/sieges/" in simple_flow.url:
            log_error(json.dumps(simple_flow.response, indent=2))
        try:

            sieges = simple_flow.response['sieges']

            for siege in sieges:

                boss_id = siege['id']

                if not boss_id in self.known_bosses.bosses:
                    log_error(f"[+] going to add boss with id {boss_id}.")
                    self.known_bosses.bosses.append(boss_id)
                log_error(
                    f"[+] update currentHP for boss_id {boss_id}: {siege['current_hp']}")
                # if (siege['top_users']['finder'] == self.my_id or not self.has_to_be_finder) and siege['current_hp'] == self.boss_hp:

        except Exception as e:
            # log_error(f"[-] could not parse boss details.")
            # print(str(e))
            pass


class BossDetailFinder():

    def __init__(self,  known_bosses, replayer: ClientReplay):
        self.known_bosses = known_bosses
        self.replayer = replayer
        self.api_session_flow = None
        self.doStuff = True

    def try_set_flow(self, simple_flow: SimpleFlow) -> None:
        # if "https://gw.soulhunters.beyondmars.io/api/boss_sieges/sieges/" in simple_flow.url:
        if "find_boss_for_siege" in str(simple_flow.request):
            self.api_session_flow = simple_flow.flow.copy()
            self.api_session_flow.request.method = "GET"
            log_error("[+] Successfully set flow for boss identification.")

    def handle_request(self, simple_flow: SimpleFlow) -> None:
        self.try_set_flow(simple_flow)

    def handle_response(self, simple_flow: SimpleFlow) -> None:
        self.try_set_flow(simple_flow)

        log_error(" - 1")
        if self.known_bosses.bosses and self.doStuff:
            log_error(" - 2")
            if not self.api_session_flow:
                log_error(" - 3")
                log_error(f"[-] could not identify boss. Flow is missing")
                return
            if not self.replayer.isIdle():
                log_error(" - 4")
                log_error(f"[-] could not identify boss.replayer issnt idle")
                return

            # self.doStuff = False  # single shot.

            log_error(" - 5")
            fake_request = self.api_session_flow.copy()
            expected_full_url = f"https://gw.soulhunters.beyondmars.io/api/boss_sieges/sieges/{self.known_bosses.bosses[0]}"
            fake_request.request.host = 'gw.soulhunters.beyondmars.io'
            fake_request.request.path = f'/api/boss_sieges/sieges/{self.known_bosses.bosses[0]}'
            if expected_full_url != fake_request.request.pretty_url:
                log_error("[-] wrong url")
                log_error(f"[-] should be {expected_full_url}")
                log_error(f"[-] but was { fake_request.request.pretty_url}")
                exit(1)

            # request_content = "{}"
            # fake_request.request.content = request_content.encode('utf-8')
            # fake_request.request.method = "PUT"
            self.replayer.replay(fake_request)

        # try:
        #     sieges = simple_flow.response['sieges']
        #     for siege in sieges:
        #         if siege['id'] not in self.knownBosses:  # /... toto
        #             if siege['top_attack_id'] == None:
        #                 # https://gw.soulhunters.beyondmars.io/api/boss_sieges/sieges/c520146c-b889-4226-aeee-6d530ff87ab9
        #                 self.replayer.replay(get_boss_details)  # TODO
        # except:
        #     pass


replayer = ClientReplay()
sequence_number_modifier = Sequence_Number()

known_bosses = KnownBosses()
boss_detail_analyzer = BossDetailAnalyzer(known_bosses)
boss_detail_finder = BossDetailFinder(known_bosses, replayer)


def request(flow: http.HTTPFlow) -> None:
    simple_flow = SimpleFlow.from_flow(flow)
    log_error(f"[+] URL: {simple_flow.url}")
    # log_error(f"[+] request-content: {simple_flow.request}")

    log_warning(
        "------------------ REQUEST starts -------------------")
    boss_detail_analyzer.handle_request(simple_flow)
    sequence_number_modifier.try_update_request(simple_flow)
    replayer.handle_request(simple_flow)
    log_warning("------------------ REQUEST ends -------------------")


def response(flow: http.HTTPFlow) -> None:
    simple_flow = SimpleFlow.from_flow(flow)

    log_warning(
        "------------------ RESPONSE starts -------------------")

    if simple_flow.status_code >= 400:
        error = simple_flow.response.get("error", {})
        if error:
            log_error(json.dumps(simple_flow.response, indent=2))
            message = error['message']

            if "[outside] Wrong action sequence number = " in message:
                correct_seq_num = message.split(" ")[-1]
                correct_seq_num = message.split("!")[0]
                log_error(f"corret seq_num should be {correct_seq_num}")
            if "Sequence number mismatch" in message:
                log_error(f"[-] Error:  {message}")
            if "Session started on other device" in message:
                log_error(f"[-] Error:  {message}")

            if "[find_boss_for_siege] Boss siege limit reached!" in message:
                pass
            else:
                exit(1)

    boss_detail_analyzer.handle_response(simple_flow)
    boss_detail_finder.handle_response(simple_flow)
    replayer.handle_response(simple_flow)
    log_warning(
        "------------------ RESPONSE ende -------------------")
