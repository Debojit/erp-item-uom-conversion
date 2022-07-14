import resource
from urllib import response
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
import requests

from typing import List, Tuple, Dict, Optional

import json
import os


def _invoke_api(verb: str, resource_url: str, headers: Optional[Dict] = None, payload: Optional[Dict] = None) -> Tuple:
    """Generic API invocation method"""

    payload = {} if payload == None else payload
    headers = {} if headers == None else headers

    payload = json.dumps(payload)

    api_url = 'https://' + \
        os.getenv('erp.host') + ':' + os.getenv('erp.port') + resource_url
    response = requests.request(method=verb, url=api_url, auth=HTTPBasicAuth(os.getenv('erp.user'),
                                                                             os.getenv('erp.password')), headers={'Content-Type': 'application/json'}, data=payload)
    response.raise_for_status()
    return (response.status_code, response.json())


def get_intraclass_conversions(uom_code: str, item_id: int) -> Dict:
    """Get interclass conversion for UOM Code and Item ID"""

    resource_url: str = f'/fscmRestApi/resources/11.13.18.05/unitsOfMeasure/{uom_code}/child/intraclassConversions?q=InventoryItemId={item_id}&onlyData=true'
    try:
        status_code, response_payload = _invoke_api(verb='GET', resource_url=resource_url)
        if len(response_payload['items']) > 0:
            response_item = response_payload['items'][0]
            return {
                'status_code': status_code,
                'data': {
                    'conversion_id': response_item['ConversionId'],
                    'item_id': response_item['InventoryItemId'],
                    'item_number': response_item['ItemNumber'],
                    'conversion_value': response_item['IntraclassConversion']
                }
            }
        else:
            return {
                'status_code': status_code,
                'data': {}
            }
    except requests.exceptions.HTTPError as httpe:
        return {
            'status_code': httpe.response.status_code,
            'error': f'Invalid UOM Code {uom_code} and Item ID {item_id} combination'
        }


def create_intraclass_conversion(uom_code: str, item_id, conv_value: float) -> Dict:
    """Create new intraclass conversion"""

    resource_url: str = f'/fscmRestApi/resources/11.13.18.05/unitsOfMeasure/{uom_code}/child/intraclassConversions'
    request_payload: Dict = {
        'InventoryItemId': item_id,
        'IntraclassConversion': conv_value
    }

    try:
        status_code, response_payload = _invoke_api(verb='POST', resource_url=resource_url, payload=request_payload)
        return {
            'status_code': status_code,
            'data': {
                'conversion_id': response_payload['ConversionId'],
                'item_id': response_payload['InventoryItemId'],
                'item_number': response_payload['ItemNumber'],
                'conversion_value': response_payload['IntraclassConversion']
            }
        }
    except requests.exceptions.HTTPError as httpe:
        return {
            'status_code': httpe.response.status_code,
            'error': httpe.response.text
        }

def update_intraclass_conversion(conv_id: int, uom_code: str, item_id: int, conv_value: float) -> Dict:
    """Update intraclass conversion for an item"""

    resource_url: str = f'/fscmRestApi/resources/11.13.18.05/unitsOfMeasure/{uom_code}/child/intraclassConversions/{conv_id}'
    request_payload: Dict = {
        'InventoryItemId': item_id,
        'IntraclassConversion': conv_value
    }
    try:
        status_code, response_payload = _invoke_api(verb='PATCH', resource_url=resource_url, payload=request_payload)
        return {
            'status_code': status_code,
            'data': {
                'conversion_id': response_payload['ConversionId'],
                'item_id': response_payload['InventoryItemId'],
                'item_number': response_payload['ItemNumber'],
                'conversion_value': response_payload['IntraclassConversion']
            }
        }
    except requests.exceptions.HTTPError as httpe:
        return {
            'status_code': httpe.response.status_code,
            'error': httpe.response.text
        }
