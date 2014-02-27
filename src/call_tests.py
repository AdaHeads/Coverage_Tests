import logging
import websocket
import os
import sys
import json
import thread
import time
import httplib2
import pprint
import config

from agent_pool import AgentPool, Agent, AgentConfigs, CustomerConfigs

from static_agent_pools import Receptionsts, Customers

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from pprint import pformat
from subprocess import Popen, PIPE

# Local classes.
from event_stack import EventListenerThread
from sip_utils import SipAgent, SipAccount
from call_flow_communication import callFlowServer, Server_404

# Sip accounts
from sip_profiles import agent1100, agent1101, agent1102, agent1103, agent1107, agent1108, agent1109

class EventTests(unittest.TestCase):

    def test_call_offer(self):
        pass

class BasicStuff(unittest.TestCase):

    # Makes a call and then asserts that there is a
    # call in the call queue.
    def test_call_presence(self):

        test_receptionist = Receptionsts.Aquire()

        try:
            reception = "12340001"

            current_call_list = test_receptionist.Call_Control.CallList()
            if not current_call_list.Empty():
                logging.error(current_call_list.toString())
                self.fail("non-empty call list: ")

            # Register the customers' sip client.
            test_receptionist.SIP_Phone.Dial(reception)
            test_receptionist.Event_Stack.WaitFor(event_type="call_offer")

            # Check that there is a call in the queue.
            current_call_list = test_receptionist.Call_Control.CallList()
            if current_call_list.Empty():
                logging.error(current_call_list.toString())
                self.fail("Empty call list: " + str(current_call_list))

            test_receptionist.SIP_Phone.HangupAllCalls()
            test_receptionist.Event_Stack.WaitFor(event_type="call_hangup")

            # Check that the call is now absent from the call list.
            current_call_list = test_receptionist.Call_Control.CallList()
            if not current_call_list.Empty():
                self.fail("Found a non-empty call list: " + current_call_list.toString())
            Receptionsts.Release(test_receptionist)
        except:
            Receptionsts.Release(test_receptionist)
            raise

    # Makes a call and then tries to pick it up from the server.
    #
    def test_unspecified_call_pickup(self):

        reception_id = 1
        reception = "1234000" + str(reception_id)

        test_receptionist = Receptionsts.Aquire()
        test_customer     = Customers.Aquire()

        try:

            # Register the receptionists' sip client.

            # Make a call into the reception
            logging.info ("Spawning a single call to the reception at " + reception)
            test_customer.SIP_Phone.Dial(reception)
            test_receptionist.Event_Stack.WaitFor(event_type="call_offer")

            call = test_receptionist.Call_Control.PickupCall()
            if call['reception_id'] != reception_id:
                self.fail ("Invalid reception ID in allocated call.")

            logging.info ("Got call " + call['id'] + " waiting for transfer..")
            test_receptionist.Event_Stack.WaitFor(event_type="call_pickup",
                                                  call_id=call['id'])

            test_receptionist.Call_Control.HangupCall (call_id=call['id'])


            test_receptionist.Event_Stack.WaitFor(event_type="call_hangup", call_id=call['id'])

            # Check that no calls are in the call list.
            current_call_list = test_receptionist.Call_Control.CallList()
            if not current_call_list.Empty():
                self.fail("Non-empty call list: " + str (current_call_list ))
            test_receptionist.Release()
            test_customer.Release()
        except:
            test_receptionist.Release()
            test_customer.Release()
            raise


    # Makes a call and then asserts that there is a
    # call in the call queue.
    def test_pickup_and_park (self):
        reception_id = 1
        reception = "1234000" + str(reception_id)

        test_receptionist = Receptionsts.Aquire()
        test_customer     = Customers.Aquire()

        try:

            # Register the receptionists' sip client.

            # Make a call into the reception
            logging.info ("Spawning a single call to the reception at " + reception)
            test_customer.SIP_Phone.Dial(reception)
            test_receptionist.Event_Stack.WaitFor(event_type="call_offer")

            call = test_receptionist.Call_Control.PickupCall()
            if call['reception_id'] != reception_id:
                self.fail ("Invalid reception ID in allocated call.")

            logging.info ("Got call " + call['id'] + " waiting for transfer..")
            test_receptionist.Event_Stack.WaitFor(event_type="call_pickup",
                                                  call_id=call['id'])

            test_receptionist.Call_Control.ParkCall (call_id=call['id'])
            test_receptionist.Event_Stack.WaitFor(event_type="call_park", call_id=call['id'])
            test_receptionist.Call_Control.PickupCall (call_id=call['id'])
            test_receptionist.Event_Stack.WaitFor(event_type="call_unpark", call_id=call['id'])
            test_receptionist.Event_Stack.WaitFor(event_type="call_pickup", call_id=call['id'])

            test_receptionist.Call_Control.HangupCall (call_id=call['id'])

            test_receptionist.Event_Stack.WaitFor(event_type="call_hangup", call_id=call['id'])

            test_receptionist.Release()
            test_customer.Release()
        except:
            test_receptionist.Release()
            test_customer.Release()
            raise

    def t_pickup_and_park (self):
        try:



            Receptionsts.Release(test_receptionist)
            Customers.Release(test_customer)
        except:
            Receptionsts.Release(test_receptionist)
            Customers.Release(test_customer)
            raise

# Below is just testing code. Everything interesting (and automatable) will be located in the TestCase classes.
if __name__ == "__main__":
    ap = AgentPool(AgentConfigs)

    try:
        a1 = ap.Aquire()
        a2 = ap.Aquire()

        print("call list empty: " + str(a1.Call_Control.CallList().Empty()))

        # Make a call into the reception
        a2.SIP_Phone.Dial("12340001")
        a1.Event_Stack.WaitFor(event_type="call_offer")

        start = time.time()
        logging.info ("Trying to pickup call")
        print("call list empty: " + str(a1.Call_Control.CallList().Empty()))

        try:
            call = a1.Call_Control.PickupCall()
        except Server_404:
            a1.Event_Stack.WaitFor (event_type='call_lock')
            a1.Event_Stack.WaitFor (event_type='call_unlock')
            call = a1.Call_Control.PickupCall()

        logging.info ("Got call " + str (call['id']))
        a1.Event_Stack.WaitFor (event_type='call_pickup', call_id=call['id'])
        end = time.time()
        logging.info ("Got Pickup!" + str (call['id']) + " transfer took " + str (end - start))

        time.sleep(2)
        ap.Release(a1)
        ap.Release(a2)
    except:
        ap.Release(a1)
        ap.Release(a2)
        raise

