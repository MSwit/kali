#!/usr/bin/env python3

from mitmproxy import http
from mitmproxy import ctx
import json


class Sequence_Number:

    def __init__(self):
        self.last_sequence_number = None
        self.last_seq_num = None
        self.error = False

    def check(self, flow: http.HTTPFlow):
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

            for json_content in json_content_list:

                ctx.log.error(str(json_content))

                try:
                    sequence_number = json_content['sequence_number']
                    seq_num = json_content['seq_num']
                    kind = json_content['kind']
                    if self.last_sequence_number is not None and self.last_seq_num is not None:

                        expected_sequence_number = self.last_sequence_number
                        expected_seq_num = self.last_seq_num + 1
                        ctx.log.error(f"Kind : {kind}")

                        if kind in "bank_lot_consumed":
                            bank_lot_id = json_content['bank_lot_id']
                            if bank_lot_id == 811:
                                pass
                            if bank_lot_id == 801:
                                expected_sequence_number = 0
                            if bank_lot_id == 200:
                                expected_sequence_number = 0

                        if kind in "mob_reward_consumed":
                            # TODO this is not correct, but ok for now.
                            if json_content['level'] >= 122:
                                mob_reward_consumed_modifier = 2
                            expected_sequence_number = self.last_sequence_number + mob_reward_consumed_modifier

                        if kind in "battler_reward_chest_consumed":
                            expected_sequence_number = self.last_sequence_number + mob_reward_consumed_modifier

                        if kind in 'state_updated':
                            expected_sequence_number = self.last_sequence_number + 1

                        if sequence_number != expected_sequence_number:
                            ctx.log.error(
                                "[-] Error: expected sequence_number wrong.")
                            ctx.log.error(
                                f"[-] Error: sequence_number wrong. Expected {expected_sequence_number}, but was {sequence_number}")
                            self.error = True

                        if seq_num != expected_seq_num:
                            ctx.log.error(
                                f"[-] Error: seq_num wrong. Expected {expected_seq_num}, but was {seq_num}")
                            self.error = True

                        if self.error:
                            ctx.log.warn("[-] Es ist ein Fehler aufgetreten.")
                            # exit(1)
                    ctx.log.error(
                        f"setting sequence_number: {sequence_number} and seq_num: {seq_num}")
                    last_sequence_number = sequence_number
                    last_seq_num = seq_num

                except Exception as e:
                    ctx.log.error(
                        "Error during printing seq numbers \n" + str(e))

        except Exception as e:
            ctx.log.error(f"[-] Error: {str(e)}")
            content = json.loads(flow.request.get_content())
            ctx.log.error(str(type(content)))
            ctx.log.error(f"[-] {json.dumps(content,indent=2)}")

            self.error = True
        if self.error:
            ctx.log.warn("[-] Es ist ein Fehler aufgetreten.")


this_class = Sequence_Number()


def request(flow: http.HTTPFlow) -> None:
    this_class.check(flow)
