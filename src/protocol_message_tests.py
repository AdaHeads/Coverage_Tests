__author__ = 'krc'

####
#
#  Tests protocol interface documented at:
#  https://github.com/AdaHeads/DatabaseServers/wiki/Server-Reception
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


messages = ["I'm selling these fine leather jackets",
            "Please call me back regarding stuff",
            "I love the smell of pastery",
            "Regarding your enlargement",
            "Nigirian royalties wish to send you money",
            'Call back soon',
            'The cheese has started to smell',
            'Are you paying for that?',
            'Imagination land called',
            'Roller coasters purchase']

callees  = ["Peter Paker",
            "Bob Barker",
            "Mister Green",
            "Walter White",
            "Boy Wonder",
            "Batman,"
            "Perry the Platypus",
            "Ferb Fletcher",
            "Phineas Flynn",
            "Candace Flynn",
            "Dr. Heinz Doofenshmirtz"]

urgencies = [True, False]

class Message(unittest.TestCase):

    log = logging.getLogger(__name__ + ".Message")
    server = Database_Message(uri=config.message_server_uri,authtoken=config.global_token)

    def test_CORS_headers_present(self):
        self.log.info ("Asserting that CORS headers are present on non-exisisting resources.")
        self.server.non_exisiting_path(exceptions=False)

        self.log.info ("Asserting that CORS headers are present on exisisting resources.")
        self.server.draft_list()

    def test_nonexisting_uri(self):
        try:
            self.server.non_exisiting_path()
        except Server_404:
            return

        self.fail("Expected 404 here.")


    def test_draft_list (self):
        self.server.draft_list()

    def test_message_send_single (self):
        #TODO: Extract the contact from the contact server.
        message = {"to"          : [{
                       "contact"   : {
                           "id"   : 1,
                           "name" : "A static person"},
                       "reception" : {
                           "id"   : 2,
                           "name" : "Person 1"},
                       },{
                       "contact"   : {
                           "id"   : 4,
                           "name" : "Another static person"},
                       "reception" : {
                           "id"   : 2,
                           "name" : "Person 2"},
                       }],
                   "cc"          : [{
                       "contact"   : {
                           "id"   : 3,
                           "name" : "A third static person"},
                       "reception" : {
                           "id"   : 2,
                           "name" : "Person 3"},
                       }],
                   #"bcc"         : [],
                   "message"     : random.choice(messages),
                   "context"     : {
                       "contact"   : {
                           "id"   : 1,
                           "name" : "A static person"},
                       "reception" : {
                           "id"   : 2,
                           "name" : "Person 1"},
                       },
                   "takenFrom"   : random.choice(callees),
                   "urgent"      : random.choice(urgencies)}

        self.server.message_send (message)

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
                 "takenFrom"   : random.choice(callees),
                 "urgent"      : True}

        new_draft_id = self.server.draft_create (draft)['draft_id']
        new_draft    = self.server.draft_single(new_draft_id)['json'];

        assert (new_draft['to']          == draft['to'])
        assert (new_draft['cc']          == draft['cc'])
        assert (new_draft['message']     == draft['message'])
        assert (new_draft['toContactID'] == draft['toContactID'])

        draft = {"to"          : ["1@2", "4@2"],
                 "cc"          : ["4@2"],
                 "bcc"         : [],
                 "message"     : random.choice(messages),
                 "toContactID" : 3,
                 "takenFrom"   : random.choice(callees),
                 "urgent"      : True}

        self.server.draft_update (new_draft_id, draft)
        new_draft    = self.server.draft_single(new_draft_id)['json'];

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

