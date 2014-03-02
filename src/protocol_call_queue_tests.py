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

class Queue(unittest.TestCase):

    log = logging.getLogger(__name__ + ".Queue")

    def test_queue_interface(self):

        receptionist = Receptionsts.request()
        self.log.info("Got receptionst " + receptionist.to_string())
        customer     = Customers.request()
        self.log.info("Got customer " + customer.to_string())

        try:
            reception = "12340002"

            self.log.info ("Checking if the call queue is initially empty.")
            current_call_list = receptionist.call_control.CallQueue()
            if not current_call_list.Empty():
                self.log.error(current_call_list.to_string())
                self.fail("non-empty call list: ")

            # Register the customers' sip client.
            self.log.info ("Dialling " + reception + ".")
            customer.sip_phone.Dial(reception)

            self.log.info ("Wating for the call to be received by the PBX.")
            receptionist.event_stack.WaitFor(event_type="call_offer")

            self.log.info ("Wating for the call to be queued.")
            receptionist.event_stack.WaitFor(event_type="queue_join")

            self.log.info ("Got queue_join event, checking queue interface.")
            # Check that there is a call in the queue.
            current_call_list = receptionist.call_control.CallQueue()
            if current_call_list.Empty():
                self.log.error(current_call_list.to_string())
                self.fail("Empty call list: " + str(current_call_list))

            self.log.info ("Call found in queue. Hanging up and checking if it disappears from queue.")

            customer.sip_phone.HangupAllCalls()
            self.log.info ("Wating for queue_leave.")
            receptionist.event_stack.WaitFor(event_type="queue_leave")
            self.log.info ("Wating for call_hangup.")
            receptionist.event_stack.WaitFor(event_type="call_hangup")

            self.log.info ("Checking if the call is now absent from the call list.")
            current_call_list = receptionist.call_control.CallList()
            if not current_call_list.Empty():
                self.fail("Found a non-empty call list: " + current_call_list.to_string())

            self.log.info ("Test success. Cleaning up.")

            receptionist.release()
            customer.release()
        except:
            receptionist.release()
            customer.release()
            raise
