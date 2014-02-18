import logging
import websocket
import os, sys
import json
import thread
import time
import httplib2
import pprint
import config

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from pprint import pformat
from subprocess import Popen, PIPE

# Local classes.
from event_stack import EventListenerThread
from sip_utils import SipAgent, SipAccount
from call_flow_communication import callFlowServer

# Sip accounts
from sip_profiles import agent1100, agent1101, agent1102, agent1103, agent1107, agent1108, agent1109

h = httplib2.Http(".cache")
logging.basicConfig(level=logging.INFO)

class Event_Tests(unittest.TestCase):

    def test_Call_Offer (self):
        pass

class BasicStuff(unittest.TestCase):

    # Makes a call and then asserts that there is a
    # call in the call queue.
    def test_Call_Presence (self):

        customer_agent = SipAgent(account=SipAccount(username=agent1109.username, password=agent1109.password, sip_port=agent1109.sipport))
        elt = EventListenerThread(uri=config.call_flow_events, token=agent1109.authtoken)
        elt.start()
        cfs = callFlowServer(uri=config.call_flow_server_uri, authtoken=agent1109.authtoken)
        customer_agent.Connect()

        try:
            reception      = "12340001"

            current_call_list = cfs.CallList();
            if not current_call_list.Empty():
                logging.error (current_call_list.toString())
                self.fail("non-empty call list: ")

            # Register the customers' sip client.
            customer_agent.Dial (reception)
            elt.WaitFor(event_type="call_offer")

            # Check that there is a call in the queue.
            current_call_list = cfs.CallList();
            if current_call_list.Empty():
                logging.error (current_call_list.toString())
                self.fail("Empty call list: " + str(current_call_list))

            customer_agent.QuitProcess()
            elt.WaitFor(event_type="call_hangup")

            # Check that the call is now absent from the call list.
            current_call_list = cfs.CallList();
            if not current_call_list.Empty():
                self.fail("Found a non-empty call list: " + current_call_list.toString())
            elt.stop()
        except:
            logging.error (elt.dump_stack())
            elt.stop()
            raise

    # Makes a call and then tries to pick it up from the server.
    #
    def test_Unspecified_Call_Pickup (self):

        reception_id = 1
        reception = "1234000" + str(reception_id)

        # Start the event stack task.
        elt = EventListenerThread(uri=config.call_flow_events, token=agent1100.authtoken)
        elt.start();
        cfs = callFlowServer(uri=config.call_flow_server_uri, authtoken=agent1100.authtoken)

        try:
            # Register the reeptionists' sip client.
            logging.info ("Registering receptionist agent " + agent1100.username)
            receptionist_agent = SipAgent(account=SipAccount(username=agent1100.username, password=agent1100.password, sip_port=agent1100.sipport))

            receptionist_agent.Connect()

            # Register the customers' sip client.
            logging.info ("Registering customer agent " + agent1108.username)
            customer_agent = SipAgent(account=SipAccount(username=agent1108.username, password=agent1108.password, sip_port=agent1108.sipport))
            customer_agent.Connect()

            # Make a call into the reception
            logging.info ("Spawing a single call to the reception at " + reception)
            customer_agent.Dial(reception)
            elt.WaitFor(event_type="call_offer")

            call = cfs.PickupCall()
            if call['reception_id'] != reception_id:
                self.fail ("Invalid reception ID in allocated call.")

            logging.info ("Got call " + call['id'] + " waiting for transfer..")
            elt.WaitFor(event_type="call_pickup", call_id=call['id'])

            cfs.HangupCall (call_id=call['id'])
            customer_agent.QuitProcess
            receptionist_agent.QuitProcess

            elt.WaitFor(event_type="call_hangup", call_id=call['id'])
            # Check that no calls are in the call list.
            current_call_list = cfs.CallList();
            elt.stop()
        except:
            logging.error (elt.dump_stack())
            elt.stop()
            raise


    # Makes a call and then asserts that there is a
    # call in the call queue.
    def test_Call_Park_And_Pickup (self):
        reception_id = 2
        reception = "1234000" + str (reception_id)

        # Start the event stack task.
        elt = EventListenerThread(uri=config.call_flow_events, token=agent1101.authtoken)
        elt.start();
        cfs = callFlowServer(uri=config.call_flow_server_uri, authtoken=agent1101.authtoken)

        try:
            # Register the reeptionists' sip client.
            logging.info ("Registering receptionist agent " + agent1101.username)
            receptionist_agent = SipAgent(account=SipAccount(username=agent1101.username, password=agent1101.password, sip_port=agent1101.sipport))

            receptionist_agent.Connect()

            # Register the customers' sip client.
            logging.info ("Registering customer agent " + agent1107.username)
            customer_agent = SipAgent(account=SipAccount(username=agent1107.username, password=agent1107.password, sip_port=agent1107.sipport))
            customer_agent.Connect()

            # Make a call into the reception
            logging.info ("Spawing a single call to the reception at " + reception)
            customer_agent.Dial(reception)
            elt.WaitFor(event_type="call_offer")

            call = cfs.PickupCall()
            if call['reception_id'] != reception_id:
                self.fail ("Invalid reception ID in allocated call.")

            logging.info ("Got call " + call['id'] + " waiting for transfer..")
            elt.WaitFor(event_type="call_pickup", call_id=call['id'])

            cfs.ParkCall (call_id=call['id'])
            elt.WaitFor(event_type="call_park", call_id=call['id'])
            cfs.PickupCall (call_id=call['id'])
            elt.WaitFor(event_type="call_unpark", call_id=call['id'])
            elt.WaitFor(event_type="call_pickup", call_id=call['id'])

            cfs.HangupCall (call_id=call['id'])

            elt.WaitFor(event_type="call_hangup", call_id=call['id'])

            customer_agent.QuitProcess;
            receptionist_agent.QuitProcess;

            elt.stop()
        except:
            elt.stop()
            raise

# Below is just testing code. Everything interesting (and automatable) will be located in the TestCase classes.
if __name__ == "__main__":

    cfs = callFlowServer(uri=config.call_flow_server_uri, authtoken=agent1100.authtoken)
    reception = config.queued_reception

    if not cfs.TokenValid():
        logging.fatal("Could not validate token")
        sys.exit(1)

    elt = EventListenerThread(uri=config.call_flow_events, token=agent1100.authtoken)
    elt.start();

    #logging.info ("Starting agent 2")
    #p1 = Popen(["../bin/basic_agent", agent2.username, agent2.password, config.pbx, agent2.sipport], stdout=PIPE, stderr=PIPE)

    #time.sleep (2)
    #p1.stdout.close()
    # Register the reeptionists' sip client.
    logging.info ("Registering receptionist 1")
    receptionist_agent = SipAgent(account=SipAccount(username=agent1100.username, password=agent1100.password, sip_port=agent1100.sipport))

    receptionist_agent.Connect()

    # Register the customers' sip client.
    logging.info ("Registering customer 1")
    customer_agent = SipAgent(account=SipAccount(username=agent1109.username, password=agent1109.password, sip_port=agent1109.sipport))
    customer_agent.Connect()
    print "call list empty: " + str (cfs.CallList().Empty())

    # Make a call into the reception
    logging.info ("Spawing a single call to the reception at " + reception)
    customer_agent.Dial(reception)
    elt.WaitFor(event_type="call_offer")

    logging.info ("Trying to pickup call")
    print "call list empty: " + str (cfs.CallList().Empty())

    call = cfs.PickupCall()

    logging.info (call)
    #stdoutdata, stderrdata = p2.communicate(input=None)
    #print (stdoutdata)
    #print (stderrdata)

    time.sleep(10)
    #logging.info ("Waiting for p2: " + content)

    customer_agent.QuitProcess()

    self.cfs.HangupCall (call_id=call['id'])
    receptionist_agent.QuitProcess()

    #TODO assert that the call list is empty at this point.

    logging.info ("Has call_offer:" + str (elt.stack_contains ("call_offer")));
    logging.info (elt.dump_stack());
    elt.stop()

