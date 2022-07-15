from reports.erp_report import ErpReportClient
from api import erp_api_client as client

from typing import List, Dict
from argparse import ArgumentParser, Namespace

import json


def _convert_intraclass(report: dict) -> List[Dict]:
    """Calculate intraclass UOM conversion(s) and load to ERP"""

    data = report['DATA_DS']['G_1']

    if(type(data) == dict):
        data = [data]

    response_buffer:List[Dict] = []
    error_items:List = [item for item in data if item['ERROR_FLAG'] == 'Y']
    for item in data:
        if item in error_items:
            continue # TODO: Load to response buffer
        else:
            item_id: str = item['INVENTORY_ITEM_ID']
            item_number: str = item['ITEM_NUMBER']
            item_desc: str = item['DESCRIPTION']
            uom_code: str = item['UOM_CODE']
            from_uom_name: str = item['UNIT_OF_MEASURE']
            to_uom_name: str = item['BASE_UOM_NAME']
            inverse_flag: str = item['INVERSE']
            conversion_value: float = float(item['CONV_VALUE'])
            conversion_rate: float = float(item['CONVERSION_RATE'])

            if inverse_flag == 'Yes':
                intraclass_conv = 1 / (conversion_value * conversion_rate)
            if inverse_flag == 'No':
                intraclass_conv = conversion_value * conversion_rate

            # Fetch Intraclass conversions for item
            intraclass_conv_data = \
                client.get_intraclass_conversions(uom_code, item_id)

            # Check if conversion data exists.
            if intraclass_conv_data['status_code'] == 200 \
                and intraclass_conv_data['data'] != {}:
                conversion_data: Dict = intraclass_conv_data['data']
                current_intraclass_conv: float = conversion_data['conversion_value']

                # If conversion data exists and is identical to existing conversion data,
                # skip to next conversion item
                if current_intraclass_conv == intraclass_conv:
                    response_buffer.append({
                            'item_number': item_number,
                            'item_desc': item_desc,
                            'conv_type': 'Intraclass',
                            'from_uom': from_uom_name,
                            'conversion': current_intraclass_conv,
                            'to_uom': to_uom_name,
                            'status': 'Conversion Value Unchanged; Skipping'
                        })
                    continue
                else:
                    conversion_id: int = conversion_data['conversion_id']
                    conversion_update_data: Dict = \
                        client.update_intraclass_conversion(conversion_id, uom_code, item_id, intraclass_conv)
                    if conversion_update_data['status_code'] == 200:
                        response_buffer.append({
                            'item_number': item_number,
                            'item_desc': item_desc,
                            'conv_type': 'Intraclass',
                            'from_uom': from_uom_name,
                            'conversion': conversion_update_data['data']['conversion_value'],
                            'to_uom': to_uom_name,
                            'status': 'Success'
                        })
                    else:
                        response_buffer.append({
                            'item_number': item_number,
                            'item_desc': item_desc,
                            'conv_type': 'Intraclass',
                            'from_uom': from_uom_name,
                            'conversion': intraclass_conv,
                            'to_uom': to_uom_name,
                            'status': 'Error',
                            'error_message': conversion_update_data['error']
                        })
            else:  # If conversion does not exist, call create API
                conversion_create_data = \
                    client.create_intraclass_conversion(uom_code, item_id, intraclass_conv)
                if conversion_create_data['status_code'] == 201:
                    response_buffer.append({
                            'item_number': item_number,
                            'item_desc': item_desc,
                            'conv_type': 'Intraclass',
                            'from_uom': from_uom_name,
                            'conversion': conversion_create_data['data']['conversion_value'],
                            'to_uom': to_uom_name,
                            'status': 'Success'
                        })
                else:
                    response_buffer.append({
                            'item_number': item_number,
                            'item_desc': item_desc,
                            'conv_type': 'Intraclass',
                            'from_uom': from_uom_name,
                            'conversion': intraclass_conv,
                            'to_uom': to_uom_name,
                            'status': 'Error',
                            'error_message': conversion_create_data['error']
                        })
    return response_buffer


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
