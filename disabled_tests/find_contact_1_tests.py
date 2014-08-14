# -*- coding: utf-8 -*-
# https://github.com/AdaHeads/Hosted-Telephone-Reception-System/wiki/Use-case%3A-Finde-en-kontakt#variant-1-1

from disabled_tests.find_contact import Test_Case

class Sequence_Diagram (Test_Case):
    def test_Run (self):
        try:
            self.Preconditions ()

            self.Step (Message = "Receptionist-N     ->> Klient-N          [genvej: for-kontaktliste]")
            self.Step (Message = "Receptionist-N    <<-  Klient-N          [fokus: kontaktliste og soegefelt]")
            self.Step (Message = "=== loop ===")
            self.Step (Message = "Receptionist-N     ->> Klient-N          [arrow up/down]")
            self.Step (Message = "Receptionist-N    <<-  Klient-N          [update contact view]")
            self.Step (Message = "=== end loop ===")

            self.Postprocessing ()
        except:
            self.Postprocessing ()
            raise

