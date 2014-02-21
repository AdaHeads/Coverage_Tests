import logging
from pprint     import pformat
from time       import sleep
from subprocess import call
   
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

logging.basicConfig (level = logging.INFO)

class Test_Case (unittest.TestCase):
    Caller             = None
    Caller_Agent       = None
    
    Receptionist       = None
    Receptionist_Agent = None
    Call_Flow_Control  = None
    Reception_Database = None
    
    Reception          = None
    
    Next_Step          = 1

    def Clean_Up_And_Settle (self):
        # Remove any SIP agents started by other test cases: 
        call (["killall", "basic_agent"])
        # Let the system have time to clean up and settle after the previous test run:
        sleep (1.0) 

    def Setup (self, Caller, Receptionist, Reception):
        self.Next_Step    = 1
        self.Caller       = Caller
        self.Receptionist = Receptionist
        self.Reception    = Reception
        
        logging.info ("Creating SIP agents...")
        self.Caller_Agent       = SipAgent (account = SipAccount (username = self.Caller.username,
                                                                  password = self.Caller.password,
                                                                  sip_port = self.Caller.sipport))
        self.Receptionist_Agent = SipAgent (account = SipAccount (username = self.Receptionist.username,
                                                                  password = self.Receptionist.password,
                                                                  sip_port = self.Receptionist.sipport))
        
        logging.info ("Connecting receptionist agent...")
        self.Receptionist_Agent.Connect ()
        
        logging.info ("Creating Call-Flow-Control connector...")
        self.Call_Flow_Control  = callFlowServer (uri = config.call_flow_server_uri, authtoken = Receptionist.authtoken)

        logging.info ("Checking token validity against Call-Flow-Control...")
        if self.Call_Flow_Control.TokenValid:
            logging.info ("Valid token.")
        else:
            self.fail ("Invalid authentication token.")

        self.Reception_Database = Database_Reception (uri       = config.reception_server_uri,
                                                      authtoken = self.Receptionist.authtoken)

    def Tear_Down (self):
        self.Caller_Agent.QuitProcess ()
        self.Receptionist_Agent.Quit_Process ()        
             
    def Step (self,
              Message,
              Delay_In_Seconds = 0.0):
        logging.info ("Step " + str (self.Next_Step) + ": " + Message)
        sleep (Delay_In_Seconds)
        self.Next_Step = self.Next_Step + 1
        
    def Caller_Places_Call (self):
        self.Step (Message = "Caller places call...")
        
        logging.info("Connecting caller agent...")
        self.Caller_Agent.Connect ()
        
        logging.info("Dialling through caller agent...")
        self.Caller_Agent.Dial (self.Reception)

    def Caller_Hears_Dialtone (self):
        self.Step (Message = "Caller hears dial-tone...")
        
        logging.info("Caller agent waits for dial-tone...")
        self.Caller_Agent.Wait_For_Dialtone ()
        
    def Call_Announced (self, Client):
        self.Step (Message = "Receptionist's client waits for 'call_offer'...")

        try:
            Client.WaitFor ("call_offer")
        except TimeOutReached:
            logging.critical (Client.dump_stack ())
            self.fail ("Call offer didn't arrive from Call-Flow-Control.")

        if not Client.stack_contains(event_type="call_offer", destination=self.Reception):
            logging.critical (Client.dump_stack ())
            self.fail ("The arrived call offer was not for the expected reception (destination).")
            
        return Client.Get_Latest_Event (Event_Type="call_offer", Destination=self.Reception)['call']['reception_id']
        
    def Request_Information (self, Reception_ID):
        self.Step (Message = "Requesting (updated) information about reception " + str(Reception_ID))

        Data_On_Reception = self.Reception_Database.Single (Reception_ID)
        
        self.Step (Message = "Received information: " + pformat (Data_On_Reception))
        
        return Data_On_Reception
        
    def Offers_To_Answer_Call (self, Call_Flow_Control, Reception_ID):
        self.Step (Message = "Client offers to answer call...")

        Call = Call_Flow_Control.PickupCall()

        if Call['destination'] != self.Reception: 
            self.fail ("Unexpected destination in allocated call.")
        if Call['reception_id'] != Reception_ID: 
            self.fail ("Unexpected reception ID in allocated call.")
        
    def Call_Allocation_Acknowledgement (self, Client, Reception_ID, Receptionist_ID):
        self.Step (Message = "Receptionist's client waits for 'call_pickup'...")

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
        
    def Receptionist_Answers (self, Call_Information, Reception_Information, After_Greeting_Played):
        self.Step (Message = "Receptionist answers...")
        
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

        if After_Greeting_Played:
            if not Call_Information['call']['greeting_played']:
                self.fail ("It appears that the receptionist didn't wait long enough to allow the caller to hear the recorded message.")
        else:
            if Call_Information['call']['greeting_played']:
                self.fail ("It appears that the receptionist waited too long, and allowed the caller to hear the recorded message.")
