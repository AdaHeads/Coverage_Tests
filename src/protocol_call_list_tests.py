__author__ = 'krc'

####
#
#  Tests protocol interface documented at:
#  https://github.com/AdaHeads/call-flow-control/wiki/Protocol-Call-List
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

class List(unittest.TestCase):

    log = logging.getLogger(__name__ + ".List")

    def test_list(self):

        test_receptionist = Receptionists.request()
        test_customer = Customers.request()

        try:
            reception = "12340001"

            self.log.info ("Customer " + test_customer.username + " dials " + reception)
            test_customer.sip_phone.Dial(reception)
            test_receptionist.event_stack.WaitFor(event_type="call_offer")
            offered_call = test_receptionist.event_stack.Get_Latest_Event (Event_Type ="call_offer",
                                                                           Destination=reception)

            call_list = test_receptionist.call_control.CallList()
            try:
                call_list.locateCall (call_id=offered_call['call']['id'])
            except NotFound:
                self.fail (str(offered_call['call']['id']) + " not found in " + call_list.to_string())

            test_receptionist.release()
            test_customer.release()
        except:
            test_receptionist.release()
            test_customer.release()
            raise

