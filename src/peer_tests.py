import logging
import config
from call_flow_communication import callFlowServer

from sip_profiles import agent1107
from sip_utils import SipAccount, SipAgent

try:
    import unittest2 as unittest
except ImportError:
    import unittest

logging.basicConfig(level=logging.INFO)

class PeerTests(unittest.TestCase):

    cfs = callFlowServer(uri=config.call_flow_server_uri, authtoken=agent1107.authtoken)
    # Tests whether a call-flow server responds correctly to peer registrations
    # 
    def testRegisterAgent(self):
        sipagent = SipAgent(account=SipAccount(username=agent1107.username, password=agent1107.password, sip_port=agent1107.sipport))
    
        peer = self.cfs.peerList().locatePeer(agent1107.username)
        if peer ['registered']:
            self.fail("Peer seems to be already registered: " + peer.toString())
        
        sipagent.Connect()
        peer = self.cfs.peerList().locatePeer(agent1107.username)
        if not peer ['registered']:
            self.fail("Peer does not seem to be registered: " + peer.toString())
        
        sipagent.QuitProcess()
        peer = self.cfs.peerList().locatePeer(agent1107.username)
        if peer ['registered']:
            self.fail("Peer is still registered: " + peer.toString())
    
