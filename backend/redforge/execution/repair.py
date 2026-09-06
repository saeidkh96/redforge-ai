from __future__ import annotations

import json

from redforge.agents.gateway import LLMMessage, LLMProvider
from redforge.models import Patch, TestRun


class RepairAgent:
    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    def propose_repair(
        self,
        failed_patch: Patch,
        test_run: TestRun,
        *,
        attempt: int = 1,
    ) -> Patch:
        prompt = (
            "Return JSON only with keys diff, rationale, files. "
            "Produce the smallest safe repair patch for the current working tree.\n"
            f"Repair attempt: {attempt}\n"
            f"Previous patch:\n{failed_patch.diff}\n"
            f"Test results: {test_run.model_dump_json()}"
        )
        response = self.provider.complete(
            [
                LLMMessage(
                    role="system",
                    content=(
                        "You are RedForge Repair Agent. Repair only the demonstrated failure. "
                        "Do not broaden scope or rewrite unrelated code."
                    ),
                ),
                LLMMessage(role="user", content=prompt),
            ]
        )
        try:
            payload = json.loads(response.content)
        except json.JSONDecodeError as exc:
            raise ValueError("Repair provider did not return valid JSON.") from exc
        return Patch.model_validate(payload)
