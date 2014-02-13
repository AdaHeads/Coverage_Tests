import logging
import config
from call_flow_communication import callFlowServer

from sip_profiles import customer1
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
        sipagent = SipAgent(account=SipAccount(username=customer1.username, password=customer1.password, sip_port=customer1.sipport))
    
        assert not self.cfs.peerList().locatePeer(customer1.username)['registered']
        
        sipagent.Connect()
        assert self.cfs.peerList().locatePeer(customer1.username)['registered']
        
        sipagent.QuitProcess()
        assert not self.cfs.peerList().locatePeer(customer1.username)['registered']
    
