# https://github.com/AdaHeads/Hosted-Telephone-Reception-System/wiki/Use-case%3A-Indg%C3%A5ende-opkald#wiki-variant-i2a

from incoming_calls          import Test_Case
from sip_profiles            import agent1102 as Caller
from sip_profiles            import agent1103 as Receptionist
from config                  import queued_reception as Reception

class Sequence_Diagram (Test_Case):
    def test_Run (self):
        try:
            self.Preconditions (Caller       = Caller,
                                Receptionist = Receptionist,
                                Reception    = Reception)

            self.Caller_Places_Call ()
            self.Caller_Hears_Dialtone ()
            self.Step (Message = "FreeSWITCH: checks dial-plan => to queue")
            self.Step (Message = "FreeSWITCH->Call-Flow-Control: call queued with dial-tone")
            self.Step (Message = "FreeSWITCH: pauses dial-plan processing for # seconds")
            Call_ID, Reception_ID = self.Call_Announced ()
            self.Step (Message = "Client-N->Receptionist-N: shows call (with dial-tone)")
            self.Step (Message = "Receptionist-N->Client-N: take call")
            Reception_Data = self.Request_Information (Reception_ID = Reception_ID)
            self.Offer_To_Pick_Up_Call (Call_Flow_Control = self.Call_Flow_Control,
                                        Call_ID           = Call_ID)
            Call_Information = self.Call_Allocation_Acknowledgement (Call_ID         = Call_ID,
                                                                     Receptionist_ID = Receptionist.ID)
            self.Step (Message = "Client-N->Receptionist-N: Information on JSA R&I (with full greeting).")
            self.Step (Message = "Call-Flow-Control->FreeSWITCH: connect call to phone-N")
            self.Receptionist_Answers (Call_Information      = Call_Information,
                                       Reception_Information = Reception_Data,
                                       After_Greeting_Played = False)

            self.Client.stop ()
        except:
            if not self.Client == None:
                self.Client.stop ()
            raise
