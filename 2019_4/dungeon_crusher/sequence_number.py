#!/usr/bin/env python3

from mitmproxy import http
from mitmproxy import ctx
import json


class Sequence_Number:

    def __init__(self):
        self.last_sequence_number = None
        self.last_seq_num = None
        self.error = False

    def is_interesting_request(self, flow: http.HTTPFlow):
        url = flow.request.pretty_url
        if not url.startswith("https://soulhunters"):
            return False
        if len(flow.request.get_content()) == 0:
            return False

        json_content = json.loads(flow.request.get_content())

        if type(json_content) is not list:
            return False
        return True

    def update(self, flow: http.HTTPFlow):
        original_content = flow.request.content
        if not self.is_interesting_request(flow):
            return
        # ctx.log.error("going to udpate sequence numbers...")
        json_content_list = json.loads(flow.request.get_content())

        for json_content in json_content_list:
            try:
                sequence_number = json_content['sequence_number']
                seq_num = json_content['seq_num']
                kind = json_content['kind']
                if self.last_sequence_number is None and self.last_seq_num is None:
                    self.last_sequence_number = sequence_number
                    self.last_seq_num = seq_num
                    # ctx.log.warn("[#] last_sequence_number not set yet. going to skip this request.")
                    return

                expected_sequence_number = self.last_sequence_number
                expected_seq_num = self.last_seq_num + 1
                # ctx.log.error(f"Kind : {kind}")

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

                # if sequence_number != expected_sequence_number:
                #     ctx.log.error(
                #         "[-] Error: expected sequence_number wrong.")
                #     ctx.log.error(
                #         f"[-] Error: sequence_number wrong. Expected {expected_sequence_number}, but was {sequence_number}")
                #     self.error = True

                # if seq_num != expected_seq_num:
                #     ctx.log.error(
                #         f"[-] Error: seq_num wrong. Expected {expected_seq_num}, but was {seq_num}")
                #     self.error = True

                    # exit(1)
                # ctx.log.error(
                #     f"setting sequence_number: {expected_sequence_number} and seq_num: {expected_seq_num}")
                # last_sequence_number =
                # last_seq_num =

                self.last_sequence_number = expected_sequence_number
                self.last_seq_num = expected_seq_num

                json_content['sequence_number'] = expected_sequence_number
                json_content['seq_num'] = expected_seq_num

            except Exception as e:
                ctx.log.error(
                    "Error during printing seq numbers \n" + str(e))
        new_content = json.dumps(json_content_list)
        # new_content = new_content.replace(": ", ":")
        flow.request.set_content(new_content.encode('utf-8'))
        possible_modified_content = flow.request.content
        # ctx.log.error(
        #     "[-] nearly at the end of updating sequence numbers.")
        # flow.request.content = json.dumps(
        #     json_content_list).encode('utf-8')
        # if(last_seq_num == sequence_number and last_seq_num == seq_num):
        #     ctx.log.warn(
        #         "[#] sequence numbers are not updated. Content should stay the same")
        if possible_modified_content != original_content:
            pass
            # ctx.log.error(f"[-] Type of origiginal content = {type(original_content)}")
            # ctx.log.error(f"[-] Type of modified content = {type(possible_modified_content)}")
            # ctx.log.error(f"[-] ---------------------------------------------------------------")
            # ctx.log.error(f"[-] Length of origiginal = {len(original_content)}")
            # ctx.log.error(f"[-] Length of  modified content = {len(possible_modified_content)}")
            # ctx.log.error(
            #     "[-] original content and updated content differs")

            # modified_content_get = flow.request.get_content()
            # ctx.log.error(f"[-] Length of newly getted content = {len(modified_content_get)}")

            # ctx.log.error(f"[-] original content = {original_content}")
            # ctx.log.warn(f"[-] ---------------------------------------")
            # ctx.log.error(f"[-] modified content = {possible_modified_content}")

            # exit(1)
        else:
            ctx.log.error(
                "[-] Test? is everything fine?")

        flow.request.content = original_content

    def check(self, flow: http.HTTPFlow):
        url = flow.request.pretty_url

        ctx.log.error("going to check sequence numbers...")
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

                # ctx.log.error(str(json_content))

                try:
                    sequence_number = json_content['sequence_number']
                    seq_num = json_content['seq_num']
                    kind = json_content['kind']
                    if self.last_sequence_number is not None and self.last_seq_num is not None:
                        ctx.log.error(str(self.last_sequence_number))
                        ctx.log.error(str(self.last_seq_num))
                        # exit(1)
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
                    self.last_sequence_number = sequence_number
                    self.last_seq_num = seq_num

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
            exit(1)

    def print(self, flow: http.HTTPFlow):
        url = flow.request.pretty_url

        # ctx.log.error("going to check sequence numbers...")

        if not url.startswith("https://soulhunters"):
            return
        if len(flow.request.get_content()) == 0:
            return

        json_content = json.loads(flow.request.get_content())

        if type(json_content) is not list:
            return

        json_content_list = json_content

        ctx.log.info("-------------------------------------------")
        for json_content in json_content_list:
            sequence_number = json_content['sequence_number']
            seq_num = json_content['seq_num']
            kind = json_content['kind']
            ctx.log(f"Original: sequence_number: {sequence_number}, seq_num: {seq_num}, kind: {kind}")


this_class = Sequence_Number()


def request(flow: http.HTTPFlow) -> None:
    this_class.print(flow)
    this_class.update(flow)
    ctx.log.warn("-------------------------------------------")
    this_class.print(flow)
