import httplib2
from urllib import urlencode
import logging
import json as JSON


class Server_Unavailable(Exception):
    pass


class Server_404(Exception):
    pass


class Server_403(Exception):
    pass

class Server_401(Exception):
    pass

class Server_400(Exception):
    pass

class Server_Error(Exception):
    pass

class Database_Message:

    class Protocol:

        message_base     = "/message"
        draft_base       = message_base + "/draft"
        send_message     = message_base + "/send"
        list_messages    = message_base + "/list"
        show_message     = message_base + "/"
        list_drafts      = draft_base   + "/list"
        single_draft     = draft_base   + "/"
        create_draft     = draft_base   + "/create"
        invalid_resource = "/nonexiting"
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

    def Request(self, path, method="GET", exceptions=True, body=None):

        if not body:
            body = {}

        uri_path = self.uri + path + self.Protocol.token_parameter + self.authentication_token

        self.log.debug(method + " " + uri_path)

        try:
            if method in ['POST', 'PUT']:
                headers, body = self.http.request(uri_path, method,
                                                  headers={'Origin'       :  self.uri,
                                                           'Content-Type' : 'application/x-www-form-urlencoded'},
                                                  body=JSON.dumps(body))
            else:
                headers, body = self.http.request(uri_path, method, headers={'Origin' : self.uri})

        except:
            logging.error("Reception JSON-database gateway unreachable!")

            raise Server_Unavailable (uri_path)

        assert 'access-control-allow-origin' in headers or 'Access-Control-Allow-Origin' in headers

        if exceptions:
            if headers['status'] == '404':
                raise Server_404 (method + " " + path + " Response:" + body)
            elif headers['status'] == '401':
                raise Server_401 (method + " " + path + " Response:" + body)
            elif headers['status'] == '403':
                raise Server_403 (method + " " + path + " Response:" + body)
            elif headers['status'] == '400':
                raise Server_400 (method + " " + path + " Response:" + body)
            elif headers['status'] != '200':
                raise Server_Error (method + " " + path + " Response:" + headers['status']+ " : " + body)

        return headers, body

    def message_list (self):
        headers, body = self.Request(self.Protocol.list_messages)
        return JSON.loads(body)

    def non_exisiting_path (self, exceptions=True):
        headers, body = self.Request(self.Protocol.invalid_resource, exceptions=exceptions)
        return JSON.loads(body)

    def message (self, message_id):
        headers, body = self.Request(self.Protocol.show_message + str(message_id))
        return JSON.loads(body)

    def message_send (self, message):
        headers, body = self.Request(self.Protocol.send_message, method="POST", body=message)
        return JSON.loads(body)

    def draft_list (self):
        headers, body = self.Request(self.Protocol.list_drafts)
        return JSON.loads(body)

    def draft_single (self, draft_id):
        headers, body = self.Request(self.Protocol.single_draft + str(draft_id))
        return JSON.loads(body)

    def draft_create (self, draft):
        headers, body = self.Request(self.Protocol.create_draft, method="POST", body=draft)
        return JSON.loads(body)

    def draft_remove (self, draft_id):
        headers, body = self.Request(self.Protocol.single_draft + str(draft_id), method="DELETE")
        return JSON.loads(body)

    def draft_update (self, draft_id, draft):
        headers, body = self.Request(self.Protocol.single_draft + str(draft_id), method="PUT", body=draft)
        return JSON.loads(body)
