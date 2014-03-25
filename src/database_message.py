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


class Database_Message:

    class Protocol:

        reception_base   = "/message"
        send             = reception_base + "/send"
        token_parameter  = "?token="

        def __init__(self):
            pass

    log       = None
    uri       = None
    http      = httplib2.Http(".cache")
    authentication_token = None

    def __init__(self, uri, authtoken):
        self.log = logging.getLogger(self.__class__.__name__)
        self.uri = uri
        self.authentication_token = authtoken

    def token_valid(self):
        path = self.Protocol.reception_base
        headers, body = self.Request(path)
        return headers['status'] == '200'

    def Request(self, path, method="GET", params=None, exceptions=True):

        if not params:
            params = {}

        uri_path = self.uri + path + self.Protocol.token_parameter + self.authentication_token

        self.log.debug(method + " " + uri_path)

        try:
            if method == 'POST':
                headers, body = self.http.request(uri_path, method,
                                                  headers={'Origin'       :  self.uri,
                                                           'Content-Type' : 'application/x-www-form-urlencoded'},
                                                  body=urlencode(params))
            else:
                headers, body = self.http.request(uri_path, method, headers={'Origin' : self.uri})

        except:
            logging.error("Reception JSON-database gateway unreachable!")
            raise Server_Unavailable (uri_path)
        if exceptions:
            if headers['status'] == '404':
                raise Server_404 (method + " " + path + " Response:" + body)
            elif headers['status'] == '401':
                raise Server_401 (method + " " + path + " Response:" + body)

        return headers, body

    def List (self):
        headers, body = self.Request(self.Protocol.list)
        return JSON.loads(body)

    def Single (self, Reception):
        headers, body = self.Request(self.Protocol.single + str(Reception))
        return JSON.loads(body)

