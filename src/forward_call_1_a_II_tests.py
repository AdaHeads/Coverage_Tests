# https://github.com/AdaHeads/Hosted-Telephone-Reception-System/wiki/Use-case%3A-Sende-opkald-videre#wiki-variant-1aii-1

from forward_call import Test_Case
from config       import queued_reception as Reception

class Sequence_Diagram (Test_Case):
    def test_Run (self):
        try:
            self.Preconditions (Reception = Reception)

            self.Step (Message = "Receptionist-N     ->> Klient-N          [genvejstast-ring-til-primaert-nummer]")
            self.Receptionist_Places_Call (Number = self.Callee.Number)
            self.Step (Message = "Call-Flow-Control  ->> FreeSWITCH        [ring-op: telefon-N, nummer]")
            self.Callee_Receives_Call ()
            self.Step (Message = "FreeSWITCH         ->> FreeSWITCH        [forbind opkald og telefon-N]")
            self.Receptionist_Hears_Dialtone ()
            self.Callee_Receives_Call ()
            self.Callee_Accepts_Call ()
            self.Step (Message = "=== loop ===")
            self.Step (Message = "Receptionist-N     ->> Telefon-N         [label = "snak]")
            self.Step (Message = "Telefon-N          ->> FreeSWITCH        [label = "SIP: lyd]")
            self.Step (Message = "FreeSWITCH         ->> Medarbejder       [label = "SIP: lyd]")
            self.Step (Message = "Medarbejder        ->> FreeSWITCH        [label = "SIP: lyd]")
            self.Step (Message = "FreeSWITCH         ->> Telefon-N         [label = "SIP: lyd]")
            self.Step (Message = "Telefon-N          ->> Receptionist-N    [label = "snak]")
            self.Step (Message = "=== end loop ===")
            self.Step (Message = "Receptionist-N     ->> Klient-N          [genvejstast-afslut-udgaaende-samtale]")
            self.Receptionist_Hangs_Up ()
            self.Step (Message = "Call-Flow-Control  ->> FreeSWITCH        [afslut telefon-N's udgaaende samtale]")
            self.Callee_Receives_Hangup ()
            self.Step (Message = "FreeSWITCH         ->  FreeSWITCH        [label = "forbind opkalder og telefon-N]")
            self.Step (Message = "=== loop ===")
            self.Step (Message = "Receptionist-N     ->> Telefon-N         [label = "snak]")
            self.Step (Message = "Telefon-N          ->> FreeSWITCH        [label = "SIP: lyd]")
            self.Step (Message = "FreeSWITCH         ->> Opkalder          [label = "SIP: lyd]")
            self.Step (Message = "Opkalder           ->> FreeSWITCH        [label = "SIP: lyd]")
            self.Step (Message = "FreeSWITCH         ->> Telefon-N         [label = "SIP: lyd]")
            self.Step (Message = "Telefon-N          ->> Receptionist-N    [label = "snak]")
            self.Step (Message = "=== end loop ===")

            self.Postprocessing ()
        except:
            self.Postprocessing ()
            raise

