from reports.erp_report import ErpReportClient
from api import erp_api_client as client

from typing import List, Dict
from argparse import ArgumentParser, Namespace

from tabulate import tabulate
import json


def _convert_intraclass(conversion: Dict) -> Dict:
    """Calculate intraclass UOM conversion(s) and load to ERP"""

    item_id: str = conversion['INVENTORY_ITEM_ID']
    item_number: str = conversion['ITEM_NUMBER']
    item_desc: str = conversion['DESCRIPTION']
    uom_code: str = conversion['UOM_CODE']
    from_uom_name: str = conversion['UNIT_OF_MEASURE']
    to_uom_name: str = conversion['BASE_UOM_NAME']
    inverse_flag: str = conversion['INVERSE']
    conversion_value: float = float(conversion['CONV_VALUE'])
    conversion_rate: float = float(conversion['CONVERSION_RATE'])

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
            return {
                'item_number': item_number,
                'item_desc': item_desc,
                'conv_type': 'Intraclass',
                'from_uom': from_uom_name,
                'conversion': current_intraclass_conv,
                'to_uom': to_uom_name,
                'status': 'Success',
                'message': 'Conversion value identical; skipped'
            }
        else:
            conversion_id: int = conversion_data['conversion_id']
            conversion_update_data: Dict = \
                client.update_intraclass_conversion(
                    conversion_id, uom_code, item_id, intraclass_conv)
            if conversion_update_data['status_code'] == 200:
                return {
                    'item_number': item_number,
                    'item_desc': item_desc,
                    'conv_type': 'Intraclass',
                    'from_uom': from_uom_name,
                    'conversion': conversion_update_data['data']['conversion_value'],
                    'to_uom': to_uom_name,
                    'status': 'Success'
                }
            else:
                return {
                    'item_number': item_number,
                    'item_desc': item_desc,
                    'conv_type': 'Intraclass',
                    'from_uom': from_uom_name,
                    'conversion': intraclass_conv,
                    'to_uom': to_uom_name,
                    'status': 'Error',
                    'error_message': conversion_update_data['error']
                }
    else:  # If conversion does not exist, call create API
        conversion_create_data = \
            client.create_intraclass_conversion(
                uom_code, item_id, intraclass_conv)
        if conversion_create_data['status_code'] == 201:
            return {
                'item_number': item_number,
                'item_desc': item_desc,
                'conv_type': 'Intraclass',
                'from_uom': from_uom_name,
                'conversion': conversion_create_data['data']['conversion_value'],
                'to_uom': to_uom_name,
                'status': 'Success'
            }
        else:
            return {
                'item_number': item_number,
                'item_desc': item_desc,
                'conv_type': 'Intraclass',
                'from_uom': from_uom_name,
                'conversion': intraclass_conv,
                'to_uom': to_uom_name,
                'status': 'Error',
                'error_message': conversion_create_data['error']
            }


def _convert_interclass(conversion: Dict) -> List[Dict]:
    """Calculate interclass UOM conversion(s) and load to ERP"""

    item_id: str = conversion['INVENTORY_ITEM_ID']
    item_number: str = conversion['ITEM_NUMBER']
    item_desc: str = conversion['DESCRIPTION']
    from_uom_code: str = conversion['FROM_UOM_CODE']
    from_uom_name: str = conversion['FROM_UOM_NAME']
    to_uom_code: str = conversion['TO_UOM_CODE']
    to_uom_name: str = conversion['TO_UOM_NAME']
    primary_uom_class: str = conversion['ITEM_PRIMARY_UOM_CLASS_CODE']
    conversion_value: float = float(conversion['UOM_CONV_VALUE'])
    from_conveersion_rate: float = float(conversion['FROM_CONV_RATE'])
    to_conversion_rate: float = float(conversion['TO_CONV_RATE'])
    to_uom_class: str = conversion['TO_CLASS_NAME']

    interclass_conversion = from_conveersion_rate / \
        (conversion_value * to_conversion_rate)

    # Check if conversion exists
    interclass_conv_data: Dict = \
        client.get_interclass_conversions(
            primary_uom_class, item_id, from_uom_code, to_uom_code)

    if interclass_conv_data['status_code'] == 200 and \
            interclass_conv_data['data'] != {}:
        conversion_data: Dict = interclass_conv_data['data']
        current_interclass_conv: float = conversion_data['conversion_value']

        # If conversion exists and conversion value equals new conversion value,
        # skip conversion item
        if current_interclass_conv == interclass_conversion:
            return {
                'item_number': item_number,
                'item_desc': item_desc,
                'conv_type': 'Interclass',
                'from_uom': from_uom_name,
                'conversion': current_interclass_conv,
                'to_uom': to_uom_name,
                'status': 'Success',
                'message': 'Conversion value identical; skipped'
            }
        else:
            conversion_id = conversion_data['conversion_id']
            conversion_update_data: Dict = \
                client.update_interclass_conversion(
                    primary_uom_class, conversion_id, from_uom_code, to_uom_code, interclass_conversion)
            if conversion_update_data['status_code'] == 200:
                return {
                    'item_number': item_number,
                    'item_desc': item_desc,
                    'conv_type': 'Interclass',
                    'from_uom': from_uom_name,
                    'conversion': conversion_update_data['data']['conversion_value'],
                    'to_uom': to_uom_name,
                    'status': 'Success'
                }
            else:
                return {
                    'item_number': item_number,
                    'item_desc': item_desc,
                    'conv_type': 'Interclass',
                    'from_uom': from_uom_name,
                    'conversion': interclass_conversion,
                    'to_uom': to_uom_name,
                    'status': 'Error',
                    'error_message': conversion_update_data['error']
                }
    else:
        conversion_create_data: Dict = \
            client.create_interclass_conversion(
                to_uom_class, item_number, from_uom_code, to_uom_code, interclass_conversion)
        if conversion_create_data['status_code'] == 200:
            return {
                'item_number': item_number,
                'item_desc': item_desc,
                'conv_type': 'Interclass',
                'from_uom': from_uom_name,
                'conversion': conversion_create_data['data']['conversion_value'],
                'to_uom': to_uom_name,
                'status': 'Success'
            }
        else:
            return {
                'item_number': item_number,
                'item_desc': item_desc,
                'conv_type': 'Interclass',
                'from_uom': from_uom_name,
                'conversion': interclass_conversion,
                'to_uom': to_uom_name,
                'status': 'Error',
                'error_message': conversion_create_data['error']
            }


def item_uom_conversion(item_number: str, item_class: str) -> Dict:
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

    client = ErpReportClient()
    # Convert Intraclass
    intraclass_report = client.run_report(request)
    intraclass_conversions: List[Dict] = []
    try:
        intraclass_data: List[Dict] = intraclass_report['DATA_DS']['G_1']
        for item in intraclass_data:
            if item['ERROR_FLAG'] == 'Y':  # Skip items with data error
                intraclass_conversions.append({
                    'item_number': item['ITEM_NUMBER'],
                    'item_desc': item['DESCRIPTION'],
                    'conv_type': 'Intraclass',
                    'from_uom': item['UNIT_OF_MEASURE'],
                    'conversion': None,
                    'to_uom': item['BASE_UOM_NAME'],
                    'status': 'Error',
                    'status': f'Intraclass conversion excluded as the UOM Class {item["CLASS_NAME"]} does not belong to Item Primary UOM Class which is {item["ITEM_PRIMARY_UOM_CLASS"]}'
                })
            else:
                conversion_data = _convert_intraclass(item)
                intraclass_conversions.append(conversion_data)
    except KeyError:
        pass

    # Convert Interclass
    request['reportRequest']['parameterNameValues'][0]['item'][2]['values'][0]['item'] = 'INTERCLASS'
    interclass_report = client.run_report(request)
    interclass_conversions: List[Dict] = []
    try:
        interclass_data: List[Dict] = interclass_report['DATA_DS']['G_2']
        for item in interclass_data:
            conversion_data = _convert_interclass(item)
            interclass_conversions.append(conversion_data)
    except KeyError:
        pass
    
    return {
        'intraclass_conversions': intraclass_conversions,
        'interclass_conversions': interclass_conversions
    }

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
    conversion_data: Dict = item_uom_conversion(args.item_number, args.item_class)

    # Format Output
    table_headers_success = ['Item Number', 'Description', 'Conversion Type',
                             'From Base UOM', 'Conversion', 'To Base UOM', 'Message']
    table_headers_error = ['Item Number', 'Description', 'Conversion Type',
                           'From Base UOM', 'Conversion', 'To Base UOM', 'Error Message']
    
    intraclass_conversions: List = conversion_data['intraclass_conversions']
    intraclass_conv_success: List = [[item['item_number'], item['item_desc'], item['conv_type'], item['from_uom'],
                                      item['conversion'], item['to_uom'], item['message']] for item in intraclass_conversions if item['status'] == 'Success']
    intraclass_conv_error: List = [[item['item_number'], item['item_desc'], item['conv_type'], item['from_uom'],
                                    item['conversion'], item['to_uom'], item['status']] for item in intraclass_conversions if item['status'] == 'Error']

    interclass_conversions: List = conversion_data['interclass_conversions']
    interclass_conv_success: List = [[item['item_number'], item['item_desc'], item['conv_type'], item['from_uom'],
                                      item['conversion'], item['to_uom'], item['message']] for item in interclass_conversions if item['status'] == 'Success']
    interclass_conv_error: List = [[item['item_number'], item['item_desc'], item['conv_type'], item['from_uom'],
                                    item['conversion'], item['to_uom'], item['status']] for item in interclass_conversions if item['status'] == 'Error']

    print('--Intraclass Conversions--')
    print(tabulate(intraclass_conv_success,
          headers=table_headers_success, tablefmt="grid"))
    print(tabulate(intraclass_conv_error,
          headers=table_headers_error, tablefmt="grid"))
    print('--Interclass Conversions--')
    print(tabulate(interclass_conv_success,
          headers=table_headers_success, tablefmt="grid"))
    print(tabulate(interclass_conv_error,
          headers=table_headers_error, tablefmt="grid"))

