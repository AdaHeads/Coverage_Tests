# https://github.com/AdaHeads/Hosted-Telephone-Reception-System/wiki/Use-case%3A-Sende-opkald-videre#wiki-variant-2b-1

from forward_call import Test_Case
from config       import queued_reception as Reception

class Sequence_Diagram (Test_Case):
    def test_Run (self):
        try:
            self.Preconditions (Reception = Reception)

            self.Step (Message = "Receptionist-N     ->> Klient-N          [genvejstast-liste-med-sekundaere-numre]")
            self.Step (Message = "Receptionist-N     ->> Klient-N          [pil op/ned - nogle gange]")
            self.Step (Message = "Receptionist-N     ->> Klient-N          [genvejstast-ring-markeret-nummer-op]")
            self.Receptionist_Places_Call (Number = self.Callee.Number)
            self.Step (Message = "Call-Flow-Control  ->> FreeSWITCH        [ring-op: nummer, telefon-N]")
            self.Callee_Receives_Call ()
            self.Step (Message = "FreeSWITCH         ->  FreeSWITCH        [forbind opkald med telefon-N]")
            self.Receptionist_Hears_Dialtone ()
            self.Callee_Receives_Call ()
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

