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

    api_url = 'https://' + os.getenv('erp.host') + ':' + os.getenv('erp.port') + resource_url
    response = requests.request(method=verb, url=api_url, auth=HTTPBasicAuth(os.getenv('erp.user'),
                                                                    os.getenv('erp.password')), headers={'Content-Type': 'application/json'}, data=payload)
    response.raise_for_status()
    return (response.status_code, response.json())


def get_intraclass_conversions(uom_code: str, item_id: str) -> Optional[Dict]:
    """Get interclass conversion for UOM Code and Item ID"""

    resource_url: str = f'/fscmRestApi/resources/11.13.18.05/unitsOfMeasure/{uom_code}/child/intraclassConversions?q=InventoryItemId={item_id}&onlyData=true'
    try:
        status_code, response_payload = _invoke_api(verb='GET', resource_url=resource_url)
        return {
            'status_code': status_code,
            'data': response_payload['items']
        }
    except requests.exceptions.HTTPError as httpe:
        return {
            'status_code': httpe.response.status_code,
            'error': httpe.response.text
        }
