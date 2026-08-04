from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from import_to_notion import markdown_to_blocks  # noqa: E402


class ImportToNotionTests(unittest.TestCase):
    def test_converts_dictionary_hierarchy_and_groups_entries(self) -> None:
        markdown = """＃発音記号
米・英: /test/

＃意味や関連情報の出力（日本語訳）
1. 【名詞】試験

【日本語訳・定義】能力などを確認するための試験。

【コロケーション】

・take a test  
用途: 試験を受ける。  
例: I took a test yesterday.  
訳: 私は昨日試験を受けた。  

・pass a test  
用途: 試験に合格する。  
例: She passed the test.  
訳: 彼女はその試験に合格した。  
"""
        blocks = markdown_to_blocks(markdown)
        block_types = [block["type"] for block in blocks]
        self.assertEqual(block_types.count("heading_1"), 2)
        self.assertEqual(block_types.count("heading_2"), 1)
        self.assertEqual(block_types.count("heading_3"), 2)

        grouped = [
            block["paragraph"]["rich_text"][0]["text"]["content"]
            for block in blocks
            if block["type"] == "paragraph"
            and block["paragraph"]["rich_text"][0]["text"]["content"].startswith("・")
        ]
        self.assertEqual(len(grouped), 2)
        self.assertIn("\n用途:", grouped[0])
        self.assertIn("\n例:", grouped[0])
        self.assertIn("\n訳:", grouped[0])

    def test_does_not_add_ai_attribution(self) -> None:
        blocks = markdown_to_blocks("＃発音記号\n米・英: /test/")
        serialized = str(blocks)
        self.assertNotIn("AI", serialized)
        self.assertNotIn("OpenAI", serialized)


if __name__ == "__main__":
    unittest.main()

