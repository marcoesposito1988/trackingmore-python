import json
import requests

headers = None


COURIERS = {
    'Italy': {
        'Poste Italiane': 'poste-italiane',
        'Nexive': 'nexive',
        'GLS Italia': 'gls-italy',
        'Bartolini': 'bartolini',
        'TNT Italia': 'tnt-it',
        'SGT Italia': 'sgt-it',
        'SDA Italia': 'italy-sda',
    }
}


def set_api_key(api_key):
    global headers
    headers = {
        'Content-Type': 'application/json',
        'Trackingmore-Api-Key': api_key,
        'X-Requested-With': 'XMLHttpRequest'
    }


def check_api_key():
    if headers is None:
        raise ValueError("did you set the API key with trackingmore.set_api_key('...')?")


BASE_URL = 'http://api.trackingmore.com/v2'


def get_all_trackings(status=None, limit=None, page=None,
                      created_at_min=None, created_at_max=None, update_time_min=None, update_time_max=None):
    check_api_key()

    payload={}
    add_if_existing(locals(), 'status', payload)
    add_if_existing(locals(), 'limit', payload)
    add_if_existing(locals(), 'page', payload)
    add_if_existing(locals(), 'created_at_min', payload)
    add_if_existing(locals(), 'created_at_max', payload)
    add_if_existing(locals(), 'update_time_min', payload)
    add_if_existing(locals(), 'update_time_max', payload)

    r = requests.get(BASE_URL+'/trackings/get', headers=headers)
    return r.json()


def add_if_existing(args, arg_name, target_dict):
    if args[arg_name]:
        target_dict[arg_name] = args[arg_name]


def create_tracking_data(carrier_code, tracking_number, title=None, customer_name=None, customer_email=None,
                         order_id=None, lang=None):
    tracking_data = {
        'carrier_code': carrier_code,
        'tracking_number': tracking_number,
    }
    add_if_existing(locals(), 'title', tracking_data)
    add_if_existing(locals(), 'customer_name', tracking_data)
    add_if_existing(locals(), 'customer_email', tracking_data)
    add_if_existing(locals(), 'order_id', tracking_data)
    add_if_existing(locals(), 'lang', tracking_data)
    return tracking_data


def create_tracking_item(tracking_data):
    check_api_key()
    r = requests.post(BASE_URL+'/trackings/post', headers=headers, data=json.dumps(tracking_data))
    return r.json()


def create_tracking_items_batch(tracking_data_list):
    check_api_key()
    r = requests.post(BASE_URL+'/trackings/batch', headers=headers, data=json.dumps(tracking_data_list))
    return r.json()


def get_tracking_item(carrier_code, tracking_number):
    check_api_key()
    r = requests.get(BASE_URL+'/trackings/{}/{}'.format(carrier_code, tracking_number), headers=headers)
    return r.json()


def update_tracking_item(carrier_code, tracking_number):
    check_api_key()
    r = requests.put(BASE_URL+'/trackings/{}/{}'.format(carrier_code, tracking_number), headers=headers)
    return r.json()


def delete_tracking_item(carrier_code, tracking_number):
    check_api_key()
    r = requests.delete(BASE_URL+'/trackings/{}/{}'.format(carrier_code, tracking_number), headers=headers)
    return r.json()


def realtime_tracking(tracking_data):
    check_api_key()
    r = requests.post(BASE_URL+'/trackings/realtime', headers=headers, data=json.dumps(tracking_data))
    return r.json()


def detect_carrier_from_code(tracking_code):
    check_api_key()
    payload = {'tracking_number': tracking_code.strip()}
    r = requests.post(BASE_URL+'/carriers/detect', headers=headers, data=json.dumps(payload))
    return r.json()


