import httplib2
from urllib import urlencode
import logging
import json as JSON

class Server_Unavailable(Exception):
    pass

class Server_404(Exception):
    pass

class Server_401(Exception):
    pass

class Database_Reception:

    class Protocol:
        Single                   = "/reception/"
        List                     = Single + "list"
        Authentication_Parameter = "?token="

    uri       = None
    http      = httplib2.Http(".cache")
    authtoken = None

    def __init__ (self, uri, authtoken):
        self.uri       = uri
        self.authtoken = authtoken

    def Request (self, path, method="GET", params={}):
        logging.info(method + " " + path + " " + urlencode(params))
        uri_path = "<not declared yet>"
        try:
            uri_path = self.uri + path + self.Protocol.Authentication_Parameter + self.authtoken

            if method == 'POST':
                headers, body = self.http.request(uri_path , method, headers={'Origin' : self.uri,
                                                                              'Content-Type' : 'application/x-www-form-urlencoded'}, body=urlencode(params))
            else:
                headers, body = self.http.request(uri_path , method, headers={'Origin' : self.uri})

        except:
            logging.error("Reception JSON-database gateway unreachable!")
            raise Server_Unavailable (uri_path)
        if headers['status'] == '404':
            raise Server_404 (method + " " + path + " Response:" + body)
        elif headers['status'] == '401':
            raise Server_401 (method + " " + path + " Response:" + body)

        return headers, body

    def List (self):
        headers, body = self.Request(self.Protocol.List)
        return JSON.loads (body)

    def Single (self, Reception):
        headers, body = self.Request(self.Protocol.Single + str(Reception))
        return JSON.loads (body)
