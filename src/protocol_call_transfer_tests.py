__author__ = 'krc'

import config
import logging


# Exceptions
from call_flow_communication import Server_404
from call_utils import NotFound

try:
    import unittest2 as unittest
except ImportError:
    import unittest

class Transfer(unittest.TestCase):

    log = logging.getLogger(__name__ + ".Transfer")

    def test_transfer(self):
        pass
        #self.fail ("Not implemented")
