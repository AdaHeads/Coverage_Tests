# -*- coding: utf-8 -*-
# https://github.com/AdaHeads/Hosted-Telephone-Reception-System/wiki/Use-case%3A-Indg%C3%A5ende-opkald#variant-i1aii-1

from disabled_tests.incoming_calls import Test_Case
from config         import queued_reception as Reception

class Sequence_Diagram (Test_Case):
    def test_Run (self):
        try:
            self.Preconditions (Reception = Reception)

            self.Caller_Places_Call (Number = Reception)
            self.Caller_Hears_Dialtone ()
            self.Step (Message = "FreeSWITCH: checks dial-plan => to queue")
            self.Step (Message = "FreeSWITCH->Call-Flow-Control: call queued with dial-tone")
            self.Step (Message = "FreeSWITCH: pauses dial-plan processing for # seconds")
            Call_ID, Reception_ID = self.Call_Announced ()
            self.Step (Message = "Client-N->Receptionist-N: shows call (with dial-tone)")
            Reception_Data = self.Request_Information (Reception_ID = Reception_ID)
            self.Log (Message = "- Call stealer interferes")
            self.Offer_To_Pick_Up_Call (Call_Flow_Control = self.Receptionist_2.call_control,
                                        Call_ID           = Call_ID)
            self.Log (Message = "We wait 210 ms to assure that client-N will miss the 200 ms time-window for responding.", Delay_In_Seconds = 0.210)
            self.Offer_To_Pick_Up_Call (Call_Flow_Control = self.Receptionist.call_control,
                                        Call_ID           = Call_ID)
            Call_Information = self.Call_Allocation_Acknowledgement (Call_ID         = Call_ID,
                                                                     Receptionist_ID = self.Receptionist_2.ID)
            self.Step (Message = "Client-N->Receptionist-N: Un-queue: <reception name>.")

            self.Postprocessing ()
        except:
            self.Postprocessing ()
            raise

