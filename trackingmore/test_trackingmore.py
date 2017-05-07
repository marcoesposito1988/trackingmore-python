from . import trackingmore
from trackingmore.testdata import testdata

trackingmore.set_api_key(testdata.API_KEY)


def test_create_tracking_data():
    ttd = testdata.TEST_TRACKING_DATAS[0]
    td = trackingmore.create_tracking_data(ttd['carrier_code'], ttd['tracking_number'])
    test_data = {
        'carrier_code': ttd['carrier_code'],
        'tracking_number': ttd['tracking_number'],
    }
    assert td == test_data


def test_create_tracking_data_one_extra_arg():
    ttd = testdata.TEST_TRACKING_DATAS[0]
    td = trackingmore.create_tracking_data(ttd['carrier_code'], ttd['tracking_number'], customer_email=ttd['customer_email'])
    test_data = {
        'carrier_code': ttd['carrier_code'],
        'tracking_number': ttd['tracking_number'],
        'customer_email': ttd['customer_email'],
    }
    assert td == test_data


def test_create_tracking_data_all_extra_args():
    ttd = testdata.TEST_TRACKING_DATAS[0]
    td = trackingmore.create_tracking_data(**ttd)
    assert td == ttd


def test_create_one_tracking_item():
    ttd = dict(testdata.TEST_TRACKING_DATAS[0])
    ret = trackingmore.create_tracking_item(ttd)

    assert 'id' in ret['data']
    ret['data'].pop('id')

    assert 'created_at' in ret['data']
    ret['data'].pop('created_at')

    assert 'status' in ret['data']
    ret['data'].pop('status')

    ttd.pop('lang')
    assert ret['data'] == ttd

    expected_meta = {'type': 'Success',
                     'message': 'Success',
                     'code': 200}
    assert ret['meta'] == expected_meta


def test_delete_one_tracking_item():
    ttd = dict(testdata.TEST_TRACKING_DATAS[0])
    ret = trackingmore.delete_tracking_item(ttd['carrier_code'], ttd['tracking_number'])
    expected_ret = {
        'data': [],
        'meta': {'type': 'Success',
                 'message': 'Success',
                 'code': 200}
    }
    assert ret == expected_ret


def test_create_tracking_items_batch():
    ttds = [dict(ttd) for ttd in testdata.TEST_TRACKING_DATAS]
    ret = trackingmore.create_tracking_items_batch(ttds)

    expected_meta = {'type': 'Success',
                     'message': 'The request was successful and a resource was created.',
                     'code': 201}
    assert ret['meta'] == expected_meta

    assert ret['data']['submitted'] == 4
    assert ret['data']['added'] == 3
    assert len(ret['data']['trackings']) == 3
    assert len(ret['data']['errors']) == 1



def test_get_all_trackings():
    ret = trackingmore.get_all_trackings()
    expected_meta = {'type': 'Success',
                     'message': 'Success',
                     'code': 200}
    assert ret['meta'] == expected_meta
    # TODO: check with trackings added so far


def test_cleanup():
    for ttd in testdata.TEST_TRACKING_DATAS:
        trackingmore.delete_tracking_item(ttd['carrier_code'], ttd['tracking_number'])
