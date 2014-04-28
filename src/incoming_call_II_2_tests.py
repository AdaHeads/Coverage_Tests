# -*- coding: utf-8 -*-
# https://github.com/AdaHeads/Hosted-Telephone-Reception-System/wiki/Use-case%3A-Indg%C3%A5ende-opkald#variant-ii2-1

from incoming_calls import Test_Case
from config         import queued_reception as Reception

class Sequence_Diagram (Test_Case):
    def test_Run (self):
        try:
            self.Preconditions (Reception = Reception)

            self.Caller_Places_Call (Number = Reception)
            self.Caller_Hears_Dialtone ()
            self.Step (Message = "FreeSWITCH         ->  FreeSWITCH        [Checks dial-plan.  Result: Queue call.]")
            self.Step (Message = "FreeSWITCH         ->> Call-Flow-Control [event: call-offer; destination: Reception]")
            self.Step (Message = "FreeSWITCH: pauses dial-plan processing for # seconds")
            Call_ID, Reception_ID = self.Call_Announced ()
            self.Step (Message = "Call-Flow-Control  ->  Call-Flow-Control [wait 0.200 s]", Delay_In_Seconds = 0.200)
            self.Step (Message = "Call-Flow-Control  ->  Call-Flow-Control [no responses to call-offer]")
            self.Step (Message = "Call-Flow-Control  ->> FreeSWITCH        [force-end-pause: <call_ID>]")
            self.Step (Message = "FreeSWITCH         ->> Call-Flow-Control [queued-unavailable: <call_ID>]")
            self.Step (Message = "FreeSWITCH         ->> Opkalder          »De har ringet til <reception name>. Vent venligst.«")
            self.Call_Announced_As_Locked (Call_ID = Call_ID)
            self.Step (Message = "Klient-N           ->> Receptionist-N    [Queue: <reception name> (optaget)]")
            self.Step (Message = "FreeSWITCH->Call-Flow-Control: call queued with dial-tone")
            self.Step (Message = "FreeSWITCH->Caller: pause music")
            self.Call_Announced_As_Unlocked (Call_ID = Call_ID)
            self.Step (Message = "Client-N->Receptionist-N: Queue: <reception name> (venter)")
            self.Step (Message = "Receptionist-N->Client-N: take call")
            Reception_Data = self.Request_Information (Reception_ID = Reception_ID)
            self.Offer_To_Pick_Up_Call (Call_Flow_Control = self.Receptionist.call_control,
                                        Call_ID           = Call_ID)
            Call_Information = self.Call_Allocation_Acknowledgement (Call_ID         = Call_ID,
                                                                     Receptionist_ID = self.Receptionist.ID)
            self.Step (Message = "Call-Flow-Control->FreeSWITCH: connect call to phone-N")
            self.Receptionist_Answers (Call_Information      = Call_Information,
                                       Reception_Information = Reception_Data,
                                       After_Greeting_Played = True)

            self.Postprocessing ()
        except:
            self.Postprocessing ()
            raise
