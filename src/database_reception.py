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

    log       = None
    uri       = None
    http      = httplib2.Http(".cache")
    authentication_token = None

    class Protocol:

        token_parameter  = "?token="

        def __init__(self):
            pass

    def __init__(self, uri, authtoken):
        self.log = logging.getLogger(self.__class__.__name__)
        self.uri = uri
        self.authentication_token = authtoken

    def token_valid(self):
        headers, body = self.Request("/reception/"+str(reception_id))
        return headers['status'] == '200'

    def Request(self, path, method="GET", body=None, exceptions=True):

        if not body:
            body = {}

        uri_path = self.uri + path + self.Protocol.token_parameter + self.authentication_token

        self.log.debug(method + " " + uri_path)

        try:
            if method in ['POST', 'PUT']:
                headers, response_body = self.http.request(uri_path, method,
                                                  headers={'Origin'       :  self.uri,
                                                           'Content-Type' : 'application/json'},
                                                  body=JSON.dumps(body))
            else:
                headers, response_body = self.http.request(uri_path, method, headers={'Origin' : self.uri})

        except:
            logging.error("Contact JSON-database gateway unreachable!")
            raise Server_Unavailable (uri_path)
        if exceptions:
            if headers['status'] == '404':
                raise Server_404 (method + " " + path + " Response:" + response_body)
            elif headers['status'] == '401':
                raise Server_401 (method + " " + path + " Response:" + response_body)

        return headers, response_body

    def list (self):
        headers, body = self.Request(self.Protocol.list)
        return JSON.loads(body)

    def get (self, reception_id):
        headers, body = self.Request("/reception/"+str(reception_id))
        return JSON.loads(body)

    def calendar_events (self, reception_id):
        headers, body = self.Request("/reception/"+str(reception_id)+"/calendar")
        return JSON.loads(body)

    def calendar_event (self, reception_id, event_id):
        headers, body = self.Request("/reception/"+str(reception_id)+"/calendar/event/" + str(event_id))
        return JSON.loads(body)

    def calendar_event_delete (self, reception_id, event_id):
        headers, body = self.Request("/reception/"+str(reception_id)+"/calendar/event/" + str(event_id), method="DELETE")
        return JSON.loads(body)

    def calendar_event_update (self, reception_id, event_id, event):
        headers, body = self.Request("/reception/"+str(reception_id)+"/calendar/event/" + str(event_id), method="PUT", body=event)
        return JSON.loads(body)

    def calendar_event_create (self,reception_id, event):
        headers, body = self.Request("/reception/"+str(reception_id)+"/calendar/event", method="POST", body=event)
        return JSON.loads(body)
