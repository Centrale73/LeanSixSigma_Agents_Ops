"""
Example: Wrapping a custom Agno Agent with DMAICHarness.

This demonstrates how a developer can create any Agno Agent and wrap it
in DMAIC governance using the DMAICHarness — without being tied to the
built-in ProductivityAgent.

Usage:
    Set PERPLEXITY_API_KEY in your environment, then:
        python -m examples.predetermined_harness
"""

from agno.agent import Agent
from agno.models.perplexity import Perplexity

from harness import DMAICHarness
from models.lss import LSSResponse

# Step 1: Create your own Agno Agent with whatever model / tools you need.
# The agent does NOT need to know about LSSResponse — the harness handles that.
my_agent = Agent(
    name="MarketAnalyst",
    model=Perplexity(id="sonar-pro"),
    description="You are a senior market research analyst.",
    instructions=[
        "Provide concise, data-backed market analysis.",
        "Always cite sources when presenting statistics.",
        "Structure your response following the DMAIC framework.",
    ],
    markdown=True,
)

# Step 2: Wrap the agent in a DMAICHarness.
# The harness will:
#   - Temporarily set response_model=LSSResponse on the agent during execution
#   - Run the self-correction loop if confidence < threshold
#   - Restore the original response_model after execution
harness = DMAICHarness(
    agent=my_agent,
    confidence_threshold=80,  # retry if control score < 80
    max_retries=2,            # up to 2 improvement retries
)

# Step 3: Execute a query through the harness.
if __name__ == "__main__":
    result: LSSResponse = harness.run(
        "What are the top 3 emerging trends in AI SaaS for 2026?"
    )

    # The result is always a validated LSSResponse with DMAIC fields.
    print(f"\n--- Define ---\n{result.define}")
    print(f"\n--- Measure ---\n{result.measure}")
    print(f"\n--- Analyze ---\n{result.analyze}")
    print(f"\n--- Improve ---\n{result.improve}")
    print(f"\n--- Control (confidence) ---\n{result.control}/100")
