from redforge.agents.gateway import LLMMessage, LLMProvider
from redforge.models import Finding, Patch, RiskLevel


class SemanticReviewer:
    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    def review(self, patch: Patch) -> list[Finding]:
        response = self.provider.complete(
            [
                LLMMessage(
                    role="system",
                    content=(
                        "Review the patch for semantic risks. Reply with OK or a concise concern."
                    ),
                ),
                LLMMessage(role="user", content=patch.diff),
            ]
        )
        content = response.content.strip()
        if not content or content.upper() == "OK":
            return []
        return [
            Finding(
                source="llm-review",
                severity=RiskLevel.MEDIUM,
                message=content,
                rule_id="semantic-review",
            )
        ]
