import json

from redforge.agents import StaticProvider
from redforge.execution import RepairAgent
from redforge.models import CommandResult, Patch
from redforge.models import TestRun as ForgeTestRun


def test_repair_agent_returns_structured_patch() -> None:
    payload = {
        "diff": "diff --git a/a.py b/a.py\n",
        "rationale": "Repair failing assertion.",
        "files": ["a.py"],
    }
    provider = StaticProvider(json.dumps(payload))
    test_run = ForgeTestRun(
        results=[
            CommandResult(
                command=["python", "-m", "pytest", "-q"],
                return_code=1,
                stderr="assert 1 == 2",
            )
        ]
    )

    patch = RepairAgent(provider).propose_repair(
        Patch(diff="previous", files=["a.py"]),
        test_run,
        attempt=1,
    )

    assert patch.files == ["a.py"]
    assert patch.rationale == "Repair failing assertion."
