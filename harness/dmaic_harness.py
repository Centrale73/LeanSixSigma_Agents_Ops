from __future__ import annotations

from typing import Optional, Type, Union

from agno.agent import Agent
from agno.team import Team

from models.lss import LSSResponse


class DMAICHarness:
    """Wraps any Agno Agent or Team in Lean Six Sigma DMAIC governance.

    The harness applies a self-correction loop: if the agent's control
    (confidence) score falls below the configured threshold, it automatically
    retries with contextual feedback until the threshold is met or retries
    are exhausted.

    The harness does **not** own or create agents -- it accepts any
    pre-configured ``Agent`` or ``Team`` and decorates its execution with
    governance behaviour.
    """

    def __init__(
        self,
        agent: Union[Agent, Team],
        confidence_threshold: int = 80,
        max_retries: int = 2,
        response_model: Type[LSSResponse] = LSSResponse,
    ) -> None:
        """Initialise the DMAIC harness.

        Args:
            agent: A fully configured Agno ``Agent`` or ``Team`` instance.
            confidence_threshold: Minimum acceptable ``control`` score (0-100).
                If the agent's response scores below this value the harness
                triggers a self-correction retry.
            max_retries: Maximum number of improvement retries before
                accepting the response as-is.
            response_model: Pydantic model the agent should return.  Defaults
                to :class:`~models.lss.LSSResponse`.
        """
        self.agent = agent
        self.confidence_threshold = confidence_threshold
        self.max_retries = max_retries
        self.response_model = response_model

    # ------------------------------------------------------------------
    # Synchronous execution
    # ------------------------------------------------------------------

    def run(self, query: str) -> LSSResponse:
        """Execute *query* under DMAIC governance with self-correction.

        The harness temporarily sets ``response_model`` on the wrapped agent
        (if it differs from the desired model) and restores the original
        value once execution completes.

        Args:
            query: The user's request / prompt.

        Returns:
            An ``LSSResponse`` (or subclass) validated by the governance loop.
        """
        original_model = getattr(self.agent, "response_model", None)
        try:
            self.agent.response_model = self.response_model
            return self._run_with_governance(query)
        finally:
            self.agent.response_model = original_model

    def _run_with_governance(self, query: str) -> LSSResponse:
        """Core self-correction loop (synchronous)."""
        print(f"--- [DMAICHarness] Processing: {query} ---")

        run_output = self.agent.run(query)
        response: LSSResponse = run_output.content

        attempts = 0
        while response.control < self.confidence_threshold and attempts < self.max_retries:
            print(
                f"--- [DMAICHarness] Low Confidence ({response.control}%). "
                f"Retrying (Attempt {attempts + 1}/{self.max_retries})... ---"
            )
            improvement_prompt = self._build_improvement_prompt(response)
            run_output = self.agent.run(improvement_prompt)
            response = run_output.content
            attempts += 1

        return response

    # ------------------------------------------------------------------
    # Asynchronous execution
    # ------------------------------------------------------------------

    async def arun(self, query: str) -> LSSResponse:
        """Async variant of :meth:`run`.

        Uses ``agent.arun()`` for non-blocking execution while applying the
        same DMAIC self-correction loop.

        Args:
            query: The user's request / prompt.

        Returns:
            An ``LSSResponse`` validated by the governance loop.
        """
        original_model = getattr(self.agent, "response_model", None)
        try:
            self.agent.response_model = self.response_model
            return await self._arun_with_governance(query)
        finally:
            self.agent.response_model = original_model

    async def _arun_with_governance(self, query: str) -> LSSResponse:
        """Core self-correction loop (asynchronous)."""
        print(f"--- [DMAICHarness] Processing (async): {query} ---")

        run_output = await self.agent.arun(query)
        response: LSSResponse = run_output.content

        attempts = 0
        while response.control < self.confidence_threshold and attempts < self.max_retries:
            print(
                f"--- [DMAICHarness] Low Confidence ({response.control}%). "
                f"Retrying (Attempt {attempts + 1}/{self.max_retries})... ---"
            )
            improvement_prompt = self._build_improvement_prompt(response)
            run_output = await self.agent.arun(improvement_prompt)
            response = run_output.content
            attempts += 1

        return response

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_improvement_prompt(response: LSSResponse) -> str:
        """Construct the feedback prompt for a self-correction retry."""
        return (
            f"Previous attempt scored {response.control}/100. "
            f"Reasoning: {response.analyze}. "
            f"CRITICAL INSTRUCTION: Re-analyze user requirements and IMPROVE "
            f"accuracy to meet the Definition of Done."
        )
