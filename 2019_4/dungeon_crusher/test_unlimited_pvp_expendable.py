import unlimited_pvp_expendable
from simple_flow import SimpleFlow


def test_removement():
    simple_flow = SimpleFlow("", [{"kind": "some_other_kind"}, {
                             "kind": "pvp_expendable_consumed"}], None, None, None)
    unlimited_pvp_expendable.process_request(simple_flow)
    assert len(simple_flow.modified_request) == 1
    assert simple_flow.modified_request[0]['kind'] == "some_other_kind"
