import logging
from time import sleep

import config
from call_flow_communication import callFlowServer
from sip_profiles import agent1103 as anyAgent
from sip_utils import SipAccount, SipAgent
from agent_pool import AgentConfigs, AgentPool
from static_agent_pools import Receptionsts

try:
    import unittest2 as unittest
except ImportError:
    import unittest

logging.basicConfig(level=logging.INFO)

class PeerTests(unittest.TestCase):

    def testRegisterAgent(self):
        a1 = None
        try: #py.test src/peer_tests.py

            a1 = Receptionsts.Aquire()
            a1.SIP_Phone.Unregister()
            sleep(0.05)

            a1.Event_Stack.flush()
            a1.SIP_Phone.Register()
            a1.Event_Stack.WaitFor(event_type="peer_state")

            peer = a1.Call_Control.peerList().locatePeer(a1.username)
            if not peer ['registered']:
                self.fail (a1.username + " was expected to be registered at this point")

            a1.SIP_Phone.Unregister()
            peer = a1.Call_Control.peerList().locatePeer(a1.username)

            if peer ['registered']:
                self.fail("Peer is still registered: " + str (peer))

            logging.info ("Waiting")
            Receptionsts.Release(a1)
        except:
            if not a1 is None:
                Receptionsts.Release(a1)
            raise
