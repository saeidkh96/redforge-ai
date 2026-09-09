from pathlib import Path

from redforge.roadmap_v140 import DockerSandbox, SandboxLimits


def test_docker_command_is_isolated_by_default(tmp_path: Path) -> None:
    sandbox = DockerSandbox(limits=SandboxLimits(network_enabled=False, read_only_root=True))
    command = sandbox.run(tmp_path, ["python", "-V"], dry_run=True).command
    assert "--network" in command and "none" in command
    assert "--read-only" in command and "--memory" in command
