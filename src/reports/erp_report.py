from soap_client import SoapClient

import xmltodict
class ErpReportClient(SoapClient):

    def __init__(self, wsdl: str, user: str, password: str):
        SoapClient.__init__(self, wsdl, user, password)

    def run_report(self, payload: dict) -> dict:
        """Run ERP report for payload and return XML response"""
        response = self.client.service.runReport(**payload)
        return xmltodict.parse(response.reportBytes)