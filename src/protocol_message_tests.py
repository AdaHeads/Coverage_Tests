# -*- coding: utf-8 -*-
__author__ = 'krc'

####
#
#  Tests protocol interface documented at:
#  https://github.com/AdaHeads/DatabaseServers/wiki/Protocol-Message
#

import config
import logging
import random

# Exceptions
from database_message import Server_404, Database_Message

try:
    import unittest2 as unittest
except ImportError:
    import unittest


messages = [u'I\'m selling these fine leather jackets',
            u'Please call me back regarding stuff',
            u'I love the smell of pastry',
            u'Regarding your enlargement',
            u'Nigerian royalties wish to send you money',
            u'Call back soon',
            u'The cheese has started to smell',
            u'Are you paying for that?',
            u'Imagination land called',
            u'Roller coasters purchase',
            u'These are not the droids you are looking for. Come to me for new ones!',
            u'All your base are belong',
            u'I would love to change the world, but they won\'t give me the source code']

callers  = [u'Bob Barker',
            u'Mister Green',
            u'Walter White',
            u'Boy Wonder',
            u'Batman',
            u'Perry the Platypus',
            u'Ferb Fletcher',
            u'Phineas Flynn',
            u'Candace Flynn',
            u'Dr. Heinz Doofenshmirtz',
            u'Reed Richards (Mr. Fantastic)',
            u'Peter Parker (Spiderman)',
            u'Bruce Banner (the Hulk)',
            u'Matt Murdock (Daredevil)',
            u'Susan Storm (Invisible Girl)',
            u'Scott Summers (Cyclops)',
            u'Stephen Strange (Dr. Strange)',
            u'Darkwing Duck']

companies = [u'Acme inc',
             u'Wayne Enterprise',
             u'Ghostbusters A/S',
             u'Slamtroldmanden',
             u'Kødbollen A/S',
             u'Blomme\'s Gartneri',
             u'Hummerspecialisten ApS',
             u'Gnaske-Grønt ApS',
             u'Firmanavn_der_fortæller_om_samtlige_produkter_hos_os A/S',
             u'BulgurKompaniget A/S',
             u'Andefødder Aps',
             u'Spirevippen I/S',
             u'Petersen\'s Globale Kobberudvinding',
             u'PingPong ApS',
             u'Kasper\'s Køkken A/S',
             u'Den Varme Radiator ApS',
             u'KludeCentralen ApS',
             u'MobileAdvolaterne A/S',
             u'Bogforlaget A/S',
             u'Revisor Søren ApS',
             u'Kalle\'s Dyrefoder ApS',
             u'Den Varme Radiator ApS',
             u'KludeCentralen ApS',
             u'MobileAdvolaterne A/S',
             u'Bogforlaget A/S',
             u'Revisor Søren ApS',
             u'Kalle\'s Dyrefoder ApS',
             u'Fantasibureauet A/S',
             u'Fem Flade fisk I/S',
             u'Advokatkontoret',
             u'Gave-Ideer ApS',
             u'Det Tredie Firmanavn I/S',
             u'Kraniosakralklinikken ApS',
             u'Hvalbøffer A/S',
             u'De gode ideer ApS',
             u'Super-supporten A/S',
             u'Doozerne A/S',
             u'Sublim Forskning A/S',
             u'Hårtotten ApS',
             u'Alt til katten A/S',
             u'Sjov og Spas',
             u'Humørbomben K/S',
             u'Kurts kartoffelskrællerservice',
             u'Det absolutte nulpunkt',
             u'Den hellige ko-kebab',
             u'Peters pottemageri',
             u'Reklamegas Aps',
             u'Lenes lækre lune lagner I/S',
             u'Grine-Gerts anti-depressiver',
             u'Kasse-kompaniet',
             u'Hårstiverne']

flagsLists = [[],
              ["pleaseCall"],
              ['urgent.','pleaseCall'],
              ['hasCalled', 'pleaseCall'],
              ["willCallBack"],
              ["urgent"],
              ["urgent","willCallBack"]]

class Message(unittest.TestCase):

    log = logging.getLogger(__name__ + ".Message")
    server = Database_Message(uri=config.message_server_uri,authtoken=config.global_token)

    def test_CORS_headers_present(self):
        self.log.info ("Asserting that CORS headers are present on non-existing resources.")
        self.server.non_exisiting_path(exceptions=False)

        self.log.info ("Asserting that CORS headers are present on exisisting resources.")
        self.server.draft_list()

    def test_nonexisting_uri(self):
        try:
            self.server.non_exisiting_path()
        except Server_404:
            return

        self.fail("Expected 404 here.")

    def test_message_list(self):
        self.server.message_list()

    def test_draft_list (self):
        self.server.draft_list()

    def test_message_send_single (self):
        #TODO: Extract a random contact from the contact server.
        message = {"recipients" :{
                    "to"          : [{
                       "contact"   : {
                           "id"   : 4,
                           "name" : "Kim (AdaHeads)"},
                       "reception" : {
                           "id"   : 1,
                           "name" : "AdaHeads K/S"},
                       },{
                       "contact"   : {
                           "id"   : 4,
                           "name" : "Kim (FF)"},
                       "reception" : {
                           "id"   : 3,
                           "name" : "Fishermans Friend"},
                       }],
                   "cc"          : [{
                       "contact"   : {
                           "id"   : 4,
                           "name" : "Frede Fiskeglad"},
                       "reception" : {
                           "id"   : 2,
                           "name" : "Fredes Fisk"},
                       }]},
                   "bcc"         : [],
                   "message"     : unicode(random.choice(messages)),
                   "context"     : {
                       "contact"   : {
                           "id"   : 4,
                           "name" : "Kim Rostgaard Christensen"},
                       "reception" : {
                           "id"   : 2,
                           "name" : unicode(random.choice(companies))},
                       },
                   "caller"       : { 'name'      : random.choice(callers),
                                      'company'   : random.choice(companies),
                                      'phone'     : '88224411',
                                      'cellphone' : '99331122'},
                   "flags"        : random.choice(flagsLists)}

        message_id = self.server.message_send (message)['id']

        server_message = self.server.message (message_id)


        assert (server_message['recipients']['to'] == message['recipients']['to'])
        assert (server_message['recipients']['cc'] == message['recipients']['cc'])
        assert (server_message['message']          == message['message'])
        assert (server_message['context']          == message['context'])
        assert (server_message['caller']           == message['caller'])
        assert (server_message['flags']            == message['flags'])


    def test_message_not_found(self):
        message_id = -1

        self.log.info ("Looking up message " + str(message_id))
        try:
            message = self.server.message (message_id=message_id)
        except Server_404:
            return

        self.fail("Expected 404 here.")

    def test_message_found(self):
        message_id = 1

        self.log.info ("Looking up message " + str(message_id))
        message = self.server.message (message_id=message_id)

    def test_draft_create(self):
        draft = {"to"          : ["1@2", "4@2"],
                 "cc"          : ["4@2"],
                 "bcc"         : [],
                 "message"     : random.choice(messages),
                 "toContactID" : 1,
                 "takenFrom"   : random.choice(callers),
                 "urgent"      : True}

        new_draft_id = self.server.draft_create (draft)['draft_id']
        new_draft    = self.server.draft_single(new_draft_id)['json']

        assert (new_draft['to']          == draft['to'])
        assert (new_draft['cc']          == draft['cc'])
        assert (new_draft['message']     == draft['message'])
        assert (new_draft['toContactID'] == draft['toContactID'])

        draft = {"to"          : ["1@2", "4@2"],
                 "cc"          : ["4@2"],
                 "bcc"         : [],
                 "message"     : random.choice(messages),
                 "toContactID" : 3,
                 "takenFrom"   : random.choice(callers),
                 "urgent"      : True}

        self.server.draft_update (new_draft_id, draft)
        new_draft    = self.server.draft_single(new_draft_id)['json']

        assert (new_draft['to']          == draft['to'])
        assert (new_draft['cc']          == draft['cc'])
        assert (new_draft['message']     == draft['message'])
        assert (new_draft['toContactID'] == draft['toContactID'])

        self.server.draft_remove (draft_id=new_draft_id)


        try:
            self.server.draft_single(new_draft_id)
        except Server_404:
            return

        self.fail("Expected 404 here.")

