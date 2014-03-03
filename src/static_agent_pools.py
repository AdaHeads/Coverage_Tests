from agent_pool import AgentPool
from sip_profiles import ReceptionistConfigs, CustomerConfigs

Receptionists = AgentPool(ReceptionistConfigs)
Customers     = AgentPool(CustomerConfigs)

