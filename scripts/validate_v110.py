from redforge import __version__
from redforge.core.config import get_settings


def main() -> None:
    settings = get_settings()
    assert __version__ == "1.1.0"
    assert settings.version == "1.1.0"
    assert settings.max_repair_attempts >= 0
    print(
        {
            "version": __version__,
            "repair_on_failure": settings.repair_on_failure,
            "max_repair_attempts": settings.max_repair_attempts,
            "ready": True,
        }
    )


if __name__ == "__main__":
    main()
