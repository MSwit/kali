#!/usr/bin/env python3
from mitmproxy import ctx
from mitmproxy import http
from mitm_logging import log_error
from simple_flow import SimpleFlow
from threading import Thread, Lock
import sys

print(sys.argv)


class ClientReplay:

    def __init__(self):
        self.pending_id = None
        self.lock = Lock()

    def replay(self, flow: http.HTTPFlow) -> None:
        if not self.isIdle():
            raise Exception("[-] There is already another flow pending")
        log_error(
            f"[+] ClientReplay: going to aquire lock for replay flow with id : {flow.id}")
        self.lock.acquire()
        # log_error(f"[+] ClientReplay: successfully aquired lock for replay flow with id : {flow.id}")
        copy = flow.copy()
        self.pending_id = copy.id
        ctx.master.commands.call("replay.client", [copy])
        # log_error(f"[+] \t\t REPLAYED flow!...... id: {self.pending_id}")
        # log_error(f"[+] \t\t self.isIdle should be false now. isIdle? : {self.isIdle()}")

        self.lock.release()

    def reset(self):
        self.pending_id = None

    def handle_request(self, simple_flow: SimpleFlow) -> None:
        if simple_flow.flow.id == self.pending_id:
            # log_error(f"[+] \t\t REPLAY - seen flow in request. id : {self.pending_id}")
            pass
        pass

    def handle_response(self, simple_flow: SimpleFlow) -> None:
        if simple_flow.flow.id == self.pending_id:
            # log_error(f"[+] \t\t REPLAY - seen flow in response -> cleanup. id : {self.pending_id}")
            self.reset()

    def isIdle(self):
        return self.pending_id == None


# .168.178.23:40779: Client Handshake failed. The client may not trust the proxy's certificate for ms.applovin.com.
# 192.168.178.23:40779: clientdisconnect
#   ------------------ REQUEST starts -------------------
#   {}
#   response starts
#   ------------------ RESPONSE starts -------------------
#   [++++++++++] boss_searcher. replayer is idle? : True
#   [+] current siege count: 0
#   replayer is idle? : True
#   [-] no api session flow set, yet. Cant search for new bosses.
#   [+] Detect Current siege count: 0........., re-schedule timer
#   ------------------ RESPONSE ende -------------------
# 192.168.178.23:46939: GET https://142.93.135.166/api/boss_sieges/sieges
#                    << 200 OK 81b
# 192.168.178.23:49733: clientconnect
# 192.168.178.23:49733: Client Handshake failed. The client may not trust the proxy's certificate for ms.applvn.com.
# 192.168.178.23:49733: clientdisconnect
#   ------------------ REQUEST starts -------------------
#   [{"level": 3284, "consumed_loot": [{"config_id": 100590, "amount": 1}], "kind": "mob_reward_consumed", "sequence_number": 2, "seq_num": 0}, {"level": 3284, "consumed_loot": [{"config_id": 100240, "amount": 1}], "kind": "mob_reward_consumed", "sequence_number": 4, "seq_num": 1}, {"kind": "find_boss_for_siege", "sequence_number": 4, "seq_num": 2}]
#   [+] Setting initial sequence_number: 2 and seq_num: 0
#   response starts
#   ------------------ RESPONSE starts -------------------
#   [++++++++++] boss_searcher. replayer is idle? : True
#   [+] current siege count: 1
#   replayer is idle? : True
#   [+] 	I send search for boss request
#   [+] 		 REPLAYED flow!...... id: f8932c16-62dc-45bc-b422-0217b30448df
#   [+] Detect Current siege count: 1........., re-schedule timer
#   ------------------ RESPONSE ende -------------------
# 192.168.178.23:46939: PUT https://142.93.135.166/api/session
#                    << 200 OK 350b
#   ------------------ REQUEST starts -------------------
#   [+] 		 REPLAY - seen flow in request. id : f8932c16-62dc-45bc-b422-0217b30448df
#   [{"kind": "find_boss_for_siege", "sequence_number": -1, "seq_num": -1}]
#   response starts
#   [+] 		 REPLAY - seen flow in response -> cleanup. id : f8932c16-62dc-45bc-b422-0217b30448df
#   ------------------ RESPONSE starts -------------------
#   [++++++++++] boss_searcher. replayer is idle? : True
#   [+] current siege count: 2
#   replayer is idle? : True
#   [+] 	I send search for boss request
#   [+] 		 REPLAYED flow!...... id: f3c5b6d2-3e7e-4514-8d02-454c7035be9c
#   [+] Detect Current siege count: 2........., re-schedule timer
#   ------------------ RESPONSE ende -------------------
# 192.168.178.23:46939: PUT https://142.93.135.166/api/session
#                    << 200 OK 433b
#   ------------------ REQUEST starts -------------------
#   [+] 		 REPLAY - seen flow in request. id : f3c5b6d2-3e7e-4514-8d02-454c7035be9c
#   [{"kind": "find_boss_for_siege", "sequence_number": -1, "seq_num": -1}]
#   response starts
#   [+] 		 REPLAY - seen flow in response -> cleanup. id : f3c5b6d2-3e7e-4514-8d02-454c7035be9c
#   ------------------ RESPONSE starts -------------------
#   [#] I will send boss siege attack.
#   [+] 		 REPLAYED flow!...... id: f06df648-64f2-4c00-8ec9-51a4bab58e33
#   [++++++++++] boss_searcher. replayer is idle? : True
#   [+] current siege count: 3
#   replayer is idle? : True
#   [+] 	I send search for boss request
# 192.168.178.23:46939: PUT https://142.93.135.166/api/session
#                    << 200 OK 512b
# Addon error: Traceback (most recent call last):
#   File "dungeon_crusher/sieges.py", line 213, in response
#     [addon.handle_response(simple_flow) for addon in my_addons]
#   File "dungeon_crusher/sieges.py", line 213, in <listcomp>
#     [addon.handle_response(simple_flow) for addon in my_addons]
#   File "dungeon_crusher/boss_searcher.py", line 63, in handle_response
#     self.try_search_for_boss()
#   File "dungeon_crusher/boss_searcher.py", line 88, in try_search_for_boss
#     self.replayer.replay(fake_request)
#   File "dungeon_crusher/client_replay.py", line 16, in replay
#     raise Exception("[-] There is already another flow pending")
# Exception: [-] There is already another flow pending

#   ------------------ REQUEST starts -------------------
#   [+] 		 REPLAY - seen flow in request. id : f06df648-64f2-4c00-8ec9-51a4bab58e33
#   [{"kind": "boss_siege_refill_attack", "sequence_number": -1, "seq_num": -1}, {"siege_id": "66f03464-60de-47e7-bcb2-80490770cec1", "power_attack": false, "autorestore_is_on": true, "kind": "boss_siege_attack", "sequence_number": -1, "seq_num": -1}]
#   response starts
#   [+] 		 REPLAY - seen flow in response -> cleanup. id : f06df648-64f2-4c00-8ec9-51a4bab58e33
#   ------------------ RESPONSE starts -------------------
#   [-] Did 2583734 dmg to Boss with currenthp 8416266
#   [++++++++++] boss_searcher. replayer is idle? : True
#   ------------------ RESPONSE ende -------------------
