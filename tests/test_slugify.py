from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from slugify import slugify  # noqa: E402


class SlugifyTests(unittest.TestCase):
    def test_required_examples(self) -> None:
        cases = {
            "take off": "take-off",
            "can't help doing": "cant-help-doing",
            "as well as": "as-well-as",
            "look up/to": "look-up-to",
            "immaculate": "immaculate",
        }
        for headword, expected in cases.items():
            with self.subTest(headword=headword):
                self.assertEqual(slugify(headword), expected)


if __name__ == "__main__":
    unittest.main()
