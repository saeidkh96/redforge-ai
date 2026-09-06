import subprocess
from pathlib import Path

from redforge.execution import PatchEngine
from redforge.models import Patch


def test_patch_engine_checks_and_applies_patch(tmp_path: Path) -> None:
    subprocess.run(
        ["git", "-C", str(tmp_path), "init"],
        check=True,
        capture_output=True,
    )
    target = tmp_path / "hello.txt"
    target.write_text("hello\n", encoding="utf-8")

    patch = Patch(
        files=["hello.txt"],
        diff=(
            "diff --git a/hello.txt b/hello.txt\n"
            "--- a/hello.txt\n"
            "+++ b/hello.txt\n"
            "@@ -1 +1 @@\n"
            "-hello\n"
            "+world\n"
        ),
    )

    engine = PatchEngine()
    engine.check(tmp_path, patch)
    engine.apply(tmp_path, patch)

    assert target.read_text(encoding="utf-8") == "world\n"
