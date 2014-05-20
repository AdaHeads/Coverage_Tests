__author__ = 'krc'

####
#
#  Tests protocol interface documented at:
#  https://github.com/AdaHeads/call-flow-control/wiki/Protocol-Call-Hangup
#

import config
import logging

# Exceptions
from call_flow_communication import Server_404
from call_utils import NotFound

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from static_agent_pools import Receptionists, Customers

class Hangup(unittest.TestCase):

    log = logging.getLogger(__name__ + ".Hangup")

    # Test for the presence of hangup events and call interface.
    def test_event(self):
        test_receptionist = Receptionists.request()
        test_customer = Customers.request()

        try:
            reception = "12340001"

            self.log.info ("Customer " + test_customer.username + " dials " + reception)
            test_customer.sip_phone.Dial(reception)
            test_receptionist.event_stack.WaitFor(event_type="call_offer")

            test_customer.sip_phone.HangupAllCalls()
            test_receptionist.event_stack.WaitFor(event_type="call_hangup")

            test_receptionist.release()
            test_customer.release()
        except:
            test_receptionist.release()
            test_customer.release()
            raise

    def test_interface_call_found(self):
        test_receptionist = Receptionists.request()
        test_customer = Customers.request()

        try:
            reception = "12340003"

            self.log.info ("Customer " + test_customer.username + " dials " + reception)
            test_customer.sip_phone.Dial(reception)
            test_receptionist.event_stack.WaitFor(event_type="call_offer")

            test_customer.sip_phone.HangupAllCalls()
            test_receptionist.event_stack.WaitFor(event_type="call_hangup")
            test_receptionist.event_stack.flush()

            test_customer.sip_phone.Dial(reception)
            test_receptionist.event_stack.WaitFor(event_type="call_offer")
            self.log.info ("Extracting latest event.")
            offered_call = test_receptionist.event_stack.Get_Latest_Event (Event_Type ="call_offer",
                                                                           Destination=reception)['call']
            self.log.info  ("Got offered call " + str(offered_call['id']) + " - picking it up.")
            test_receptionist.pickup_call_wait_for_lock(call_id=offered_call['id'])

            test_receptionist.event_stack.WaitFor(event_type="call_pickup")
            test_receptionist.hang_up(call_id=offered_call['id'])
            test_receptionist.event_stack.WaitFor(event_type="call_hangup")

            test_receptionist.release()
            test_customer.release()
        except:
            test_receptionist.release()
            test_customer.release()
            raise

    def test_interface_call_not_found(self):
        test_receptionist = Receptionists.request()

        try:
            reception = "12340004"


            try:
                test_receptionist.hang_up(call_id="null")
            except Server_404:
                pass # Expected

            test_receptionist.release()
        except:
            test_receptionist.release()
            raise
