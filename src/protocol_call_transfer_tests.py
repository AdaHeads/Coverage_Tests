__author__ = 'krc'

import logging

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from pprint import pformat

from static_agent_pools import Receptionists, Customers

class Transfer(unittest.TestCase):

    log = logging.getLogger(__name__ + ".Transfer")

    def test_transfer(self):
        pass

        receptionist = Receptionists.request()
        self.log.info("Got receptionist " + receptionist.to_string())
        customer     = Customers.request()
        callee       = Customers.request()

        try:
            reception = "12340001"

            callee.sip_phone.disable_auto_answer()

            customer.sip_phone.Dial(reception)

            self.log.info ("Waiting for the call to be received by the PBX.")
            receptionist.event_stack.WaitFor(event_type="call_offer")
            offer_event = receptionist.event_stack.Get_Latest_Event (Event_Type  = "call_offer",
                                                                     Destination = reception)

            call = receptionist.call_control.PickupCall (call_id=offer_event['call']['id'])

            self.log.info ("got call: " + str(call['id']))

            receptionist.event_stack.WaitFor(event_type="call_pickup")
            receptionist.event_stack.flush()

            outbound_call = receptionist.call_control.Originate_Arbitrary (context="@2", extension="port"+callee.sip_port)

            self.log.info ("Outbound call id: " + str(outbound_call['call']['id']))

            receptionist.event_stack.WaitFor(event_type="call_pickup")

            originate_event = receptionist.event_stack.Get_Latest_Event (Event_Type  = "call_pickup")

            self.assertEquals(originate_event['call']['b_leg'], outbound_call['call']['id'])

            receptionist.call_control.TransferCall (source=originate_event['call']['id'], destination=call['id'])
            receptionist.event_stack.WaitFor(event_type="call_transfer")

            self.log.info ("Test success. Cleaning up.")

            receptionist.release()
            customer.release()
            callee.release()
        except:
            self.log.error("Event stack: " + pformat (receptionist.event_stack.dump_stack ()))
            receptionist.release()
            customer.release()
            callee.release()
            raise
