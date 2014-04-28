# -*- coding: utf-8 -*-
# https://github.com/AdaHeads/Hosted-Telephone-Reception-System/wiki/Use-case%3A-Sende-opkald-videre#variant-3aii-1

from forward_call import Test_Case

class Sequence_Diagram (Test_Case):
    def test_Run (self):
        try:
            Incoming_Call_ID = self.Preconditions ()

            self.Step (Message = "Receptionist-N     ->> Klient-N          [genvej: viderestil-til-nummer]")
            self.Step (Message = "Klient-N           ->> Receptionist-N    [indtastningsfelt: telefonnummer]")
            self.Step (Message = "Receptionist-N     ->> Klient-N          [indtaster/indkopierer nummer]")
            self.Step (Message = "Receptionist-N     ->> Klient-N          [genvej: ring-op]")
            Outgoing_Call_ID = self.Receptionist_Places_Call (Number = self.Callee.sip_uri ())
            self.Step (Message = "Call-Flow-Control  ->> FreeSWITCH        [samtale: telefon-N, <nummer>]")
            self.Step (Message = "FreeSWITCH         ->> Telefon-N         [SIP: opkald]")
            self.Step (Message = "FreeSWITCH         ->> Medarbejder       [SIP: opkald]")
            self.Step (Message = "FreeSWITCH         ->> FreeSWITCH        [Brokobler opkald.]")
            self.Receptionist_Receives_Call ()
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
            self.Step (Message = "Receptionist-N     ->> Klient-N          [genvej: afslut-udgaaende-samtale]")
            self.Receptionist_Hangs_Up (Call_ID = Outgoing_Call_ID)
            self.Step (Message = "Call-Flow-Control  ->> FreeSWITCH        [afslut telefon-N's udgaaende samtale]")
            self.Callee_Receives_Hangup ()
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

