from redforge.agents import StaticProvider
from redforge.roadmap_v200 import AgentKind, AgentTeam


def test_specialized_agent() -> None:
    result = AgentTeam(StaticProvider("ok")).agent(AgentKind.REVIEWER).run("review")
    assert result.agent == AgentKind.REVIEWER
    assert result.content == "ok"
