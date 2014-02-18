import httplib2
from urllib import urlencode
import logging
import json
from peer_utils import PeerList
from call_utils import CallList

class Server_Unavailable(Exception):
    pass

class Server_404(Exception):
    pass

class Server_401(Exception):
    pass

class callFlowServer:
    
    class protocol:
        callHangup = "/call/hangup"
        callList   = "/call/list"
        callQueue  = "/call/queue"
        callPark   = "/call/park"
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

    def Request (self, path, method="GET", params={}):
        logging.info(method + " " + path + " " + urlencode(params))
        try:
            uri_path = self.uri + path + self.protocol.tokenParam + self.authtoken
            
            if method == 'POST':
                headers, body = self.http.request(uri_path , method, headers={'Origin' : self.uri,
                                                                              'Content-Type' : 'application/x-www-form-urlencoded'}, body=urlencode(params))
            else:
                headers, body = self.http.request(uri_path , method, headers={'Origin' : self.uri})
                
        except:
            logging.error("call-flow server unreachable!")
            raise Server_Unavailable (uri_path)
        if headers['status'] == '404':
            raise Server_404 (method + " " + path + " Response:" + body)
        elif headers['status'] == '401':
            raise Server_401 (method + " " + path + " Response:" + body)
        
        return headers, body

    def PickupCall (self, call_id=None):
        if call_id == None:
            headers, body = self.Request(self.protocol.callPickup, "POST")
        else:
            headers, body = self.Request(self.protocol.callPickup, "POST", params={'call_id' : call_id})
            
        return json.loads (body)

    def HangupCall (self, call_id):
        headers, body = self.Request(self.protocol.callHangup, "POST", params={'call_id' : call_id})
            
        return json.loads (body)

    def HangupAllCalls (self):
        
        for call in self.CallList().Calls():
            self.HangupCall(call['id'])

    def ParkCall (self, call_id=None):
        if call_id == None:
            headers, body = self.Request(self.protocol.callPark, "POST")
        else:
            headers, body = self.Request(self.protocol.callPark, "POST", params={'call_id' : call_id})
            
        return json.loads (body)

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
    