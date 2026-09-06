import json

from redforge.agents.gateway import LLMMessage, LLMProvider
from redforge.models import Patch, TestRun


class RepairAgent:
    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    def propose_repair(self, failed_patch: Patch, test_run: TestRun) -> Patch:
        prompt = (
            "Return JSON only with keys diff, rationale, files. Produce a minimal repair patch.\n"
            f"Previous patch:\n{failed_patch.diff}\n"
            f"Test results: {test_run.model_dump_json()}"
        )
        response = self.provider.complete(
            [
                LLMMessage(role="system", content="You are RedForge Repair Agent."),
                LLMMessage(role="user", content=prompt),
            ]
        )
        try:
            return Patch.model_validate(json.loads(response.content))
        except json.JSONDecodeError as exc:
            raise ValueError("Repair provider did not return valid JSON.") from exc
