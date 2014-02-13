import config

from call_flow_communication import callFlowServer

try:
    import unittest2 as unittest
except ImportError:
    import unittest

class TechnicalStuff(unittest.TestCase):
    
    cfs = callFlowServer(uri=config.call_flow_server_uri, authtoken=config.authtoken)
    
    def test_token_valid(self):
        assert self.cfs.TokenValid()

    # Make sure that the cors headers are present
    def test_CORS_present(self):
        headers, body = self.cfs.Request(self.cfs.protocol.peerList) 
        assert 'access-control-allow-origin' in headers or 'Access-Control-Allow-Origin' in headers
    
    def test_404_OK (self):
        headers, body = self.cfs.Request("/abyss_nonexting") 
        
        assert headers['status'] == '404'

    def test_JSON_Content_Type (self):
        headers, body = self.cfs.Request("/abyss_nonexting") 
        
        if 'application/json' not in headers['content-type']:
            self.fail ("Expected JSON content type, got: " +  headers['content-type'])

