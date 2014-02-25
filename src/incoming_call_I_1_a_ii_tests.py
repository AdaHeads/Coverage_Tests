# https://github.com/AdaHeads/Hosted-Telephone-Reception-System/wiki/Use-case%3A-Indg%C3%A5ende-opkald#wiki-variant-i1a2

from incoming_calls          import Test_Case
from sip_profiles            import agent1102 as Caller
from sip_profiles            import agent1103 as Receptionist
from sip_profiles            import agent1106 as Call_Stealer
from config                  import queued_reception as Reception

import logging

from time                    import sleep

from sip_utils               import SipAgent, SipAccount
from call_flow_communication import callFlowServer
from config                  import call_flow_server_uri as Call_Flow_Server_URI

class Incorrectly_Allocated_Call (Exception):
    pass

class Sequence_Diagram (Test_Case):
    Call_Stealing_Agent = None
    Call_Steal_Control  = None

    def Preconditions (self):
        super (Sequence_Diagram, self).Preconditions (Caller       = Caller,
                                                      Receptionist = Receptionist,
                                                      Reception    = Reception)

        logging.info ("Creating call stealing SIP agent...")
        self.Call_Stealing_Agent = SipAgent (account = SipAccount (username = Call_Stealer.username,
                                                                   password = Call_Stealer.password,
                                                                   sip_port = Call_Stealer.sipport))

        logging.info ("Connecting call stealing agent...")
        self.Call_Stealing_Agent.Connect ()

        logging.info ("Creating call stealing Call-Flow-Control connection...")
        self.Call_Steal_Control = callFlowServer (uri       = Call_Flow_Server_URI,
                                                  authtoken = Call_Stealer.authtoken)

        logging.info ("Checking call stealing token validity against Call-Flow-Control...")
        if self.Call_Steal_Control.TokenValid:
            logging.info ("Valid token.")
        else:
            self.fail ("Invalid call stealing authentication token.")

    def __del__ (self):
        self.Call_Stealing_Agent.QuitProcess ()

        super (Sequence_Diagram, self).__del__ ()

    def test_Run (self):
        try:
            self.Preconditions ()

            self.Caller_Places_Call ()
            self.Caller_Hears_Dialtone ()
            self.Step (Message = "FreeSWITCH: checks dial-plan => to queue")
            self.Step (Message = "FreeSWITCH->Call-Flow-Control: call queued with dial-tone")
            self.Step (Message = "FreeSWITCH: pauses dial-plan processing for # seconds")
            self.Step (Message = "Call-Flow-Control: finds free receptionists")
            Reception_ID = self.Call_Announced ()
            self.Step (Message = "Client-N->Receptionist-N: shows call (with dial-tone)")
            Reception_Data = self.Request_Information (Reception_ID = Reception_ID)

            logging.info ("- Call stealer interferes")
            self.Offers_To_Answer_Call (Call_Flow_Control = self.Call_Steal_Control,
                                        Reception_ID      = Reception_ID)
            Stolen_Call_Information = self.Call_Allocation_Acknowledgement (Reception_ID    = Reception_ID,
                                                                            Receptionist_ID = Call_Stealer.ID)
            self.Receptionist_Answers (Call_Information      = Stolen_Call_Information,
                                       Reception_Information = Reception_Data,
                                       After_Greeting_Played = False)
            sleep (0.250)
            logging.info ("- Now we expect that the call stealer has succeeded")

            self.Offers_To_Answer_Call (Call_Flow_Control = self.Call_Flow_Control,
                                        Reception_ID      = Reception_ID)
            try:
                Call_Information = self.Call_Allocation_Acknowledgement (Reception_ID    = Reception_ID,
                                                                         Receptionist_ID = Receptionist.ID)
                raise Incorrectly_Allocated_Call
            except Incorrectly_Allocated_Call:
                self.fail("The incoming call was somehow allocated to the late receptionist. :-(")
            except:
                logging.info ("We're happy to note that the receptionist - as planned - didn't get the call.")

            self.Client.stop ()
        except:
            if not self.Client == None:
                self.Client.stop ()
            raise
