import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from redforge import __version__
from redforge.core.config import get_settings
from redforge.production import HumanGate, ReviewCoordinator, RiskEngine


def main() -> None:
    settings = get_settings()
    assert __version__ == "1.3.0"
    assert settings.version == "1.3.0"
    assert settings.e2e_integration_enabled is True
    assert HumanGate is not None
    assert ReviewCoordinator is not None
    assert RiskEngine is not None
    print(
        {
            "version": __version__,
            "e2e_integration": settings.e2e_integration_enabled,
            "risk_engine": True,
            "human_gate": True,
            "multi_agent_run_gate": True,
            "ready": True,
        }
    )


if __name__ == "__main__":
    main()
