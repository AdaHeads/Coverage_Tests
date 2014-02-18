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
from sip_profiles import agent1100, agent1109 

h = httplib2.Http(".cache")
logging.basicConfig(level=logging.INFO)

class Event_Tests(unittest.TestCase):
    
    def test_Call_Offer (self):
        pass 

class BasicStuff(unittest.TestCase):
    
    cfs = callFlowServer(uri=config.call_flow_server_uri, authtoken=agent1109.authtoken)
    
    # Makes a call and then asserts that there is a
    # call in the call queue.
    def test_Call_Presence (self): 
        customer_agent = SipAgent(account=SipAccount(username=agent1109.username, password=agent1109.password, sip_port=agent1109.sipport))
        customer_agent.Connect()
        
        reception      = config.queued_reception
        
        # Register the customers' sip client.
        customer_agent.Dial (reception)
        time.sleep(0.5) # Let the call "settle"

        # Check that there is a call in the queue.
        assert not self.cfs.CallList().Empty()
        
        customer_agent.HangupAllCalls()
        customer_agent.QuitProcess()
        # Check that the call is now absent from the call list.

        current_call_list = self.cfs.CallList();
        if not current_call_list.Empty():
            self.fail("Found a non-empty call list: " + current_call_list.toString())

    # Makes a call and then tries to pick it up from the server.
    #
    def test_Unspecified_Call_Pickup (self):
        reception_id = 1
        reception = "1234000" + str(reception_id)
        
        # Start the event stack task.
        elt = EventListenerThread(uri=config.call_flow_events, token=agent1100.authtoken)
        elt.start();
        
        try:
            # Register the reeptionists' sip client.
            logging.info ("Registering receptionist agent " + agent1100.username)
            receptionist_agent = SipAgent(account=SipAccount(username=agent1100.username, password=agent1100.password, sip_port=agent1100.sipport))
    
            receptionist_agent.Connect()
        
            # Register the customers' sip client.
            logging.info ("Registering customer agent " + agent1109.username)
            customer_agent = SipAgent(account=SipAccount(username=agent1109.username, password=agent1109.password, sip_port=agent1109.sipport))
            customer_agent.Connect()
                        
            # Make a call into the reception
            logging.info ("Spawing a single call to the reception at " + reception)
            customer_agent.Dial(reception)

            # Let the call settle.
            time.sleep(0.5)
            
            call = self.cfs.PickupCall()
            logging.info ("Got call " + str (call))
            
            time.sleep(10.0) # Wait for the call to connect...            
             
            customer_agent.HangupAllCalls  
            customer_agent.QuitProcess
            receptionist_agent.HangupAllCalls
            receptionist_agent.QuitProcess
            
            # Tests
            if not elt.stack_contains(event_type="call_offer", call_id=call['id']):
                self.fail (elt.dump_stack())
            elif not elt.stack_contains(event_type="call_pickup", call_id=call['id']):
                self.fail (elt.dump_stack())
            elif call['reception_id'] != reception_id: 
                self.fail ("Invalid reception ID in allocated call.")
            
            #TODO Check for hangup event.
#            if not elt.stack_contains("call_hangup"):
#                self.fail("call_hangup event not found in " + elt.dump_stack())
                
            elt.stop()
        except:
            elt.stop()
            raise


    # Makes a call and then asserts that there is a
    # call in the call queue.
    def test_Call_Park_And_Pickup (self):
        reception_id = 2 
        reception = "1234000" + str (reception_id)
        
        # Start the event stack task.
        elt = EventListenerThread(uri=config.call_flow_events, token=agent1100.authtoken)
        elt.start();
        
        try:
            # Register the reeptionists' sip client.
            logging.info ("Registering receptionist agent " + agent1100.username)
            receptionist_agent = SipAgent(account=SipAccount(username=agent1100.username, password=agent1100.password, sip_port=agent1100.sipport))
    
            receptionist_agent.Connect()
        
            # Register the customers' sip client.
            logging.info ("Registering customer agent " + agent1109.username)
            customer_agent = SipAgent(account=SipAccount(username=agent1109.username, password=agent1109.password, sip_port=agent1109.sipport))
            customer_agent.Connect()
                        
            # Make a call into the reception
            logging.info ("Spawing a single call to the reception at " + reception)
            customer_agent.Dial(reception)

            # Let the call settle.
            time.sleep(0.5)
            
            call = self.cfs.PickupCall()
            logging.info ("Got call " + str (call['id']))
            
            time.sleep(5.0) # Wait for the call to connect...
            
            self.cfs.ParkCall (call_id=call['id'])
            time.sleep(1.0)
            self.cfs.PickupCall (call_id=call['id'])
            time.sleep(5.0) # Wait for the call to connect...
            
            customer_agent.HangupAllCalls  
            receptionist_agent.HangupAllCalls
            customer_agent.QuitProcess;  
            receptionist_agent.QuitProcess;

            time.sleep(2.0)
            # Tests
            if not elt.stack_contains(event_type="call_offer", call_id=call['id']):
                self.fail (elt.dump_stack())
            elif not elt.stack_contains(event_type="call_pickup", call_id=call['id']):
                self.fail (elt.dump_stack())
            elif call['reception_id'] != reception_id: 
                self.fail ("Invalid reception ID in allocated call.")
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
    
    time.sleep(2)
    logging.info ("Trying to pickup call")
    print "call list empty: " + str (cfs.CallList().Empty())
    
    call = cfs.PickupCall()

    logging.info (call)
    #stdoutdata, stderrdata = p2.communicate(input=None)
    #print (stdoutdata)
    #print (stderrdata)
    
    time.sleep(10)
    #logging.info ("Waiting for p2: " + content)
    
    customer_agent.HangupAllCalls()
    customer_agent.QuitProcess()
    
    receptionist_agent.HangupAllCalls()
    receptionist_agent.QuitProcess()

    #TODO assert that the call list is empty at this point.
        
    logging.info ("Has call_offer:" + str (elt.stack_contains ("call_offer")));
    logging.info (elt.dump_stack());
    elt.stop()

