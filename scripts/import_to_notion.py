from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from validate_entry import validate_file


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX_PATH = REPO_ROOT / "exports" / "dictionary_index.csv"
DEFAULT_DATA_SOURCE_ID = "37783e96-dad5-4fd2-82c0-37c0147b625b"
DEFAULT_NOTION_VERSION = "2026-03-11"
DEFAULT_TOKEN_ENV = "NOTION_TOKEN"
API_BASE = "https://api.notion.com/v1"
MAX_BLOCKS_PER_APPEND = 100
MAX_TEXT_CHARS = 1900
INCLUDED_STATUSES = {"checked", "final"}
SUBHEADING_LABELS = (
    "【日本語訳・定義】",
    "【頻度】",
    "【レジスター/領域】",
    "【文法パターン】",
    "【コロケーション】",
    "【語法・注意】",
    "【類義語】",
    "【反意語】",
)
GROUPED_ENTRY_SECTIONS = {"【コロケーション】", "【類義語】", "【反意語】"}
GROUPED_ENTRY_SCHEMAS = {
    "【コロケーション】": ("・", "用途:", "例:", "訳:"),
    "【類義語】": ("・", "定義:", "頻度:", "違い:", "例:", "訳:"),
    "【反意語】": ("・", "定義:", "頻度:", "違い:", "例:", "訳:"),
}
INLINE_MARKUP_PATTERN = re.compile(r"(<br>|\n|`[^`\n]+`|\*[^*\n]+\*)")


class NotionApiError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import checked english-dictionary entries into a Notion data source."
    )
    parser.add_argument(
        "--index",
        default=str(DEFAULT_INDEX_PATH),
        help="Fallback index CSV used when --entry is not supplied.",
    )
    parser.add_argument(
        "--entry",
        action="append",
        default=None,
        help="Import this Markdown entry directly. Can be passed multiple times.",
    )
    parser.add_argument(
        "--parent-id",
        default=os.getenv("NOTION_DATA_SOURCE_ID", DEFAULT_DATA_SOURCE_ID),
        help="Notion data source or database ID.",
    )
    parser.add_argument(
        "--parent-type",
        choices=("data_source", "database"),
        default="data_source",
    )
    parser.add_argument("--token-env", default=DEFAULT_TOKEN_ENV)
    parser.add_argument(
        "--notion-version",
        default=os.getenv("NOTION_VERSION", DEFAULT_NOTION_VERSION),
    )
    parser.add_argument("--title-property", default="ALL")
    parser.add_argument("--status-property", default="Status")
    parser.add_argument(
        "--status-value",
        default="進行中",
        help="Status applied before any Notion body mutation begins.",
    )
    parser.add_argument(
        "--complete-status-value",
        default="完了",
        help="Status applied only after the complete body is verified.",
    )
    parser.add_argument("--tag-property", default="タグ")
    parser.add_argument("--tag-value", default="英単語")
    parser.add_argument(
        "--note-property",
        default="",
        help="Optional rich_text property name. Empty by default.",
    )
    parser.add_argument("--note-value", default="")
    parser.add_argument(
        "--existing-policy",
        choices=("create", "update", "skip", "error"),
        default="create",
        help=(
            "How to handle a page with the same ALL/title value. "
            "The default always creates a new page and preserves all earlier pages."
        ),
    )
    parser.add_argument(
        "--skip-existing",
        action=argparse.BooleanOptionalAction,
        default=None,
        help=(
            "Deprecated compatibility flag. --skip-existing selects the skip policy; "
            "--no-skip-existing selects the update policy."
        ),
    )
    parser.add_argument(
        "--include-unchecked",
        action="store_true",
        help="Allow entries whose status is not checked/final.",
    )
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--headword", action="append", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--sleep", type=float, default=0.35)
    return parser.parse_args()


def _split_front_matter(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("Entry is missing YAML front matter.")
    end = next(
        (index for index in range(1, len(lines)) if lines[index].strip() == "---"),
        None,
    )
    if end is None:
        raise ValueError("Entry has unterminated YAML front matter.")
    values: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        cleaned = value.strip()
        if cleaned.startswith('"') and cleaned.endswith('"'):
            try:
                cleaned = json.loads(cleaned)
            except json.JSONDecodeError:
                pass
        values[key.strip()] = str(cleaned)
    return values, "\n".join(lines[end + 1 :]).strip()


def read_index(
    index_path: Path,
    include_unchecked: bool,
    headwords: set[str] | None,
) -> list[dict[str, str]]:
    with index_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return _select_rows(rows, include_unchecked, headwords)


def read_entry_rows(
    entry_paths: list[str],
    include_unchecked: bool,
    headwords: set[str] | None,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for raw_path in entry_paths:
        path = Path(raw_path)
        if not path.is_absolute():
            path = REPO_ROOT / path
        values, _ = _split_front_matter(path.read_text(encoding="utf-8"))
        rows.append(
            {
                "headword": values.get("headword", ""),
                "status": values.get("status", ""),
                "checked": values.get("checked", ""),
                "file": str(path),
            }
        )
    return _select_rows(rows, include_unchecked, headwords)


def _select_rows(
    rows: list[dict[str, str]],
    include_unchecked: bool,
    headwords: set[str] | None,
) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    for row in rows:
        headword = (row.get("headword") or "").strip()
        if not headword:
            raise ValueError(f"Entry has no headword: {row.get('file', '<unknown>')}")
        if headwords is not None and headword not in headwords:
            continue
        if not include_unchecked:
            status = (row.get("status") or "").strip()
            checked = (row.get("checked") or "").strip().lower()
            if status not in INCLUDED_STATUSES or checked != "true":
                continue
        selected.append(row)
    return selected


def read_entry_body(row: dict[str, str]) -> str:
    raw_path = row.get("file", "")
    if not raw_path:
        raise ValueError(f"Missing file path for {row.get('headword', '<unknown>')}")
    path = Path(raw_path)
    if not path.is_absolute():
        path = REPO_ROOT / path
    validation_errors = validate_file(path)
    if validation_errors:
        details = "; ".join(validation_errors)
        raise ValueError(f"Entry failed validation before Notion import: {path}: {details}")
    _, body = _split_front_matter(path.read_text(encoding="utf-8"))
    return body


def chunk_text(text: str, limit: int = MAX_TEXT_CHARS) -> list[str]:
    if len(text) <= limit:
        return [text]
    chunks: list[str] = []
    rest = text
    while len(rest) > limit:
        split_at = rest.rfind(" ", 0, limit)
        if split_at < limit // 2:
            split_at = limit
        chunks.append(rest[:split_at].rstrip())
        rest = rest[split_at:].lstrip()
    if rest:
        chunks.append(rest)
    return chunks


def _rich_text_item(content: str, *, italic: bool = False, code: bool = False) -> dict[str, Any]:
    item: dict[str, Any] = {"type": "text", "text": {"content": content}}
    if italic or code:
        item["annotations"] = {
            "bold": False,
            "italic": italic,
            "strikethrough": False,
            "underline": False,
            "code": code,
            "color": "default",
        }
    return item


def rich_text(content: str) -> list[dict[str, Any]]:
    """Compile the repository's inline Markdown to Notion rich-text objects."""
    items: list[dict[str, Any]] = []
    cursor = 0
    for match in INLINE_MARKUP_PATTERN.finditer(content):
        if match.start() > cursor:
            items.append(_rich_text_item(content[cursor : match.start()]))
        token = match.group(0)
        if token in {"<br>", "\n"}:
            # <br> is the conversion contract; the API's native representation is a
            # newline inside the same rich_text block, not the literal HTML string.
            items.append(_rich_text_item("\n"))
        elif token.startswith("`"):
            items.append(_rich_text_item(token[1:-1], code=True))
        else:
            items.append(_rich_text_item(token[1:-1], italic=True))
        cursor = match.end()
    if cursor < len(content):
        items.append(_rich_text_item(content[cursor:]))
    return items or [_rich_text_item("")]


def text_block(block_type: str, content: str) -> dict[str, Any]:
    return {
        "object": "block",
        "type": block_type,
        block_type: {"rich_text": rich_text(content)},
    }


def _heading_block(
    line: str,
) -> tuple[dict[str, Any] | None, str | None, str | None]:
    stripped = line.strip()
    fullwidth = re.match(r"^＃\s*(.+)$", stripped)
    if fullwidth:
        return text_block("heading_1", fullwidth.group(1)), None, None
    markdown = re.match(r"^(#{1,3})\s*(.+)$", stripped)
    if markdown:
        level = min(len(markdown.group(1)), 3)
        return text_block(f"heading_{level}", markdown.group(2)), None, None
    if re.match(r"^\d+\.\s*【.+】", stripped):
        return text_block("heading_2", stripped), None, None
    for label in SUBHEADING_LABELS:
        if stripped.startswith(label):
            remainder = stripped[len(label) :].strip()
            return text_block("heading_3", label[1:-1]), label, remainder or None
    return None, None, None


def markdown_to_blocks(markdown: str) -> list[dict[str, Any]]:
    lines = markdown.splitlines()
    blocks: list[dict[str, Any]] = []
    grouped_section: str | None = None
    index = 0

    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped:
            index += 1
            continue

        heading, label, remainder = _heading_block(stripped)
        if heading is not None:
            blocks.append(heading)
            grouped_section = label if label in GROUPED_ENTRY_SECTIONS else None
            if grouped_section and remainder:
                raise ValueError(f"{grouped_section} must be a standalone source heading.")
            if remainder:
                for chunk in chunk_text(remainder):
                    blocks.append(text_block("paragraph", chunk))
            index += 1
            continue

        if grouped_section and stripped.startswith("・"):
            entry_lines = [stripped]
            index += 1
            while index < len(lines):
                candidate = lines[index].strip()
                if not candidate:
                    break
                candidate_heading, _, _ = _heading_block(candidate)
                if candidate_heading is not None or candidate.startswith("・"):
                    break
                entry_lines.append(candidate)
                index += 1
            expected_prefixes = GROUPED_ENTRY_SCHEMAS[grouped_section]
            if len(entry_lines) != len(expected_prefixes) or any(
                not line.startswith(prefix)
                for line, prefix in zip(entry_lines, expected_prefixes)
            ):
                raise ValueError(
                    f"Malformed {grouped_section} entry; expected "
                    f"{len(expected_prefixes)} fixed lines in one block."
                )
            entry_text = "<br>".join(entry_lines)
            if len(entry_text) > MAX_TEXT_CHARS:
                raise ValueError(
                    f"A {grouped_section} entry exceeds Notion's safe text size: "
                    f"{len(entry_text)} characters"
                )
            blocks.append(text_block("paragraph", entry_text))
            continue

        grouped_section = None
        if stripped.startswith("・") or stripped.startswith("- ") or stripped.startswith("* "):
            content = stripped[1:].strip() if stripped.startswith("・") else stripped[2:].strip()
            for chunk in chunk_text(content):
                blocks.append(text_block("bulleted_list_item", chunk))
        else:
            for chunk in chunk_text(stripped):
                blocks.append(text_block("paragraph", chunk))
        index += 1
    return blocks


def notion_request(
    method: str,
    path: str,
    token: str,
    notion_version: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    data = None
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": notion_version,
        "Content-Type": "application/json",
    }
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        f"{API_BASE}{path}", data=data, headers=headers, method=method
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise NotionApiError(f"{method} {path} failed: HTTP {error.code}: {body}") from error
    except urllib.error.URLError as error:
        raise NotionApiError(f"{method} {path} failed: {error}") from error


def query_path(parent_type: str, parent_id: str) -> str:
    if parent_type == "data_source":
        return f"/data_sources/{parent_id}/query"
    return f"/databases/{parent_id}/query"


def find_pages(
    token: str,
    notion_version: str,
    parent_type: str,
    parent_id: str,
    title_property: str,
    headword: str,
) -> list[dict[str, Any]]:
    pages: list[dict[str, Any]] = []
    cursor: str | None = None
    while True:
        payload: dict[str, Any] = {
            "filter": {"property": title_property, "title": {"equals": headword}},
            "page_size": 100,
        }
        if cursor:
            payload["start_cursor"] = cursor
        result = notion_request(
            "POST", query_path(parent_type, parent_id), token, notion_version, payload
        )
        pages.extend(result.get("results", []))
        if not result.get("has_more"):
            return pages
        cursor = result.get("next_cursor")
        if not cursor:
            raise NotionApiError("Notion query indicated more pages without a cursor.")


def select_latest_edited_page(pages: list[dict[str, Any]]) -> dict[str, Any]:
    """Select the most recently edited page, with deterministic tie-breaking."""
    candidates: list[tuple[str, str, str, dict[str, Any]]] = []
    for page in pages:
        page_id = page.get("id")
        last_edited_time = page.get("last_edited_time")
        if not isinstance(page_id, str) or not page_id:
            raise NotionApiError("Existing Notion page is missing its id.")
        if not isinstance(last_edited_time, str) or not last_edited_time:
            raise NotionApiError(
                f"Existing Notion page {page_id} is missing last_edited_time."
            )
        created_time = page.get("created_time")
        created_key = created_time if isinstance(created_time, str) else ""
        candidates.append((last_edited_time, created_key, page_id, page))
    if not candidates:
        raise NotionApiError("Cannot select the latest page from an empty result.")
    return max(candidates, key=lambda candidate: candidate[:3])[3]


def page_parent(parent_type: str, parent_id: str) -> dict[str, Any]:
    if parent_type == "data_source":
        return {"data_source_id": parent_id}
    return {"database_id": parent_id}


def page_properties(args: argparse.Namespace, headword: str) -> dict[str, Any]:
    properties: dict[str, Any] = {
        args.title_property: {"title": rich_text(headword)},
        args.status_property: {"status": {"name": args.status_value}},
        args.tag_property: {"multi_select": [{"name": args.tag_value}]},
    }
    if args.note_property:
        properties[args.note_property] = {"rich_text": rich_text(args.note_value)}
    return properties


def create_page(args: argparse.Namespace, token: str, headword: str) -> str:
    payload = {
        "parent": page_parent(args.parent_type, args.parent_id),
        "properties": page_properties(args, headword),
    }
    result = notion_request("POST", "/pages", token, args.notion_version, payload)
    return result["id"]


def update_page_status(
    args: argparse.Namespace,
    token: str,
    page_id: str,
    status_value: str,
) -> None:
    notion_request(
        "PATCH",
        f"/pages/{page_id}",
        token,
        args.notion_version,
        {
            "properties": {
                args.status_property: {"status": {"name": status_value}}
            }
        },
    )


def append_blocks(
    args: argparse.Namespace,
    token: str,
    page_id: str,
    blocks: list[dict[str, Any]],
) -> None:
    for start in range(0, len(blocks), MAX_BLOCKS_PER_APPEND):
        batch = blocks[start : start + MAX_BLOCKS_PER_APPEND]
        notion_request(
            "PATCH",
            f"/blocks/{page_id}/children",
            token,
            args.notion_version,
            {"children": batch},
        )
        time.sleep(args.sleep)


def list_child_blocks(
    args: argparse.Namespace,
    token: str,
    page_id: str,
) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    cursor: str | None = None
    while True:
        params: dict[str, Any] = {"page_size": 100}
        if cursor:
            params["start_cursor"] = cursor
        path = f"/blocks/{page_id}/children?{urllib.parse.urlencode(params)}"
        result = notion_request("GET", path, token, args.notion_version)
        blocks.extend(result.get("results", []))
        if not result.get("has_more"):
            return blocks
        cursor = result.get("next_cursor")
        if not cursor:
            raise NotionApiError("Notion block listing indicated more pages without a cursor.")


def trash_blocks(
    args: argparse.Namespace,
    token: str,
    blocks: list[dict[str, Any]],
) -> None:
    for block in blocks:
        block_id = block.get("id")
        if not block_id:
            raise NotionApiError("Existing Notion block is missing its id.")
        notion_request(
            "PATCH",
            f"/blocks/{block_id}",
            token,
            args.notion_version,
            {"in_trash": True},
        )
        time.sleep(args.sleep)


def verify_child_block_count(
    args: argparse.Namespace,
    token: str,
    page_id: str,
    expected_count: int,
) -> None:
    actual_count = len(list_child_blocks(args, token, page_id))
    if actual_count != expected_count:
        raise NotionApiError(
            f"Notion body verification failed for page {page_id}: "
            f"expected {expected_count} blocks, found {actual_count}."
        )


def existing_policy(args: argparse.Namespace) -> str:
    legacy = getattr(args, "skip_existing", None)
    if legacy is not None:
        return "skip" if legacy else "update"
    return getattr(args, "existing_policy", "create")


def import_entry(args: argparse.Namespace, token: str, row: dict[str, str]) -> str:
    headword = row["headword"]
    body = read_entry_body(row)
    blocks = markdown_to_blocks(body)
    if args.dry_run:
        return f"DRY-RUN {headword}: {len(body)} chars, {len(blocks)} blocks"
    policy = existing_policy(args)
    if policy == "create":
        page_id = create_page(args, token, headword)
        time.sleep(args.sleep)
        append_blocks(args, token, page_id, blocks)
        verify_child_block_count(args, token, page_id, len(blocks))
        update_page_status(args, token, page_id, args.complete_status_value)
        return f"CREATE {headword}: {len(blocks)} blocks, page_id={page_id}"
    pages = find_pages(
        token,
        args.notion_version,
        args.parent_type,
        args.parent_id,
        args.title_property,
        headword,
    )
    if pages:
        if policy == "skip":
            return f"SKIP {headword}: page already exists"
        if policy == "error":
            raise NotionApiError(f"Page already exists for {headword!r}.")
        selection_details = ""
        if len(pages) > 1:
            selected_page = select_latest_edited_page(pages)
            selection_details = (
                f", matched_pages={len(pages)}, "
                f"selected_last_edited_time={selected_page['last_edited_time']}"
            )
        else:
            selected_page = pages[0]
        page_id = selected_page.get("id")
        if not page_id:
            raise NotionApiError("Existing Notion page is missing its id.")
        update_page_status(args, token, page_id, args.status_value)
        old_blocks = list_child_blocks(args, token, page_id)
        # Append first so a failed upload leaves the previous complete body intact.
        append_blocks(args, token, page_id, blocks)
        trash_blocks(args, token, old_blocks)
        verify_child_block_count(args, token, page_id, len(blocks))
        update_page_status(args, token, page_id, args.complete_status_value)
        return (
            f"UPDATE {headword}: replaced {len(old_blocks)} blocks with "
            f"{len(blocks)} blocks, page_id={page_id}{selection_details}"
        )
    page_id = create_page(args, token, headword)
    time.sleep(args.sleep)
    append_blocks(args, token, page_id, blocks)
    verify_child_block_count(args, token, page_id, len(blocks))
    update_page_status(args, token, page_id, args.complete_status_value)
    return f"CREATE {headword}: {len(blocks)} blocks, page_id={page_id}"


def main() -> int:
    args = parse_args()
    token = os.getenv(args.token_env, "")
    if not token and not args.dry_run:
        print(f"ERROR: set {args.token_env} to your Notion integration token.", file=sys.stderr)
        return 2
    if not args.parent_id and not args.dry_run:
        print("ERROR: set NOTION_DATA_SOURCE_ID or pass --parent-id.", file=sys.stderr)
        return 2

    headwords = set(args.headword) if args.headword else None
    try:
        if args.entry:
            rows = read_entry_rows(args.entry, args.include_unchecked, headwords)
        else:
            rows = read_index(Path(args.index), args.include_unchecked, headwords)
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if args.limit is not None:
        rows = rows[: args.limit]
    if not rows:
        print("No entries matched the import filters.")
        return 0

    print(f"Import target: {args.parent_type} {args.parent_id}")
    print(f"Entries selected: {len(rows)}")
    failures = 0
    for row in rows:
        try:
            print(import_entry(args, token, row))
        except Exception as error:  # noqa: BLE001 - continue to report every selected entry.
            failures += 1
            print(f"ERROR {row.get('headword', '<unknown>')}: {error}", file=sys.stderr)
    if failures:
        print(f"Completed with {failures} failure(s).", file=sys.stderr)
        return 1
    print("Import complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
