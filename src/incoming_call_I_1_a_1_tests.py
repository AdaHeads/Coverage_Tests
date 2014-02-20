import config
import logging
from pprint import pformat

from sip_utils import SipAgent, SipAccount

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from sip_profiles import agent1102 as Caller 
from sip_profiles import agent1105 as Receptionist 

from event_stack import EventListenerThread
from event_stack import TimeOutReached
from call_flow_communication import callFlowServer
from database_reception import Database_Reception

logging.basicConfig(level=logging.INFO)

class Sequence_Diagram(unittest.TestCase):
    Caller_Agent       = SipAgent (account=SipAccount(username=Caller.username,       password=Caller.password,       sip_port=Caller.sipport))
    Receptionist_Agent = SipAgent (account=SipAccount(username=Receptionist.username, password=Receptionist.password, sip_port=Receptionist.sipport))
    Call_Flow_Control  = callFlowServer(uri=config.call_flow_server_uri, authtoken=Receptionist.authtoken)
    
    Reception = config.queued_reception
    Call      = None
    
    def Setup (self):
        logging.info ("Step 0:")
        logging.info ("Connecting receptionist agent...")
        self.Receptionist_Agent.Connect ()
        logging.info ("Checking token validity against Call-Flow-Control...")
        if self.Call_Flow_Control.TokenValid:
            logging.info ("Valid token.")
        else:
            self.fail ("Invalid authentication token.")
        
    def Caller_Places_Call (self):
        logging.info ("Step 1:")
        logging.info("Connecting caller agent...")
        self.Caller_Agent.Connect ()
        logging.info("Dialling through caller agent...")
        self.Caller_Agent.Dial (self.Reception)

    def Caller_Hears_Dialtone (self):
        logging.info ("Step 2:")
        logging.info("Caller agent waits for dial-tone...")
        self.Caller_Agent.Wait_For_Dialtone ()
        
    def Call_Announced (self, Client):
        logging.info ("Step 7:")
        logging.info("Receptionist's client waits for 'call_offer'...")

        try:
            Client.WaitFor ("call_offer", timeout=0.6)
        except TimeOutReached:
            self.fail (Client.dump_stack())

        if not Client.stack_contains(event_type="call_offer", destination=self.Reception):
            self.fail (Client.dump_stack())
            
        return Client.Get_Latest_Event (Event_Type="call_offer", Destination=self.Reception)['call']['reception_id']
        
    def Request_Information(self, Reception_Database, Reception_ID):
        logging.info ("Step 9:")
        logging.info("Requesting (updated) information about reception " + str(Reception_ID))
        Data_On_Reception = Reception_Database.Single(Reception_ID)
        logging.info ("Step 10:")
        logging.info("Received information: " + pformat (Data_On_Reception))
        
        return Data_On_Reception
        
    def Receptionist_Offers_To_Answer_Call(self, Reception_ID):
        logging.info ("Step 11:")

        self.Call = self.Call_Flow_Control.PickupCall()
        if self.Call['destination'] != self.Reception: 
            self.fail ("Unexpected destination in allocated call.")
        if self.Call['reception_id'] != Reception_ID: 
            self.fail ("Unexpected reception ID in allocated call.")
        
    def Call_Flow_Control_Acknowledges_Call_Allocation (self, Client, Reception_ID):
        logging.info ("Step 12:")
        logging.info("Receptionist's client waits for 'call_pickup'...")

        try:
            Client.WaitFor ("call_pickup")
        except TimeOutReached:
            self.fail (Client.dump_stack())

        if not Client.stack_contains(event_type="call_pickup", destination=self.Reception):
            self.fail (Client.dump_stack())
        if not Client.Get_Latest_Event (Event_Type="call_pickup", Destination=self.Reception)['call']['reception_id'] == Reception_ID:
            self.fail (Client.dump_stack())
        logging.info ("Call picked up: " + pformat (Client.Get_Latest_Event (Event_Type="call_pickup", Destination=self.Reception)))
        
        return Client.Get_Latest_Event (Event_Type="call_pickup", Destination=self.Reception)
        
    def Receptionist_Answers (self, Call_Information, Reception_Information):
        logging.info ("Step 14:")
        
        if Call_Information['call']['greeting_played']:
            try:
                logging.info ("Receptionist says '" + Reception_Information['greeting_after_automatic_answer'] + "'.")
            except:
                self.fail ("Reception information missing 'greeting_after_automatic_answer'.")
        else:
            try:
                logging.info ("Receptionist says '" + Reception_Information['greeting'] + "'.")
            except:
                self.fail ("Reception information missing 'greeting'.")
        
    def test_Run (self):
        Client = EventListenerThread(uri=config.call_flow_events, token=Receptionist.authtoken)
        Client.start();

        try:
            Reception_Database = Database_Reception(uri=config.reception_server_uri, authtoken=Receptionist.authtoken)
            self.Setup ()
            
            self.Caller_Places_Call ()
            self.Caller_Hears_Dialtone ()
            logging.info ("Step 3: FreeSWITCH: checks dial-plan => to queue")
            logging.info ("Step 4: FreeSWITCH->Call-Flow-Control: call queued with dial-tone")
            logging.info ("Step 5: FreeSWITCH: pauses dial-plan processing for # seconds")
            logging.info ("Step 6: Call-Flow-Control: finds free receptionists")
            Reception_ID = self.Call_Announced (Client)
            logging.info ("Step 8: Client-N shows call to receptionist-N")
            Reception_Data = self.Request_Information(Reception_Database=Reception_Database, Reception_ID=Reception_ID)
            self.Receptionist_Offers_To_Answer_Call(Reception_ID=Reception_ID)
            Call_Information = self.Call_Flow_Control_Acknowledges_Call_Allocation(Client=Client, Reception_ID=Reception_ID)
            logging.info ("Step 13: Call-Flow-Control->FreeSWITCH: connect call to phone-N")
            self.Receptionist_Answers(Call_Information=Call_Information, Reception_Information=Reception_Data)
            
            Client.stop()            
        except:
            Client.stop()
            raise
