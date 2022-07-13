from reports.erp_report import ErpReportClient

from argparse import ArgumentParser

if __name__ == '__main__':

    # Parse command-line arguments
    parser = ArgumentParser()
    parser.add_argument('-i', '--item-number', type=str, help='Number of the item created in Fusion ERP. e.g. FDF-500013')
    parser.add_argument('-c', '--item-class', type=str, help='Class of the item as defined in Fusion ERP.')
    args = parser.parse_args()

    # Fetch Report Data
    
    # Convert Intraclass

    # Convert Interclass

    # Format Output