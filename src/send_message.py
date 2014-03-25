# -*- coding: utf-8 -*-
import logging
from time       import clock, sleep

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from database_message        import Database_Message
from static_agent_pools      import Receptionists

import config

class Test_Case (unittest.TestCase):
    Receptionist       = None
    Message_Database   = None
    Start_Time         = None
    Next_Step          = 1

    def Preconditions (self):
        self.Start_Time = clock ()
        self.Next_Step  = 1

        self.Log ("Send message test case: Setting up preconditions...")

        self.Log ("Requesting a receptionist...")
        self.Receptionist = Receptionists.request ()

        self.Log ("Select a reception database connection...")
        self.Message_Database = Database_Message (uri       = config.message_server_uri,
                                                  authtoken = self.Receptionist.call_control.authtoken)

        self.Log ("Send message test case: Preconditions set up.")

    def Postprocessing (self):
        self.Step ("Send message test case: Cleaning up after test...")

        if not self.Receptionist is None:
            self.Receptionist.release ()

        self.Step ("Send message test case: Done cleaning up after test.")

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

    def Receptionist_Send_Message (self):
        self.Step (Message = "Receptionist sends a message...")
        self.Message_Database.Request(path   = Database_Message.Protocol.send,
                                      method = "POST",
                                      params = "{\"to\": [\"1@1\"], \"message\": \"Jens må gerne ringe til Peter.\"}")
        self.Step (Message = "Receptionist has sent message.")

