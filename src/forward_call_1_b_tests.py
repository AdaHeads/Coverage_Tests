# https://github.com/AdaHeads/Hosted-Telephone-Reception-System/wiki/Use-case%3A-Sende-opkald-videre#wiki-variant-1b-1

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
            self.Step (Message = "Callee phone rings.")
            self.Step (Message = "Receptionist-N     ->> Klient-N          [genvejstast-opgiv-opkald]")
            self.Receptionist_Hangs_Up ()
            self.Step (Message = "Call-Flow-Control  ->> FreeSWITCH        [afslut telefon-N's udgaaende opkald]")
            self.Step (Message = "FreeSWITCH         ->> Medarbejder       [SIP: hang-up]")
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

