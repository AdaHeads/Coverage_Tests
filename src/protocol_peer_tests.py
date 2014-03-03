import logging
from time import sleep

import config
from call_flow_communication import callFlowServer
from sip_profiles import agent1103 as anyAgent
from sip_utils import SipAccount, SipAgent

from static_agent_pools import Receptionists

try:
    import unittest2 as unittest
except ImportError:
    import unittest

logging.basicConfig(level=logging.INFO)

from static_agent_pools import Receptionists, Customers

class Peer(unittest.TestCase):

    log = logging.getLogger(__name__ + ".Peer")

    def test_event_and_list_presence(self):
        try: #py.test src/protocol_peer_tests.py

            self.log.info ("Unregistering agent to assert that we get a registration event.")
            receptionist = Receptionists.request()
            receptionist.sip_phone.Unregister()


            self.log.info ("Flushing event stack.")
            receptionist.event_stack.flush() # Purge any registration events.

            self.log.info ("Registering receptionst sip agent.")
            receptionist.sip_phone.Register()
            self.log.info ("Expecting peer_state event.")
            receptionist.event_stack.WaitFor(event_type="peer_state")

            self.log.info ("Event received, looking up receptionist in peerlist.")
            peer = receptionist.call_control.peerList().locatePeer(receptionist.username)
            if not peer ['registered']:
                self.fail (receptionist.username + " expected to be in peer list at this point")

            self.log.info ("Flushing event stack.")
            receptionist.event_stack.flush() # Purge any registration events.

            self.log.info ("Unregistering agent again to complete cycle.")
            receptionist.sip_phone.Unregister()

            self.log.info ("Expecting peer_state event.")
            receptionist.event_stack.WaitFor(event_type="peer_state")

            self.log.info ("Event received, looking up receptionist in peerlist.")
            peer = receptionist.call_control.peerList().locatePeer(receptionist.username)
            if peer ['registered']:
                self.fail("Peer is still registered: " + str (peer))

            self.log.info ("Peer is no longer registered, run complete.")
            receptionist.release()

        except:
            receptionist.release()
            raise