
from sequence_number import Sequence_Number


def generate_request(sequence_number, seq_num, kind):
    return {'sequence_number': sequence_number, 'seq_num': seq_num, 'kind': kind}


def test_first_request_issnt_modified():
    request = generate_request(0, 0, "some_kind")
    updater = Sequence_Number()
    updated_request = updater.generate_updated_json(request)
    assert updated_request == request


def test_second_request_gets_updated_seq_num():
    request = generate_request(0, 0, "some_kind")
    updater = Sequence_Number()
    updated_request1 = updater.generate_updated_json(request)
    updated_request2 = updater.generate_updated_json(request)
    assert updated_request2['seq_num'] == 1
    assert updated_request2['sequence_number'] == request['sequence_number']
