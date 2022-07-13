from reports.erp_report import ErpReportClient

from argparse import ArgumentParser, Namespace

import json


def _convert_intraclass(report: dict) -> None:
    """Calculate intraclass UOM conversion(s) and load to ERP"""
    data = report['DATA_DS']['G_1']

    if(type(data) == dict):
        data = [data]
    
    error_items = [item for item in data if item['ERROR_FLAG'] == 'Y']
    for item in data:
        if item in error_items:
            pass
        else:
            item_number = item['ITEM_NUMBER']
            to_base_uom_code = item['UOM']
            from_base_uom_code = item['BASE_UOM_CODE']
            inverse_flag = item['INVERSE']
            conversion_value = float(item['CONV_VALUE'])
            conversion_rate = float(item['CONVERSION_RATE'])

            if inverse_flag == 'Yes':
                conversion_value = 1 / (conversion_value * conversion_rate)
            if inverse_flag == 'No':
                conversion_value = conversion_value * conversion_rate
            
            # Call Intraclass Convertsion Create API

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
    try:
        _convert_intraclass(intraclass_report)
    except KeyError:
        print(f'Intraclass conversions absent for item {item_number}')
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
