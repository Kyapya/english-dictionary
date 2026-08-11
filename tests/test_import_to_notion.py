from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import import_to_notion  # noqa: E402
from import_to_notion import (  # noqa: E402
    NotionApiError,
    import_entry,
    markdown_to_blocks,
    read_entry_body,
)


class ImportToNotionTests(unittest.TestCase):
    @staticmethod
    def plain_text(block: dict[str, object]) -> str:
        block_type = block["type"]
        rich_text = block[block_type]["rich_text"]
        return "".join(item["text"]["content"] for item in rich_text)

    def notion_args(self, policy: str = "create") -> SimpleNamespace:
        return SimpleNamespace(
            dry_run=False,
            existing_policy=policy,
            skip_existing=None,
            notion_version="2026-03-11",
            parent_type="data_source",
            parent_id="data-source-id",
            title_property="ALL",
            status_property="Status",
            status_value="未着手",
            tag_property="タグ",
            tag_value="英単語",
            note_property="",
            note_value="",
            sleep=0,
        )

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

        heading_3_texts = [
            self.plain_text(block) for block in blocks if block["type"] == "heading_3"
        ]
        self.assertEqual(heading_3_texts, ["日本語訳・定義", "コロケーション"])
        self.assertNotIn("能力などを確認するための試験。", heading_3_texts[0])
        self.assertTrue(
            any(
                block["type"] == "paragraph"
                and self.plain_text(block) == "能力などを確認するための試験。"
                for block in blocks
            )
        )

        grouped = [
            self.plain_text(block)
            for block in blocks
            if block["type"] == "paragraph"
            and self.plain_text(block).startswith("・")
        ]
        self.assertEqual(len(grouped), 2)
        self.assertIn("\n用途:", grouped[0])
        self.assertIn("\n例:", grouped[0])
        self.assertIn("\n訳:", grouped[0])
        self.assertNotIn("<br>", grouped[0])

    def test_compiles_inline_markdown_without_changing_visible_text(self) -> None:
        blocks = markdown_to_blocks(
            "【語法・注意】*embrace* と `accept` を区別する。"
        )
        self.assertEqual([block["type"] for block in blocks], ["heading_3", "paragraph"])
        self.assertEqual(self.plain_text(blocks[0]), "語法・注意")
        self.assertEqual(self.plain_text(blocks[1]), "embrace と accept を区別する。")
        rich = blocks[1]["paragraph"]["rich_text"]
        self.assertTrue(any(item.get("annotations", {}).get("italic") for item in rich))
        self.assertTrue(any(item.get("annotations", {}).get("code") for item in rich))

    def test_rejects_malformed_grouped_entry_before_upload(self) -> None:
        markdown = """【コロケーション】

・take a test
用途: 試験を受ける。
例: I took a test.
"""
        with self.assertRaisesRegex(ValueError, "expected 4 fixed lines"):
            markdown_to_blocks(markdown)

    def test_rejects_invalid_source_file_before_notion_conversion(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "invalid.md"
            path.write_text("---\nheadword: invalid\n---\n\n＃発音記号\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "failed validation"):
                read_entry_body({"headword": "invalid", "file": str(path)})

    def test_does_not_add_ai_attribution(self) -> None:
        blocks = markdown_to_blocks("＃発音記号\n米・英: /test/")
        serialized = str(blocks)
        self.assertNotIn("AI", serialized)
        self.assertNotIn("OpenAI", serialized)

    def test_updates_one_existing_page_body_without_touching_properties(self) -> None:
        calls: list[tuple[str, str, object]] = []

        def fake_request(
            method: str,
            path: str,
            token: str,
            notion_version: str,
            payload: object = None,
        ) -> dict[str, object]:
            calls.append((method, path, payload))
            if method == "POST" and path.endswith("/query"):
                return {"results": [{"id": "existing-page"}], "has_more": False}
            if method == "GET":
                return {
                    "results": [{"id": "old-1"}, {"id": "old-2"}],
                    "has_more": False,
                }
            return {}

        new_blocks = [{"object": "block", "type": "paragraph"}]
        with (
            patch.object(import_to_notion, "notion_request", side_effect=fake_request),
            patch.object(import_to_notion, "read_entry_body", return_value="new body"),
            patch.object(import_to_notion, "markdown_to_blocks", return_value=new_blocks),
            patch.object(import_to_notion.time, "sleep"),
        ):
            result = import_entry(
                self.notion_args("update"),
                "token",
                {"headword": "approximately", "file": "unused.md"},
            )

        self.assertIn("UPDATE approximately", result)
        mutations = [(method, path, payload) for method, path, payload in calls if method == "PATCH"]
        self.assertEqual(mutations[0][1], "/blocks/existing-page/children")
        self.assertEqual(mutations[1][1], "/blocks/old-1")
        self.assertEqual(mutations[2][1], "/blocks/old-2")
        self.assertEqual(mutations[1][2], {"in_trash": True})
        self.assertFalse(any(path.startswith("/pages/") for _, path, _ in calls))

    def test_updates_most_recently_edited_duplicate_page(self) -> None:
        calls: list[tuple[str, str, object]] = []

        def fake_request(
            method: str,
            path: str,
            token: str,
            notion_version: str,
            payload: object = None,
        ) -> dict[str, object]:
            calls.append((method, path, payload))
            if method == "POST" and path.endswith("/query"):
                return {
                    "results": [
                        {
                            "id": "duplicate-newest",
                            "created_time": "2026-08-01T00:00:00.000Z",
                            "last_edited_time": "2026-08-11T12:00:00.000Z",
                        },
                        {
                            "id": "duplicate-old",
                            "created_time": "2026-08-10T00:00:00.000Z",
                            "last_edited_time": "2026-08-10T12:00:00.000Z",
                        },
                    ],
                    "has_more": False,
                }
            if method == "GET":
                return {"results": [{"id": "old-block"}], "has_more": False}
            return {}

        new_blocks = [{"object": "block", "type": "paragraph"}]
        with (
            patch.object(import_to_notion, "notion_request", side_effect=fake_request),
            patch.object(import_to_notion, "read_entry_body", return_value="new body"),
            patch.object(import_to_notion, "markdown_to_blocks", return_value=new_blocks),
            patch.object(import_to_notion.time, "sleep"),
        ):
            result = import_entry(
                self.notion_args("update"),
                "token",
                {"headword": "approximately", "file": "unused.md"},
            )

        self.assertIn("page_id=duplicate-newest", result)
        self.assertIn("matched_pages=2", result)
        self.assertIn("selected_last_edited_time=2026-08-11T12:00:00.000Z", result)
        self.assertTrue(
            any(
                method == "GET" and path.startswith("/blocks/duplicate-newest/children")
                for method, path, _ in calls
            )
        )
        self.assertFalse(any("duplicate-old" in path for _, path, _ in calls))

    def test_duplicate_page_selection_requires_last_edited_time(self) -> None:
        with self.assertRaisesRegex(NotionApiError, "missing last_edited_time"):
            import_to_notion.select_latest_edited_page(
                [
                    {
                        "id": "complete",
                        "last_edited_time": "2026-08-11T12:00:00.000Z",
                    },
                    {"id": "incomplete"},
                ]
            )

    def test_create_policy_always_creates_without_querying_existing_titles(self) -> None:
        calls: list[tuple[str, str, object]] = []

        def fake_request(
            method: str,
            path: str,
            token: str,
            notion_version: str,
            payload: object = None,
        ) -> dict[str, object]:
            calls.append((method, path, payload))
            if method == "POST" and path == "/pages":
                return {"id": "new-page"}
            return {}

        new_blocks = [{"object": "block", "type": "paragraph"}]
        with (
            patch.object(import_to_notion, "notion_request", side_effect=fake_request),
            patch.object(import_to_notion, "read_entry_body", return_value="new body"),
            patch.object(import_to_notion, "markdown_to_blocks", return_value=new_blocks),
            patch.object(import_to_notion.time, "sleep"),
        ):
            result = import_entry(
                self.notion_args(),
                "token",
                {"headword": "approximately", "file": "unused.md"},
            )

        self.assertIn("CREATE approximately", result)
        create_payload = next(payload for method, path, payload in calls if path == "/pages")
        self.assertEqual(create_payload["properties"]["Status"], {"status": {"name": "未着手"}})
        self.assertFalse(any(path.endswith("/query") for _, path, _ in calls))
        self.assertTrue(
            any(path == "/blocks/new-page/children" for _, path, _ in calls)
        )

    def test_skip_policy_keeps_an_existing_page_unchanged(self) -> None:
        calls: list[tuple[str, str]] = []

        def fake_request(
            method: str,
            path: str,
            token: str,
            notion_version: str,
            payload: object = None,
        ) -> dict[str, object]:
            calls.append((method, path))
            return {"results": [{"id": "existing-page"}], "has_more": False}

        with (
            patch.object(import_to_notion, "notion_request", side_effect=fake_request),
            patch.object(import_to_notion, "read_entry_body", return_value="new body"),
            patch.object(import_to_notion, "markdown_to_blocks", return_value=[]),
        ):
            result = import_entry(
                self.notion_args("skip"),
                "token",
                {"headword": "approximately", "file": "unused.md"},
            )

        self.assertIn("SKIP approximately", result)
        self.assertEqual(calls, [("POST", "/data_sources/data-source-id/query")])


if __name__ == "__main__":
    unittest.main()
