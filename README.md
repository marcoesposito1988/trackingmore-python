[![PyPI version](https://badge.fury.io/py/trackingmore.svg)](https://badge.fury.io/py/trackingmore)
[![Build Status](https://travis-ci.org/marcoesposito1988/trackingmore-python.svg?branch=master)](https://travis-ci.org/marcoesposito1988/trackingmore-python)
[![codecov](https://codecov.io/gh/marcoesposito1988/trackingmore-python/branch/master/graph/badge.svg)](https://codecov.io/gh/marcoesposito1988/trackingmore-python)

# pytrackingmore
Python wrapper for the TrackingMore API

This library supports the following methods of the TrackingMore API:

- Creating a new tracking item, given the courier code and the tracking number
- Creating a batch of tracking items, given the courier code and the tracking number
- Updating a tracking item, given the courier code and the tracking number
- Deleting a tracking item, given the courier code and the tracking number
- Querying the tracking data for an item from the courier API in real time
- Detecting the courier from the tracking number

## Installation
```pip install trackingmore```

## Setup
You need a TrackingMore account in order to use the API. You can then 
generate an API token, which you 
will need to pass to the trackingmore module. 

You can just do it once somewhere in the program, before using the API.

```$xslt
import trackingmore

trackingmore.set_api_key('my-api-key')

```

## Creating tracking items
Before accessing information about a shipment, you must create a tracking item 
in TrackingMore's system. It will then be also visible in the dashboard.

### Creating a single tracking item
Each shipment is identifiable through its courier code and tracking number.
 
```$xslt
>>> td = trackingmore.create_tracking_data('poste-italiane', '1234567890')
>>> trackingmore.create_tracking_item(td)

{
    "id": "b6321d71ad627cbf8c141ccc25fc659f",
    "tracking_number": "1234567890",
    "carrier_code": "poste-italiane",
    "status": "pending",
    "created_at": "2017-05-20T17:39:21+08:00",
    "customer_email": "null",
    "customer_name": "null",
    "order_id": "null",
    "title": null
}
```

However, while creating a tracking item, it is possible to provide additional 
metadata to be stored in TrackingMore's database, to facilitate your own operations. 
The trackingmore module includes a helper function to create a TrackingData object.

```$xslt
>>> td = trackingmore.create_tracking_data(
        carrier_code='poste-italiane', 
        tracking_number='0987654321', 
        title='my_first_package', 
        customer_name='Marco Esposito',
        customer_email='marcoesposito1988@gmail.com', 
        order_id='my_order_id', 
        lang='it'
    )
    
>>> trackingmore.create_tracking_item(td)

{
    "id": "b6321d71ad627cbf8c141ccc25fc6600",
    "tracking_number": "0987654321",
    "carrier_code": "poste-italiane",
    "status": "pending",
    "created_at": "2017-05-20T17:39:23+08:00",
    "customer_email": "marcoesposito1988@gmail.com",
    "customer_name": "Marco Esposito",
    "order_id": "my_order_id",
    "title": "my_first_package"
}
```

### Batch creation
It is possible to create multiple tracking items with a single API call.

```$xslt
>>> tds = [
        trackingmore.create_tracking_data('poste-italiane', '1234567890'),
        trackingmore.create_tracking_data('dhl', 'abc123456')
    ]
    
>>> trackingmore.create_tracking_items_batch(tds)
[
    {
        "id": "b6321d71ad627cbf8c141ccc25fc6601",
        "tracking_number": "1234567890",
        "carrier_code": "poste-italiane",
        "status": "pending",
        "created_at": "2017-05-20T17:39:26+08:00",
        "customer_email": "null",
        "customer_name": "null",
        "order_id": "null",
        "title": null
    },
    {
        "id": "b6321d71ad627cbf8c141ccc25fc6602",
        "tracking_number": "abc123456",
        "carrier_code": "dhl",
        "status": "pending",
        "created_at": "2017-05-20T17:39:26+08:00",
        "customer_email": "null",
        "customer_name": "null",
        "order_id": "null",
        "title": null
    }
]
```

## Updating tracking items
It is also possible to update the tracking item metadata after creation. 

```$xslt
>>> td = trackingmore.create_tracking_data(
        carrier_code='poste-italiane', 
        tracking_number='1234567890', 
        customer_name='Marco Esposito',
        customer_email='marcoesposito1988@gmail.com'
    )
    
>>> trackingmore.update_tracking_item(td)
{
    "id": "b6321d71ad627cbf8c141ccc25fc659f",
    "tracking_number": "1234567890",
    "carrier_code": "poste-italiane",
    "status": "pending",
    "created_at": "2017-05-20T17:39:21+08:00",
    "customer_email": "marcoesposito1988@gmail.com",
    "customer_name": "Marco Esposito",
    "order_id": "null",
    "title": null
}
```

## Fetching information about tracking items
Once a tracking item has been created, it will synchronize periodically 
(every few hours) with the courier's system. 

### Normal query
It is possible to fetch the latest information from the TrackingMore 
servers by providing the courier code and tracking number.

```$xslt
>>> trackingmore.get_tracking_item('ups', '1Z97X17XYW06605211')
{
    "id": "ac9326a212b9b8660759f55bac89df2b",
    "tracking_number": "1Z97X17XYW06605211",
    "carrier_code": "ups",
    "status": "transit",
    "created_at": "2015-11-20T21:01:30+08:00",
    "updated_at": "2015-11-21T15:27:26+08:00",
    "original_country": "United States",
    "itemTimeLength": null,
    "origin_info": {
        "weblink": "http:\/\/www.ups.com\/content\/us\/en\/contact\/index.html?WT.svl=Footer",
        "phone": null,
        "carrier_code": "ups",
        "trackinfo": [{
            "Date": "2015-11-06 09:46:00",
            "StatusDescription": "package transferred to post office.",
            "Details": ""
        }, {
            "Date": "2015-11-06 05:41:00",
            "StatusDescription": "destination scan",
            "Details": "US,BALDWIN PARK"
        }, 
        ...
        ]
    }
}
```

### Realtime query
This method forces the TrackingMore server to fetch the latest information available 
from the courier's system. A rate limit applies.

```$xslt
>>> td = trackingmore.create_tracking_data('china-ems', 'LK664578623CN')
    
>>> trackingmore.realtime_tracking(td)

{
    "items": [{
        "id": "442f798ea35749e7605d1a73d4181a01",
        "tracking_number": "RE113184005HK",
        "carrier_code": "hong-kong-post",
        "status": "transit",
        "original_country": "Hong Kong [CN]",
        "destination_country": "Colombia",
        "itemTimeLength": null,
        "origin_info": {
            "weblink": "http:\/\/www.hongkongpost.hk\/",
            "phone": "852 2921 2222",
            "carrier_code": "hong-kong-post",
            "trackinfo": [{
                "Details": "CO",
                "StatusDescription": "The item ( RE113184005HK ) left Hong Kong for its destination on  10-Oct-2015 ",
                "Date": "2015-10-09 00:00"
            }]
        },
        "destination_info": {
            "weblink": "http:\/\/www.4-72.com.co\/",
            "phone": "(57-1) 4722000",
            "carrier_code": "colombia-post",
            "trackinfo": [{
                "Date": "2015-10-22 20:52",
                "StatusDescription": "DIGITALIZADO",
                "Details": "CTP.CENTRO A"
            }, {
                "Date": "2015-10-22 17:02",
                "StatusDescription": "Registro de entrega exitosa",
                "Details": ""
            }, {
                "Date": "2015-10-22 16:55",
                "StatusDescription": "ENTREGADO",
                "Details": "CD.MONTEVIDEO"
            },
            ...
            ]
        }
    "lastEvent": "DIGITALIZADO,CTP.CENTRO A,2015-10-22 20:52",
    "lastUpdateTime": "2015-10-22 20:52"
    }]
}
```

## Deleting a tracking item
It is possible to delete a tracking item when it is not needed any more. It can 
be added again later at no additional cost (TrackingMore charges per package).

```$xslt
>>> trackingmore.delete_tracking_item('ups', '1Z97X17XYW06605211')
[]
```

## Notes

The author is not affiliated to TrackingMore. Every responsibility is declined.
