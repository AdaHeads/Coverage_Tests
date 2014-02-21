import logging
from pprint import pformat
from time   import sleep

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import config
from sip_utils               import SipAgent, SipAccount
from event_stack             import EventListenerThread
from event_stack             import TimeOutReached
from call_flow_communication import callFlowServer
from database_reception      import Database_Reception
from sip_profiles            import agent1102 as Caller 
from sip_profiles            import agent1103 as Receptionist 
from sip_profiles            import agent1106 as Call_Stealer 

logging.basicConfig (level = logging.INFO)

class Sequence_Diagram (unittest.TestCase):
    Caller_Agent        = SipAgent (account=SipAccount(username=Caller.username,       password=Caller.password,       sip_port=Caller.sipport))
    Receptionist_Agent  = SipAgent (account=SipAccount(username=Receptionist.username, password=Receptionist.password, sip_port=Receptionist.sipport))
    Call_Stealing_Agent = SipAgent (account=SipAccount(username=Call_Stealer.username, password=Call_Stealer.password, sip_port=Call_Stealer.sipport))
    Call_Flow_Control   = callFlowServer(uri=config.call_flow_server_uri, authtoken=Receptionist.authtoken)
    Call_Steal_Control  = callFlowServer(uri=config.call_flow_server_uri, authtoken=Call_Stealer.authtoken)
    
    Reception = config.queued_reception
    
    def Setup (self):
        logging.info ("Step 0:")
        
        logging.info ("Connecting receptionist agent...")
        self.Receptionist_Agent.Connect ()

        logging.info ("Connecting call stealing agent...")
        self.Call_Stealing_Agent.Connect ()
        
        logging.info ("Checking token validity against Call-Flow-Control...")
        if self.Call_Flow_Control.TokenValid:
            logging.info ("Valid token.")
        else:
            self.fail ("Invalid authentication token.")

        logging.info ("Checking call stealing token validity against Call-Flow-Control...")
        if self.Call_Steal_Control.TokenValid:
            logging.info ("Valid token.")
        else:
            self.fail ("Invalid call stealing authentication token.")
        
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
            Client.WaitFor ("call_offer")
        except TimeOutReached:
            logging.critical (Client.dump_stack ())
            self.fail ("Call offer didn't arrive from Call-Flow-Control.")

        if not Client.stack_contains(event_type="call_offer", destination=self.Reception):
            logging.critical (Client.dump_stack ())
            self.fail ("The arrived call offer was not for the expected reception (destination).")
            
        return Client.Get_Latest_Event (Event_Type="call_offer", Destination=self.Reception)['call']['reception_id']
        
    def Request_Information(self, Reception_Database, Reception_ID):
        logging.info ("Step 9:")
        logging.info("Requesting (updated) information about reception " + str(Reception_ID))
        Data_On_Reception = Reception_Database.Single(Reception_ID)
        
        logging.info ("Step 10:")
        logging.info("Received information: " + pformat (Data_On_Reception))
        
        return Data_On_Reception
        
    def Offers_To_Answer_Call(self, Call_Flow_Control, Reception_ID):
        logging.info ("Step 11:")

        Call = Call_Flow_Control.PickupCall()
        
        if Call['destination'] != self.Reception: 
            self.fail ("Unexpected destination in allocated call.")
        if Call['reception_id'] != Reception_ID: 
            self.fail ("Unexpected reception ID in allocated call.")
        
    def Call_Allocation_Acknowledgement (self, Client, Reception_ID, Receptionist_ID):
        logging.info ("Step 12:")
        logging.info("Receptionist's client waits for 'call_pickup'...")

        try:
            Client.WaitFor ("call_pickup")
        except TimeOutReached:
            logging.critical (Client.dump_stack ())
            self.fail ("No 'call_pickup' event arrived from Call-Flow-Control.")

        if not Client.stack_contains(event_type="call_pickup", destination=self.Reception):
            logging.critical (Client.dump_stack ())
            self.fail ("The arrived 'call_pickup' event was not for the expected reception (destination).")

        if not Client.Get_Latest_Event (Event_Type="call_pickup", Destination=self.Reception)['call']['reception_id'] == Reception_ID:
            logging.critical (Client.dump_stack ())
            self.fail ("The arrived 'call_pickup' event was not for the expected reception (reception ID).")

        if not Client.Get_Latest_Event (Event_Type="call_pickup", Destination=self.Reception)['call']['assigned_to'] == Receptionist_ID:
            logging.critical (Client.dump_stack ())
            self.fail ("The arrived 'call_pickup' event was not for the expected receptionist (receptionist ID).")

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
        sleep (1.0) # Letting the system clean up and settle after the previous test run.

        Client = EventListenerThread (uri   = config.call_flow_events,
                                      token = Receptionist.authtoken)
        Client.start ();

        Stealing_Client = EventListenerThread (uri   = config.call_flow_events,
                                               token = Call_Stealer.authtoken)
        Stealing_Client.start ();

        try:
            Reception_Database = Database_Reception (uri       = config.reception_server_uri,
                                                     authtoken = Receptionist.authtoken)
            self.Setup ()
            
            self.Caller_Places_Call ()
            self.Caller_Hears_Dialtone ()
            logging.info ("Step 3: FreeSWITCH: checks dial-plan => to queue")
            logging.info ("Step 4: FreeSWITCH->Call-Flow-Control: call queued with dial-tone")
            logging.info ("Step 5: FreeSWITCH: pauses dial-plan processing for # seconds")
            logging.info ("Step 6: Call-Flow-Control: finds free receptionists")
            Reception_ID = self.Call_Announced (Client = Client)
            logging.info ("Step 8: Client-N shows call to receptionist-N")
            Reception_Data = self.Request_Information (Reception_Database = Reception_Database,
                                                       Reception_ID       = Reception_ID)
            
            logging.info ("- Call stealer interferes")
            self.Offers_To_Answer_Call (Call_Flow_Control = self.Call_Steal_Control,
                                        Reception_ID      = Reception_ID)
            Stolen_Call_Information = self.Call_Allocation_Acknowledgement (Client          = Client,
                                                                            Reception_ID    = Reception_ID,
                                                                            Receptionist_ID = Call_Stealer.ID)
            self.Receptionist_Answers (Call_Information      = Stolen_Call_Information,
                                       Reception_Information = Reception_Data)
            sleep (0.250)
            logging.info ("- Now we expect that the call stealer has succeeded")
            
            self.Offers_To_Answer_Call (Call_Flow_Control = self.Call_Flow_Control,
                                        Reception_ID      = Reception_ID)
            try:
                Call_Information = self.Call_Allocation_Acknowledgement (Client          = Client,
                                                                         Reception_ID    = Reception_ID,
                                                                         Receptionist_ID = Receptionist.ID)
                raise Incorrectly_Allocated_Call
            except Incorrectly_Allocated_Call:
                self.fail("The incoming call was somehow allocated to the late receptionist. :-(")
            except:
                logging.info ("We're happy to note that the receptionist - as planned - didn't get the call.")
                
            Client.stop()            
            Stealing_Client.stop()            
        except:
            Client.stop()
            Stealing_Client.stop()            
            raise
