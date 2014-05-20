__author__ = 'krc'

import config
import logging
import time

# Exceptions
from call_flow_communication import Server_404, Server_400
from call_utils import NotFound

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from static_agent_pools import Receptionists, Customers

class Originate(unittest.TestCase):
    """
    Tests for the Origination interface on the call-flow server.
    """

    log = logging.getLogger(__name__ + ".Originate")

    def test_origination_to_known_number(self):
        receptionist = Receptionists.request()

        try:
            contact_id   = "2"
            reception_id = "1"
            extension    = "39990141"

            self.log.info ("Receptionist " + receptionist.username + " dials extension" + extension + \
                           " in context " + contact_id + "@" + reception_id)

            response = receptionist.dial(contact_id   = contact_id,
                                         reception_id = reception_id,
                                         extension    = extension)


            self.log.info ("Receptionist " + receptionist.username + " Originated new call with ID " +
                           str(response['call']['id']))
            #TODO Check that the call is picked up or that in any other way confirm that the origination
            # was indedd a success.

            receptionist.release()
        except:
            receptionist.release()
            raise

    def origination_to_arbitrary_number(self):

        receptionist = Receptionists.request()

        try:
            context = "2@2"
            extension = "12340002"

            self.log.info ("Receptionist " + receptionist.username + " dials " + extension + " in context " + context)

            receptionist.call_control.Originate_Arbitrary(context=context, extension=extension)
            #TODO Check that the call is picked up or that in any other way confirm that the origination
            # was indedd a success.

            receptionist.release()
        except:
            receptionist.release()
            raise

    def origination_to_known_peer(self):

        receptionist = Receptionists.request()
        customer     = Customers.request()

        try:
            context = "2@2"
            extension = "port" + str(customer.sip_port);

            self.log.info ("Receptionist " + receptionist.username + " dials " + extension + " in context " + context)

            receptionist.call_control.Originate_Arbitrary(context=context, extension=extension)
            #TODO Check that the call is picked up or that in any other way confirm that the origination
            # was indedd a success.
            time.sleep(10);

            receptionist.release()
            customer.release()
        except:
            receptionist.release()
            customer.release()
            raise

    ##TODO; missing parameters.

    def test_origination_to_forbidden_number(self):
        receptionist = Receptionists.request()

        try:
            contact_id   = "2"
            reception_id = "1"
            extension    = "x"

            try:
                response = receptionist.dial(contact_id   = contact_id,
                                             reception_id = reception_id,
                                             extension    = extension)
            except Server_400:
                receptionist.release()
                return

            self.fail ("Expected 400 on on origination request!")
        except:
            receptionist.release()
            raise

    def test_origination_to_invalid_phone_id(self):
        receptionist = Receptionists.request()

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
