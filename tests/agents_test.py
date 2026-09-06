from redforge.agents import CodingAgent, StaticProvider
from redforge.models import Issue, Plan
from redforge.repository.models import RepositorySnapshot


def test_coding_agent_parses_structured_patch() -> None:
    provider = StaticProvider('{"diff":"","rationale":"test","files":[]}')
    patch = CodingAgent(provider).propose_patch(
        Issue(title="test"), Plan(summary="test"), RepositorySnapshot(root=".", name="repo")
    )
    assert patch.rationale == "test"
