from agno.agent import Agent
from agno.models.perplexity import Perplexity
# from agno.models.groq import Groq  # Uncomment when needed
# from agno.models.openrouter import OpenRouter # Uncomment when needed
from agno.db.postgres import PostgresDb
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.embedder.fastembed import FastEmbedEmbedder
from agno.vectordb.pgvector import PgVector

from settings import settings
from harness import DMAICHarness

# --- Database & Knowledge Setup ---
# Using the specific DB URL structure from your snippet
db_url = settings.DATABASE_URL
knowledge_table = "lss_knowledge"

# Initialize Knowledge Base (RAG)
# Using FastEmbedEmbedder for local embeddings (No OpenAI API key required)
knowledge = Knowledge(
    vector_db=PgVector(
        table_name=knowledge_table,
        db_url=db_url,
        embedder=FastEmbedEmbedder(),
    ),
)

# Placeholder: In a real scenario, you would add content here
# knowledge.add_content(url="https://github.com/Lmao53and2/LeanSixSigma_Agents_Ops/blob/main/lss_methodology.pdf")

# --- The Productivity Agent Definition ---
productivity_agent = Agent(
    name="ProductivityAgent",

    # Cognitive Core: Native Perplexity Model
    # Leveraging the 'sonar-pro' model as requested
    model=Perplexity(
        id=settings.PERPLEXITY_MODEL,
        api_key=settings.PERPLEXITY_API_KEY
    ),

    # Memory: PostgresDb for user memories and session summaries
    db=PostgresDb(db_url=db_url),
    enable_user_memories=True,
    enable_session_summaries=True,

    # Knowledge: RAG capabilities
    knowledge=knowledge,

    # Governance: Enforce DMAIC Structure (harness will manage response_model)
    markdown=True,

    description="You are a Lean Six Sigma Master Black Belt AI. You do not just answer; you optimize.",
    instructions=[
        "Follow the DMAIC process for every request.",
        "DEFINE: Clarify the intent.",
        "MEASURE: Set success metrics.",
        "ANALYZE: Use your native search capabilities and knowledge base to gather facts.",
        "IMPROVE: Synthesize the answer.",
        "CONTROL: Rate your own confidence."
    ]
)

# --- DMAIC Governance Harness ---
harness = DMAICHarness(agent=productivity_agent)
