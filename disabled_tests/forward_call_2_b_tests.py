# -*- coding: utf-8 -*-
# https://github.com/AdaHeads/Hosted-Telephone-Reception-System/wiki/Use-case%3A-Sende-opkald-videre#variant-2b-1

from disabled_tests.forward_call import Test_Case

class Sequence_Diagram (Test_Case):
    def test_Run (self):
        try:
            Incoming_Call_ID = self.Preconditions ()

            self.Step (Message = "Receptionist-N     ->> Klient-N          [genvej: liste-med-sekundaere-numre]")
            self.Step (Message = "Receptionist-N     ->> Klient-N          [pil op/ned - nogle gange]")
            self.Step (Message = "Receptionist-N     ->> Klient-N          [genvej: ring-markeret-nummer-op]")
            Outgoing_Call_ID = self.Receptionist_Places_Call (Number = self.Callee.extension)
            self.Step (Message = "Call-Flow-Control  ->> FreeSWITCH        [ring-op: nummer, telefon-N]")
            self.Callee_Receives_Call ()
            self.Step (Message = "FreeSWITCH         ->  FreeSWITCH        [forbind opkald med telefon-N]")
            self.Receptionist_Hears_Dialtone ()
            self.Step (Message = "Callee phone rings.")
            self.Step (Message = "Receptionist-N     ->> Klient-N          [genvej: opgiv-opkald]")
            self.Receptionist_Hangs_Up (Call_ID = Outgoing_Call_ID)
            self.Step (Message = "Call-Flow-Control  ->> FreeSWITCH        [afslut telefon-N's udgaaende opkald]")
            self.Callee_Receives_Hang_Up ()
            self.Step (Message = "FreeSWITCH         ->  FreeSWITCH        [forbind opkalder og telefon-N]")
            self.Step (Message = "=== loop ===")
            self.Step (Message = "Receptionist-N     ->> Telefon-N         [snak]")
            self.Step (Message = "Telefon-N          ->> FreeSWITCH        [SIP: lyd]")
            self.Step (Message = "FreeSWITCH         ->> Opkalder          [SIP: lyd]")
            self.Step (Message = "Opkalder           ->> FreeSWITCH        [SIP: lyd]")
            self.Step (Message = "FreeSWITCH         ->> Telefon-N         [SIP: lyd]")
            self.Step (Message = "Telefon-N          ->> Receptionist-N    [snak]")
            self.Step (Message = "=== end loop ===")

            self.Postprocessing ()
        except:
            self.Postprocessing ()
            raise

