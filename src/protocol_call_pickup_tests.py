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

class Pickup(unittest.TestCase):

    log = logging.getLogger(__name__ + ".Pickup")

    def test_pickup_unspecified(self):

        reception_id = 1
        reception = "1234000" + str(reception_id)

        test_receptionist = Receptionsts.request()
        test_customer     = Customers.request()

        try:

            # Register the receptionists' sip client.

            # Make a call into the reception
            self.log.info ("Spawning a single call to the reception at " + reception)
            test_customer.sip_phone.Dial(reception)
            test_receptionist.event_stack.WaitFor(event_type="call_offer")

            call = test_receptionist.call_control.PickupCall()
            if call['reception_id'] != reception_id:
                self.fail ("Invalid reception ID in allocated call.")

            self.log.info ("Got call " + call['id'] + " waiting for transfer..")
            test_receptionist.event_stack.WaitFor(event_type="call_pickup",
                                                  call_id=call['id'])

            test_receptionist.call_control.HangupCall (call_id=call['id'])


            test_receptionist.event_stack.WaitFor(event_type="call_hangup", call_id=call['id'])

            # Check that no calls are in the call list.
            current_call_list = test_receptionist.call_control.CallList()
            if not current_call_list.Empty():
                self.fail("Non-empty call list: " + str (current_call_list ))
            test_receptionist.release()
            test_customer.release()
        except:
            test_receptionist.release()
            test_customer.release()
            raise

    def test_pickup_specified(self):
        self.fail ("Not implemented.")

    def test_pickup_nonexisting_call(self):
        self.fail ("Not implemented.")