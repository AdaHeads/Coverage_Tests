# -*- coding: utf-8 -*-

import httplib2
import logging
import json

from jsonschema import Draft3Validator
from jsonschema.exceptions import SchemaError, ValidationError, UnknownType


def verify_schema(schema, instance):
    try:
        validator = Draft3Validator(schema)
        validator.validate(instance)

    except ValidationError as e:
        print 'Data did not comply with json schema. Schema: "' + str(schema) + '"' + \
              ' Response: "' + str(instance) + '"'
        raise e

    except (SchemaError, UnknownType, TypeError) as e:
        print 'Error in the json schema. Schema: "' + str(schema) + '"'
        raise e


class ServerUnavailable(Exception):
    pass


class ServerBadStatus(Exception):
    pass


class Server401(ServerBadStatus):
    pass


class Server403(ServerBadStatus):
    pass


class Server404(ServerBadStatus):
    pass


class Server500(ServerBadStatus):
    pass


class ManagementServer():
    class Protocol:
        # noinspection PyPep8
        contactTypeUrl  = "/contacttypes"
        dialplanUrl     = "/dialplan"
        receptionUrl    = "/reception"
        contactUrl      = "/contact"
        organizationUrl = "/organization"
        userUrl         = "/user"
        tokenParam      = "?token="

    http = httplib2.Http(".cache")

    def __init__(self, uri, auth_token):
        self.log = logging.getLogger(self.__class__.__name__)
        self.uri = uri
        self.auth_token = auth_token

    def request(self, path, method="GET", params=None):
        if not params:
            params = {}
        self.log.info(method + " " + path + " " + json.dumps(params))
        uri_path = self.uri + path + self.Protocol.tokenParam + self.auth_token

        try:
            if method in ('POST', 'PUT'):
                headers, body = self.http.request(uri_path,
                                                  method,
                                                  headers={'Origin': self.uri},
                                                  body=json.dumps(params))
            else:
                headers, body = self.http.request(uri_path, method, headers={'Origin': self.uri})

        except ValueError:
            logging.error('Server unreachable! ' + str(ValueError))
            raise ServerUnavailable(uri_path)
        if headers['status'] == '401':
            raise Server401('401 Unauthorized ' + method + ' ' + path + ' Response:' + body)

        elif headers['status'] == '403':
            raise Server403('403 Forbidden ' + method + ' ' + path + ' Response:' + body)

        elif headers['status'] == '404':
            raise Server404('404 Not Found ' + method + ' ' + path + ' Response:' + body)

        elif headers['status'] == '500':
            raise Server500('500 Internal Server Error ' + method + ' ' + path + ' Response:' + body)

        elif headers['status'] != '200':
            raise ServerBadStatus(headers['status'] + ' ' + method + ' ' + path + ' Response:' + body)

        return headers, body

######################## Reception ##############################
    def get_reception(self, reception_id):
        return self.request(self.Protocol.receptionUrl + "/" + str(reception_id), "GET")

    def get_reception_list(self):
        return self.request(self.Protocol.receptionUrl, "GET")

    def create_reception(self, organization_id, reception):
        """
        Creates a new reception

        @type organization_id: int
        @param organization_id: An integer

        @type reception: dict
        @param reception: The reception object

        @rtype: headers, body
        @return: Returns the headers and the body of the response
        """
        path = self.Protocol.organizationUrl + "/" + str(organization_id) + self.Protocol.receptionUrl
        return self.request(path, "PUT", reception)

    def delete_reception(self, reception_id):
        path = self.Protocol.receptionUrl + "/" + str(reception_id)
        return self.request(path, "DELETE")

    def get_organizations_receptions(self, organization_id):
        path = self.Protocol.organizationUrl + "/" + str(organization_id) + self.Protocol.receptionUrl
        return self.request(path, "GET")