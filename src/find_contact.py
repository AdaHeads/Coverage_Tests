import logging
from time       import clock, sleep

try:
    import unittest2 as unittest
except ImportError:
    import unittest

logging.basicConfig (level = logging.INFO)

class Test_Case (unittest.TestCase):
    Start_Time         = None
    Next_Step          = 1

    def Preconditions (self):
        self.Start_Time = clock ()
        self.Next_Step  = 1

        self.Log ("Find contact test case: Setting up preconditions...")

    def Postprocessing (self):
        self.Log ("Find contact test case: Cleaning up after test...")

    def Step (self,
              Message,
              Delay_In_Seconds = 0.0):
        if self.Next_Step is None:
            self.Next_Step = 1
        if self.Start_Time is None:
            self.Start_Time = clock ()

        logging.info ("Step " + str (self.Next_Step) + "@" + str (clock() - self.Start_Time) + ": " + Message)
        sleep (Delay_In_Seconds)
        self.Next_Step = self.Next_Step + 1

    def Log (self,
             Message,
             Delay_In_Seconds = 0.0):
        if self.Next_Step is None:
            self.Next_Step = 1
        if self.Start_Time is None:
            self.Start_Time = clock ()

        logging.info ("     " + str (self.Next_Step - 1) + "@" + str (clock() - self.Start_Time) + ": " + Message)
        sleep (Delay_In_Seconds)

