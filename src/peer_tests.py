import logging
import config
from call_flow_communication import callFlowServer

from sip_profiles import agent1103
from sip_utils import SipAccount, SipAgent

try:
    import unittest2 as unittest
except ImportError:
    import unittest

logging.basicConfig(level=logging.INFO)

class PeerTests(unittest.TestCase):

    cfs = callFlowServer(uri=config.call_flow_server_uri, authtoken=agent1103.authtoken)
    # Tests whether a call-flow server responds correctly to peer registrations
    # 
    def testRegisterAgent(self):
        sipagent = SipAgent(account=SipAccount(username=agent1103.username, password=agent1103.password, sip_port=agent1103.sipport))
    
        peer = self.cfs.peerList().locatePeer(agent1103.username)
        if peer ['registered']:
            self.fail("Peer seems to be already registered: " + str (peer))
        
        sipagent.Connect()
        peer = self.cfs.peerList().locatePeer(agent1103.username)
        if not peer ['registered']:
            self.fail("Peer does not seem to be registered: " + str (peer))
        
        sipagent.QuitProcess()
        peer = self.cfs.peerList().locatePeer(agent1103.username)
        if peer ['registered']:
            self.fail("Peer is still registered: " + str (peer))
    
