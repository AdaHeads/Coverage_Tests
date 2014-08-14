# -*- coding: utf-8 -*-

import config
import datetime
from random import randint
from management_server_manager import *
from sip_profiles import agent1100 as any_agent

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class ManagementReception(unittest.TestCase):
    management_server = ManagementServer(uri=config.management_server_uri, auth_token=any_agent.authtoken)

    def log_info(self, message):
        logging.info(str(self.__class__.__name__) + message)

    def __init__(self, *args, **kwargs):
        super(ManagementReception, self).__init__(*args, **kwargs)

    # noinspection PyPep8
    receptionAttributeSchema = {'type': 'object',
                                'required': True,
                                'properties':
                                    {'shortgreeting':
                                         {'type': 'string'},
                                     'addresses':
                                         {'type': 'array'}}}

    # noinspection PyPep8
    receptionSchema = {'type': 'object',
                       'required': True,
                       'properties':
                           {'id':
                                {'type': 'integer',
                                 'required': True,
                                 'minimum': 0},
                            'organization_id':
                                {'type': 'integer',
                                 'required': True,
                                 'minimum': 0},
                            'full_name':
                                {'type': 'string',
                                 'required': True},
                            'extradatauri':
                                {'type': ['string', 'null'],
                                 'required': True},
                            'enabled':
                                {'type': 'boolean',
                                 'required': True},
                            'number':
                                {'type': 'string',
                                 'required': True,},
                            'attributes': receptionAttributeSchema}}

    # noinspection PyPep8
    receptionListSchema = {'type': 'object',
                           'required': True,
                           'properties':
                               {'receptions':
                                    {'type': 'array',
                                     'required': True,
                                     'items': receptionSchema}}}

    def test_get_reception_1(self):
        reception_id = 1
        headers, body = self.management_server.get_reception(reception_id)
        json_body = json.loads(body)
        schema = self.receptionSchema
        verify_schema(schema, json_body)

    def test_get_reception_list(self):
        headers, body = self.management_server.get_reception_list()
        json_body = json.loads(body)
        schema = self.receptionListSchema
        verify_schema(schema, json_body)

    def test_create_reception(self):
        organization_id = 1
        random_number = datetime.datetime.now().strftime("%s") + str(randint(1000000, 9999999))
        reception = {
            'full_name': 'TestMania',
            'attributes': {},
            'enabled': False,
            'number': random_number
        }
        headers, body = self.management_server.create_reception(organization_id, reception)
        json_body = json.loads(body)
        try:
            reception_id = json_body['id']

            self.management_server.delete_reception(reception_id)
        except Exception, e:
            self.fail('Creating a new reception did not give the expected output. Response: "' +
                      str(json_body) + '" Error' + str(e))

    def test_get_organizations_reception(self):
        organization_id = 1
        headers, body = self.management_server.get_organizations_receptions(organization_id)
        json_body = json.loads(body)
        schema = self.receptionListSchema
        verify_schema(schema, json_body)
