"""Regression tests for authoritative Python and release package metadata."""

import email
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - exercised on supported Python 3.9/3.10 CI
    tomllib = None

from nmap_flow_analyzer import __version__


ROOT = Path(__file__).resolve().parents[1]
HUMAN_VERSION = "1.6.0-rc1"
PYTHON_VERSION = "1.6.0rc1"
DEBIAN_VERSION = "1.6.0~rc1"
CORE_VERSION = "0.3.0rc1"
CORE_SHA = "e86440a1e1af2b1aaf62ded3cdc35bf656c8796f"


def _metadata():
    if tomllib is None:
        import pytest

        pytest.skip("tomllib metadata validation requires Python 3.11+")
    with (ROOT / "pyproject.toml").open("rb") as handle:
        return tomllib.load(handle)


def test_pyproject_is_authoritative_for_version_and_entry_point():
    project = _metadata()["project"]
    assert project["version"] == __version__ == HUMAN_VERSION
    assert project["scripts"]["nmap-flow-analyzer"] == (
        "nmap_flow_analyzer.cli:main"
    )


def test_legacy_runtime_requirements_match_pyproject_dependencies():
    project_dependencies = {
        requirement.split(">=")[0].lower()
        for requirement in _metadata()["project"]["dependencies"]
    }
    legacy_dependencies = {
        line.split(">=")[0].strip().lower()
        for line in (ROOT / "requirements.txt").read_text("utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    assert legacy_dependencies == project_dependencies


def test_pytest_is_development_only_dependency():
    metadata = _metadata()
    runtime = "\n".join(metadata["project"]["dependencies"]).lower()
    development = "\n".join(
        metadata["project"]["optional-dependencies"]["dev"]
    ).lower()
    assert "pytest" not in runtime
    assert "pytest" in development


def test_core_rc_dependency_and_immutable_ci_source_are_consistent():
    project = _metadata()["project"]
    lock = (ROOT / "requirements.lock").read_text(encoding="utf-8").splitlines()
    inventory = (ROOT / "licenses/DEPENDENCY_LICENSE_INVENTORY.json").read_text(
        encoding="utf-8"
    )
    assert f"shadow-core>={CORE_VERSION},<0.4" in project["dependencies"]
    assert f"shadow-core=={CORE_VERSION}" in lock
    assert '"version": "0.3.0-rc1"' in inventory
    assert f'"identifier": "shadow-core=={CORE_VERSION}"' in inventory
    for workflow_name in ("build-v130-ubuntu.yml", "build-v130-rhel.yml"):
        workflow = (ROOT / ".github/workflows" / workflow_name).read_text(
            encoding="utf-8"
        )
        assert CORE_SHA in workflow
        assert "shadow_core-0.3.0rc1-py3-none-any.whl" in workflow
        assert "0.3.0.dev0" not in workflow


def test_current_release_inputs_use_one_version_family():
    current_inputs = [
        ROOT / "scripts/build-ubuntu.sh",
        ROOT / "scripts/build-rhel.sh",
        ROOT / "scripts/package-linux-portable.sh",
        ROOT / "scripts/try-build-appimage.sh",
        ROOT / ".github/workflows/build-v130-ubuntu.yml",
        ROOT / ".github/workflows/build-v130-rhel.yml",
        ROOT / ".github/workflows/release-candidate.yml",
    ]
    for path in current_inputs:
        content = path.read_text(encoding="utf-8")
        assert HUMAN_VERSION in content, path
    control = (ROOT / "packaging/ubuntu/control").read_text(encoding="utf-8")
    assert f"Version: {DEBIAN_VERSION}" in control
    installed_launcher = (
        ROOT / "packaging/common/installed-launcher.sh"
    ).read_text(encoding="utf-8")
    assert "exec /opt/nmap-flow-analyzer/nmap-flow-analyzer" in installed_launcher
    assert "Version: 1.6.0" in (
        ROOT / "packaging/rhel/nmap-flow-analyzer.spec"
    ).read_text(encoding="utf-8")


def test_wheel_metadata_normalizes_authoritative_version():
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            [sys.executable, "-m", "build", "--wheel", "--outdir", tmp],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        wheel = next(Path(tmp).glob("nmap_flow_analyzer-*.whl"))
        assert wheel.name.startswith(f"nmap_flow_analyzer-{PYTHON_VERSION}-")
        with zipfile.ZipFile(wheel) as archive:
            metadata_name = next(
                name for name in archive.namelist() if name.endswith(".dist-info/METADATA")
            )
            metadata = email.message_from_bytes(archive.read(metadata_name))
        assert metadata["Version"] == PYTHON_VERSION
