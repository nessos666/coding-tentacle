"""CLOUD LLM ADAPTER — RC75 (stub)"""
from coding_tentacle.llm.repair_agent_interface import AgentInput


class CloudLLMAdapter:
    """Cloud LLM adapter (stub - no API key required)."""
    
    def __init__(self, provider: str = 'openai'):
        self.provider = provider
        self.api_key = None  # Set via env or config
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def generate(self, agent_input: AgentInput) -> str:
        raise NotImplementedError('Cloud adapter not yet implemented — set api_key first')


# Self-test
if __name__ == "__main__":
    adapter = CloudLLMAdapter()
    assert not adapter.is_available(), "Should be unavailable without API key"
    print("✅ CloudLLMAdapter: unavailable without key (correct)")
