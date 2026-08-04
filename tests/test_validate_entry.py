from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from validate_entry import validate_file  # noqa: E402


VALID_MARKDOWN = """---
headword: immaculate
type: word
status: checked
prompt_version: entry_spec_v2
model: unknown
created_at: 2026-07-21
updated_at: 2026-07-21
checked: true
tags: []
---

＃発音記号

米: /ɪˈmækjələt/｜英: /ɪˈmækjʊlət/

＃語源

ラテン語由来の語で、「汚れのない」という核を持つ。

＃語形成

・immaculately（副詞）— 隙なく、完璧に。

＃コアイメージ

「しみがない」ことから、清潔さと欠点のなさへ広がる。

＃意味や関連情報の出力（日本語訳）

1. 【形容詞】完全に清潔な、傷や汚れがない。

【日本語訳・定義】汚れや乱れがなく、隅々まで整っている。

【頻度】〈頻度: 5/10〉

【レジスター/領域】一般、やや書き言葉寄り。

【文法パターン】immaculate + 名詞／be + immaculate。

【コロケーション】

・in immaculate condition
用途: 中古品などが傷や汚れのない状態であること。
例: The car is in immaculate condition.
訳: その車は新品同様の状態だ。

【語法・注意】clean より強く、手入れの行き届いた印象を含む。

【類義語】

・spotless
定義: 汚れやしみが全く見当たらない。
頻度: 〈6/10〉
違い: 清潔さに焦点があり、immaculateほど完璧さ全般を含まないことがある。
例: The room was spotless.
訳: 部屋は非常に清潔だった。

【反意語】

・dirty
定義: 汚れている。
頻度: 〈8/10〉
違い: 清潔さという軸で反対になる一般語。
例: His shoes were dirty after the walk.
訳: 散歩の後、彼の靴は汚れていた。
"""


INVALID_MARKDOWN = """---
headword: broken
---

＃語源

例: This is broken.
"""


def _make_v3_markdown() -> str:
    lines = VALID_MARKDOWN.replace(
        "prompt_version: entry_spec_v2",
        "prompt_version: entry_spec_v3",
    ).splitlines()
    fixed_section = False
    fixed_markers = {"【コロケーション】", "【類義語】", "【反意語】"}
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped in fixed_markers:
            fixed_section = True
            continue
        if fixed_section and (
            stripped.startswith("＃")
            or stripped.startswith("【")
            or (stripped and stripped[0].isdigit() and ". 【" in stripped)
        ):
            fixed_section = False
        if fixed_section and stripped:
            lines[index] = f"{line}  "
    return "\n".join(lines) + "\n"


VALID_V3_MARKDOWN = _make_v3_markdown()
VALID_V4_MARKDOWN = VALID_V3_MARKDOWN.replace(
    "prompt_version: entry_spec_v3",
    "prompt_version: entry_spec_v4",
)


class ValidateEntryTests(unittest.TestCase):
    def _write_temp_markdown(self, text: str) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        path = Path(temp_dir.name) / "entry.md"
        path.write_text(text, encoding="utf-8")
        return path

    def test_valid_markdown_passes(self) -> None:
        path = self._write_temp_markdown(VALID_MARKDOWN)
        self.assertEqual(validate_file(path), [])

    def test_valid_v3_markdown_passes(self) -> None:
        path = self._write_temp_markdown(VALID_V3_MARKDOWN)
        self.assertEqual(validate_file(path), [])

    def test_valid_v4_markdown_passes(self) -> None:
        path = self._write_temp_markdown(VALID_V4_MARKDOWN)
        self.assertEqual(validate_file(path), [])

    def test_v4_uses_current_format_checks(self) -> None:
        text = VALID_V4_MARKDOWN.replace(
            "・in immaculate condition  \n",
            "・in immaculate condition\n",
            1,
        )
        path = self._write_temp_markdown(text)
        errors = validate_file(path)
        self.assertTrue(any("must end with two spaces" in error for error in errors))

    def test_optional_headings_may_be_omitted(self) -> None:
        text = VALID_MARKDOWN.replace(
            "＃語形成\n\n・immaculately（副詞）— 隙なく、完璧に。\n\n",
            "",
        ).replace(
            "＃コアイメージ\n\n「しみがない」ことから、清潔さと欠点のなさへ広がる。\n\n",
            "",
        )
        path = self._write_temp_markdown(text)
        self.assertEqual(validate_file(path), [])

    def test_optional_heading_order_is_checked(self) -> None:
        text = VALID_MARKDOWN.replace(
            "＃語形成\n\n・immaculately（副詞）— 隙なく、完璧に。\n\n"
            "＃コアイメージ\n\n「しみがない」ことから、清潔さと欠点のなさへ広がる。",
            "＃コアイメージ\n\n「しみがない」ことから、清潔さと欠点のなさへ広がる。\n\n"
            "＃語形成\n\n・immaculately（副詞）— 隙なく、完璧に。",
        )
        path = self._write_temp_markdown(text)
        errors = validate_file(path)
        self.assertTrue(any("heading order is wrong" in error for error in errors))

    def test_all_relation_lines_are_checked(self) -> None:
        text = VALID_MARKDOWN.replace(
            "訳: 部屋は非常に清潔だった。",
            "translation: 部屋は非常に清潔だった。",
        )
        path = self._write_temp_markdown(text)
        errors = validate_file(path)
        self.assertTrue(any("translation line should start with 訳:" in error for error in errors))

    def test_invalid_markdown_reports_errors(self) -> None:
        path = self._write_temp_markdown(INVALID_MARKDOWN)
        errors = validate_file(path)
        self.assertTrue(errors)
        self.assertTrue(any("status" in error for error in errors))
        self.assertTrue(any("missing required heading" in error for error in errors))

    def test_v3_fixed_block_lines_require_two_trailing_spaces(self) -> None:
        text = VALID_V3_MARKDOWN.replace(
            "・in immaculate condition  \n",
            "・in immaculate condition\n",
            1,
        )
        path = self._write_temp_markdown(text)
        errors = validate_file(path)
        self.assertTrue(any("must end with two spaces" in error for error in errors))

    def test_v3_rejects_continuation_marker(self) -> None:
        text = VALID_V3_MARKDOWN + "\n【続きあり】\n"
        path = self._write_temp_markdown(text)
        errors = validate_file(path)
        self.assertTrue(any("must not contain 【続きあり】" in error for error in errors))

    def test_v3_rejects_bad_relation_frequency(self) -> None:
        text = VALID_V3_MARKDOWN.replace("頻度: 〈6/10〉", "頻度: 〈11/10〉", 1)
        path = self._write_temp_markdown(text)
        errors = validate_file(path)
        self.assertTrue(any("frequency must be" in error for error in errors))

    def test_v3_collocation_pattern_must_include_headword(self) -> None:
        text = VALID_V3_MARKDOWN.replace(
            "・in immaculate condition",
            "・in perfect condition",
            1,
        )
        path = self._write_temp_markdown(text)
        errors = validate_file(path)
        self.assertTrue(any("must include headword" in error for error in errors))

    def test_unknown_prompt_version_is_rejected(self) -> None:
        text = VALID_MARKDOWN.replace(
            "prompt_version: entry_spec_v2",
            "prompt_version: entry_spec_v99",
        )
        path = self._write_temp_markdown(text)
        errors = validate_file(path)
        self.assertTrue(any("unsupported prompt_version" in error for error in errors))

    def test_json_quoted_front_matter_values_are_unquoted(self) -> None:
        text = VALID_V4_MARKDOWN.replace(
            "headword: immaculate",
            'headword: "immaculate"',
        ).replace(
            "type: word",
            'type: "word"',
        )
        path = self._write_temp_markdown(text)
        self.assertEqual(validate_file(path), [])


if __name__ == "__main__":
    unittest.main()
