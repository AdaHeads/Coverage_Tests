# https://github.com/AdaHeads/Hosted-Telephone-Reception-System/wiki/Use-case%3A-Finde-en-kontakt#wiki-variant-2-1

from find_contact import Test_Case

class Sequence_Diagram (Test_Case):
    def test_Run (self):
        try:
            self.Preconditions ()

            self.Step (Message = "Receptionist-N     ->> Klient-N          [genvejstast-for-kontaktliste]")
            self.Step (Message = "Receptionist-N    <<-  Klient-N          [fokus: kontaktliste og soegefelt]")
            self.Step (Message = "=== loop ===")
            self.Step (Message = "Receptionist-N     ->> Klient-N          [any character]")
            self.Step (Message = "Klient-N           ->> Receptionist-N    [narrow down contact list]")
            self.Step (Message = "Receptionist-N    <<-  Klient-N          [update contact view]")
            self.Step (Message = "=== end loop ===")
            self.Step (Message = "=== loop ===")
            self.Step (Message = "Receptionist-N     ->> Klient-N          [arrow up/down]")
            self.Step (Message = "Receptionist-N    <<-  Klient-N          [update contact view]")
            self.Step (Message = "=== end loop ===")

            self.Postprocessing ()
        except:
            self.Postprocessing ()
            raise

