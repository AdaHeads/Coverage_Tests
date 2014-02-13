from websocket import create_connection
import logging
import websocket
import os, sys
import json
import threading
import thread
import time
import httplib2
import pprint
import config
from sip_utils import SipAgent, SipAccount
from call_flow_communication import callFlowServer

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from pprint import pformat
from subprocess import Popen, PIPE

h = httplib2.Http(".cache")
logging.basicConfig(level=logging.INFO)

class customer1 :
    username = '1011'
    password = '1234'
    sipport  = "5081"

class customer2 :
    username = '1012'
    password = '1234'
    sipport  = "5072"

class agent1 :
    username = '1001'
    password = '1234'
    sipport  = "5071"

class agent2 :
    username = '1002'
    password = '1234'
    sipport  = "5062"
    
class WebSocketThread(threading.Thread):
    ws = None
    messageStack = []
    #messageStack = dict()
    
    def stack_contains (self, event_type, call_id=None):
        for item in self.messageStack:
            if item['event'] == event_type:
                if call_id == None: 
                    return True
                elif item['call']['id'] == call_id:
                    return True
        return False

    def dump_stack(self):
        logging.info (pformat(self.messageStack))
    
    def on_error(self, ws, error):
        logging.error (error)

    def on_open (self, ws):
        logging.info ("Opened websocket")

    def on_close(self, ws):
        logging.info ("Closed websocket")
        
    def on_message(self, ws, message):
        #x.update({3:4})
        self.messageStack.append(json.loads(message)['notification'])
        logging.info (message)
    
    def connect (self):
        try:
            self.ws = websocket.WebSocketApp ("ws://localhost:4242/notifications?token="+config.authtoken,
                                              on_message = self.on_message,
                                              on_error = self.on_error,
                                              on_close = self.on_close)
            self.ws.on_open = self.on_open
        except:
            logging.critical("Websocket connect failed!")
    
    def run(self):
        try:
            logging.info ("Starting websocket")
            self.connect()
            self.ws.run_forever()
        except:
            logging.critical("Run in thread failed!")
            
    def stop(self):
        logging.info ("stopping websocket")
        self.ws.close();


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
        resp, content = h.request("http://localhost:4242/call/queue?token="+authtoken, "GET")
        
        assert resp['status'] == '200'
        call_list = json.loads(content)
        if len(call_list['calls']) != 0:
            logging.error("Empty call list found:" + json.dumps(call_list))
        customer_agent.stdin.write("h\n"); # Hangup
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


if __name__ == "__main__":
    
    cfs = callFlowServer(uri=config.call_flow_server_uri, authtoken=config.authtoken)
    reception = "12340001"

    
    if not cfs.TokenValid():
        logging.fatal("Could not validate token")
        sys.exit(1)

    wst = WebSocketThread()
    wst.start()
    
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
    
    # Make a call into the reception
    logging.info ("Spawing a single call to the reception at " + reception)
    customer_agent.Dial(reception)
    
    time.sleep(2)
    logging.info ("Trying to pickup call")
    
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
    logging.info ("Has call_offer:" + str (wst.stack_contains ("call_offer")));
    wst.stop()

