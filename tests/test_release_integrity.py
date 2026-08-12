"""Release checksum and inventory tooling coverage."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE_VERSION = "1.6.0-rc1"


def _run(*arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, *arguments], cwd=ROOT, text=True, capture_output=True
    )


def test_release_inventory_round_trip_and_tamper_detection():
    with tempfile.TemporaryDirectory() as tmp:
        release = Path(tmp)
        artifact = release / f"nmap-flow-analyzer-{RELEASE_VERSION}-ubuntu-x64.deb"
        artifact.write_bytes(b"package")
        created = _run(
            "scripts/create-checksums.py", "--version", RELEASE_VERSION,
            "--output-dir", str(release), str(artifact),
        )
        assert created.returncode == 0, created.stderr
        manifest = release / "release-manifest.json"
        payload = json.loads(manifest.read_text("utf-8"))
        assert payload["artifacts"][0]["platform"] == "ubuntu"
        assert payload["artifacts"][0]["architecture"] == "x64"
        verified = _run(
            "scripts/verify-release.py", "--directory", str(release),
            "--manifest", str(manifest), "--version", RELEASE_VERSION,
        )
        assert verified.returncode == 0, verified.stdout + verified.stderr
        artifact.write_bytes(b"tampered")
        rejected = _run(
            "scripts/verify-release.py", "--directory", str(release),
            "--manifest", str(manifest), "--version", RELEASE_VERSION,
        )
        assert rejected.returncode != 0
        assert "mismatch" in rejected.stdout


def test_release_inventory_rejects_wrong_version_filename():
    with tempfile.TemporaryDirectory() as tmp:
        release = Path(tmp)
        artifact = release / "nmap-flow-analyzer-1.2.5-ubuntu-x64.deb"
        artifact.write_bytes(b"package")
        result = _run(
            "scripts/create-checksums.py", "--version", RELEASE_VERSION,
            "--output-dir", str(release), str(artifact),
        )
        assert result.returncode != 0
