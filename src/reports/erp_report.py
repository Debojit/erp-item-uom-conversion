from dotenv import load_dotenv

from .soap_client import SoapClient

import xmltodict
import os

class ErpReportClient(SoapClient):

    def __init__(self):
        """Initalise ERP report SOAP client"""
        load_dotenv('../.env')
        wsdl:str = 'https://' + os.getenv('erp.host') + ':' + os.getenv('erp.port') + '/xmlpserver/services/ExternalReportWSSService?WSDL'
        user:str = os.getenv('erp.user', None)
        password:str = os.getenv('erp.password', None)
        SoapClient.__init__(self, wsdl, user, password)

    def run_report(self, payload: dict) -> dict:
        """Run ERP report for payload and return XML response"""
        response = self.client.service.runReport(**payload)
        return xmltodict.parse(response.reportBytes)