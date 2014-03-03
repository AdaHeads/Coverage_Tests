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

from static_agent_pools import Receptionists, Customers

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from pprint import pformat

# Local classes.
from event_stack import EventListenerThread
from sip_utils import SipAgent, SipAccount
from call_flow_communication import callFlowServer, Server_404

# Below is just testing code. Everything interesting (and automatable) will be located in the TestCase classes.
if __name__ == "__main__":
    ap = AgentPool(AgentConfigs)

    try:
        a1 = ap.request()
        a2 = ap.request()

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
        ap.release(a1)
        ap.release(a2)
    except:
        ap.release(a1)
        ap.release(a2)
        raise

