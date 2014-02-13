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
from sip_profiles import agent2, customer1 

h = httplib2.Http(".cache")
logging.basicConfig(level=logging.INFO)

class Event_Tests(unittest.TestCase):
    
    def test_Call_Offer (self):
        pass 

class BasicStuff(unittest.TestCase):
    
    cfs            = callFlowServer(uri=config.call_flow_server_uri, authtoken=config.authtoken)
    
    # Makes a call and then asserts that there is a
    # call in the call queue.
    def test_Call_Presence (self): 
        customer_agent = SipAgent(account=SipAccount(username=customer1.username, password=customer1.password, sip_port=customer1.sipport))
        customer_agent.Connect(
                               )
        reception      = "12340001"
        
        # Register the customers' sip client.
        customer_agent.Dial (reception)

        # Check that there is a call in the queue.
        assert not cfs.CallList().Empty()        
        customer_agent.stdin.write("h\n"); # Hangup
        
        # Check that the call is now absent from the call list.
        assert cfs.CallList().Empty()
        customer_agent.stdin.write("q\n"); # Quit

    # Makes a call and then tries to pick it up from the server.
    #
    def test_Unspecified_Call_Pickup (self):
        reception = "12340001@"+config.pbx
        
        # Start the event stack task.
        wst = WebSocketThread()
        wst.start()
        
        # Register the reeptionists' sip client.
        logging.info ("Registering receptionist 1")
        try:
            receptionist_agent = Popen(["bin/basic_agent", agent2.username, agent2.password, config.pbx, agent2.sipport], stdin=PIPE, stdout=PIPE)
            got_reply = False
            while not got_reply:
                line = receptionist_agent.stdout.readline()
                if "+READY" in line:
                    got_reply = True
                    logging.info("Receptionist is ready.");
                elif "-ERROR" in line:
                    logging.fatal("SIP Agent returned "+line)
                    self.fail("SIP Agent returned "+line)
    
            # Register the customers' sip client.
            logging.info ("Registering customer 1")
            customer_agent = Popen(["bin/basic_agent", customer1.username, customer1.password, config.pbx, customer1.sipport], stdin=PIPE, stdout=PIPE)
            # Wait for registration.
            got_reply = False
            while not got_reply:
                line = customer_agent.stdout.readline()
                if "+READY" in line:
                    got_reply = True
                    logging.info("Customer is ready.");
                elif "-ERROR" in line:
                    logging.fatal("SIP Agent returned "+line)
                    self.fail("SIP Agent returned "+line)
                    
            customer_agent.stdin.write("dsip:"+reception+"\n")
    
            got_reply = False
            while not got_reply:
                line = customer_agent.stdout.readline()
                if "+OK" in line:
                    got_reply = True
                    logging.info("Customer is ready.");
                elif "-ERROR" in line:
                    logging.fatal("SIP Agent returned "+line)
                    self.fail("SIP Agent returned "+line)
            
            #TODO: Check that the event stack contains a call offer and a call pickup event. 
            assert wst.stack_contains("call_offer")
            assert wst.stack_contains("call_pickup")
        
            customer_agent.stdin.write("h\n"); # Hangup
            customer_agent.stdin.write("q\n"); # Quit        
            receptionist_agent.stdin.write("h\n"); # Hangup
            receptionist_agent.stdin.write("q\n"); # Quit
            assert wst.stack_contains("call_hangup")
            wst.stop()
        except:
            wst.stop()


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
    
    resp, content = cfs.PickupCall()

    logging.info ("Got call: " + content)
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
    elt.stop()

