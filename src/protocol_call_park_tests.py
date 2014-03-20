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

class Park(unittest.TestCase):

    log = logging.getLogger(__name__ + ".Park")


    def test_unpark_event_from_hangup(self):
        """
        Tests if call unpark events occur when a call is being hung up while in a parking lot.
        """
        reception = "12340001"

        receptionist = Receptionists.request()
        customer     = Customers.request()

        try:
            # Make a call into the reception
            self.log.info ("Spawning a single call to the reception at " + reception)
            customer.sip_phone.Dial(reception)
            receptionist.event_stack.WaitFor(event_type="call_offer")

            call = receptionist.call_control.PickupCall()
            if call['destination'] != reception:
                self.fail ("Invalid reception ID in allocated call.")

            self.log.info ("Got call " + call['id'] + " waiting for transfer..")
            receptionist.event_stack.WaitFor(event_type="call_pickup",
                                                  call_id=call['id'])

            receptionist.call_control.ParkCall (call_id=call['id'])
            receptionist.event_stack.WaitFor(event_type="call_park", call_id=call['id'])

            customer.sip_phone.HangupAllCalls()

            receptionist.event_stack.WaitFor(event_type="call_unpark", call_id=call['id'])
            receptionist.event_stack.WaitFor(event_type="call_hangup", call_id=call['id'])

            receptionist.release()
            customer.release()
        except:
            receptionist.release()
            customer.release()
            raise


    def test_park_nonexisting_call(self):
        """
        Validates that the /call/park interface indeed returns 404 when the call is
        no longer present.
        """
        receptionist = Receptionists.request()

        try:
            # Make a call into the reception
            try:
                receptionist.call_control.ParkCall (call_id="non_existing_id")
            except Server_404:
                receptionist.release()
                return

            self.fail("Expected to see a 404 on a non-existing call!")
        except:
            receptionist.release()
            raise

    def test_explicit_park(self):
        """
        Tests the /call/park interface on a known call.
        """
        reception = "12340001"

        receptionist = Receptionists.request()
        customer     = Customers.request()

        try:
            # Make a call into the reception
            self.log.info ("Spawning a single call to the reception at " + reception)
            customer.sip_phone.Dial(reception)
            receptionist.event_stack.WaitFor(event_type="call_offer")

            call = receptionist.call_control.PickupCall()
            if call['destination'] != reception:
                self.fail ("Invalid reception ID in allocated call.")

            self.log.info ("Got call " + call['id'] + " waiting for transfer..")
            receptionist.event_stack.WaitFor(event_type="call_pickup",
                                                  call_id=call['id'])

            receptionist.call_control.ParkCall (call_id=call['id'])
            receptionist.event_stack.WaitFor(event_type="call_park", call_id=call['id'])
            receptionist.call_control.PickupCall (call_id=call['id'])
            receptionist.event_stack.WaitFor(event_type="call_unpark", call_id=call['id'])
            receptionist.event_stack.WaitFor(event_type="call_pickup", call_id=call['id'])

            receptionist.call_control.HangupCall (call_id=call['id'])

            receptionist.event_stack.WaitFor(event_type="call_hangup", call_id=call['id'])

            receptionist.release()
            customer.release()
        except:
            receptionist.release()
            customer.release()
            raise

    def test_implicit_park_on_pickup(self):
        """
        Validates that in implicit park indeed occurs when originating a new call
        while having an active call. Doesn't use the /call/park interface
        """
        reception = "12340001"
        origination_context = "2@1"
        origination_extension = "12340002"


        receptionist = Receptionists.request()
        customer     = Customers.request()
        customer2    = Customers.request()

        try:
            # Make a call into the reception
            self.log.info ("Spawning a signle call to the reception at " + reception)
            customer.sip_phone.Dial(reception)

            receptionist.event_stack.WaitFor(event_type="call_offer")

            call = receptionist.call_control.PickupCall()
            if call['destination'] != reception:
                self.fail ("Invalid reception ID in allocated call.")

            self.log.info ("Got call " + call['id'] + " waiting for transfer..")
            receptionist.event_stack.WaitFor(event_type="call_pickup",
                                                  call_id=call['id'])


            receptionist.event_stack.flush()

            self.log.info ("Spawning another call to the reception at " + reception)
            customer2.sip_phone.Dial(reception)

            receptionist.event_stack.WaitFor(event_type="call_offer")
            event = receptionist.event_stack.Get_Latest_Event(Event_Type="call_offer")

            receptionist.call_control.PickupCall(call_id=event['call']['id'])

            receptionist.event_stack.WaitFor(event_type="call_park", call_id=call['id'])

            receptionist.release()
            customer.release()
            customer2.release()
        except:
            receptionist.release()
            customer.release()
            customer2.release()
            raise

    def test_implicit_park_on_originate(self):
        """
        Validates that in implicit park indeed occurs when originating a new call
        while having an active call. Doesn't use the /call/park interface
        """
        reception = "12340001"
        origination_context = "2@1"
        origination_extension = "12340002"


        receptionist = Receptionists.request()
        customer     = Customers.request()

        try:
            # Make a call into the reception
            self.log.info ("Spawning a single call to the reception at " + reception)
            customer.sip_phone.Dial(reception)
            receptionist.event_stack.WaitFor(event_type="call_offer")

            call = receptionist.call_control.PickupCall()
            if call['destination'] != reception:
                self.fail ("Invalid reception ID in allocated call.")

            self.log.info ("Got call " + call['id'] + " waiting for transfer..")
            receptionist.event_stack.WaitFor(event_type="call_pickup",
                                                  call_id=call['id'])

            receptionist.call_control.Originate_Arbitrary(context   = origination_context,
                                                          extension = origination_extension)

            receptionist.event_stack.WaitFor(event_type="call_park", call_id=call['id'])

            receptionist.release()
            customer.release()
        except:
            receptionist.release()
            customer.release()
            raise
