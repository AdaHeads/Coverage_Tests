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

    def test_transfer_inbound_is_parked(self):
        pass

        receptionist = Receptionists.request()
        self.log.info("Got receptionist " + receptionist.to_string())
        customer     = Customers.request()
        callee       = Customers.request()

        try:
            reception    = "12340003"
            reception_id = "1"
            contact_id   = "2"

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

            self.log.info ("Receptionist parks the inbound call.")
            receptionist.call_control.ParkCall(call_id=call ['id'])
            receptionist.event_stack.WaitFor(event_type="call_park", call_id=call ['id'])
            receptionist.sip_phone.wait_for_hangup()

            outbound_call = receptionist.call_control.Originate_Arbitrary (reception_id = reception_id,
                                                                           contact_id   = contact_id,
                                                                           extension    ="port"+callee.sip_port)

            self.log.info ("Outbound call id: " + str(outbound_call['call']['id']))

            callee.sip_phone.wait_for_call()
            callee.sip_phone.pickup_call()

            receptionist.event_stack.WaitFor(event_type="call_pickup")

            originate_event = receptionist.event_stack.Get_Latest_Event (Event_Type  = "call_pickup")

            self.assertEquals(originate_event['call']['b_leg'], outbound_call['call']['id'])

            outbound_call = originate_event['call']

            # Validate that the object matches the expected.
            self.assertEquals(int(reception_id), outbound_call['reception_id'])
            self.assertEquals(receptionist.ID, outbound_call['assigned_to'])
            self.assertEquals(receptionist.username, outbound_call['caller_id'])

            receptionist.call_control.TransferCall (source=outbound_call['id'], destination=call['id'])
            receptionist.event_stack.WaitFor(event_type="call_transfer")

            self.log.info ("Waiting for the receptionist phone to hang up.")
            receptionist.sip_phone.wait_for_hangup()

            self.log.info ("The customer hangs up.")
            customer.sip_phone.HangupAllCalls()
            customer.sip_phone.wait_for_hangup()

            self.log.info ("Waiting for the callee phone to also hang up.")
            callee.sip_phone.wait_for_hangup()

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

    def test_transfer_outbound_is_parked(self):
        pass

        receptionist = Receptionists.request()
        self.log.info("Got receptionist " + receptionist.to_string())
        customer     = Customers.request()
        callee       = Customers.request()

        try:
            reception = "12340003"
            reception_id = "1"
            contact_id   = "2"

            callee.sip_phone.disable_auto_answer()

            customer.sip_phone.Dial(reception)

            self.log.info ("Waiting for the call to be received by the PBX.")
            receptionist.event_stack.WaitFor(event_type="call_offer")
            offer_event = receptionist.event_stack.Get_Latest_Event (Event_Type  = "call_offer",
                                                                     Destination = reception)

            inbound_call = receptionist.call_control.PickupCall (call_id=offer_event['call']['id'])

            self.log.info ("got call: " + str(inbound_call ['id']))

            receptionist.event_stack.WaitFor(event_type="call_pickup", call_id=inbound_call ['id'])

            self.log.info ("Receptionist parks the inbound call.")
            receptionist.call_control.ParkCall(call_id=inbound_call ['id'])
            receptionist.event_stack.WaitFor(event_type="call_park", call_id=inbound_call ['id'])
            receptionist.sip_phone.wait_for_hangup()

            outbound_channel = receptionist.call_control.Originate_Arbitrary (reception_id = reception_id,
                                                                              contact_id   = contact_id,
                                                                              extension    ="port"+callee.sip_port)

            self.log.info ("Outbound channel: " + str(outbound_channel['call']['id']))

            receptionist.event_stack.flush()
            callee.sip_phone.wait_for_call()
            callee.sip_phone.pickup_call()

            receptionist.event_stack.WaitFor(event_type="call_pickup")
            originate_event = receptionist.event_stack.Get_Latest_Event (Event_Type  = "call_pickup")

            self.assertEquals(originate_event['call']['b_leg'], outbound_channel['call']['id'])

            outbound_call = originate_event['call']

            # Validate that the object matches the expected.
            self.assertEquals(int(reception_id), outbound_call['reception_id'])
            self.assertEquals(receptionist.ID, outbound_call['assigned_to'])
            self.assertEquals(receptionist.username, outbound_call['caller_id'])

            self.log.info ("Receptionist parks the outbound call.")
            outbound_channel = receptionist.call_control.ParkCall(call_id=outbound_call['id'])
            receptionist.event_stack.WaitFor(event_type="call_park", call_id=outbound_call['id'])
            receptionist.sip_phone.wait_for_hangup()

            receptionist.event_stack.flush()
            self.log.info ("Receptionist picks up the inbound call again.")
            inbound_call = receptionist.call_control.PickupCall (call_id=inbound_call['id'])
            receptionist.event_stack.WaitFor(event_type="call_pickup", call_id=inbound_call ['id'])

            self.log.info ("Receptionist transfers call " + str(inbound_call['id']) +
                                                   " to " + str(outbound_call['id']))

            receptionist.call_control.TransferCall (source      = inbound_call['id'],
                                                    destination = outbound_call['id'])
            receptionist.event_stack.WaitFor(event_type="call_transfer")

            self.log.info ("Waiting for the receptionist phone to hang up.")
            receptionist.sip_phone.wait_for_hangup()

            self.log.info ("The customer hangs up.")
            customer.sip_phone.HangupAllCalls()
            customer.sip_phone.wait_for_hangup()

            self.log.info ("Waiting for the callee phone to also hang up.")
            callee.sip_phone.wait_for_hangup()

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
