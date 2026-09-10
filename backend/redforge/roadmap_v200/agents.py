from __future__ import annotations

from redforge.agents.gateway import LLMMessage, LLMProvider
from redforge.roadmap_v200.models import AgentKind, AgentResult

_SYSTEM_PROMPTS = {
    AgentKind.PLANNER: "Create a minimal, repository-aware implementation plan.",
    AgentKind.CODER: "Propose the smallest safe code change that satisfies the task.",
    AgentKind.REPAIR: "Repair only the observed failure. Avoid unrelated changes.",
    AgentKind.REVIEWER: "Review for correctness, regression risk, and maintainability.",
    AgentKind.VERIFIER: "Evaluate evidence. Do not approve without sufficient verification.",
}


class SpecializedAgent:
    def __init__(self, kind: AgentKind, provider: LLMProvider) -> None:
        self.kind = kind
        self.provider = provider

    def run(self, instruction: str, *, context: str = "") -> AgentResult:
        response = self.provider.complete(
            [
                LLMMessage(role="system", content=_SYSTEM_PROMPTS[self.kind]),
                LLMMessage(
                    role="user",
                    content=f"Task:\n{instruction}\n\nContext:\n{context}".strip(),
                ),
            ]
        )
        metadata = dict(response.metadata)
        if response.model:
            metadata["model"] = response.model
        return AgentResult(agent=self.kind, content=response.content, metadata=metadata)


class AgentTeam:
    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    def agent(self, kind: AgentKind) -> SpecializedAgent:
        return SpecializedAgent(kind, self.provider)
