from zeep import Client
from zeep.transports import Transport
from zeep.plugins import HistoryPlugin

from requests import Session
from requests.auth import HTTPBasicAuth

from abc import ABC, abstractmethod

class SoapClient(ABC):
    
    def __init__(self, wsdl: str, user: str, password: str):
        """Initialise a SOAP client with WSDL and optional username and password"""
        if user.strip() != '' and user != None and password.strip() != '' and password != None:
            session = Session()
            session.auth = HTTPBasicAuth(user, password)
        
        self.history = HistoryPlugin() #Required for logging SOAP request/response payloads
        self.client = Client(wsdl, transport=Transport(session=session), plugins=[self.history])
    
    def get_last_request(self):
        """Returns latest SOAP request"""
        return self.history.last_sent

    def get_last_response(self):
        """Returns latest SOAP response"""
        return self.history.last_received