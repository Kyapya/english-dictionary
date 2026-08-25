from __future__ import annotations

import argparse
import hashlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKUP_ROOT = REPO_ROOT / "backups" / "2026-08-25-process-refactor"
DEFAULT_OUTPUT = REPO_ROOT / "prompts" / "migration_table_v5_to_v6.md"
SOURCES = {
    "AGENTS": BACKUP_ROOT / "AGENTS.md",
    "CHECK": BACKUP_ROOT / "prompts" / "check_spec_v5.md",
    "FINAL": BACKUP_ROOT / "prompts" / "final_review_spec_v1.md",
}
LIST_ITEM = re.compile(r"^\s*(?:-|\d+\.)\s+")
NORMATIVE_SIGNAL = re.compile(
    r"(する|しない|ならない|禁止|必須|確認|使う|扱う|認めない|限る|"
    r"必要|保存|記録|実行|決定|同期|渡す|開始|作る|置く|読む|"
    r"更新|維持|出力|合格|不合格|PASS|REJECT)"
)


@dataclass(frozen=True)
class Rule:
    source: str
    line_start: int
    line_end: int
    heading: str
    text: str

    @property
    def id(self) -> str:
        return f"{self.source}-L{self.line_start:04d}"


@dataclass(frozen=True)
class Migration:
    disposition: str
    destination: str
    reason: str


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def extract_rules(source: str, path: Path) -> list[Rule]:
    lines = path.read_text(encoding="utf-8").splitlines()
    rules: list[Rule] = []
    heading = "(preamble)"
    in_code = False
    index = 0
    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            index += 1
            continue
        if in_code:
            index += 1
            continue
        if stripped.startswith("#"):
            heading = stripped.lstrip("#").strip()
            index += 1
            continue
        if not stripped:
            index += 1
            continue
        start = index
        if LIST_ITEM.match(raw):
            parts = [LIST_ITEM.sub("", stripped, count=1)]
            index += 1
            while index < len(lines):
                candidate = lines[index]
                candidate_stripped = candidate.strip()
                if (
                    not candidate_stripped
                    or candidate_stripped.startswith("#")
                    or candidate_stripped.startswith("```")
                    or LIST_ITEM.match(candidate)
                ):
                    break
                if candidate.startswith((" ", "\t")):
                    parts.append(candidate_stripped)
                    index += 1
                    continue
                break
            rules.append(
                Rule(source, start + 1, index, heading, _clean(" ".join(parts)))
            )
            continue
        parts = [stripped]
        index += 1
        while index < len(lines):
            candidate = lines[index]
            candidate_stripped = candidate.strip()
            if (
                not candidate_stripped
                or candidate_stripped.startswith("#")
                or candidate_stripped.startswith("```")
                or LIST_ITEM.match(candidate)
            ):
                break
            parts.append(candidate_stripped)
            index += 1
        text = _clean(" ".join(parts))
        if NORMATIVE_SIGNAL.search(text):
            rules.append(Rule(source, start + 1, index, heading, text))
    return rules


def _route_check(rule: Rule) -> Migration:
    value = f"{rule.heading} {rule.text}"
    if any(
        marker in rule.heading
        for marker in (
            "v5書式監査",
            "大見出し",
            "空行と行末",
            "コロケーションの固定書式",
            "類義語・反意語の固定書式",
        )
    ) or any(
        marker in value
        for marker in (
            "front matter",
            "行末半角スペース",
            "固定行数",
            "全角 `＃`",
            "【続きあり】",
            "絵文字",
            "validate_entry.py",
            "ラベルと本文を同一行",
            "単独行",
        )
    ):
        return Migration(
            "scripted",
            "scripts/validate_entry.py",
            "決定的な構造・書式検査として機械化し、checker proseへ重複させない。",
        )
    if any(
        marker in value
        for marker in (
            "コールドレビュー",
            "final_review",
            "最終審査",
            "run ID",
            "context ID",
            "status",
            "checked",
            "queue",
            "logs",
            "監査ファイル",
            "raw_outputs",
            "body_revisions",
            "start-cycle",
            "add-revision",
            "semantic_gate",
            "constraint",
            "scope anchor",
            "scope_anchor",
            "blast radius",
            "heartbeat",
            "budget",
            "commit",
            "push",
        )
    ):
        destination = (
            "scripts/semantic_resolution_gate.py; scripts/content_audit.py"
            if any(
                marker in value
                for marker in (
                    "semantic",
                    "constraint",
                    "scope",
                    "blast",
                    "raw_outputs",
                    "body_revisions",
                )
            )
            else "scripts/run_word.py; scripts/entry_workflow_guard.py"
        )
        return Migration(
            "scripted",
            destination,
            "工程順序・入力分離・記録・安全停止をオーケストレータまたはgateが強制する。",
        )
    if any(
        marker in value
        for marker in (
            "発音",
            "IPA",
            "強勢",
            "音節",
            "フラッピング",
            "同化",
            "脱落",
        )
    ):
        return Migration(
            "moved",
            "prompts/check_pass_pronunciation_v6.md",
            "発音記号と説明の専用内容パスへ移設。",
        )
    if any(
        marker in value
        for marker in (
            "根拠",
            "資料",
            "evidence",
            "source-first",
            "引用",
            "コーパス",
        )
    ):
        return Migration(
            "moved",
            "prompts/check_pass_evidence_v6.md; prompts/source_first_audit_v2.md",
            "資料収集はsource-first、claim支持の検査はevidence passへ一意に分担。",
        )
    if any(
        marker in value
        for marker in (
            "地域",
            "米英",
            "専門",
            "制度",
            "法律",
            "保険",
            "税務",
            "医療",
            "頻度",
            "レジスター",
            "古風",
            "必ず",
            "常に",
            "のみ",
            "できない",
            "反例",
        )
    ):
        return Migration(
            "moved",
            "prompts/check_pass_qualification_v6.md",
            "限定・適用範囲・専門慣用性の専用内容パスへ移設。",
        )
    if any(
        marker in value
        for marker in (
            "類義語",
            "反意語",
            "統語フレーム",
            "文法パターン",
            "目的語",
            "再帰",
            "小辞",
            "前置詞",
            "項構造",
            "語順",
            "自動詞",
            "他動詞",
        )
    ):
        return Migration(
            "moved",
            "prompts/check_pass_frame_relation_v6.md",
            "完全フレーム・項役割・語彙関係の専用内容パスへ移設。",
        )
    if any(
        marker in value
        for marker in (
            "例文",
            "訳",
            "意味役割",
            "肯定・否定",
            "修飾範囲",
            "原因",
            "結果",
            "作用",
            "方向",
        )
    ):
        return Migration(
            "moved",
            "prompts/check_pass_translation_v6.md",
            "英文・訳・意味方向の専用内容パスへ移設。",
        )
    return Migration(
        "moved",
        "prompts/check_pass_sense_structure_v6.md",
        "語義棚卸し・境界・セクション整合の内容パスへ保守的に移設。",
    )


def _route_agents(rule: Rule) -> Migration:
    value = f"{rule.heading} {rule.text}"
    if rule.heading in {"ファイル命名", "ステータス"}:
        return Migration(
            "retained",
            "AGENTS.md",
            "ルーターに許可された命名規則またはstatus一覧として残置。",
        )
    if "Notion" in value or "NOTION_TOKEN" in value:
        return Migration(
            "moved",
            "prompts/notion_spec_v1.md; scripts/import_to_notion.py",
            "Notion固有の規範と強制実装へ移設。",
        )
    if "process_improvement" in value or "ACTIVE.md" in value or "改善" in value:
        return Migration(
            "scripted",
            "process_improvement/README.md; scripts/process_improvement.py",
            "工程改善registryの正本と機械検証へ移設。",
        )
    if any(
        marker in value
        for marker in (
            "内容",
            "語義",
            "例文",
            "類義語",
            "反意語",
            "コロケーション",
            "発音",
            "語源",
            "語形成",
            "コアイメージ",
        )
    ) and not any(
        marker in value
        for marker in (
            "監査",
            "コールド",
            "最終審査",
            "checked",
            "checkpoint",
            "status",
        )
    ):
        return Migration(
            "moved",
            "prompts/entry_spec_v5.md; prompts/check_router_v6.md",
            "辞書学的内容はentry v5を不変正本とし、検査はv6 routerへ配送。",
        )
    return Migration(
        "scripted",
        "scripts/run_word.py; scripts/entry_workflow_guard.py",
        "branch、順序、入力分離、記録、heartbeat、budget、公開をコード側へ移設。",
    )


def _route_final(rule: Rule) -> Migration:
    value = f"{rule.heading} {rule.text}"
    if any(
        marker in value
        for marker in (
            "先行コミット",
            "別コミット",
            "seal",
            "raw",
            "原出力",
            "manifest",
            "マニフェスト",
            "body_revisions",
            "Git履歴",
            "SHA-256",
            "run ID",
            "context ID",
            "source_first_audit_gate.py",
            "semantic_resolution_gate.py",
        )
    ):
        return Migration(
            "scripted",
            "scripts/run_word.py; scripts/generate_audit_manifest.py; scripts/content_audit.py",
            "最終審査の時系列・原出力整合・派生値をコードで強制する。",
        )
    return Migration(
        "moved",
        "prompts/final_review_spec_v2.md",
        "合否の意味基準を変更せず、小型の最終判断仕様へ移設。",
    )


def migrate(rule: Rule) -> Migration:
    if rule.source == "AGENTS":
        return _route_agents(rule)
    if rule.source == "CHECK":
        return _route_check(rule)
    return _route_final(rule)


def all_rules() -> list[Rule]:
    return [
        rule
        for source, path in SOURCES.items()
        for rule in extract_rules(source, path)
    ]


def _escape(value: str) -> str:
    return value.replace("|", "&#124;").replace("\n", " ")


def _implementation_commit(migration: Migration) -> str:
    if migration.disposition != "scripted":
        return "—"
    destination = migration.destination
    if "process_improvement" in destination:
        return "WI-4 commit"
    if "generate_audit_manifest.py" in destination:
        return "WI-3 commit"
    if "validate_entry.py" in destination:
        return "WI-2 commit"
    if "run_word.py" in destination or "entry_workflow_guard.py" in destination:
        return "WI-1 `70c4f6c`; follow-up WI-3/WI-4 commits"
    return "existing implementation; WI-2 contract wiring"


def render_table() -> str:
    rules = all_rules()
    counts = {
        source: sum(rule.source == source for rule in rules) for source in SOURCES
    }
    hashes = {
        source: hashlib.sha256(path.read_bytes()).hexdigest()
        for source, path in SOURCES.items()
    }
    lines = [
        "# migration_table_v5_to_v6",
        "",
        "この表はprocess-refactor-v1で削除・移動した規範の全件台帳である。"
        "実行時の指示ではなく、固定済みbackupに対する移行証跡として扱う。",
        "",
        f"- 総規範unit: {len(rules)}",
        f"- AGENTS: {counts['AGENTS']} / CHECK: {counts['CHECK']} / FINAL: {counts['FINAL']}",
        "- 未処理・要確認: 0",
        "- disposition: retained=AGENTSルーター残置、moved=小型仕様へ移設、"
        "scripted=コード/CIへ移設、retired=理由付き廃止",
        "- implementation commit欄は、この変更系列のcommit message prefixを示す。"
        "WI-1のみ表作成時点で確定済みのlocal SHAを併記する。",
        "",
    ]
    for source, digest in hashes.items():
        lines.append(f"<!-- source-sha256 {source} {digest} -->")
    lines.extend(
        [
            "",
            "| rule id | source lines | source section | rule（要約） | disposition | destination | implementation commit | 理由 |",
            "|---|---:|---|---|---|---|---|---|",
        ]
    )
    for rule in rules:
        migration = migrate(rule)
        excerpt = rule.text if len(rule.text) <= 180 else rule.text[:177] + "..."
        lines.append(
            "| "
            + " | ".join(
                (
                    rule.id,
                    f"{rule.line_start}-{rule.line_end}",
                    _escape(rule.heading),
                    _escape(excerpt),
                    migration.disposition,
                    _escape(migration.destination),
                    _implementation_commit(migration),
                    _escape(migration.reason),
                )
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def validate_table(path: Path = DEFAULT_OUTPUT) -> list[str]:
    if not path.is_file():
        return [f"migration table not found: {path}"]
    text = path.read_text(encoding="utf-8")
    expected = {rule.id for rule in all_rules()}
    found = set(re.findall(r"^\| ((?:AGENTS|CHECK|FINAL)-L\d{4}) \|", text, re.MULTILINE))
    errors: list[str] = []
    for missing in sorted(expected - found):
        errors.append(f"missing migration rule: {missing}")
    for unexpected in sorted(found - expected):
        errors.append(f"unexpected migration rule: {unexpected}")
    if len(found) != len(expected):
        errors.append(
            f"migration rule count mismatch: expected {len(expected)}, found {len(found)}"
        )
    if "未処理・要確認: 0" not in text:
        errors.append("migration table must declare zero unresolved rules")
    if re.search(r"\|\s*(?:UNRESOLVED|要確認)\s*\|", text):
        errors.append("migration table contains an unresolved disposition")
    for source, source_path in SOURCES.items():
        digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
        if f"<!-- source-sha256 {source} {digest} -->" not in text:
            errors.append(f"source hash is stale: {source}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Render or validate v5-to-v6 migration")
    parser.add_argument("command", choices=("render", "validate"))
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.command == "render":
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(render_table(), encoding="utf-8")
        print(args.output.relative_to(REPO_ROOT))
        return 0
    errors = validate_table(args.output)
    if not errors:
        print("Migration table validation passed.")
        return 0
    print("Migration table validation failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
