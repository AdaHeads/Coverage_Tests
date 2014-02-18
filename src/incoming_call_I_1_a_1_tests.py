import config
import logging
import time

from sip_utils import SipAgent, SipAccount

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from sip_profiles import agent1102 as Caller 
from sip_profiles import agent1105 as Receptionist 

import httplib2 as httplib

from event_stack import EventListenerThread

h = httplib.Http(".cache")
logging.basicConfig(level=logging.INFO)

class Sequence_Diagram(unittest.TestCase):
    Caller_Agent       = SipAgent (account=SipAccount(username=Caller.username,       password=Caller.password,       sip_port=Caller.sipport))
    Receptionist_Agent = SipAgent (account=SipAccount(username=Receptionist.username, password=Receptionist.password, sip_port=Receptionist.sipport))
    
    Reception = config.queued_reception
        
    def Caller_Places_Call (self):
        self.Caller_Agent.Connect ()
        self.Caller_Agent.Dial (self.Reception)

    def Caller_Hears_Dialtone (self):
        self.Caller_Agent.Wait_For_Dialtone ()
        
    def Call_Announced (self, Client):
        time.sleep(0.200) # As call-flow-control gives an agent 200ms to respond, the same must be fair the other way too
        if not Client.stack_contains(event_type="call_offer", destination=self.Reception):
            self.fail (Client.dump_stack())
        
    def test_Run (self):
        Client = EventListenerThread(uri=config.call_flow_events, token=Receptionist.authtoken)
        Client.start();
        
        try:
            self.Caller_Places_Call()
            self.Caller_Hears_Dialtone()
            # FreeSWITCH: checks dial-plan => to queue
            # FreeSWITCH->Call-Flow-Control: call queued with dial-tone
            # FreeSWITCH: pauses dial-plan processing for # seconds
            # Call-Flow-Control: finds free receptionists
            self.Call_Announced (Client=Client)
            
            Client.stop()            
        except:
            Client.stop()
            raise
