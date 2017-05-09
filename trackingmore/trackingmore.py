from typing import NewType, Dict, Any

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


def set_api_key(api_key: str):
    """
    Set the API key to be used for authentication with every request.
    
    If you need one, get it by registering for a TrackingMore account.
    :param api_key: Authentication token
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


class TrackingMoreAPIException(Exception):
    def __init__(self, meta_dict: dict) -> None:
        super().__init__(meta_dict['message'])
        self.err_code = meta_dict['code']
        self.err_type = meta_dict['type']


def _check_response(resp: requests.Response):
    resp.raise_for_status()
    if resp.json()['meta']['code'] not in [200, 201]:  # TrackingMore errors give an HTTP 200 status code
        raise TrackingMoreAPIException(resp.json()['meta'])


BASE_URL = 'http://api.trackingmore.com/v2'


def _add_if_existing(args, arg_name, target_dict):
    if arg_name == 'status':
        if arg_name in args and type(args[arg_name]) is TrackingStatus:
            target_dict[arg_name] = args[arg_name].name
    else:
        if args[arg_name]:
            if type(args[arg_name]) is datetime:
                dt = args[arg_name]
                target_dict[arg_name] = dt.replace(tzinfo=timezone.utc).timestamp()
            else:
                target_dict[arg_name] = args[arg_name]


TrackingData = NewType('TrackingData', Dict[str, str])


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
    _add_if_existing(locals(), 'title', tracking_data)
    _add_if_existing(locals(), 'customer_name', tracking_data)
    _add_if_existing(locals(), 'customer_email', tracking_data)
    _add_if_existing(locals(), 'order_id', tracking_data)
    _add_if_existing(locals(), 'lang', tracking_data)
    return tracking_data


def create_tracking_item(tracking_data: TrackingData) -> Dict[str, Any]:
    """
    Create a tracking item in the TrackingMore system.
    
    :param tracking_data: Information about the package to be tracked
    :return: Information about the created tracking item, or [] if already existing
    """
    _check_api_key()
    r = requests.post(BASE_URL + '/trackings/post', headers=headers, data=json.dumps(tracking_data))
    _check_response(r)
    return r.json()['data']


def create_tracking_items_batch(tracking_data_list: [TrackingData]) -> Dict[str, Any]:
    """
    Create multiple tracking items.
    
    :param tracking_data_list: Information about the packages to be tracked, in a list
    :return: Information about the created tracking items, in a list
    """
    _check_api_key()
    r = requests.post(BASE_URL + '/trackings/batch', headers=headers, data=json.dumps(tracking_data_list))
    _check_response(r)
    return r.json()['data']


def update_tracking_item(tracking_data: TrackingData) -> Dict[str, Any]:
    """
    Update information about a previously created tracking item.
    
    :param tracking_data: Partial, updated information about a tracking item
    :return: Information about the updated tracking item
    """
    _check_api_key()
    tracking_data = dict(tracking_data)
    carrier_code = tracking_data.pop('carrier_code')
    tracking_number = tracking_data.pop('tracking_number')
    r = requests.put(BASE_URL + '/trackings/{}/{}'.format(carrier_code, tracking_number), headers=headers)
    _check_response(r)
    return r.json()['data']


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
    _add_if_existing(locals(), 'status', payload)
    _add_if_existing(locals(), 'limit', payload)
    _add_if_existing(locals(), 'page', payload)
    _add_if_existing(locals(), 'created_at_min', payload)
    _add_if_existing(locals(), 'created_at_max', payload)
    _add_if_existing(locals(), 'update_time_min', payload)
    _add_if_existing(locals(), 'update_time_max', payload)

    r = requests.get(BASE_URL + '/trackings/get', headers=headers)
    _check_response(r)
    return r.json()


def get_tracking_item(carrier_code: str, tracking_number: str) -> Dict[str, Any]:
    """
    Fetch information about a previously created tracking item.
    
    :param carrier_code: The TrackingMore courier code
    :param tracking_number: The package's tracking number
    :return: A big fat dict with all possible information about the shipping
    """
    _check_api_key()
    r = requests.get(BASE_URL + '/trackings/{}/{}'.format(carrier_code, tracking_number), headers=headers)
    _check_response(r)
    return r.json()['data']


def delete_tracking_item(carrier_code: str, tracking_number: str) -> Dict[str, Any]:
    """
    Remove a tracking item from the TrackingMore system.
    
    :param carrier_code: The TrackingMore courier code
    :param tracking_number: The package's tracking number
    :return: A big fat dict with all possible information about the shipping
    """
    _check_api_key()
    r = requests.delete(BASE_URL + '/trackings/{}/{}'.format(carrier_code, tracking_number), headers=headers)
    _check_response(r)
    return r.json()['data']


def realtime_tracking(tracking_data: TrackingData) -> Dict[str, Any]:
    """
    Fetch updated tracking information from the courier's API.
    
    Stricter rate limiting applies.
    :param tracking_data: Information about the package to be found 
    :return: A big fat dict with all possible information about the shipping
    """
    _check_api_key()
    r = requests.post(BASE_URL + '/trackings/realtime', headers=headers, data=json.dumps(tracking_data))
    _check_response(r)
    return r.json()['data']


def detect_carrier_from_code(tracking_code: str) -> Dict[str, Any]:
    """
    Guess the courier from the tracking number.
    
    :param tracking_code: The package tracking number
    :return: A list of dictionaries with the possible couriers name and TrackingMore code
    """
    _check_api_key()
    payload = {'tracking_number': tracking_code.strip()}
    r = requests.post(BASE_URL + '/carriers/detect', headers=headers, data=json.dumps(payload))
    _check_response(r)
    return r.json()['data']
