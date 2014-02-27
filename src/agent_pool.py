from sip_utils import SipAccount, SipAgent
from call_flow_communication import callFlowServer
from event_stack import EventListenerThread
import config
import logging
import time

logging.basicConfig(level=logging.INFO)


AgentConfigs = [
                {
                 'username'     : '1100',
                 'password'     : '1234',
                 'sipport'      : 5160,
                 'authtoken'    : "feedabbadeadbeef0",
                 'ID'           : 10,
                 'receptionist' : True
                },
                 {
                  'username'  : '1101',
                  'password'  : '1234',
                  'sipport'   : 5161,
                  'authtoken' : "feedabbadeadbeef1",
                  'ID'        : 11,
                  'receptionist' : True
                 },
                 {
                  'username'  : '1102',
                  'password'  : '1234',
                  'sipport'   : 5162,
                  'authtoken' : "feedabbadeadbeef2",
                  'ID'        : 12,
                  'receptionist' : True
                 }
                ]

CustomerConfigs = [
                {
                 'username'  : '1200',
                 'password'  : '1234',
                 'sipport'   : 5260,
                },
                 {
                  'username'  : '1201',
                  'password'  : '1234',
                  'sipport'   : 5261,
                 }
                ]


class No_Free_Agents(Exception):
    pass

class Not_Found(Exception):
    pass

class Agent:
    
    available    = True
    username     = None
    server       = None
    sip_port     = None 
    SIP_Phone    = None
    Call_Control = None
    Event_Stack  = None
    Receptionist = False
    agent_pool  = None
    
    def __init__(self, username, password, server=config.pbx, sip_port=5060, Receptionist=False, authToken=None, pool=None):
        self.username     = username
        self.server       = server
        self.sip_port     = str (sip_port)  # This should probably be kept as int, by we really don't need the int further along the way.
        self.agent_pool   = pool;
        self.Receptionist = Receptionist

        self.SIP_Phone    = SipAgent(account=SipAccount(username=self.username, password=password, sip_port=self.sip_port))
        self.SIP_Phone.Connect()

        if self.Receptionist:
            self.Call_Control = callFlowServer(uri=config.call_flow_server_uri, authtoken=authToken)

    def toString(self):
        return self.username + "@" + self.server + ":" + self.sip_port + \
        " available: " + str (self.available) + " Receptionist: " + str(self.Receptionist)

    def Release(self):
        if not self.agent_pool is None:
            self.agent_pool.Release(self)

    def __del__(self):
        self.SIP_Phone.QuitProcess()
        if not self.Event_Stack is None:
            self.Event_Stack.stop()

class AgentPool:
    
    Agents = []
    
    def __init__(self, agentConfigs=[]):
        for config in agentConfigs:
            logging.info (config)

            if 'ID' in config:
                self.Agents.append(Agent(username=config['username'],
                                         password=config['password'],
                                         authToken=config['authtoken'],
                                         sip_port=config['sipport'],
                                         Receptionist=True,
                                         pool=self))
            else:
                self.Agents.append(Agent(username=config['username'],
                                         password=config['password'],
                                         sip_port=config['sipport'],
                                         pool=self))

    def DumpInformation (self):
        pass
        
    def Aquire (self):
        for agent in self.Agents:
            if agent.available:
                agent.available   = False
                if agent.Receptionist and agent.Event_Stack is None:
                    agent.Event_Stack = EventListenerThread(uri=config.call_flow_events, token=agent.Call_Control.authtoken)
                    agent.Event_Stack.start()
                    agent.Event_Stack.WaitForOpen()

                logging.info ("Aquired " + agent.toString())
                return agent

    def Release (self, agent):
        for a2 in self.Agents:
            if agent == a2:
                if agent.Receptionist and not agent.Event_Stack is None:
                    agent.Event_Stack.stop()
                    agent.Event_Stack = None
                agent.available = True
                logging.info ("Released " + agent.toString())
                return

        raise Not_Found()

#Receptionsts = AgentPool(AgentConfigs)

if __name__ == "__main__":
    Receptionsts = AgentPool(AgentConfigs)
    Customers    = AgentPool(CustomerConfigs)

    r = Receptionsts.Aquire()
    r1 = Receptionsts.Aquire()
    r2 = Receptionsts.Aquire()
    r.Release()
    r = Receptionsts.Aquire()
    c = Customers.Aquire()
    c.Release()
    c = Customers.Aquire()
    c.SIP_Phone.Dial("12340001")
    r.Event_Stack.WaitFor(event_type="call_offer")
    r.Release()
    r1.Release()
    r2.Release()
    c.Release()
