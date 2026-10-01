from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
import urllib.error
from email.message import Message
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import call, patch


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import import_to_notion  # noqa: E402
from import_to_notion import (  # noqa: E402
    NotionApiError,
    import_entry,
    markdown_to_blocks,
    read_entry_body,
)


class NotionRequestTests(unittest.TestCase):
    @staticmethod
    def http_error(
        status: int = 429,
        retry_after: str | None = None,
        body: str = '{"code":"rate_limited"}',
    ) -> urllib.error.HTTPError:
        headers = Message()
        if retry_after is not None:
            headers["retry-after"] = retry_after
        return urllib.error.HTTPError(
            "https://api.notion.com/v1/pages",
            status,
            "request failed",
            headers,
            io.BytesIO(body.encode("utf-8")),
        )

    def test_retries_explicit_rate_limits_with_server_wait_and_same_payload(self) -> None:
        for method, path in (("POST", "/pages"), ("PATCH", "/blocks/page/children")):
            for header, expected_delay in (("0", 0), ("7", 7), (" 125 ", 125)):
                with self.subTest(method=method, header=header):
                    error = self.http_error(retry_after=header)
                    payload = {"children": [{"text": "日本語"}]}
                    with (
                        patch.object(
                            import_to_notion.urllib.request,
                            "urlopen",
                            side_effect=[error, io.BytesIO(b'{"id":"created"}')],
                        ) as urlopen,
                        patch.object(import_to_notion.time, "sleep") as sleep,
                    ):
                        result = import_to_notion.notion_request(
                            method, path, "token", "2026-03-11", payload
                        )
                    self.assertEqual(result, {"id": "created"})
                    self.assertEqual(urlopen.call_count, 2)
                    sleep.assert_called_once_with(expected_delay)
                    requests = [args.args[0] for args in urlopen.call_args_list]
                    self.assertIs(requests[0], requests[1])
                    self.assertEqual(requests[0].get_method(), method)
                    self.assertEqual(json.loads(requests[0].data), payload)
                    self.assertTrue(error.fp.closed)

    def test_missing_or_malformed_retry_after_uses_exponential_fallback(self) -> None:
        for header in (None, "", "invalid", "-1", "1.5", "NaN", "Infinity"):
            with self.subTest(header=header):
                with (
                    patch.object(
                        import_to_notion.urllib.request,
                        "urlopen",
                        side_effect=[
                            self.http_error(retry_after=header),
                            self.http_error(retry_after=header),
                            io.BytesIO(b'{}'),
                        ],
                    ) as urlopen,
                    patch.object(import_to_notion.time, "sleep") as sleep,
                ):
                    self.assertEqual(
                        import_to_notion.notion_request("GET", "/pages/id", "token", "version"),
                        {},
                    )
                self.assertEqual(urlopen.call_count, 3)
                self.assertEqual(sleep.call_args_list, [call(1), call(2)])

    def test_rate_limit_retry_exhaustion_preserves_final_error(self) -> None:
        errors = [
            self.http_error(body=f"rate limit attempt {attempt}")
            for attempt in range(import_to_notion.MAX_RATE_LIMIT_RETRIES + 1)
        ]
        with (
            patch.object(import_to_notion.urllib.request, "urlopen", side_effect=errors) as urlopen,
            patch.object(import_to_notion.time, "sleep") as sleep,
            self.assertRaisesRegex(NotionApiError, "HTTP 429: rate limit attempt 5") as raised,
        ):
            import_to_notion.notion_request("POST", "/pages", "token", "version", {})
        self.assertEqual(urlopen.call_count, 6)
        self.assertEqual(sleep.call_args_list, [call(1), call(2), call(4), call(8), call(16)])
        self.assertIs(raised.exception.__cause__, errors[-1])
        self.assertTrue(all(error.fp.closed for error in errors))

    def test_fallback_backoff_is_capped(self) -> None:
        error = self.http_error()
        try:
            self.assertEqual(
                import_to_notion._rate_limit_retry_delay(error, "{}", 10),
                import_to_notion.MAX_RATE_LIMIT_BACKOFF_SECONDS,
            )
        finally:
            error.close()

    def test_access_restriction_is_not_retried(self) -> None:
        body = json.dumps({"additional_data": {"rate_limit_reason": "public_api_request_blocked"}})
        with (
            patch.object(
                import_to_notion.urllib.request,
                "urlopen",
                side_effect=self.http_error(retry_after="1", body=body),
            ) as urlopen,
            patch.object(import_to_notion.time, "sleep") as sleep,
            self.assertRaisesRegex(NotionApiError, "public_api_request_blocked"),
        ):
            import_to_notion.notion_request("POST", "/pages", "token", "version", {})
        urlopen.assert_called_once()
        sleep.assert_not_called()

    def test_other_http_errors_never_repeat_non_idempotent_writes(self) -> None:
        for method, path in (("POST", "/pages"), ("PATCH", "/blocks/page/children")):
            for status in (400, 401, 403, 404, 409, 500, 502, 503, 504, 529):
                with self.subTest(method=method, status=status):
                    with (
                        patch.object(
                            import_to_notion.urllib.request,
                            "urlopen",
                            side_effect=self.http_error(status, "1", "failed"),
                        ) as urlopen,
                        patch.object(import_to_notion.time, "sleep") as sleep,
                        self.assertRaisesRegex(NotionApiError, f"HTTP {status}: failed"),
                    ):
                        import_to_notion.notion_request(method, path, "token", "version", {})
                    urlopen.assert_called_once()
                    sleep.assert_not_called()

    def test_transport_failures_never_repeat_non_idempotent_writes(self) -> None:
        for method, path in (("POST", "/pages"), ("PATCH", "/blocks/page/children")):
            for error, expected in (
                (urllib.error.URLError("connection lost"), NotionApiError),
                (TimeoutError("timed out"), TimeoutError),
                (ConnectionResetError("connection reset"), ConnectionResetError),
            ):
                with self.subTest(method=method, error=type(error).__name__):
                    with (
                        patch.object(import_to_notion.urllib.request, "urlopen", side_effect=error) as urlopen,
                        patch.object(import_to_notion.time, "sleep") as sleep,
                        self.assertRaises(expected),
                    ):
                        import_to_notion.notion_request(method, path, "token", "version", {})
                    urlopen.assert_called_once()
                    sleep.assert_not_called()

    def test_uncertain_response_after_rate_limit_stops_retries(self) -> None:
        with (
            patch.object(
                import_to_notion.urllib.request,
                "urlopen",
                side_effect=[self.http_error(retry_after="3"), self.http_error(503)],
            ) as urlopen,
            patch.object(import_to_notion.time, "sleep") as sleep,
            self.assertRaisesRegex(NotionApiError, "HTTP 503"),
        ):
            import_to_notion.notion_request("PATCH", "/blocks/page/children", "token", "version", {})
        self.assertEqual(urlopen.call_count, 2)
        sleep.assert_called_once_with(3)

    def test_invalid_success_response_is_not_retried(self) -> None:
        with (
            patch.object(
                import_to_notion.urllib.request, "urlopen", return_value=io.BytesIO(b"incomplete JSON")
            ) as urlopen,
            patch.object(import_to_notion.time, "sleep") as sleep,
            self.assertRaises(json.JSONDecodeError),
        ):
            import_to_notion.notion_request("POST", "/pages", "token", "version", {})
        urlopen.assert_called_once()
        sleep.assert_not_called()


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
            status_value="進行中",
            complete_status_value="完了",
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

    def test_updates_one_existing_page_between_in_progress_and_complete(self) -> None:
        calls: list[tuple[str, str, object]] = []
        child_reads = 0

        def fake_request(
            method: str,
            path: str,
            token: str,
            notion_version: str,
            payload: object = None,
        ) -> dict[str, object]:
            nonlocal child_reads
            calls.append((method, path, payload))
            if method == "POST" and path.endswith("/query"):
                return {"results": [{"id": "existing-page"}], "has_more": False}
            if method == "GET":
                child_reads += 1
                if child_reads > 1:
                    return {"results": [{"id": "new-block"}], "has_more": False}
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
        self.assertEqual(mutations[0][1], "/pages/existing-page")
        self.assertEqual(
            mutations[0][2],
            {"properties": {"Status": {"status": {"name": "進行中"}}}},
        )
        self.assertEqual(mutations[1][1], "/blocks/existing-page/children")
        self.assertEqual(mutations[2][1], "/blocks/old-1")
        self.assertEqual(mutations[3][1], "/blocks/old-2")
        self.assertEqual(mutations[2][2], {"in_trash": True})
        self.assertEqual(mutations[4][1], "/pages/existing-page")
        self.assertEqual(
            mutations[4][2],
            {"properties": {"Status": {"status": {"name": "完了"}}}},
        )
        self.assertEqual(child_reads, 2)

    def test_failed_update_never_marks_page_complete(self) -> None:
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
                return {"results": [{"id": "old-block"}], "has_more": False}
            if method == "PATCH" and path == "/blocks/old-block":
                raise NotionApiError("simulated replacement failure")
            return {}

        with (
            patch.object(import_to_notion, "notion_request", side_effect=fake_request),
            patch.object(import_to_notion, "read_entry_body", return_value="new body"),
            patch.object(
                import_to_notion,
                "markdown_to_blocks",
                return_value=[{"object": "block", "type": "paragraph"}],
            ),
            patch.object(import_to_notion.time, "sleep"),
            self.assertRaisesRegex(NotionApiError, "simulated replacement failure"),
        ):
            import_entry(
                self.notion_args("update"),
                "token",
                {"headword": "approximately", "file": "unused.md"},
            )

        status_names = [
            payload["properties"]["Status"]["status"]["name"]
            for method, path, payload in calls
            if method == "PATCH" and path == "/pages/existing-page"
        ]
        self.assertEqual(status_names, ["進行中"])

    def test_rate_limited_update_verifies_body_before_completion(self) -> None:
        responses = [
            io.BytesIO(b'{"results":[{"id":"existing-page"}],"has_more":false}'),
            io.BytesIO(b'{}'),
            io.BytesIO(b'{"results":[{"id":"old-block"}],"has_more":false}'),
            NotionRequestTests.http_error(retry_after="2"),
            io.BytesIO(b'{}'),
            NotionRequestTests.http_error(retry_after="3"),
            io.BytesIO(b'{}'),
            io.BytesIO(b'{"results":[{"id":"new-block"}],"has_more":false}'),
            io.BytesIO(b'{}'),
        ]
        with (
            patch.object(import_to_notion.urllib.request, "urlopen", side_effect=responses) as urlopen,
            patch.object(import_to_notion, "read_entry_body", return_value="new body"),
            patch.object(import_to_notion, "markdown_to_blocks", return_value=[{"type": "paragraph"}]),
            patch.object(import_to_notion.time, "sleep") as sleep,
        ):
            result = import_entry(
                self.notion_args("update"), "token", {"headword": "approximately", "file": "unused.md"}
            )
        self.assertIn("UPDATE approximately", result)
        requests = [args.args[0] for args in urlopen.call_args_list]
        self.assertEqual(len(requests), 9)
        self.assertTrue(requests[3].full_url.endswith("/blocks/existing-page/children"))
        self.assertIs(requests[3], requests[4])
        self.assertTrue(requests[5].full_url.endswith("/blocks/old-block"))
        self.assertIs(requests[5], requests[6])
        self.assertEqual(json.loads(requests[5].data), {"in_trash": True})
        self.assertEqual(requests[7].get_method(), "GET")
        self.assertTrue(requests[7].full_url.endswith("/children?page_size=100"))
        self.assertEqual(
            json.loads(requests[8].data),
            {"properties": {"Status": {"status": {"name": "完了"}}}},
        )
        self.assertEqual(sleep.call_args_list, [call(2), call(0), call(3), call(0)])

    def test_rate_limited_append_exhaustion_preserves_old_body_and_in_progress(self) -> None:
        responses = [
            io.BytesIO(b'{"results":[{"id":"existing-page"}],"has_more":false}'),
            io.BytesIO(b'{}'),
            io.BytesIO(b'{"results":[{"id":"old-block"}],"has_more":false}'),
        ] + [NotionRequestTests.http_error() for _ in range(import_to_notion.MAX_RATE_LIMIT_RETRIES + 1)]
        with (
            patch.object(import_to_notion.urllib.request, "urlopen", side_effect=responses) as urlopen,
            patch.object(import_to_notion, "read_entry_body", return_value="new body"),
            patch.object(import_to_notion, "markdown_to_blocks", return_value=[{"type": "paragraph"}]),
            patch.object(import_to_notion.time, "sleep"),
            self.assertRaisesRegex(NotionApiError, "HTTP 429"),
        ):
            import_entry(
                self.notion_args("update"), "token", {"headword": "approximately", "file": "unused.md"}
            )
        requests = [args.args[0] for args in urlopen.call_args_list]
        self.assertFalse(any(request.full_url.endswith("/blocks/old-block") for request in requests))
        statuses = [
            json.loads(request.data)["properties"]["Status"]["status"]["name"]
            for request in requests
            if request.full_url.endswith("/pages/existing-page")
        ]
        self.assertEqual(statuses, ["進行中"])

    def test_failed_body_verification_never_marks_page_complete(self) -> None:
        for policy in ("create", "update"):
            with self.subTest(policy=policy):
                with (
                    patch.object(import_to_notion, "read_entry_body", return_value="new body"),
                    patch.object(import_to_notion, "markdown_to_blocks", return_value=[{"type": "paragraph"}]),
                    patch.object(import_to_notion, "create_page", return_value="page"),
                    patch.object(import_to_notion, "find_pages", return_value=[{"id": "page"}]),
                    patch.object(import_to_notion, "list_child_blocks", return_value=[]),
                    patch.object(import_to_notion, "append_blocks"),
                    patch.object(import_to_notion, "trash_blocks"),
                    patch.object(import_to_notion, "update_page_status") as update_status,
                    patch.object(import_to_notion.time, "sleep"),
                    self.assertRaisesRegex(NotionApiError, "body verification failed"),
                ):
                    import_entry(
                        self.notion_args(policy), "token", {"headword": "approximately", "file": "unused.md"}
                    )
                self.assertNotIn("完了", [args.args[3] for args in update_status.call_args_list])

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
            if method == "GET":
                return {"results": [{"id": "new-block"}], "has_more": False}
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
        self.assertEqual(create_payload["properties"]["Status"], {"status": {"name": "進行中"}})
        self.assertFalse(any(path.endswith("/query") for _, path, _ in calls))
        self.assertTrue(
            any(path == "/blocks/new-page/children" for _, path, _ in calls)
        )
        self.assertTrue(
            any(
                method == "PATCH"
                and path == "/pages/new-page"
                and payload
                == {"properties": {"Status": {"status": {"name": "完了"}}}}
                for method, path, payload in calls
            )
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
