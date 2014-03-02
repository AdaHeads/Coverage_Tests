from agent_pool import AgentPool
from sip_profiles import ReceptionistConfigs, CustomerConfigs

Receptionsts = AgentPool(ReceptionistConfigs)
Customers    = AgentPool(CustomerConfigs)
