import httplib2
import logging
from peer_utils import PeerList
from call_utils import CallList

class Server_Unavailable(Exception):
    pass

class callFlowServer:
    
    class protocol:
        callList   = "/call/list"
        callQueue  = "/call/queue"
        callPickup = "/call/pickup"
        peerList   = "/debug/peer/list"
        tokenParam = "?token=" 

    uri       = None 
    http      = httplib2.Http(".cache")
    authtoken = None

    def __init__ (self, uri, authtoken):
        self.uri       = uri
        self.authtoken = authtoken


    def TokenValid(self):
        path = self.protocol.callList + self.protocol.tokenParam + self.authtoken
        headers, body = self.Request(path)
        return headers['status'] == '200'

    def Request (self, path, method="GET", encoded_params=""):
        try:
            uri_path = self.uri + path + self.protocol.tokenParam + self.authtoken + encoded_params
            
            resp, content = self.http.request(uri_path , method, headers={'Origin' : self.uri})
        except:
            logging.error("call-flow server unreachable!")
            raise Server_Unavailable (uri_path)
        
        return resp, content

    def PickupCall (self, call_id=None):
        if call_id == None:
            return self.Request(self.protocol.callPickup, "POST")
        else:
            return self.Request(self.protocol.callPickup, "POST", "&call_id="+call_id)

    def CallList (self):
        headers, body = self.Request(self.protocol.callList)
        if headers['status'] != '200':
            logging.error ("Expected 200 here, got: " + headers['status'])
            raise Server_Unavailable (path)
        return CallList().fromJSON(body)

    def peerList(self):
        path = self.protocol.peerList + self.protocol.tokenParam + self.authtoken
        headers, body = self.Request(path)

        if headers['status'] != '200':
            logging.error ("Expected 200 here, got: " + headers['status'])
            raise Server_Unavailable (path)

        return PeerList().fromJSON(body)
    