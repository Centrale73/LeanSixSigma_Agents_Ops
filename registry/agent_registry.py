from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, Dict, List, Optional


@dataclass
class AgentRecord:
    """Metadata record for a tracked agent instance."""

    audit_id: str
    name: str
    role: Optional[str]
    parent_id: Optional[str]
    children_ids: List[str] = field(default_factory=list)
    phase: Optional[str] = None
    status: str = "registered"  # registered | running | completed | failed
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentRegistry:
    """Thread-safe registry for tracking agent lifecycle and hierarchy.

    ``AgentRegistry`` assigns each agent a unique ``audit_id``, records
    parent-child relationships, and exposes helpers for querying the
    agent tree at any point during execution.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._agents: Dict[str, AgentRecord] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        agent: Any,
        parent_id: Optional[str] = None,
    ) -> str:
        """Register an agent and return its unique ``audit_id``.

        Args:
            agent: An Agno ``Agent`` or ``Team`` instance (or any object
                with ``name`` and optionally ``role`` attributes).
            parent_id: The ``audit_id`` of the parent agent, if any.

        Returns:
            A newly generated UUID string used as the agent's audit ID.
        """
        audit_id = str(uuid.uuid4())
        name = getattr(agent, "name", None) or type(agent).__name__
        role = getattr(agent, "role", None) or getattr(agent, "description", None)

        record = AgentRecord(
            audit_id=audit_id,
            name=name,
            role=role,
            parent_id=parent_id,
        )

        with self._lock:
            self._agents[audit_id] = record
            if parent_id and parent_id in self._agents:
                self._agents[parent_id].children_ids.append(audit_id)

        return audit_id

    # ------------------------------------------------------------------
    # Decorator
    # ------------------------------------------------------------------

    def track(
        self,
        parent_id: Optional[str] = None,
    ) -> Callable:
        """Decorator for agent factory functions.

        Any agent returned by the decorated function is automatically
        registered with the registry, preserving parent-child relationships.

        Args:
            parent_id: Optional parent ``audit_id``.  When the decorated
                factory itself was spawned by a tracked agent, pass the
                parent's ID so the tree is connected.

        Returns:
            A decorator that wraps an agent factory function.

        Example::

            @registry.track()
            def create_research_agent(topic: str) -> Agent:
                return Agent(name=f"Researcher-{topic}", ...)
        """

        def decorator(fn: Callable) -> Callable:
            @wraps(fn)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                agent = fn(*args, **kwargs)
                # Determine the effective parent: allow runtime override
                effective_parent = kwargs.pop("_parent_id", None) or parent_id
                audit_id = self.register(agent, parent_id=effective_parent)
                # Stash the audit_id on the agent for downstream use
                agent._registry_audit_id = audit_id  # type: ignore[attr-defined]
                return agent

            return wrapper

        return decorator

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_agent(self, audit_id: str) -> AgentRecord:
        """Look up an agent record by its ``audit_id``.

        Args:
            audit_id: The UUID assigned during registration.

        Returns:
            The corresponding :class:`AgentRecord`.

        Raises:
            KeyError: If no agent with that ID has been registered.
        """
        with self._lock:
            return self._agents[audit_id]

    def set_phase(self, audit_id: str, phase: str) -> None:
        """Tag an agent with its current DMAIC phase.

        Args:
            audit_id: The agent's unique ID.
            phase: Free-form phase label (e.g. ``"Define"``, ``"Measure"``).
        """
        with self._lock:
            self._agents[audit_id].phase = phase

    def set_status(self, audit_id: str, status: str) -> None:
        """Update an agent's lifecycle status.

        Args:
            audit_id: The agent's unique ID.
            status: One of ``registered``, ``running``, ``completed``, ``failed``.
        """
        with self._lock:
            record = self._agents[audit_id]
            record.status = status
            if status in ("completed", "failed"):
                record.completed_at = datetime.now(timezone.utc)

    def list_agents(
        self,
        phase: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[AgentRecord]:
        """Return registered agents, optionally filtered by phase/status.

        Args:
            phase: If given, only return agents in this DMAIC phase.
            status: If given, only return agents with this lifecycle status.

        Returns:
            A list of matching :class:`AgentRecord` instances.
        """
        with self._lock:
            results = list(self._agents.values())

        if phase is not None:
            results = [r for r in results if r.phase == phase]
        if status is not None:
            results = [r for r in results if r.status == status]
        return results

    def get_agent_tree(self) -> Dict[str, Any]:
        """Build and return the full agent hierarchy as a nested dict.

        Each node contains the agent's metadata and a ``children`` list
        of recursively nested child nodes.

        Returns:
            A dict with a ``roots`` key containing top-level agents (those
            with no parent), each with nested ``children``.
        """
        with self._lock:
            snapshot = dict(self._agents)

        def _build_node(record: AgentRecord) -> Dict[str, Any]:
            return {
                "audit_id": record.audit_id,
                "name": record.name,
                "role": record.role,
                "status": record.status,
                "phase": record.phase,
                "created_at": record.created_at.isoformat(),
                "completed_at": record.completed_at.isoformat() if record.completed_at else None,
                "metadata": record.metadata,
                "children": [
                    _build_node(snapshot[cid])
                    for cid in record.children_ids
                    if cid in snapshot
                ],
            }

        roots = [r for r in snapshot.values() if r.parent_id is None]
        return {"roots": [_build_node(r) for r in roots]}
