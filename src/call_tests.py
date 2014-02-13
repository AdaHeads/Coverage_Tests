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
from sip_profiles import agent2, customer1, customer2 

h = httplib2.Http(".cache")
logging.basicConfig(level=logging.INFO)

class Event_Tests(unittest.TestCase):
    
    def test_Call_Offer (self):
        pass 

class BasicStuff(unittest.TestCase):
    
    cfs = callFlowServer(uri=config.call_flow_server_uri, authtoken=config.authtoken)
    
    # Makes a call and then asserts that there is a
    # call in the call queue.
    def test_Call_Presence (self): 
        customer_agent = SipAgent(account=SipAccount(username=customer2.username, password=customer2.password, sip_port=customer2.sipport))
        customer_agent.Connect()
        
        reception      = "12340001"
        
        # Register the customers' sip client.
        customer_agent.Dial (reception)
        time.sleep(0.5) # Let the call "settle"

        # Check that there is a call in the queue.
        assert not self.cfs.CallList().Empty()
        
        customer_agent.QuitProcess()
        # Check that the call is now absent from the call list.

        current_call_list = self.cfs.CallList();
        if not current_call_list.Empty():
            self.fail("Found a non-empty call list: " + current_call_list.toString())

    # Makes a call and then tries to pick it up from the server.
    #
    def test_Unspecified_Call_Pickup (self):
        reception = "12340002"
        
        # Start the event stack task.
        elt = EventListenerThread(uri="ws://localhost:4242/notifications", token=config.authtoken)
        elt.start();
        
        try:
            # Register the reeptionists' sip client.
            logging.info ("Registering receptionist 2")
            receptionist_agent = SipAgent(account=SipAccount(username=agent2.username, password=agent2.password, sip_port=agent2.sipport))
        
            receptionist_agent.Connect()
        
            # Register the customers' sip client.
            logging.info ("Registering customer 1")
            customer_agent = SipAgent(account=SipAccount(username=customer1.username, password=customer1.password, sip_port=customer1.sipport))
            customer_agent.Connect()
                        
            customer_agent.Dial(reception)
            time.sleep(0.5)
            
            call = self.cfs.PickupCall()
             
            if not elt.stack_contains(event_type="call_offer"):
                self.fail (elt.dump_stack())
            assert elt.stack_contains(event_type="call_pickup")
        
            customer_agent.QuitProcess;  
            receptionist_agent.QuitProcess;
            assert elt.stack_contains("call_hangup")
            elt.stop()
        except:
            elt.stop()
            raise


    # Makes a call and then asserts that there is a
    # call in the call queue.
    def test_Call_Park_And_Pickup (self): 
        reception = "12340002"
        
        # Start the event stack task.
        elt = EventListenerThread(uri="ws://localhost:4242/notifications", token=config.authtoken)
        elt.start();
        
        try:
            # Register the reeptionists' sip client.
            logging.info ("Registering receptionist 2")
            receptionist_agent = SipAgent(account=SipAccount(username=agent2.username, password=agent2.password, sip_port=agent2.sipport))
        
            receptionist_agent.Connect()
        
            # Register the customers' sip client.
            logging.info ("Registering customer 1")
            customer_agent = SipAgent(account=SipAccount(username=customer1.username, password=customer1.password, sip_port=customer1.sipport))
            customer_agent.Connect()
                        
            customer_agent.Dial(reception)
                
            assert elt.stack_contains("call_offer")
            assert elt.stack_contains("call_pickup")
        
            self.cfs.ParkCall ()
            
            assert elt.stack_contains("call_park")
            customer_agent.QuitProcess;  
            receptionist_agent.QuitProcess;
            assert elt.stack_contains("call_hangup")
            elt.stop()
        except:
            elt.stop()

# Below is just testing code. Everything interesting (and automatable) will be located in the TestCase classes. 
if __name__ == "__main__":
    
    cfs = callFlowServer(uri=config.call_flow_server_uri, authtoken=config.authtoken)
    reception = "12340001"
    
    if not cfs.TokenValid():
        logging.fatal("Could not validate token")
        sys.exit(1)

    elt = EventListenerThread(uri="ws://localhost:4242/notifications", token=config.authtoken)
    elt.start();
    
    #logging.info ("Starting agent 2")
    #p1 = Popen(["../bin/basic_agent", agent2.username, agent2.password, config.pbx, agent2.sipport], stdout=PIPE, stderr=PIPE)

    #time.sleep (2)
    #p1.stdout.close()
    # Register the reeptionists' sip client.
    logging.info ("Registering receptionist 1")
    receptionist_agent = SipAgent(account=SipAccount(username=agent2.username, password=agent2.password, sip_port=agent2.sipport))
    
    receptionist_agent.Connect()
    
    # Register the customers' sip client.
    logging.info ("Registering customer 1")
    customer_agent = SipAgent(account=SipAccount(username=customer1.username, password=customer1.password, sip_port=customer1.sipport))
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
    
    #logging.info ("Waiting for p2: " + content)
    
    customer_agent.HangupAllCalls()
    customer_agent.QuitProcess()
    
    receptionist_agent.HangupAllCalls()
    receptionist_agent.QuitProcess()

    #TODO assert that the call list is empty at this point.
        
    #wst.dump_stack()
    logging.info ("Has call_offer:" + str (elt.stack_contains ("call_offer")));
    logging.info (elt.dump_stack());
    elt.stop()

