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
from config                  import queued_reception as Reception

class Call_Failure (Exception):
    pass

class Test_Case (unittest.TestCase):
    Caller             = None
    Receptionist       = None
    Receptionist_2     = None
    Callee             = None

    Reception_Database = None

    Start_Time         = None
    Next_Step          = 1

    def Preconditions (self):
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

        self.Log ("Select a reception database connection...")
        self.Reception_Database = Database_Reception (uri       = config.reception_server_uri,
                                                      authtoken = self.Receptionist.call_control.authtoken)

        self.Next_Step = 0
        self.Caller_Places_Call (Number = Reception)

        self.Next_Step = 0
        Call_ID, Reception_ID = self.Call_Announced ()

        self.Next_Step = 0
        self.Offer_To_Pick_Up_Call (Call_Flow_Control = self.Receptionist.call_control,
                                    Call_ID           = Call_ID)

        self.Log ("Forward call test case: Preconditions set up.")
        self.Log ("Forward call test case: Returning ID of incoming call...")
        return Call_ID

    def Postprocessing (self):
        self.Step ("Forward call test case: Cleaning up after test...")

        if not self.Caller is None:
            self.Caller.release ()
            self.Caller = None
        if not self.Receptionist is None:
            self.Receptionist.release ()
            self.Receptionist = None
        if not self.Receptionist_2 is None:
            self.Receptionist_2.release ()
            self.Receptionist_2 = None
        if not self.Callee is None:
            self.Callee.release ()
            self.Callee = None

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
        self.Next_Step += 1

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
        try:
            Response = self.Receptionist.call_control.Originate_Arbitrary (contact_id = "2",
                                                                       reception_id = "1",
                                                                       extension = Number)
            self.Log (Message = "Call-Flow-Control has accepted request to place call.")
            return Response["call"]["id"]
        except:
            self.Log (Message = "Receptionist failed to place call.")
            raise Call_Failure ("Failed to call " + str (Number) + ".")

    def Receptionist_Hears_Dialtone (self):
        self.Step (Message = "Receptionist hears dial-tone...")
        self.Log (Message = "(we assume, as we can't test it directly with our current setup)")

    def Receptionist_Hangs_Up (self, Call_ID):
        self.Step (Message = "Receptionist hangs up...")
        self.Receptionist.hang_up (call_id = Call_ID)
        self.Log (Message = "Succeeded hanging up " + str (Call_ID) + ".")

    def Receptionist_Waits_For_Hang_Up (self):
        self.Step (Message = "Receptionist waits for hangs up...")
        self.Receptionist.event_stack.WaitFor (event_type = "call_hangup")

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

    def Receptionist_Forwards_Call (self, Incoming_Call, Outgoing_Call):
        self.Step (Message = "Receptionist forwards call...")

        self.Log (Message = "Waiting for 'call_pickup' event...")
        self.Receptionist.event_stack.WaitFor (event_type = "call_pickup")

        self.Log (Message = "Grabbing the 'call_pickup' event...")
        originate_event = self.Receptionist.event_stack.Get_Latest_Event (Event_Type = "call_pickup")

        self.assertEquals (originate_event['call']['b_leg'], Outgoing_Call)

        self.Log (Message = "Transfer the incoming call to the A leg of the outgoing call...")
        self.Receptionist.call_control.TransferCall (source      = originate_event['call']['id'],
                                                     destination = Incoming_Call)

        self.Log (Message = "Waiting for the 'call_transfer' event...")
        self.Receptionist.event_stack.WaitFor (event_type = "call_transfer")

        self.Log (Message = "Receptionist has forwarded call.")

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

    def Callee_Receives_Hang_Up (self):
        self.Step (Message = "Callee receives hangup on active call...")

        self.Log (Message = "Callee agent waits for hangup on active call...")
        #self.Callee.sip_phone.wait_for_hangup ()
        self.Log (Message = "Callee agent got a hangup on the active call.")
        raise NotImplementedError

    def Call_Announced (self):
        self.Step (Message = "Receptionist's client waits for 'call_offer'...")

        try:
            self.Receptionist.event_stack.WaitFor ("call_offer")
        except TimeOutReached:
            logging.critical (self.Receptionist.event_stack.dump_stack ())
            self.fail ("Call offer didn't arrive from Call-Flow-Control.")

        if not self.Receptionist.event_stack.stack_contains (event_type="call_offer",
                                                             destination=Reception):
            logging.critical (self.Receptionist.event_stack.dump_stack ())
            self.fail ("The arrived call offer was not for the expected reception (destination).")

        Event = self.Receptionist.event_stack.Get_Latest_Event (Event_Type="call_offer", Destination=Reception)

        return Event['call']['id'],\
               Event['call']['reception_id']

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
                                                             destination = Reception,
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
                                                             destination = Reception,
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

