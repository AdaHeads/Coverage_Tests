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

class Queue(unittest.TestCase):

    log = logging.getLogger(__name__ + ".Queue")

    def validate_queue_empty(self, from_perspective):
        self.log.info ("Checking if the call queue is empty.")

        current_call_list = from_perspective.call_control.CallQueue()

        if not current_call_list.Empty():
            self.log.error(current_call_list.to_string())
            self.fail("Non-empty call list: ")

    def validate_queue_not_empty(self, from_perspective):
        self.log.info ("Checking if the call queue is non-empty.")

        current_call_list = from_perspective.call_control.CallQueue()

        if current_call_list.Empty():
            self.log.error(current_call_list.to_string())
            self.fail("Empty call list: ")

    def test_queue_leave_event_from_pickup(self):

        receptionist = Receptionists.request()
        self.log.info("Got receptionst " + receptionist.to_string())
        customer     = Customers.request()

        try:
            reception = "12340002"

            self.validate_queue_empty(from_perspective=receptionist)

            customer.sip_phone.Dial(reception)

            self.log.info ("Wating for the call to be received by the PBX.")
            receptionist.event_stack.WaitFor(event_type="call_offer")
            offer_event = receptionist.event_stack.Get_Latest_Event (Event_Type  = "call_offer",
                                                                     Destination = reception)

            self.log.info ("Wating for the call to be queued.")
            receptionist.event_stack.WaitFor(event_type="queue_join", call_id=offer_event['call']['id'])

            self.log.info ("Got queue_join event, checking queue interface.")
            current_call_list = receptionist.call_control.CallQueue()
            self.validate_queue_not_empty(from_perspective=receptionist)

            receptionist.call_control.PickupCall (call_id=offer_event['call']['id'])

            self.log.info ("Wating for queue_leave.")
            receptionist.event_stack.WaitFor(event_type="queue_leave")

            customer.sip_phone.HangupAllCalls()

            self.log.info ("Wating for call_hangup.")
            receptionist.event_stack.WaitFor(event_type="call_hangup")

            self.log.info ("Checking if the call is now absent from the call list.")
            self.validate_queue_empty(from_perspective=receptionist)

            self.log.info ("Test success. Cleaning up.")

            receptionist.release()
            customer.release()
        except:
            receptionist.release()
            customer.release()
            raise

    def test_queue_leave_event_from_hangup(self):
        """
        Tests if call unpark events occur when a call is being hung up while in a queue.
        """
        receptionist = Receptionists.request()
        customer     = Customers.request()

        try:
            reception = "12340002"

            self.validate_queue_empty(from_perspective=receptionist)

            customer.sip_phone.Dial(reception)

            self.log.info ("Wating for the call to be received by the PBX.")
            receptionist.event_stack.WaitFor(event_type="call_offer")

            self.log.info ("Wating for the call to be queued.")
            receptionist.event_stack.WaitFor(event_type="queue_join")

            self.log.info ("Got queue_join event, checking queue interface.")
            current_call_list = receptionist.call_control.CallQueue()
            self.validate_queue_not_empty(from_perspective=receptionist)

            self.log.info ("A call is found in the queue. Hanging up and checking if it disappears from queue.")
            customer.sip_phone.HangupAllCalls()

            self.log.info ("Wating for queue_leave.")
            receptionist.event_stack.WaitFor(event_type="queue_leave")

            self.log.info ("Wating for call_hangup.")
            receptionist.event_stack.WaitFor(event_type="call_hangup")

            self.log.info ("Checking if the call is now absent from the call list.")
            self.validate_queue_empty(from_perspective=receptionist)

            self.log.info ("Test success. Cleaning up.")

            receptionist.release()
            customer.release()
        except:
            receptionist.release()
            customer.release()
            raise

