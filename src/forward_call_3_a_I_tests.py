# https://github.com/AdaHeads/Hosted-Telephone-Reception-System/wiki/Use-case%3A-Sende-opkald-videre#wiki-variant-3ai-1

from forward_call import Test_Case
from config       import queued_reception as Reception

class Sequence_Diagram (Test_Case):
    def test_Run (self):
        try:
            self.Preconditions (Reception = Reception)

            self.Step (Message = "Receptionist-N     ->> Klient-N          [genvejstast-viderestil-til-nummer]")
            self.Step (Message = "Klient-N           ->> Receptionist-N    [indtastningsfelt: telefonnummer]")
            self.Step (Message = "Receptionist-N     ->> Klient-N          [indtaster/indkopierer nummer]")
            self.Step (Message = "Receptionist-N     ->> Klient-N          [genvejstast-ring-op]")
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
            self.Step (Message = "Receptionist-N     ->> Klient-N          [genvejstast-stil-igennem]")
            self.Step (Message = "Klient-N           ->> Call-Flow-Control [stil-igennem]")
            self.Step (Message = "Klient-N           ->> Klient-N          [ny tilstand: ledig]")
            self.Step (Message = "Call-Flow-Control  ->> FreeSWITCH        [connect: incoming, outgoing]")
            self.Step (Message = "FreeSWITCH         ->> Telefon-N         [SIP: hang-up]")
            self.Step (Message = "FreeSWITCH         ->> Call-Flow-Control [free: telefon-N]")
            self.Step (Message = "FreeSWITCH         ->> FreeSWITCH        [connect: incoming, outgoing]")

            self.Postprocessing ()
        except:
            self.Postprocessing ()
            raise

