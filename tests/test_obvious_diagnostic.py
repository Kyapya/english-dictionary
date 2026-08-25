from __future__ import annotations

import base64
import gzip
import json
import subprocess
import unittest
from pathlib import Path

from scripts import content_audit


class ObviousAuditDiagnostic(unittest.TestCase):
    def test_emit_diagnostics(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        entry = repo / "entries/o/obvious.md"
        current_hash = content_audit.body_sha256(entry)
        previous = subprocess.run(
            ["git", "show", "e1856da1777bc89e3a150e733ca2779586a9e687^:entries/o/obvious.md"],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        front, body = content_audit._split_front_matter(previous)
        previous_hash = content_audit._digest(body)
        manifest = content_audit.build_manifest(entry)
        payload = json.dumps(manifest, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        compressed = base64.b64encode(gzip.compress(payload, compresslevel=9)).decode("ascii")
        print(f"OBVIOUS_PRE_FIX_BODY_SHA={previous_hash}")
        print(f"OBVIOUS_CURRENT_BODY_SHA={current_hash}")
        print(f"OBVIOUS_AUDIT_SKELETON_GZIP_B64={compressed}")
        self.assertTrue(front)
        self.assertTrue(manifest["targets"])
        self.assertTrue(manifest["relations"])


if __name__ == "__main__":
    unittest.main()
