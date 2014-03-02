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

class Park(unittest.TestCase):

    log = logging.getLogger(__name__ + ".Park")

    def explicit_park(self):
        reception = "12340001"

        test_receptionist = Receptionsts.request()
        test_customer     = Customers.request()

        try:
            # Make a call into the reception
            self.log.info ("Spawning a single call to the reception at " + reception)
            test_customer.SIP_Phone.Dial(reception)
            test_receptionist.Event_Stack.WaitFor(event_type="call_offer")

            call = test_receptionist.Call_Control.PickupCall()
            if call['reception_id'] != reception_id:
                self.fail ("Invalid reception ID in allocated call.")

            self.log.info ("Got call " + call['id'] + " waiting for transfer..")
            test_receptionist.Event_Stack.WaitFor(event_type="call_pickup",
                                                  call_id=call['id'])

            test_receptionist.Call_Control.ParkCall (call_id=call['id'])
            test_receptionist.Event_Stack.WaitFor(event_type="call_park", call_id=call['id'])
            test_receptionist.Call_Control.PickupCall (call_id=call['id'])
            test_receptionist.Event_Stack.WaitFor(event_type="call_unpark", call_id=call['id'])
            test_receptionist.Event_Stack.WaitFor(event_type="call_pickup", call_id=call['id'])

            test_receptionist.Call_Control.HangupCall (call_id=call['id'])

            test_receptionist.Event_Stack.WaitFor(event_type="call_hangup", call_id=call['id'])

            test_receptionist.release()
            test_customer.release()
        except:
            test_receptionist.release()
            test_customer.release()
            raise
