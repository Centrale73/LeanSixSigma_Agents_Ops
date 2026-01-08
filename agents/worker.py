from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.agent.postgres import PostgresAgentStorage
# from agno.knowledge import AgentKnowledge # Placeholder for RAG - commented out as not fully implemented in snippet but required by import
from settings import settings
from models.lss import LSSResponse
from tools.perplexity import PerplexitySearchTool

# --- Database Storage for Long-Term Memory ---
# Note: Ensure the table exists or is created by the storage engine
storage = PostgresAgentStorage(
    table_name="agent_memory",
    db_url=settings.DATABASE_URL
)

# --- The Productivity Agent Definition ---
productivity_agent = Agent(
    name="ProductivityAgent",
    # Cognitive Core: Using Perplexity via OpenAI Interface
    model=OpenAIChat(
        id=settings.MODEL_NAME,
        base_url=settings.PERPLEXITY_BASE_URL,
        api_key=settings.PERPLEXITY_API_KEY,
    ),
    # Tooling: Real-time research capabilities
    tools=[PerplexitySearchTool()],
    # Memory: Persist interactions
    storage=storage,
    add_history_to_messages=True,
    # Governance: Enforce DMAIC Structure
    response_model=LSSResponse,
    description="You are a Lean Six Sigma Master Black Belt AI. You do not just answer; you optimize.",
    instructions=[
        "Follow the DMAIC process for every request.",
        "DEFINE: Clarify the intent.",
        "MEASURE: Set success metrics.",
        "ANALYZE: Use Perplexity tools to gather facts.",
        "IMPROVE: Synthesize the answer.",
        "CONTROL: Rate your own confidence."
    ]
)

def run_agent_with_governance(query: str, max_retries: int = 2) -> LSSResponse:
    """
    Implements the 'Self-Correction' Loop.
    If Control Score < 80, the system recursively improves itself.
    """
    print(f"--- [Cognitive Core] Processing: {query} ---")
    
    # First Pass
    response: LSSResponse = productivity_agent.run(query)
    
    attempts = 0
    while response.control < 80 and attempts < max_retries:
        print(f"--- [LSS Governance] Alert: Low Confidence ({response.control}%). Retrying (Attempt {attempts+1})... ---")
        
        # Feedback Loop: Feed the failure back into the context
        improvement_prompt = (
            f"Previous attempt scored {response.control}/100. "
            f"Reasoning: {response.analyze}. "
            f"CRITICAL INSTRUCTION: Re-analyze user requirements and IMPROVE accuracy to meet the Definition of Done."
        )
        
        response = productivity_agent.run(improvement_prompt)
        attempts += 1
        
    return response