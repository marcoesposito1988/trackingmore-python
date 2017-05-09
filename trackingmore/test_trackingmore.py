import pytest
from . import trackingmore
from .testdata import testdata


def test_set_api_key():
    with pytest.raises(ValueError):
        trackingmore._check_api_key()

    trackingmore.set_api_key(testdata.API_KEY)

    trackingmore._check_api_key()


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


def test_get_tracking_item():
    try:
        ttd = dict(testdata.TEST_TRACKING_DATAS[0])
        ret = trackingmore.get_tracking_item(ttd['carrier_code'], ttd['tracking_number'])
    except trackingmore.TrackingMoreAPIException as tme:
        assert tme.err_code == 4021  # if we fail because we do not have any more credit it's ok


def test_realtime_tracking():
    try:
        ttd = dict(testdata.TEST_TRACKING_DATAS[0])
        ret = trackingmore.realtime_tracking(ttd)
    except trackingmore.TrackingMoreAPIException as tme:
        assert tme.err_code == 4021  # if we fail because we do not have any more credit it's ok


def test_update_tracking_item():
    try:
        ttd = dict(testdata.TEST_TRACKING_DATAS[0])
        ttd['title'] = 'new_title'
        ret = trackingmore.update_tracking_item(ttd)
    except trackingmore.TrackingMoreAPIException as tme:
        assert tme.err_code in [4017, 4021]  # if we fail because we do not have any more credit it's ok


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
    try:
        ret = trackingmore.get_all_trackings()
        assert len(ret['items']) == 3
        # TODO: check with trackings added so far
    except trackingmore.TrackingMoreAPIException as tme:
        assert tme.err_code == 4021  # if we fail because we do not have any more credit it's ok


def test_detect_courier():
    for ttd in testdata.TEST_TRACKING_DATAS[:-1]:
        tracking_number = ttd['tracking_number']
        carrier_code = ttd['carrier_code']

        ret = trackingmore.detect_carrier_from_code(tracking_number)
        assert any(r['code'] == carrier_code for r in ret)


def test_cleanup():
    try:
        for ttd in testdata.TEST_TRACKING_DATAS:
            trackingmore.delete_tracking_item(ttd['carrier_code'], ttd['tracking_number'])
    except trackingmore.TrackingMoreAPIException as tme:
        assert tme.err_code in [4017, 4021]  # if we fail because we do not have any more credit it's ok
