"""
Example: Dynamic agent tracking with AgentRegistry.

This demonstrates how to use the ``@registry.track`` decorator to
automatically register agents created by factory functions, and how to
inspect the resulting agent hierarchy after execution.

Usage:
    Set PERPLEXITY_API_KEY in your environment, then:
        python -m examples.dynamic_agents
"""

import json

from agno.agent import Agent
from agno.models.perplexity import Perplexity

from harness import DMAICHarness
from registry import AgentRecord, AgentRegistry

# Step 1: Create a shared registry instance.
registry = AgentRegistry()


# Step 2: Define agent factory functions and decorate them with @registry.track().
# Every agent returned by these factories will be auto-registered.

@registry.track()
def create_coordinator() -> Agent:
    """Factory for the top-level coordinator agent."""
    return Agent(
        name="Coordinator",
        model=Perplexity(id="sonar-pro"),
        description="Orchestrates sub-agents for complex research tasks.",
        instructions=["Break complex questions into sub-tasks and delegate."],
        markdown=True,
    )


@registry.track()
def create_sub_agent(topic: str, _parent_id: str = None) -> Agent:
    """Factory for a specialised sub-agent.

    Pass ``_parent_id`` to link this agent to its parent in the registry tree.
    The ``@registry.track`` decorator picks up ``_parent_id`` automatically.
    """
    return Agent(
        name=f"Researcher-{topic}",
        model=Perplexity(id="sonar-pro"),
        description=f"Deep-dive researcher for {topic}.",
        instructions=[
            f"You are a domain expert in {topic}.",
            "Provide data-backed analysis following the DMAIC framework.",
        ],
        markdown=True,
    )


# Step 3: Build an agent tree — a coordinator with two sub-agents.
if __name__ == "__main__":
    # Create the coordinator (root agent, no parent).
    coordinator = create_coordinator()
    coord_id = coordinator._registry_audit_id

    # Tag the coordinator as running in the "Define" phase.
    registry.set_status(coord_id, "running")
    registry.set_phase(coord_id, "Define")

    # Spawn sub-agents linked to the coordinator.
    agent_ai = create_sub_agent("AI-Infrastructure", _parent_id=coord_id)
    agent_fin = create_sub_agent("FinTech-Regulation", _parent_id=coord_id)

    # Mark sub-agents as running in the "Analyze" phase.
    for sub in [agent_ai, agent_fin]:
        sub_id = sub._registry_audit_id
        registry.set_status(sub_id, "running")
        registry.set_phase(sub_id, "Analyze")

    # --- (Optional) Run one sub-agent through a DMAICHarness ---
    # harness = DMAICHarness(agent=agent_ai)
    # result = harness.run("What are the top AI infrastructure trends?")

    # Simulate completion.
    registry.set_status(agent_ai._registry_audit_id, "completed")
    registry.set_status(agent_fin._registry_audit_id, "completed")
    registry.set_status(coord_id, "completed")

    # Step 4: Inspect the agent tree.
    tree = registry.get_agent_tree()
    print(json.dumps(tree, indent=2, default=str))

    # Step 5: Query agents by phase or status.
    analyze_agents = registry.list_agents(phase="Analyze")
    print(f"\nAgents in 'Analyze' phase: {[a.name for a in analyze_agents]}")

    completed = registry.list_agents(status="completed")
    print(f"Completed agents: {[a.name for a in completed]}")

    # Step 6: Look up a single agent record.
    record: AgentRecord = registry.get_agent(coord_id)
    print(f"\nCoordinator children: {record.children_ids}")
