# -*- coding: utf-8 -*-
# https://github.com/AdaHeads/Hosted-Telephone-Reception-System/wiki/Use-case%3A-Sende-opkald-videre#wiki-variant-2ai-1

from forward_call import Test_Case
from config       import queued_reception as Reception

class Sequence_Diagram (Test_Case):
    def test_Run (self):
        try:
            self.Preconditions (Reception = Reception)

            self.Step (Message = "Receptionist-N     ->> Klient-N          [genvej: liste-med-sekundaere-numre]")
            self.Step (Message = "Receptionist-N     ->> Klient-N          [pil op/ned - nogle gange]")
            self.Step (Message = "Receptionist-N     ->> Klient-N          [genvej: ring-markeret-nummer-op]")
            self.Receptionist_Places_Call (Number = self.Callee.sip_uri ())
            self.Step (Message = "Call-Flow-Control  ->> FreeSWITCH        [ring-op: nummer, telefon-N]")
            self.Callee_Receives_Call ()
            self.Step (Message = "FreeSWITCH         ->  FreeSWITCH        [forbind opkald med telefon-N]")
            self.Receptionist_Hears_Dialtone ()
            self.Step (Message = "Callee phone rings.")
            self.Callee_Accepts_Call ()
            self.Step (Message = "=== loop ===")
            self.Step (Message = "Receptionist-N     ->> Telefon-N         [snak]")
            self.Step (Message = "Telefon-N          ->> FreeSWITCH        [SIP: lyd]")
            self.Step (Message = "FreeSWITCH         ->> Medarbejder       [SIP: lyd]")
            self.Step (Message = "Medarbejder        ->> FreeSWITCH        [SIP: lyd]")
            self.Step (Message = "FreeSWITCH         ->> Telefon-N         [SIP: lyd]")
            self.Step (Message = "Telefon-N          ->> Receptionist-N    [snak]")
            self.Step (Message = "=== end loop ===")
            self.Step (Message = "Receptionist-N     ->> Klient-N          [genvej: stil-igennem]")
            self.Receptionist_Forwards_Call (Incoming_Call = Call_ID,
                                             Outgoing_Call = Outgoing_Call_ID)
            self.Step (Message = "Klient-N           ->> Klient-N          [ny tilstand: ledig]")
            self.Step (Message = "Call-Flow-Control  ->> FreeSWITCH        [connect: incoming, outgoing]")
            self.Receptionist_Waits_For_Hang_Up ()
            self.Step (Message = "FreeSWITCH         ->> Call-Flow-Control [free: telefon-N]")
            self.Step (Message = "FreeSWITCH         ->> FreeSWITCH        [connect: incoming, outgoing]")

            self.Postprocessing ()
        except:
            self.Postprocessing ()
            raise

