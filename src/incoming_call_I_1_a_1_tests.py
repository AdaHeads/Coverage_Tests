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

from event_stack import EventListenerThread
from call_flow_communication import callFlowServer
from database_reception import Database_Reception

logging.basicConfig(level=logging.INFO)

class Sequence_Diagram(unittest.TestCase):
    Caller_Agent       = SipAgent (account=SipAccount(username=Caller.username,       password=Caller.password,       sip_port=Caller.sipport))
    Receptionist_Agent = SipAgent (account=SipAccount(username=Receptionist.username, password=Receptionist.password, sip_port=Receptionist.sipport))
    Call_Flow_Control  = callFlowServer(uri=config.call_flow_server_uri, authtoken=Receptionist.authtoken)
    
    Reception = config.queued_reception
        
    def Caller_Places_Call (self):
        logging.info("Connecting caller agent...")
        self.Caller_Agent.Connect ()
        logging.info("Dialling through caller agent...")
        self.Caller_Agent.Dial (self.Reception)

    def Caller_Hears_Dialtone (self):
        logging.info("Caller agent waits for dial-tone...")
        self.Caller_Agent.Wait_For_Dialtone ()
        
    def Call_Announced (self, Client):
        logging.info("Receptionist's client waits for 'call_offer'...")

        try:
            Client.WaitFor ("call_offer")
        except TimeOutReached:
            self.fail (Client.dump_stack())

        if not Client.stack_contains(event_type="call_offer", destination=self.Reception):
            self.fail (Client.dump_stack())
            
        return Client.Get_Latest_Event (Event_Type="call_offer", Destination=self.Reception)['call']['reception_id']
        
    def Request_Information(self, Reception_Database, Reception_ID):
        logging.info("Requesting (updated) information about reception " + str(Reception_ID))
        Data_On_Reception = Reception_Database.Single(Reception_ID)
        logging.info("Received information: " + str(Data_On_Reception))
        
    def Receptionist_Offers_To_Answer_Call(self):
        self.Call_Flow_Control.PickupCall()
        
    def test_Run (self):
        Client = EventListenerThread(uri=config.call_flow_events, token=Receptionist.authtoken)
        Client.start();
        
        Reception_Database = Database_Reception(uri=config.reception_server_uri, authtoken=Receptionist.authtoken)
        
        try:
            self.Caller_Places_Call()
            self.Caller_Hears_Dialtone()
            # FreeSWITCH: checks dial-plan => to queue
            # FreeSWITCH->Call-Flow-Control: call queued with dial-tone
            # FreeSWITCH: pauses dial-plan processing for # seconds
            # Call-Flow-Control: finds free receptionists
            Reception_ID = self.Call_Announced (Client)
            # Client-N shows call to receptionist-N
            self.Request_Information(Reception_Database=Reception_Database, Reception_ID=Reception_ID)
            self.Receptionist_Offers_To_Answer_Call()
            
            Client.stop()            
        except:
            Client.stop()
            raise
