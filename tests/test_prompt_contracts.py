from __future__ import annotations

import fnmatch
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_passes  # noqa: E402


def _routed_pass_specifications() -> list[str]:
    router = check_passes.load_router(REPO_ROOT / "prompts" / "check_router_v6.md")
    return [str(item["specification"]) for item in router["passes"]]


def _documented_pass_specifications(text: str) -> set[str]:
    return set(re.findall(r"prompts/check_pass_[A-Za-z0-9_*]+\.md", text))


class PromptContractTests(unittest.TestCase):
    def test_entry_v5_complete_spec_keeps_all_quality_gates(self) -> None:
        text = (REPO_ROOT / "prompts" / "entry_spec_v5.md").read_text(encoding="utf-8")
        required = (
            "生成前の必須構文マトリクス",
            "分詞形容詞の必須監査",
            "再帰形・代名詞位置・語順交替の必須監査",
            "品詞境界とブロック整合",
            "最小対立の必須化",
            "コアイメージと歴史的語義",
            "語義棚卸しと構文棚卸しを別々",
            "行末に半角スペースをちょうど2個",
            "コロケーションエントリは次の4行固定",
            "類義語・反意語の各エントリは次の6行固定",
            "他の語義としても同程度に解釈できる例文",
            "prompt_version: entry_spec_v5",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_pre_refactor_specs_are_preserved_except_requested_additions(self) -> None:
        backup = REPO_ROOT / "backups" / "2026-08-25-process-refactor" / "prompts"
        additions = {
            "entry_spec_v5.md": (
                "- 同一または類似の統語フレームが複数の語義に現れる見出し語では、各例文を当該語義でのみ、または最も自然に、解釈できる文にする。語義の判別が統語形式から決まらず、意味（意図、対象領域、目的語の種類、評価）にのみ依存する場合は、判別根拠となる目的語、修飾語、文脈語を例文内に語彙的に含める。\n",
                "- 専門義に限らず、他の語義としても同程度に解釈できる例文を、その語義の例文として置かない。当該語義を明確に示す例文へ置き換えるか、実際に帰属する語義ブロックへ移す。\n",
            ),
            "check_spec_v5.md": (
                "- 専門義に限らず全語義について、各例文が所属ブロックの語義でのみ、または最も自然に、解釈できるか確認する。同一統語フレームが複数語義に現れる見出し語では、例文内の目的語・修飾語・文脈語だけから帰属語義を判別できない例文、および別語義として読む方が自然な例文を、置換または移動の対象とする。所属ブロックの【語法・注意】が示す語義区別に、そのブロック自身の例文が反していないかも確認する。\n",
            ),
        }
        for name, inserted_lines in additions.items():
            with self.subTest(name=name):
                current = (REPO_ROOT / "prompts" / name).read_text(encoding="utf-8")
                for line in inserted_lines:
                    self.assertEqual(current.count(line), 1)
                    current = current.replace(line, "")
                if name == "entry_spec_v5.md":
                    current = current.replace(
                        "通常はstandard profileを使い、開始から全工程60分、draft保存20分、検索query 12件、候補page 18件を上限とする。多義性または専門領域の広さについて具体的理由を記録した場合だけextendedを使え、開始から全工程90分、draft保存30分、検索query 18件、候補page 26件を上限とする。heartbeatは進捗時刻を残す監査情報であり、実行間隔に上限を設けない。個別budget上限を引き上げてはならない。",
                        "通常はstandard profileを使い、開始から全工程60分、draft保存20分、検索query 12件、候補page 18件、heartbeat間隔10分を上限とする。多義性または専門領域の広さについて具体的理由を記録した場合だけextendedを使え、開始から全工程90分、draft保存30分、検索query 18件、候補page 26件を上限とする。個別上限を引き上げてはならない。",
                    ).replace(
                        "採用した資料だけでなく、検索を試みるqueryと開く候補pageを、各外部調査batchの前に `entry_workflow_guard.py record-research` で記録する。`heartbeat` は各batchの前後などで進捗時刻を残すために実行できるが、間隔超過を停止条件にしない。終了コード2またはbudget到達時は、同じ依頼内で探索・再生成・新cycleを続けず、存在するdraftを `checked: false` のまま保存し、run JSONの `stop_reason` と `open_questions` をcommit・pushして安全停止する。時間不足を理由に合格基準を緩めてはならない。",
                        "採用した資料だけでなく、検索を試みるqueryと開く候補pageを、各外部調査batchの前に `entry_workflow_guard.py record-research` で記録する。各batchの前後と、作業中少なくとも10分ごとに `heartbeat` を実行する。終了コード2またはbudget到達時は、同じ依頼内で探索・再生成・新cycleを続けず、存在するdraftを `checked: false` のまま保存し、run JSONの `stop_reason` と `open_questions` をcommit・pushして安全停止する。時間不足を理由に合格基準を緩めてはならない。",
                    )
                self.assertEqual(current, (backup / name).read_text(encoding="utf-8"))
        current_final = (REPO_ROOT / "prompts" / "final_review_spec_v1.md").read_text(encoding="utf-8").replace(
            "全体時間・検索query・候補page budget",
            "全体時間・検索query・候補page・heartbeat budget",
        )
        self.assertEqual(
            current_final,
            (backup / "final_review_spec_v1.md").read_text(encoding="utf-8"),
        )

    def test_v6_checker_prompts_are_taxonomy_focused(self) -> None:
        router = (REPO_ROOT / "prompts" / "check_router_v6.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("finding_scope_transfer_loss", router)
        self.assertIn("raw_adjudication_manifest_divergence", router)
        for path in sorted((REPO_ROOT / "prompts").glob("check_pass_*_v6.md")):
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("## 担当タクソノミー分類", text)
                self.assertIn("## 入力として受け取るセクション", text)
                self.assertIn("## findingの出力スキーマ", text)
                self.assertNotIn("行末に半角スペースをちょうど2個", text)

    def test_three_party_inputs_are_separated_by_the_orchestrator(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/run_word.py", "--dry-run", "obvious"],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        stages = {item["name"]: item for item in json.loads(completed.stdout)["stages"]}
        self.assertEqual(stages["cold_review"]["input_scope"], ["entry body without front matter"])
        self.assertEqual(stages["final_blind"]["input_scope"], ["latest entry body only"])
        self.assertEqual(
            stages["final_review"]["input_scope"],
            [
                "latest entry body",
                "sealed final-blind output",
                "all checker, cold, and sealed final-blind findings",
                "finding resolution records",
            ],
        )
        self.assertEqual(stages["cold_review"]["context_mode"], "context_free_cold")
        self.assertEqual(stages["final_blind"]["context_mode"], "context_free_final_blind")
        self.assertEqual(
            stages["final_review"]["context_mode"], "final_reconciliation_context"
        )
        for stage in (stages["cold_review"], stages["final_blind"]):
            self.assertNotIn("ACTIVE.md", json.dumps(stage))
            self.assertNotIn("findings", json.dumps(stage))

    def test_final_v2_preserves_the_semantic_pass_fail_boundary(self) -> None:
        text = (REPO_ROOT / "prompts" / "final_review_spec_v2.md").read_text(
            encoding="utf-8"
        )
        for marker in (
            "事実、語法、発音、例文、訳",
            "主要な品詞、語義、派生・転換、専門用法、完全な統語フレーム",
            "語義境界、コアイメージ、定義、語法、コロケーション、語彙関係",
            "反例・矛盾・適用範囲",
            "すべてのfinding",
            "semantic_assertion",
            "条件付き合格は使わない",
            "非blocking note",
            "`REJECT` は審査失敗ではなく",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)
        self.assertIn("scripts/generate_audit_manifest.py", text)
        self.assertNotIn("entry_workflow_guard.py start", text)
        self.assertNotIn("start-cycle", text)
        self.assertNotIn("add-revision", text)

    def test_final_blind_prompt_has_no_reconciliation_identifiers(self) -> None:
        text = (REPO_ROOT / "prompts" / "final_blind_prompt_v2.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("semantic_assertions", text)
        self.assertIn("article_findings", text)
        self.assertIn("ACTIVE.md", text)
        self.assertIn("渡さない", text)
        self.assertIn("本文側target ID", text)

    def test_agents_routes_to_the_orchestrator(self) -> None:
        text = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        for marker in (
            "python scripts/run_word.py --dry-run <headword>",
            "prompts/entry_spec_v5.md",
            "prompts/check_router_v6.md",
            "prompts/check_pass_*_v6.md",
            "prompts/final_blind_prompt_v2.md",
            "prompts/final_review_spec_v2.md",
            "prompts/notion_spec_v1.md",
        ):
            self.assertIn(marker, text)
        for removed_procedure in (
            "record-research",
            "confirm-remote",
            "最大2回",
            "Pull Requestの機械検証が成功したら",
        ):
            self.assertNotIn(removed_procedure, text)

    def test_process_documents_point_at_the_specifications_the_router_selects(
        self,
    ) -> None:
        """AGENTS.md and README.md must not drift from check_router_v6.md.

        A router bump the process documents miss sends an agent to the previous
        pass specification, whose output the current ingestion contract rejects.
        """
        routed = _routed_pass_specifications()
        self.assertIn("prompts/check_pass_frame_relation_v7.md", routed)
        for name in ("AGENTS.md", "README.md"):
            document = (REPO_ROOT / name).read_text(encoding="utf-8")
            references = _documented_pass_specifications(document)
            self.assertTrue(references, f"{name} names no checker pass specification")
            for specification in routed:
                with self.subTest(document=name, specification=specification):
                    self.assertTrue(
                        any(
                            fnmatch.fnmatch(specification, reference)
                            for reference in references
                        ),
                        f"{name} does not cover {specification}",
                    )
            for reference in references:
                with self.subTest(document=name, reference=reference):
                    self.assertTrue(
                        any(
                            fnmatch.fnmatch(specification, reference)
                            for specification in routed
                        ),
                        f"{name} references {reference}, which the router does not select",
                    )

    def test_process_documents_describe_the_two_round_checker_handoff(self) -> None:
        """The checker handoff needs two responses; a one-round reading loops."""
        for name in ("AGENTS.md", "README.md"):
            document = (REPO_ROOT / name).read_text(encoding="utf-8")
            for marker in (
                "2往復",
                "checker_passes.stage1.json",
                "checker_passes.stage2.request.md",
                "checker_passes.frame-relation.stage2.response.json",
                "antonym_axis_blind_record",
                "budget_exhausted",
            ):
                with self.subTest(document=name, marker=marker):
                    self.assertIn(marker, document)

    def test_readme_routes_instead_of_repeating_the_old_process_specs(self) -> None:
        text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("OpenAI APIキーは不要", text)
        self.assertIn("scripts/run_word.py --dry-run", text)
        self.assertIn("content_audit_v4", text)
        self.assertIn("scripts/generate_audit_manifest.py", text)
        self.assertNotIn("prompts/check_spec_v5.md だけを全文", text)
        self.assertNotIn("scripts/content_audit.py start-cycle", text)

    def test_github_flow_keeps_generation_local_and_reviews_independent(self) -> None:
        validate_workflow = (
            REPO_ROOT / ".github" / "workflows" / "validate.yml"
        ).read_text(encoding="utf-8")
        notion_workflow = (
            REPO_ROOT / ".github" / "workflows" / "sync-notion.yml"
        ).read_text(encoding="utf-8")
        orchestrator = (REPO_ROOT / "scripts" / "run_word.py").read_text(
            encoding="utf-8"
        )
        review_caller = (REPO_ROOT / "scripts" / "review_call.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("generate_entry", orchestrator)
        self.assertIn("DICT_REVIEW_API_KEY", review_caller)
        self.assertIn('SUPPORTED_PROVIDERS = {"openai", "anthropic"}', review_caller)
        self.assertIn("independent_llm", orchestrator)
        self.assertIn("pull_request:", validate_workflow)
        self.assertIn("scripts/validate_repository.py", validate_workflow)
        self.assertIn("scripts/content_audit.py validate-changed", validate_workflow)
        self.assertIn("scripts/content_audit.py validate-sync", notion_workflow)
        self.assertFalse((REPO_ROOT / "scripts" / "generate_entry.py").exists())


if __name__ == "__main__":
    unittest.main()
