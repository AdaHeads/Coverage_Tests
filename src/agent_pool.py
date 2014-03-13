from sip_utils import SipAccount, SipAgent
from call_flow_communication import callFlowServer, Server_404
from event_stack import EventListenerThread
import logging
import config

from sip_profiles import ReceptionistConfigs, CustomerConfigs

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import socket
def Public_IP_Address ():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((config.pbx, 5060))
    result = s.getsockname()[0]
    s.close()
    return result

class NoFreeAgents(Exception):
    pass


class NotFound(Exception):
    pass

class Agent:
    
    log = logging.getLogger(__name__ + ".Agent")
    available = True
    username = None
    server = None
    sip_port = None
    sip_phone = None
    call_control = None
    event_stack = None
    receptionist = False
    agent_pool = None
    
    def __init__(self, username, password, id=None,
                 server=config.pbx,
                 sip_port=5060,
                 receptionist=False,
                 auth_token=None,
                 pool=None):

        self.username     = username
        self.ID           = id
        self.server       = server
        self.sip_port     = str(sip_port) # TODO Convert to int all the way.
        self.agent_pool   = pool
        self.receptionist = receptionist

        self.sip_phone    = SipAgent(account=SipAccount(username=self.username,
                                                        password=password,
                                                        sip_port=self.sip_port))

        if self.receptionist:
            self.call_control = callFlowServer(uri=config.call_flow_server_uri, authtoken=auth_token)

    def to_string(self):
        return self.username + "@" + self.server + ":" + self.sip_port + \
            " available: " + str(self.available) + " Receptionist: " + str(self.receptionist)

    def sip_uri(self):
        if self.receptionist:
            return "sip:" + str(self.username) + "@" + self.server
        else:
            return "sip:" + str(self.username) + "@" + Public_IP_Address() + ":" + str (self.sip_port)

    def pickup_call_wait_for_lock(self, call_id):
        try:
            self.call_control.PickupCall(call_id=call_id)
        except Server_404:
            if not self.event_stack.stack_contains (event_type = "call_lock",
                                                    call_id    = call_id):
                raise AssertionError ("Expected to find call_lock event in " + \
                                      str(self.event_stack.dump_stack()))

            self.event_stack.WaitFor (event_type = "call_unlock",
                                      call_id    = call_id)

            self.call_control.PickupCall(call_id=call_id)

        self.event_stack.WaitFor(event_type = "call_pickup",
                                 call_id    =  call_id)

    def dial(self, end_point):
        if self.receptionist:
            self.call_control.Originate_Arbitrary(context="1@1",
                                                  extension=end_point)
        else:
            self.sip_phone.Dial(extension=end_point)

    def hang_up(self, call_id=None):
        if self.receptionist:
            self.call_control.HangupCall(call_id = call_id)
        else:
            self.sip_phone.HangupCurrentCall()

    def prepare(self):
        if not self.sip_phone.Connected():
            self.sip_phone.Connect()

        if self.receptionist: # Customers need not register because they should hit the external dialplan context.
            self.sip_phone.Register()

        # If we are preparing a receptionist, then we need to start an event stack and a call-flow connection.
        if self.receptionist and self.event_stack is None:
            self.event_stack = EventListenerThread(uri=config.call_flow_events, token=self.call_control.authtoken)
            self.event_stack.start()
            self.event_stack.WaitForOpen()

        self.log.info ("Acquired" + self.to_string())
        self.available   = False

        return self

    def release(self):
        if self.sip_phone.Connected():
            self.sip_phone.HangupAllCalls()
            if self.receptionist: # Customers need not register because they should hit the external dialplan context.
                self.sip_phone.Unregister()

        if not self.agent_pool is None:
            self.agent_pool.release(self)

    def __del__(self):
        self.sip_phone.QuitProcess()
        if not self.event_stack is None:
            self.event_stack.stop()

class AgentPool:
    
    agents = None
    log = logging.getLogger(__name__ + ".AgentPool")


    def __init__(self, agent_configs=None):

        if not agent_configs: agent_configs = []
        self.agents = []

        for agent_config in agent_configs:
            if 'ID' in agent_config:
                self.agents.append(Agent(username=agent_config['username'],
                                         id=agent_config['ID'],
                                         password=agent_config['password'],
                                         auth_token=agent_config['authtoken'],
                                         sip_port=agent_config['sipport'],
                                         receptionist=True,
                                         pool=self))
            else:
                self.agents.append(Agent(username=agent_config['username'],
                                         password=agent_config['password'],
                                         sip_port=agent_config['sipport'],
                                         pool=self))

    def request(self):
        for agent in self.agents:
            if agent.available:
                return agent.prepare()

    def release(self, agent):
        for a2 in self.agents:
            if agent == a2:
                if agent.receptionist and not agent.event_stack is None:
                    agent.event_stack.stop()
                    agent.event_stack = None
                agent.available = True
                self.log.info("Released " + agent.to_string())
                return

        raise NotFound()

#Receptionsts = AgentPool(AgentConfigs)

if __name__ == "__main__":
    Receptionists = AgentPool(ReceptionistConfigs)
    Customers     = AgentPool(CustomerConfigs)

    for i in range (1, 10):
        r = Receptionists.request()
        r1 = Receptionists.request()
        r2 = Receptionists.request()
        r.release()
        r = Receptionists.request()
        c = Customers.request()
        c.release()
        c = Customers.request()
        c.sip_phone.Dial("12340001")
        r.event_stack.WaitFor(event_type="call_offer")
        r.release()
        r1.release()
        r2.release()
        c.release()
