from reports.erp_report import ErpReportClient
from  api import erp_api_client as api

from typing import List, Dict
from argparse import ArgumentParser, Namespace

import json


def _convert_intraclass(report: dict) -> List[Dict]:
    """Calculate intraclass UOM conversion(s) and load to ERP"""

    data = report['DATA_DS']['G_1']

    if(type(data) == dict):
        data = [data]
    response_buffer = []
    error_items = [item for item in data if item['ERROR_FLAG'] == 'Y']
    for item in data:
        if item in error_items:
            continue
        else:
            item_id:str = item['INVENTORY_ITEM_ID']
            uom_code:str = item['UOM_CODE']
            inverse_flag:str = item['INVERSE']
            conversion_value:float = float(item['CONV_VALUE'])
            conversion_rate:float = float(item['CONVERSION_RATE'])

            if inverse_flag == 'Yes':
                intraclass_conv = 1 / (conversion_value * conversion_rate)
            if inverse_flag == 'No':
                intraclass_conv = conversion_value * conversion_rate
            
            # Call Intraclass Conversion Create API
            intraclass_conv_data = api.get_intraclass_conversions(uom_code, item_id)
            # Check if conversion data exists. If exists, call update API
            if intraclass_conv_data['status_code'] == 200 and intraclass_conv_data['data'] != {}:
                conversion_data:Dict = intraclass_conv_data['data']
                current_intraclass_conv:float = conversion_data['conversion_value']
                if current_intraclass_conv != intraclass_conv:
                    conversion_id:int = conversion_data['conversion_id']
                    #conversion_update_data:Dict = api.update_intraclass_conversion(conversion_id, uom_code, item_id, intraclass_conv)
            else: # If does not exist, call create API
                pass




def item_uom_conversion(item_number: str, item_class: str) -> None:
    """Create Item UOM conversion data for item number and/or class"""
    # Convert Intraclass
    # Create request payload
    template_path = 'templates/item_code.json'
    with open(template_path) as request_template:
        request = json.load(request_template)
    if item_number != None or item_class != None:
        request['reportRequest']['parameterNameValues'][0]['item'][0]['values'][0]['item'] = item_number
        request['reportRequest']['parameterNameValues'][0]['item'][1]['values'][0]['item'] = item_class
        request['reportRequest']['parameterNameValues'][0]['item'][2]['values'][0]['item'] = 'INTRACLASS'

    # Fetch Report Data
    client = ErpReportClient()
    intraclass_report = client.run_report(request)
    _convert_intraclass(intraclass_report)
    # Convert Interclass

    # Format Output


if __name__ == '__main__':

    # Parse command-line arguments
    parser = ArgumentParser()
    requried_args = parser.add_argument_group('required named arguments')
    requried_args.add_argument('-i', '--item-number', type=str,
                               help='Number of the item created in Fusion ERP. e.g. FDF-500013')
    requried_args.add_argument('-c', '--item-class', type=str,
                               help='Class of the item as defined in Fusion ERP.')
    args: Namespace = parser.parse_args()

    # Invoke conversion function
    item_uom_conversion(args.item_number, args.item_class)
