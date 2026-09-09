from pathlib import Path

from redforge.roadmap_v140 import AutonomousEngineeringPlatform


def _stages() -> dict:
    def passed(_: dict) -> dict:
        return {}

    return {
        "understand": passed,
        "plan": passed,
        "code": passed,
        "patch": passed,
        "test": lambda _: {"tests_passed": True},
        "repair": lambda _: {"tests_passed": True},
        "verify": lambda _: {"verification_passed": True},
        "policy": lambda _: {"policy_allowed": True},
        "risk": lambda _: {"risk": "low"},
        "review": lambda _: {"review_approved": True},
        "approval": lambda _: {"awaiting_human_approval": False},
        "audit": passed,
        "delivery": lambda _: {"delivery_ready": True, "branch": "redforge/test"},
    }


def test_platform_reaches_delivery_ready(tmp_path: Path) -> None:
    result = AutonomousEngineeringPlatform(tmp_path, stages=_stages()).start({"issue": "test"})
    assert result.checkpoint.completed is True
    assert result.delivery_ready is True
    assert result.branch == "redforge/test"
