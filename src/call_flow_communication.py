# -*- coding: utf-8 -*-
#
# Interface to the Call-Flow-Control server: https://github.com/AdaHeads/Call-Flow-Control

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

class Server_400(Exception):
    pass

class Unspecified_Server_Error(Exception):
    pass

class callFlowServer:

    class protocol:
        call_namespace  = "/call"
        callHangup      = call_namespace + "/hangup"
        callList        = call_namespace + "/list"
        callQueue       = call_namespace + "/queue"
        callPark        = call_namespace + "/park"
        callOriginate   = call_namespace + "/originate"
        callPickup      = call_namespace + "/pickup"
        callTransfer    = call_namespace + "/transfer"
        callOffer       = call_namespace + "/offer"
        callOfferAccept = callOffer + "/accept"
        callOfferWait   = callOffer + "/wait"
        peerList        = "/debug/peer/list"
        tokenParam      = "?token="

    log       = None
    uri       = None
    http      = httplib2.Http(".cache")
    authtoken = None

    def __init__ (self, uri, authtoken):
        self.log = logging.getLogger(self.__class__.__name__)
        self.uri       = uri
        self.authtoken = authtoken

    def TokenValid(self):
        path = self.protocol.callList + self.protocol.tokenParam + self.authtoken
        headers, body = self.Request(path)
        return headers['status'] == '200'

    def Request (self, path, method="GET", params={}):

        uri_path = self.uri + path + self.protocol.tokenParam + self.authtoken

        self.log.debug(method + " " + uri_path)
        try:


            if method == 'POST':
                headers, body = self.http.request(uri_path , method,
                                                  headers={'Origin' : self.uri,
                                                           'Content-Type' : 'application/x-www-form-urlencoded'},
                                                  body=urlencode(params))
            else:
                headers, body = self.http.request(uri_path , method, headers={'Origin' : self.uri})

        except:
            self.log.error("call-flow server unreachable!")
            raise Server_Unavailable (uri_path)

        if headers['status'] == '404':
            raise Server_404 (method + " " + path + " Response:" + body)

        elif headers['status'] == '401':
            raise Server_401 (method + " " + path + " Response:" + body)

        elif headers['status'] == '400':
            raise Server_400 (method + " " + path + " Response:" + body)

        elif headers['status'] != '200':
            raise Unspecified_Server_Error (method + " " + path + " Response:" + body)

        return headers, body

    def PickupCall (self, call_id=None):
        if call_id == None:
            headers, body = self.Request(self.protocol.callPickup, "POST")
        else:
            headers, body = self.Request(self.protocol.callPickup, "POST", params={'call_id' : call_id})

        return json.loads (body)

    def Originate_Arbitrary (self, context, extension):
        headers, body = self.Request(self.protocol.callOriginate, "POST",
                                     params={'context' : context, 'extension' : extension})

        return json.loads (body)

    def Originate_Specific (self, context, phone_id):
        headers, body = self.Request(self.protocol.callOriginate, "POST",
                                     params={'context' : context, 'phone_id' : phone_id})

        return json.loads (body)

    def TransferCall (self, source, destination):
        headers, body = self.Request(self.protocol.callTransfer, "POST",
                                     params={'source' : source, 'destination' : destination})

        return json.loads (body)

    def HangupCall (self, call_id):
        # https://github.com/AdaHeads/call-flow-control/wiki/Protocol-Call-Hangup

        try:
            headers, body = self.Request(self.protocol.callHangup, "POST", params={'call_id' : call_id})

            return json.loads (body)
        except Server_404:
            self.log.error ("Hanging up " + str (call_id) + " didn't succeed.  We assume that the call was terminated by other means.")

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

        return CallList().fromJSON(body)

    def CallQueue (self):
        headers, body = self.Request(self.protocol.callQueue)

        return CallList().fromJSON(body)

    def peerList(self):
        headers, body = self.Request(self.protocol.peerList)

        return PeerList().fromJSON(body)

