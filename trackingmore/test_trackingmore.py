from . import trackingmore
from .testdata import testdata

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

    assert 'id' in ret
    ret.pop('id')

    assert 'created_at' in ret
    ret.pop('created_at')

    assert 'status' in ret
    ret.pop('status')

    ttd.pop('lang')
    assert ret == ttd


def test_delete_one_tracking_item():
    ttd = dict(testdata.TEST_TRACKING_DATAS[0])
    ret = trackingmore.delete_tracking_item(ttd['carrier_code'], ttd['tracking_number'])
    expected_ret = []
    assert ret == expected_ret


def test_create_tracking_items_batch():
    ttds = [dict(ttd) for ttd in testdata.TEST_TRACKING_DATAS]
    ret = trackingmore.create_tracking_items_batch(ttds)

    assert ret['submitted'] == 4
    assert ret['added'] == 3
    assert len(ret['trackings']) == 3
    assert len(ret['errors']) == 1


def test_get_all_trackings():
    ret = trackingmore.get_all_trackings()
    assert len(ret['items']) == 3
    # TODO: check with trackings added so far


def test_cleanup():
    for ttd in testdata.TEST_TRACKING_DATAS:
        trackingmore.delete_tracking_item(ttd['carrier_code'], ttd['tracking_number'])
