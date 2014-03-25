# -*- coding: utf-8 -*-
import logging
from pprint     import pformat
from time       import clock, sleep

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import config
from event_stack             import TimeOutReached
from database_reception      import Database_Reception
from static_agent_pools      import Receptionists, Customers

logging.basicConfig (level = logging.INFO)

class Call_Failure (Exception):
    pass

class Test_Case (unittest.TestCase):
    Caller             = None
    Receptionist       = None
    Receptionist_2     = None
    Callee             = None

    Reception_Database = None

    Reception          = None

    Start_Time         = None
    Next_Step          = 1

    def Preconditions (self, Reception):
        self.Start_Time = clock ()
        self.Next_Step  = 1

        self.Log ("Forward call test case: Setting up preconditions...")

        self.Log ("Requesting a customer (caller)...")
        self.Caller = Customers.request ()
        self.Log ("Put caller agent on manual answer...")
        self.Caller.sip_phone.disable_auto_answer ()

        self.Log ("Requesting a receptionist...")
        self.Receptionist = Receptionists.request ()
        self.Log ("Put receptionist agent on auto-answer...")
        self.Receptionist.sip_phone.enable_auto_answer ()

        self.Log ("Requesting a customer (callee)...")
        self.Callee = Customers.request ()
        self.Log ("Put callee agent on manual answer...")
        self.Callee.sip_phone.disable_auto_answer ()

        self.Log ("Select which reception to test...")
        self.Reception    = Reception

        self.Log ("Select a reception database connection...")
        self.Reception_Database = Database_Reception (uri       = config.reception_server_uri,
                                                      authtoken = self.Receptionist.call_control.authtoken)

        self.Next_Step = 0
        self.Caller_Places_Call (Number = self.Reception)

        self.Next_Step = 0
        Call_ID, Reception_ID = self.Call_Announced ()

        self.Next_Step = 0
        self.Offer_To_Pick_Up_Call (Call_Flow_Control = self.Receptionist.call_control,
                                    Call_ID           = Call_ID)

        self.Log ("Forward call test case: Preconditions set up.")

    def Postprocessing (self):
        self.Step ("Forward call test case: Cleaning up after test...")

        if not self.Caller is None:
            self.Caller.release ()
        if not self.Receptionist is None:
            self.Receptionist.release ()
        if not self.Receptionist_2 is None:
            self.Receptionist_2.release ()
        if not self.Callee is None:
            self.Callee.release ()

        self.Step ("Forward call test case: Done cleaning up after test.")

    def Step (self,
              Message,
              Delay_In_Seconds = 0.0):
        if self.Next_Step is None:
            self.Next_Step = 1
        if self.Start_Time is None:
            self.Start_Time = clock ()

        logging.info ("Step " + str (self.Next_Step) + ": " + Message)
        sleep (Delay_In_Seconds)
        self.Next_Step = self.Next_Step + 1

    def Log (self,
             Message,
             Delay_In_Seconds = 0.0):
        if self.Next_Step is None:
            self.Next_Step = 1
        if self.Start_Time is None:
            self.Start_Time = clock ()

        logging.info ("     " + str (self.Next_Step - 1) + ": " + Message)
        sleep (Delay_In_Seconds)

    def Caller_Places_Call (self, Number):
        self.Step (Message = "Caller places call to " + str (Number) + "...")
        self.Caller.dial (Number)
        self.Log (Message = "Caller has placed call.")

    def Caller_Hears_Dialtone (self):
        self.Step (Message = "Caller hears dial-tone...")

        self.Log (Message = "Caller agent waits for dial-tone...")
        self.Caller.sip_phone.Wait_For_Dialtone ()
        self.Log (Message = "Caller agent hears dial-tone now.")

    def Receptionist_Places_Call (self, Number):
        self.Step (Message = "Receptionist places call to " + str (Number) + "...")
        Response = self.Receptionist.call_control.Originate_Arbitrary (context   = "1@1",
                                                                       extension = Number)
        if Response["status"] == "ok":
            self.Log (Message = "Call-Flow-Control has accepted request to place call.")
            return Response["call"]["id"]
        else:
            self.Log (Message = "Receptionist failed to place call.")
            raise Call_Failure ("Failed to call " + str (Number) + ".")

    def Receptionist_Hears_Dialtone (self):
        self.Step (Message = "Receptionist hears dial-tone...")
        self.Log (Message = "(we assume, as we can't test it directly with our current setup)")

    def Receptionist_Hangs_Up (self, Call_ID):
        self.Step (Message = "Receptionist hangs up...")
        self.Receptionist.Hangup_Current_Call (call_id = Call_ID)
        self.Log (Message = "Succeeded hanging up " + str (Call_ID) + ".")

    def Receptionist_Receives_Call (self):
        self.Step (Message = "Receptionist receives call...")
        self.Receptionist.sip_phone.wait_for_call ()
        self.Log (Message = "Receptionist SIP phone got an incoming call.")

    def Receptionist_Answers (self, Call_Information, Reception_Information, After_Greeting_Played):
        self.Step (Message = "Receptionist answers...")

        if Call_Information['call']['greeting_played']:
            try:
                self.Log (Message = "Receptionist says '" + Reception_Information['short_greeting'] + "'.")
            except:
                self.fail ("Reception information missing 'short_greeting'.")
        else:
            try:
                self.Log (Message = "Receptionist says '" + Reception_Information['greeting'] + "'.")
            except:
                self.fail ("Reception information missing 'greeting'.")

        if After_Greeting_Played:
            if not Call_Information['call']['greeting_played']:
                self.fail ("It appears that the receptionist didn't wait long enough to allow the caller to hear the recorded message.")
        else:
            if Call_Information['call']['greeting_played']:
                self.fail ("It appears that the receptionist waited too long, and allowed the caller to hear the recorded message.")

    def Callee_Receives_Call (self):
        self.Step (Message = "Callee receives call...")

        self.Log (Message = "Callee agent waits for incoming call...")
        self.Callee.sip_phone.wait_for_call ()
        self.Log (Message = "Callee agent got an incoming call.")

    def Callee_Accepts_Call (self):
        self.Step (Message = "Callee accepts call...")

        self.Log (Message = "Callee agent accepts incoming call...")
        self.Callee.sip_phone.pickup_call ()
        self.Log (Message = "Callee agent has picked up the incoming call.")

    def Callee_Receives_Hangup (self):
        self.Step (Message = "Callee receives hangup on active call...")

        self.Log (Message = "Callee agent waits for hangup on active call...")
        self.Callee.sip_phone.wait_for_hangup ()
        self.Log (Message = "Callee agent got a hangup on the active call.")

    def Call_Announced (self):
        self.Step (Message = "Receptionist's client waits for 'call_offer'...")

        try:
            self.Receptionist.event_stack.WaitFor ("call_offer")
        except TimeOutReached:
            logging.critical (self.Receptionist.event_stack.dump_stack ())
            self.fail ("Call offer didn't arrive from Call-Flow-Control.")

        if not self.Receptionist.event_stack.stack_contains (event_type="call_offer",
                                                             destination=self.Reception):
            logging.critical (self.Receptionist.event_stack.dump_stack ())
            self.fail ("The arrived call offer was not for the expected reception (destination).")

        return self.Receptionist.event_stack.Get_Latest_Event (Event_Type="call_offer", Destination=self.Reception)['call']['id'],\
               self.Receptionist.event_stack.Get_Latest_Event (Event_Type="call_offer", Destination=self.Reception)['call']['reception_id']

    def Call_Announced_As_Locked (self, Call_ID):
        self.Step (Message = "Call-Flow-Control sends out 'call_lock'...")

        try:
            self.Receptionist.event_stack.WaitFor (event_type = "call_lock",
                                                   call_id    = Call_ID,
                                                   timeout    = 20.0)
        except TimeOutReached:
            logging.critical (self.Receptionist.event_stack.dump_stack ())
            self.fail ("No 'call_lock' event arrived from Call-Flow-Control.")

        if not self.Receptionist.event_stack.stack_contains (event_type  = "call_lock",
                                                             destination = self.Reception,
                                                             call_id     = Call_ID):
            logging.critical (self.Receptionist.event_stack.dump_stack ())
            self.fail ("The arrived 'call_lock' event was not for the expected reception (destination).")

    def Call_Announced_As_Unlocked (self, Call_ID):
        self.Step (Message = "Call-Flow-Control sends out 'call_unlock'...")

        try:
            self.Receptionist.event_stack.WaitFor (event_type = "call_unlock",
                                                   call_id    = Call_ID)
        except TimeOutReached:
            logging.critical (self.Receptionist.event_stack.dump_stack ())
            self.fail ("No 'call_unlock' event arrived from Call-Flow-Control.")

        if not self.Receptionist.event_stack.stack_contains (event_type  = "call_unlock",
                                                             destination = self.Reception,
                                                             call_id     = Call_ID):
            logging.critical (self.Receptionist.event_stack.dump_stack ())
            self.fail ("The arrived 'call_unlock' event was not for the expected reception (destination).")

    def Request_Information (self, Reception_ID):
        self.Step (Message = "Requesting (updated) information about reception " + str (Reception_ID))

        Data_On_Reception = self.Reception_Database.Single (Reception_ID)

        self.Step (Message = "Received information on reception " + str (Reception_ID))

        return Data_On_Reception

    def Offer_To_Pick_Up_Call (self, Call_Flow_Control, Call_ID):
        self.Step (Message = "Client offers to answer call...")

        try:
            Call_Flow_Control.PickupCall (call_id = Call_ID)
        except:
            self.Log (Message = "Pick-up call returned an error of some kind.")

    def Call_Allocation_Acknowledgement (self, Call_ID, Receptionist_ID):
        self.Step (Message = "Receptionist's client waits for 'call_pickup'...")

        try:
            self.Receptionist.event_stack.WaitFor (event_type = "call_pickup",
                                                   call_id    = Call_ID)
        except TimeOutReached:
            logging.critical (self.Receptionist.event_stack.dump_stack ())
            self.fail ("No 'call_pickup' event arrived from Call-Flow-Control.")

        try:
            Event = self.Receptionist.event_stack.Get_Latest_Event (Event_Type = "call_pickup",
                                                                    Call_ID    = Call_ID)
        except:
            logging.critical (self.Receptionist.event_stack.dump_stack ())
            self.fail ("Could not extract the received 'call_pickup' event from the Call-Flow-Control client.")

        try:
            if not Event['call']['assigned_to'] == Receptionist_ID:
                logging.critical (self.Receptionist.event_stack.dump_stack ())
                self.fail ("The arrived 'call_pickup' event was for " + str (Event['call']['assigned_to']) + ", and not for " + str (Receptionist_ID) + " as expected.")
        except:
            logging.critical (self.Receptionist.event_stack.dump_stack ())
            raise

        self.Log (Message = "Call picked up: " + pformat (Event))

        return Event

