from reports.erp_report import ErpReportClient

from argparse import ArgumentParser, Namespace

import json


def item_uom_conversion(item_number: str, item_class: str) -> None:
    """Create Item UOM conversion data for item number and/or class"""
    # Convert Intraclass
    # Create request payload
    template_path = 'templates/item_code.json'
    with open(template_path) as request_template:
        request = json.load(request_template)
    if args.item_number != None or args.item_class != None:
        request['reportRequest']['parameterNameValues'][0]['item'][0]['values'][0]['item'] = item_number
        request['reportRequest']['parameterNameValues'][0]['item'][1]['values'][0]['item'] = item_class
        request['reportRequest']['parameterNameValues'][0]['item'][2]['values'][0]['item'] = 'INTRACLASS'

    # Fetch Report Data
    client = ErpReportClient()
    intraclass_report = client.run_report(request)
    
    # Convert Interclass

    # Format Output


if __name__ == '__main__':

    # Parse command-line arguments
    parser = ArgumentParser()
    requried_args = parser.add_argument_group('required named arguments')
    requried_args.add_argument('-i', '--item-number', type=str,
                               help='Number of the item created in Fusion ERP. e.g. FDF-500013')
    requried_args.add_argument(
        '-c', '--item-class', type=str, help='Class of the item as defined in Fusion ERP.')
    args:Namespace = parser.parse_args()

    # Invoke conversion function
    item_uom_conversion(args.item_number, args.item_class)
