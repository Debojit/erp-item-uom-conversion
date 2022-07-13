from dotenv import load_dotenv

from soap_client import SoapClient

import xmltodict

import os

class ErpReportClient(SoapClient):

    def __init__(self):
        """Initalise ERP report SOAP client"""
        load_dotenv('../../.env')
        wsdl:str = 'https://' + os.environ.get('ERP_HOST') + ':' + os.environ.get('ERP_PORT')
        user:str = os.environ.get('erp.user') if 'erp.user' in os.environ else None
        password:str = os.environ.get('erp.password') if 'erp.password' in os.environ else None
        SoapClient.__init__(self, wsdl, user, password)

    def run_report(self, payload: dict) -> dict:
        """Run ERP report for payload and return XML response"""
        response = self.client.service.runReport(**payload)
        return xmltodict.parse(response.reportBytes)