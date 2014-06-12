__author__ = 'krc'

####
#
#  Tests protocol interface documented at:
#  https://github.com/AdaHeads/DatabaseServers/wiki/Server-Reception
#

import config
import logging
import time


# Exceptions
from database_reception import Server_404, Database_Reception

try:
    import unittest2 as unittest
except ImportError:
    import unittest

class Reception_List(unittest.TestCase):

    log = logging.getLogger(__name__)
    server = Database_Reception(uri=config.reception_server_uri,authtoken=config.global_token)

    def test_CORS_headers_present(self):
        headers, body = self.server.Request ("/nonexistingpath", exceptions=False)
        assert 'access-control-allow-origin' in headers or 'Access-Control-Allow-Origin' in headers

        reception_id = 1

        self.log.info ("Looking up reception " + str(reception_id) +".")
        headers, body = self.server.Request("/reception/"+str(reception_id))
        assert 'access-control-allow-origin' in headers or 'Access-Control-Allow-Origin' in headers

    def test_nonexisting_uri(self):
        try:
            self.server.Request ("/nonexistingpath")
        except Server_404:
            return

        self.fail("Expected 404 here.")

    def test_found(self):
        reception_id = 1

        self.log.info ("Looking up reception " + str(reception_id))
        reception = self.server.get (reception_id=reception_id)

    def test_found_single(self):
        reception_id = 1

        self.log.info ("Looking up reception " + str(reception_id) +".")
        self.server.get (reception_id=reception_id)

    def test_not_found_single(self):
        reception_id = -1

        self.log.info ("Looking up reception " + str(reception_id) +".")
        try:
            self.server.get (reception_id=reception_id)
        except Server_404:
            return

        self.fail("Expected 404 here.")

    def test_calendar_single_lookup_single(self):
        reception_id = 1
        event_id     = 4

        self.log.info ("Looking up contact reception " + str(reception_id) +".")
        event = self.server.calendar_event (reception_id = reception_id,
                                            event_id     = event_id)

    def test_calendar_create(self):
        start        = time.time() #NOW

        reception_id = 1

        event        = {'event' : {'start'  : int(start),
                                   'stop'   : int(start)+3600,
                                   'content': 'Merely a reception event test.'}}

        self.log.info ("Looking up reception " + str(reception_id) +".")
        response = self.server.calendar_event_create (reception_id = reception_id,
                                                      event        = event)

    def test_calendar_update(self):
        start        = time.time() #NOW

        reception_id = 1

        events = self.server.calendar_events (reception_id = reception_id)['CalendarEvents']

        last_event      = events[-1]

        event        = self.server.calendar_event (reception_id = reception_id,
                                                   event_id     = last_event['id'])
        # bump start time
        event['event']['start'] = int(start)
        event['event']['stop']  = int(start)+3600

        self.log.info ("Looking up contact reception " + str(reception_id) +".")
        response = self.server.calendar_event_update (reception_id = reception_id,
                                                      event_id     = last_event['id'],
                                                      event        = event)


        remote_event = self.server.calendar_event (reception_id = reception_id,
                                                   event_id     = last_event['id'])

        assert (event['event']['start']   == remote_event['event']['start'])
        assert (event['event']['stop']    == remote_event['event']['stop'])
        assert (event['event']['content'] == remote_event['event']['content'])


    def test_calendar_list(self):
        reception_id = 1

        events = self.server.calendar_events (reception_id = reception_id)

    def test_calendar_delete(self):
        reception_id = 1

        events = self.server.calendar_events (reception_id = reception_id)['CalendarEvents']

        previous_length = len(events)
        last_event      = events[-1]

        response = self.server.calendar_event_delete (reception_id = reception_id,
                                                      event_id     = last_event['id'])
        #Refetch the event list
        events = self.server.calendar_events (reception_id = reception_id)['CalendarEvents']

        assert (len(events) != previous_length)

        self.log.info ("Looking up calendar of reception " + str(reception_id) +".")
        try:
           self.server.calendar_event (reception_id = reception_id,
                                       event_id     = last_event['id'])
        except Server_404:
            return

        self.fail("Expected 404 here.")
