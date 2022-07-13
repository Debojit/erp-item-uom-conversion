from zeep import Client
from zeep.transports import Transport
from zeep.plugins import HistoryPlugin

from requests import Session
from requests.auth import HTTPBasicAuth

class SoapClient:
    
    def __init__(self, wsdl: str, user:str = None, password:str = None):
        """Initialise a SOAP client with WSDL and optional username and password"""
        session:Session = Session()

        self.history:HistoryPlugin = HistoryPlugin()
        
        if user != None and password != None:
            session.auth:HTTPBasicAuth = HTTPBasicAuth(user, password)
            self.client:Client = Client(wsdl, transport = Transport(session = session), plugins = [self.history])
        else:
            self.client:Client = Client(wsdl, plugins = [self.history])
    
    def get_last_request(self):
        """Returns latest SOAP request"""
        return self.history.last_sent

    def get_last_response(self):
        """Returns latest SOAP response"""
        return self.history.last_received