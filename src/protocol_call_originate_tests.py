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

from static_agent_pools import Receptionsts, Customers

class Originate(unittest.TestCase):
    """
    Tests for the Origination interface on the call-flow server.
    """

    log = logging.getLogger(__name__ + ".Originate")

    def test_origination_to_known_number(self):
        receptionist = Receptionsts.request()

        try:
            context = "2@1"
            phone_id = "2"

            self.log.info ("Receptionist " + receptionist.username + " dials phone id" + phone_id + \
                           " in context " + context)

            receptionist.call_control.Originate_Specific(context="2@1", phone_id=phone_id)
            #TODO Check that the call is picked up or that in any other way confirm that the origination
            # was indedd a success.

            receptionist.release()
        except:
            receptionist.release()
            raise

    def test_origination_to_arbitrary_number(self):

        receptionist = Receptionsts.request()

        try:
            context = "2@1"
            extension = "12340002"

            self.log.info ("Receptionist " + receptionist.username + " dials " + extension + " in context " + context)

            receptionist.call_control.Originate_Arbitrary(context=context, extension=extension)
            #TODO Check that the call is picked up or that in any other way confirm that the origination
            # was indedd a success.

            receptionist.release()
        except:
            receptionist.release()
            raise

    def test_origination_to_forbidden_number(self):
        self.fail ("Not implemented")

    def test_origination_to_invalid_phone_id(self):
        receptionist = Receptionsts.request()

        try:
            context = "2@1"
            phone_id = "1"

            self.log.info ("Receptionist " + receptionist.username + " dials phone id" + phone_id + \
                           " in context " + context)

            try:
                receptionist.call_control.Originate_Specific(context="2@1", phone_id=phone_id)
            except Server_404:
                receptionist.release()
                return
            #TODO Check that the call is picked up or that in any other way confirm that the origination
            # was indedd a success.

            self.fail ("Expected 404 on on origination request!")
        except:
            receptionist.release()
            raise