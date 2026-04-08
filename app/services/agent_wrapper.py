from agent.react_agent import ReactAgent

_agent_instance = None
def get_agent():
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = ReactAgent()
    return _agent_instance