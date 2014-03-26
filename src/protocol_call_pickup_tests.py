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

from static_agent_pools import Receptionists, Customers

class Pickup(unittest.TestCase):

    log = logging.getLogger(__name__ + ".Pickup")

    def test_pickup_unspecified(self):

        reception_id = 4
        reception = "1234000" + str(reception_id)

        receptionist = Receptionists.request()
        customer     = Customers.request()

        try:

            # Register the receptionists' sip client.

            # Make a call into the reception
            self.log.info ("Spawning a single call to the reception at " + reception)
            customer.sip_phone.Dial(reception)
            receptionist.event_stack.WaitFor(event_type="call_offer")


            call = receptionist.call_control.PickupCall()
            if call['reception_id'] != reception_id:
                self.fail ("Invalid reception ID in allocated call.")

            if call['assigned_to'] != receptionist.ID:
                self.fail ("Invalid receptionist ID in allocated call.")

            self.log.info ("Got call " + call['id'] + " waiting for transfer..")
            receptionist.event_stack.WaitFor(event_type="call_pickup",
                                                  call_id=call['id'])
            pickup_event = receptionist.event_stack.Get_Latest_Event (Event_Type  = "call_pickup",
                                                                      Destination = reception)
            if pickup_event['call']['assigned_to'] != receptionist.ID:
                self.fail ("Invalid receptionist ID in allocated call.")

            receptionist.call_control.HangupCall (call_id=call['id'])


            receptionist.event_stack.WaitFor(event_type="call_hangup", call_id=call['id'])

            # Check that no calls are in the call list.
            current_call_list = receptionist.call_control.CallList()
            if not current_call_list.Empty():
                self.fail("Non-empty call list: " + str (current_call_list ))
            receptionist.release()
            customer.release()
        except:
            receptionist.release()
            customer.release()
            raise

    def test_pickup_specified(self):
        reception_id = 1
        reception = "1234000" + str(reception_id)

        receptionist = Receptionists.request()
        customer     = Customers.request()

        try:

            # Register the receptionists' sip client.

            # Make a call into the reception
            self.log.info ("Spawning a single call to the reception at " + reception)
            customer.sip_phone.Dial(reception)
            receptionist.event_stack.WaitFor(event_type="call_offer")

            offered_call = receptionist.event_stack.Get_Latest_Event (Event_Type  = "call_offer",
                                                                      Destination = reception)['call']

            call = receptionist.call_control.PickupCall(offered_call['id'])

            if call['id'] != offered_call['id']:
                self.fail ("Did not get the call I was looking for.")

            if call['reception_id'] != reception_id:
                self.fail ("Invalid reception ID in allocated call.")

            if call['assigned_to'] != receptionist.ID:
                self.fail ("Invalid receptionist ID in allocated call.")

            self.log.info ("Got call " + call['id'] + " waiting for transfer..")
            receptionist.event_stack.WaitFor(event_type="call_pickup",
                                                  call_id=call['id'])

            pickup_event = receptionist.event_stack.Get_Latest_Event (Event_Type  = "call_pickup",
                                                                      Destination = reception)

            if pickup_event['call']['assigned_to'] != receptionist.ID:
                self.fail ("Invalid receptionist ID in allocated call.")

            receptionist.call_control.HangupCall (call_id=call['id'])


            receptionist.event_stack.WaitFor(event_type="call_hangup", call_id=call['id'])

            # Check that no calls are in the call list.
            current_call_list = receptionist.call_control.CallList()
            if not current_call_list.Empty():
                self.fail("Non-empty call list: " + str (current_call_list ))
            receptionist.release()
            customer.release()
        except:
            receptionist.release()
            customer.release()
            raise

    def test_pickup_nonexisting_call(self):
        receptionist = Receptionists.request()

        try:
            try:
                call = receptionist.call_control.PickupCall(call_id="non-existing-call")
            except Server_404:
                receptionist.release()
                return

            self.fail("Expected a 404 here!")

        except:
            receptionist.release()
            raise
