from zeep import Client
from zeep.transports import Transport
from zeep.plugins import HistoryPlugin

from requests import Session
from requests.auth import HTTPBasicAuth

from dotenv import load_dotenv

import os

class SoapClient:
    
    def __init__(self, wsdl: str):
        """Initialise a SOAP client with WSDL and optional username and password"""
        load_dotenv('../../.env')
        session = Session()
        user = os.environ.get('ERP_USER')
        password = os.environ.get('ERP_PASSWORD')
        session.auth = HTTPBasicAuth(user, password)
        
        self.history = HistoryPlugin() # Required for logging SOAP request/response payloads
        self.client = Client(wsdl, transport=Transport(session=session), plugins=[self.history])
    
    def get_last_request(self):
        """Returns latest SOAP request"""
        return self.history.last_sent

    def get_last_response(self):
        """Returns latest SOAP response"""
        return self.history.last_received