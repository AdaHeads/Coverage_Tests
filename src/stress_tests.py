__author__ = 'krc'

import config
import logging


# Exceptions
from call_flow_communication import Server_404, Server_400
from call_utils import NotFound
import time

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from static_agent_pools import Receptionists, Customers

class Stress(unittest.TestCase):
    """
    Tests for the Origination interface on the call-flow server.
    """

    log = logging.getLogger(__name__ + ".Stress")

    def test_origination_to_known_number(self):
        receptionist_list = []
        customer_list     = []

        for i in range (0,2):
            receptionist_list.append(Receptionists.request())

        for i in range (0,10):
            customer_list.append(Customers.request())

        try:

            time.sleep (3.0)

            for customer in customer_list:
                customer.dial ("12340001")
                time.sleep(0.02)

            for customer in customer_list:
                customer.dial ("12340001")
                time.sleep(0.02)

            for customer in customer_list:
                customer.dial ("12340001")
                time.sleep(0.02)

            for customer in customer_list:
                customer.dial ("12340001")
                time.sleep(0.02)

            time.sleep(4.0)
            self.log.info ("Current number of calls: " + str(receptionist_list[0].call_control.CallList().NumberOfCalls()))

            self.log.info ("Current number of calls: " + str(receptionist_list[0].call_control.CallList().NumberOfCalls()))
            try:
                while not receptionist_list[0].call_control.CallList().Empty():
                    for receptionist in receptionist_list:
                        call = receptionist.call_control.PickupCall()
                        receptionist.call_control.HangupCall(call['id'])
            except Server_404:
                pass

            time.sleep (1.0)
            self.log.info ("Current number of calls: " + str(receptionist_list[0].call_control.CallList().NumberOfCalls()))

            for item in receptionist_list:
                item.release()

            for item in customer_list:
                item.release()

        except:
            for item in receptionist_list:
                item.release()

            for item in customer_list:
                item.release()
            raise
