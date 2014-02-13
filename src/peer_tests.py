import logging
import config
from call_flow_communication import callFlowServer

from sip_profiles import customer3
from sip_utils import SipAccount, SipAgent

try:
    import unittest2 as unittest
except ImportError:
    import unittest

logging.basicConfig(level=logging.INFO)

class PeerTests(unittest.TestCase):

    cfs = callFlowServer(uri=config.call_flow_server_uri, authtoken=config.authtoken)
    # Tests whether a call-flow server responds correctly to peer registrations
    # 
    def testRegisterAgent(self):
        sipagent = SipAgent(account=SipAccount(username=customer3.username, password=customer3.password, sip_port=customer3.sipport))
    
        peer = self.cfs.peerList().locatePeer(customer3.username)
        if peer ['registered']:
            self.fail("Peer seems to be already registered: " + peer.toString())
        
        sipagent.Connect()
        peer = self.cfs.peerList().locatePeer(customer3.username)
        if not peer ['registered']:
            self.fail("Peer does not seem to be registered: " + peer.toString())
        
        sipagent.QuitProcess()
        peer = self.cfs.peerList().locatePeer(customer3.username)
        if peer ['registered']:
            self.fail("Peer is still registered: " + peer.toString())
    
