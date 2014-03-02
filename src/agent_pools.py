__author__ = 'krc'

from agent_pool import AgentPool
from sip_profiles import ReceptionistConfigs, CustomerConfigs

Receptionsts = AgentPool(ReceptionistConfigs)
Customers    = AgentPool(CustomerConfigs)

if __name__ == "__main__":
    for agent in Receptionsts.agents:
        print agent.to_string()

    for agent in Customers.agents:
        print agent.to_string()
