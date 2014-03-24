# -*- coding: utf-8 -*-
# https://github.com/AdaHeads/Hosted-Telephone-Reception-System/wiki/Use-case%3A-Sende-en-besked#wiki-variant-1a-1

from send_message import Test_Case
from config       import queued_reception as Reception

class Sequence_Diagram (Test_Case):
    def test_Run (self):
        try:
            self.Preconditions ()

            self.Step (Message = "Receptionist-N     ->> Klient-N          [taster: navn]")
            self.Step (Message = "Receptionist-N     ->> Klient-N          [genvej: fokus-besked-tekst]")
            self.Step (Message = "Receptionist-N     ->> Klient-N          [taster: besked]")
            self.Step (Message = "=== Use-case: Find en kontakt ===")
            self.Step (Message = "=== Use-case: Send opkald videre ===")
            self.Step (Message = "Klient-N           ->> Klient-N          [ryd alle 'send besked'-felter]")
            self.Step (Message = "Receptionist-N    <<-  Klient-N          [ryddet 'send besked'-dialog]")

            self.Postprocessing ()
        except:
            self.Postprocessing ()
            raise

