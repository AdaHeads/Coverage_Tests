# https://github.com/AdaHeads/Hosted-Telephone-Reception-System/wiki/Use-case%3A-Sende-en-besked#wiki-variant-1bi-1

from send_message import Test_Case
from config       import queued_reception as Reception

class Sequence_Diagram (Test_Case):
    def test_Run (self):
        try:
            self.Preconditions (Reception = Reception)

            self.Step (Message = "Receptionist-N     ->> Klient-N          [taster: navn]")
            self.Step (Message = "Receptionist-N     ->> Klient-N          [genvej: fokus-besked-tekst]")
            self.Step (Message = "Receptionist-N     ->> Klient-N          [taster: besked]")
            self.Step (Message = "=== Use-case: Find en kontakt ===")
            self.Step (Message = "=== Use-case: Send opkald videre ===")
            self.Step (Message = "Receptionist-N     ->> Klient-N          [genvej: fokus-besked-tekst]")
            self.Step (Message = "Receptionist-N    <<-  Klient-N          [viser fokus: besked-tekst]")
            self.Step (Message = "Receptionist-N     ->> Klient-N          [retter beskeden]")
            self.Step (Message = "Receptionist-N     ->> Klient-N          [genvej: fokus-modtagerliste] (måske)")
            self.Step (Message = "Receptionist-N     ->> Klient-N          [retter modtagerlisten]")
            self.Step (Message = "Receptionist-N     ->> Klient-N          [genvej: send-besked]")
            self.Step (Message = "Klient-N           ->> Call-Flow-Control [send <besked> til <modtagerliste>]")
            self.Step (Message = "Call-Flow-Control  ->> Message-Spool     [send <besked> til <modtagerliste>]")
            self.Step (Message = "Message-Spool      ->> Medarbejder       [<besked>", note = "muligvis\ntil flere]")
            self.Step (Message = "Receptionist-N    <<-  Klient-N          [ryddet 'send besked'-dialog]")

            self.Postprocessing ()
        except:
            self.Postprocessing ()
            raise

