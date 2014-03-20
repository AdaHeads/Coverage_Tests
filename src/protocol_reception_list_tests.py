__author__ = 'krc'

####
#
#  Tests protocol interface documented at:
#  https://github.com/AdaHeads/DatabaseServers/wiki/Server-Reception
#

import config
import logging


# Exceptions
from database_reception import Server_404, Database_Reception

try:
    import unittest2 as unittest
except ImportError:
    import unittest

class Reception_List(unittest.TestCase):

    log = logging.getLogger(__name__)
    server = Database_Reception(uri=config.reception_server_uri,authtoken=config.global_token)

    def test_CORS_headers_present(self):
        headers, body = self.server.Request ("/nonexistingpath", exceptions=False)
        assert 'access-control-allow-origin' in headers or 'Access-Control-Allow-Origin' in headers

        reception_id = 1

        self.log.info ("Looking up recption " + str(reception_id))
        headers, body = self.server.Request(self.server.Protocol.single + str(reception_id))
        assert 'access-control-allow-origin' in headers or 'Access-Control-Allow-Origin' in headers

    def test_nonexisting_uri(self):
        try:
            reception = self.server.Request ("/nonexistingpath")
        except Server_404:
            return

        self.fail("Expected 404 here.")

    def test_found(self):
        reception_id = 1

        self.log.info ("Looking up recption " + str(reception_id))
        reception = self.server.Single (Reception=reception_id)

    def test_not_found(self):
        reception_id = -1

        self.log.info ("Looking up recption " + str(reception_id))
        try:
            reception = self.server.Single (Reception=reception_id)
        except Server_404:
            return

        self.fail("Expected 404 here.")
