import arena_attack


class Fake_Flow:
    def __init__(self, pretty_url, request):
        self.pretty_url = pretty_url
        self.request = request

    def request(self):
        return self.request


fake_flow = Fake_Flow("https://soulhunters",
                      [{"result": 1, "kind": "pvp_finished", "sequence_number": 4, "seq_num": 13}])


def test_ensure_win():

    updated_content = arena_attack.update_json_list(fake_flow.request)
    assert updated_content[0]['result'] == 0
