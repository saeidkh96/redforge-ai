import json

from redforge.agents.gateway import LLMMessage, LLMProvider
from redforge.models import Issue, Patch, Plan
from redforge.repository import RepositorySnapshot


class CodingAgent:
    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    def propose_patch(
        self,
        issue: Issue,
        plan: Plan,
        snapshot: RepositorySnapshot,
    ) -> Patch:
        context_files = [file.path for file in snapshot.files[:100]]
        prompt = (
            "Return JSON only with keys diff, rationale, files. "
            "The diff must be a valid unified git diff.\n"
            f"Issue: {issue.model_dump_json()}\n"
            f"Plan: {plan.model_dump_json()}\n"
            f"Repository summary: {snapshot.summary}\n"
            f"Files: {json.dumps(context_files)}"
        )
        response = self.provider.complete(
            [
                LLMMessage(
                    role="system",
                    content=("You are RedForge Coding Agent. Produce minimal safe patches only."),
                ),
                LLMMessage(role="user", content=prompt),
            ]
        )
        try:
            data = json.loads(response.content)
        except json.JSONDecodeError as exc:
            raise ValueError("Coding provider did not return valid JSON.") from exc
        return Patch.model_validate(data)
