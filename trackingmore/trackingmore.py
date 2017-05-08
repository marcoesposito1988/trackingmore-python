from typing import NewType

from enum import Enum
from datetime import datetime, timezone
import json
import requests

headers = None
"""
Headers to be sent with an API request. Is set on set_api_key call.
"""

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
"""
Collection of courier codes for some selected couriers. More info at https://www.trackingmore.com/help_article-25-31-en.html
"""


class TrackingStatus(Enum):
    PENDING = 'pending'
    NOTFOUND = 'notfound'
    TRANSIT = 'transit'
    PICKUP = 'pickup'
    DELIVERED = 'delivered'
    UNDELIVERED = 'undelivered'
    EXCEPTION = 'exception'
    EXPIRED = 'expired'


def set_api_key(api_key):
    """
    Set the API key to be used for authentication with every request.
    
    If you need one, get it by registering for a TrackingMore account.
    :param api_key: Authentication token
    :return: 
    """
    global headers
    headers = {
        'Content-Type': 'application/json',
        'Trackingmore-Api-Key': api_key,
        'X-Requested-With': 'XMLHttpRequest'
    }


def _check_api_key():
    if headers is None:
        raise ValueError("did you set the API key with trackingmore.set_api_key('...')?")


def add_if_existing(args, arg_name, target_dict):
    if arg_name == 'status':
        if arg_name in args and type(args[arg_name]) is TrackingStatus:
            target_dict[arg_name] = args[arg_name].name
    else:
        if arg_name in args:
            if type(args[arg_name]) is datetime:
                dt = args[arg_name]
                target_dict[arg_name] = dt.replace(tzinfo=timezone.utc).timestamp()
            else:
                target_dict[arg_name] = args[arg_name]


BASE_URL = 'http://api.trackingmore.com/v2'


def get_all_trackings(limit: int = None, page: int = None, status: TrackingStatus = None,
                      created_at_min: datetime = None, created_at_max: datetime = None,
                      update_time_min: datetime = None, update_time_max: datetime = None):
    """
    Fetch information for all the trackings created so far.
    
    Use arguments for filtering and pagination.
    :param limit: Maximum number of results to be returned
    :param page: Number of the page to be returned (of size "limit")
    :param status: Filter by tracking status
    :param created_at_min: Get only items created after this datetime
    :param created_at_max: Get only items created before this datetime
    :param update_time_min: Get only items updated after this datetime
    :param update_time_max: Get only items updated before this datetime
    :return: 
    """
    _check_api_key()

    payload = {}
    add_if_existing(locals(), 'status', payload)
    add_if_existing(locals(), 'limit', payload)
    add_if_existing(locals(), 'page', payload)
    add_if_existing(locals(), 'created_at_min', payload)
    add_if_existing(locals(), 'created_at_max', payload)
    add_if_existing(locals(), 'update_time_min', payload)
    add_if_existing(locals(), 'update_time_max', payload)

    r = requests.get(BASE_URL + '/trackings/get', headers=headers)
    return r.json()


TrackingData = NewType('TrackingData', dict)


def create_tracking_data(carrier_code: str, tracking_number: str, title: str = None, customer_name: str = None,
                         customer_email: str = None, order_id: str = None, lang: str = None) -> TrackingData:
    """
    Create a dictionary holding information about a tracking item
    
    :param carrier_code: TrackingMore code indentifying the courier company
    :param tracking_number: Package tracking ID
    :param title: (Optional) name for this tracking item
    :param customer_name: (Optional) customer name
    :param customer_email: (Optional) customer email
    :param order_id: (Optional) your ID for this tracking item
    :param lang: (Optional) language for strings returned by the courier (if supported)
    :return: 
    """
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
    _check_api_key()
    r = requests.post(BASE_URL + '/trackings/post', headers=headers, data=json.dumps(tracking_data))
    return r.json()


def create_tracking_items_batch(tracking_data_list):
    _check_api_key()
    r = requests.post(BASE_URL + '/trackings/batch', headers=headers, data=json.dumps(tracking_data_list))
    return r.json()


def get_tracking_item(carrier_code, tracking_number):
    _check_api_key()
    r = requests.get(BASE_URL + '/trackings/{}/{}'.format(carrier_code, tracking_number), headers=headers)
    return r.json()


def update_tracking_item(carrier_code, tracking_number):
    _check_api_key()
    r = requests.put(BASE_URL + '/trackings/{}/{}'.format(carrier_code, tracking_number), headers=headers)
    return r.json()


def delete_tracking_item(carrier_code, tracking_number):
    _check_api_key()
    r = requests.delete(BASE_URL + '/trackings/{}/{}'.format(carrier_code, tracking_number), headers=headers)
    return r.json()


def realtime_tracking(tracking_data):
    _check_api_key()
    r = requests.post(BASE_URL + '/trackings/realtime', headers=headers, data=json.dumps(tracking_data))
    return r.json()


def detect_carrier_from_code(tracking_code):
    _check_api_key()
    payload = {'tracking_number': tracking_code.strip()}
    r = requests.post(BASE_URL + '/carriers/detect', headers=headers, data=json.dumps(payload))
    return r.json()


