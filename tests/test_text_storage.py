from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import entry_workflow_guard as guard
import generate_audit_manifest as audit
import review_preflight
import start_words


class TextStorageTests(unittest.TestCase):
    def test_generated_json_bytes_do_not_depend_on_windows_newline_translation(self):
        value = {"headword": "grant", "notes": "日本語の監査\n次の行"}
        expected = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        with tempfile.TemporaryDirectory() as directory:
            for name, writer in (("workflow", guard._write), ("batch", start_words.write),
                                 ("frozen", review_preflight.freeze)):
                with self.subTest(writer=name):
                    path = Path(directory) / (name + ".json")
                    writer(path, value)
                    self.assertEqual(path.read_bytes(), expected)

    def test_frozen_existing_crlf_is_not_rewritten(self):
        value = {"notes": "既存の封印済み入力"}
        original = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").replace("\n", "\r\n").encode("utf-8")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "frozen.json"
            path.write_bytes(original)
            review_preflight.freeze(path, value)
            self.assertEqual(path.read_bytes(), original)
            with self.assertRaises(ValueError):
                review_preflight.freeze(path, {"notes": "変更"})
            self.assertEqual(path.read_bytes(), original)

    @unittest.skipUnless(shutil.which("git"), "Git is needed for the storage roundtrip")
    def test_git_roundtrip_preserves_new_hashes_and_historical_bytes(self):
        # Use the real seal producer, then stage/commit/clone with both Git settings.
        cycle = "audits/runs/g/grant/20260909T144340Z-1f52139a"
        for autocrlf in ("true", "false"):
            with self.subTest(autocrlf=autocrlf), tempfile.TemporaryDirectory() as directory:
                root = Path(directory) / "source"
                root.mkdir()
                env = {**os.environ, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}

                def git(*args):
                    return subprocess.check_output(
                        ["git", "-c", "core.autocrlf=" + autocrlf, "-c", "core.safecrlf=false",
                         "-C", str(root), *args], env=env, stderr=subprocess.PIPE,
                    )

                git("init")
                (root / ".gitattributes").write_bytes((ROOT / ".gitattributes").read_bytes())
                for relative in ("entries/g/grant.md", cycle + "/final_blind.json",
                                 "prompts/check_pass_translation_v6.md"):
                    path = root / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes((ROOT / relative).read_bytes())

                legacy = b'{\r\n  "sealed": true\r\n}\n'
                historical = ["audits/legacy.json", "entries/z/legacy.md",
                              "process_improvement/history/legacy.json", "queue/legacy.json",
                              "backups/legacy.md", "tests/fixtures/legacy.json"]
                for relative in historical:
                    path = root / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(legacy)

                seal = root / cycle / "blind_seal.json"
                payload = audit.seal_blind(root / "entries/g/grant.md",
                                          root / cycle / "final_blind.json", seal,
                                          repo_root=root, sealed_at="2026-09-10T13:00:00Z")
                self.assertNotIn(b"\r", seal.read_bytes())
                self.assertEqual(payload["final_blind_sha256"],
                                 hashlib.sha256((root / cycle / "final_blind.json").read_bytes()).hexdigest())
                snapshot = root / "audits/new.snapshot.md"
                snapshot.write_text("# Snapshot\n\n日本語\n", encoding="utf-8", newline="\n")
                git("add", ".")
                git("-c", "user.name=Storage Test", "-c", "user.email=test@example.invalid",
                    "-c", "commit.gpgsign=false", "commit", "-m", "storage fixture")
                clone = Path(directory) / "checkout"
                git("clone", "--no-local", "-c", "core.autocrlf=" + autocrlf, str(root), str(clone))

                for relative in [cycle + "/blind_seal.json", cycle + "/final_blind.json",
                                 "entries/g/grant.md", "audits/new.snapshot.md",
                                 "prompts/check_pass_translation_v6.md", *historical]:
                    expected = (root / relative).read_bytes()
                    self.assertEqual(git("show", "HEAD:" + relative), expected, relative)
                    self.assertEqual((clone / relative).read_bytes(), expected, relative)
                self.assertNotIn(b"\r", (clone / "prompts/check_pass_translation_v6.md").read_bytes())

    def test_utf8_frozen_packet_ignores_legacy_windows_default_encoding(self):
        # Python 3.12 can run with the Windows locale codec instead of UTF-8.
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "request.json"
            code = (
                "import sys; from pathlib import Path; "
                "sys.path.insert(0, sys.argv[1]); import review_preflight; "
                "p=Path(sys.argv[2]); value={'notes': '\\u65e5\\u672c\\u8a9e'}; "
                "review_preflight.freeze(p,value); review_preflight.freeze(p,value)"
            )
            subprocess.run([sys.executable, "-X", "utf8=0", "-c", code, str(ROOT / "scripts"), str(path)],
                           check=True, capture_output=True)
            self.assertEqual(json.loads(path.read_bytes().decode("utf-8")), {"notes": "日本語"})


if __name__ == "__main__":
    unittest.main()
