"""One-shot, exact-source-checked implementation patch for this work branch."""
from pathlib import Path
import ast
import subprocess

ROOT = Path.cwd()


def source(path, blob):
    actual = subprocess.check_output(['git', 'hash-object', path], text=True).strip()
    if actual != blob:
        raise SystemExit(f'refusing to patch unexpected source: {path}: {actual}')
    return (ROOT / path).read_text(encoding='utf-8')


def replace(text, old, new):
    if text.count(old) != 1:
        raise SystemExit(f'expected exactly one source anchor ({text.count(old)}): {old[:160]}')
    return text.replace(old, new, 1)


def function(text, name, new):
    node = next(n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == name)
    lines = text.splitlines(keepends=True)
    return ''.join(lines[:node.lineno - 1]) + new.rstrip() + '\n' + ''.join(lines[node.end_lineno:])


path = 'scripts/generate_audit_manifest.py'
s = source(path, 'e9a7fedac86ad9f48f555fc0669366d981188933')
s = replace(s, 'import workflow_revision\n', 'import workflow_revision\nimport review_validation\n')
s = function(s, '_validate_metadata', '''def _validate_metadata(
    raw: dict[str, Any], stage: str, body_hash: str, expected_artifacts: set[str]
) -> None:
    errors = review_validation.metadata_errors(raw, stage, body_hash, expected_artifacts)
    if errors:
        raise ValueError("; ".join(row["message"] for row in errors))
''')
s = replace(s, '    final_blind_ids: set[str],\n) -> dict[str, Any] | None:',
            '    final_blind_ids: set[str],\n    require_resolved: bool = False,\n) -> dict[str, Any] | None:')
s = replace(s, '''        if workflow_revision.targeted_adjudication_blocks_pass(record) and raw[
            "final_review"
        ].get("decision") == "pass":''', '''        if workflow_revision.targeted_adjudication_blocks_pass(record) and (
            require_resolved or raw.get("final_review", {}).get("decision") == "pass"
        ):''')
a = s.index('    resolutions = _index(raw["resolutions"].get("resolutions"), "resolutions")\n')
b = s.index('    checker_and_cold_ids = {\n', a)
s = s[:a] + '''    resolution_issues = review_validation.resolution_errors(
        raw["resolutions"].get("resolutions"), set(finding_index), current_hash
    )
    if resolution_issues:
        raise ValueError("; ".join(row["message"] for row in resolution_issues))
    resolutions = _index(raw["resolutions"].get("resolutions"), "resolutions")

''' + s[b:]
(ROOT / path).write_text(s, encoding='utf-8')

path = 'scripts/entry_workflow_guard.py'
s = source(path, 'd82cba28b6a2b54c965b413d0303ac3aabacc889')
s = function(s, 'clear_review_ingest_failures', '''def clear_review_ingest_failures(manifest: dict[str, Any]) -> None:
    """Close the active streak while preserving its counts and error history."""
    previous = manifest.pop("review_ingest_failures", None)
    if isinstance(previous, dict):
        manifest.setdefault("review_ingest_failure_history", []).append(dict(previous))
        manifest.setdefault("review_ingest_failure_total", previous.get("count", 0))
''')
s = replace(s, '    manifest["review_ingest_failures"] = failures\n', '''    manifest["review_ingest_failures"] = failures
    manifest["review_ingest_failure_total"] = int(
        manifest.get("review_ingest_failure_total", count)
    ) + 1
    manifest.setdefault("review_ingest_failure_events", []).append(dict(failures))
''')
(ROOT / path).write_text(s, encoding='utf-8')

path = 'scripts/run_word_v3.py'
s = source(path, '80b86cab0e6f9e7e8a9e998f57876fa8d52522e6')
s = replace(s, 'import review_preflight\n', 'import review_preflight\nimport review_recovery\n')
s = replace(s, '''def prepare_review_inputs(
    manifest: dict[str, Any], *, repo_root: Path = REPO_ROOT
)''', '''def prepare_review_inputs(
    manifest: dict[str, Any], *, repo_root: Path = REPO_ROOT,
    refresh_final: bool = False,
)''')
# This anchor is deliberately local to the non-checker packet branch.
s = replace(s, '''    packet_path = cycle_dir / f"{stage}.request.json"
    if manifest.get("review_preflight") == review_preflight.VERSION:
        packet["contract_version"] = review_preflight.VERSION
        review_preflight.freeze(packet_path, packet)''', '''    packet_path = cycle_dir / f"{stage}.request.json"
    if manifest.get("review_preflight") == review_preflight.VERSION:
        packet["contract_version"] = review_preflight.VERSION
        if stage == "final_review":
            review_recovery.bind_final_packet(packet, packet_path, refresh=refresh_final)
            if refresh_final:
                review_recovery.replace_final_packet(manifest, packet_path, packet)
        elif refresh_final:
            raise ValueError("packet refresh is supported only for final_review")
        review_preflight.freeze(packet_path, packet)''')
s = replace(s, '''        if request_packet.get("contract_version") == review_preflight.VERSION:
            review_preflight.check_bindings(request_packet, entry, cycle_dir)
        metadata = request_packet.get("_output_metadata")''', '''        if request_packet.get("contract_version") == review_preflight.VERSION:
            review_preflight.check_bindings(request_packet, entry, cycle_dir)
        revision_id = request_packet.get("input_revision_id")
        if revision_id and value.get("input_revision_id") != revision_id:
            raise ValueError("response input_revision_id does not match the current final-review packet; obtain a fresh independent response")
        metadata = request_packet.get("_output_metadata")''')
anchor = 'def _recover_time_stop(manifest: dict[str, Any], *, repo_root: Path) -> bool:\n'
s = replace(s, anchor, '''def _report_preflight_failure(
    manifest: dict[str, Any], run_path: Path, *, stage: str,
    error: BaseException, fingerprint: str | None = None,
) -> int:
    event = review_recovery.record_validation_failure(
        manifest, stage=stage, error=error, input_fingerprint=fingerprint
    )
    record_pending_process_event(manifest, kind="review_failure", stage=stage,
                                 fact="repairable preflight rejection: " + str(error))
    guard._write(run_path, manifest)
    print(json.dumps({
        "status": "needs_review_correction", "run_status": manifest["status"],
        "review_stage": stage, "error": str(error),
        "validation_failure_count": manifest["review_preflight_failures"]["count"],
        "ingest_failure_count": manifest.get("review_ingest_failures", {}).get("count", 0),
        "diagnostics": event.get("diagnostics"),
        "action": "correct the reported inputs/response and resume this same run",
    }, ensure_ascii=False, indent=2))
    return 1


''' + anchor)
s = replace(s, '''    reviewer_agent_id: str = "",
    call_review: bool = False,
) -> int:''', '''    reviewer_agent_id: str = "",
    call_review: bool = False,
    refresh_review: str | None = None,
) -> int:''')
anchor = '    if not isinstance(manifest.get("process_improvement"), dict):\n'
# This unique anchor follows publication handling and precedes heartbeat/terminal rejection.
s = replace(s, anchor, '''    if refresh_review:
        if refresh_review != "final_review" or manifest.get("review_preflight") != review_preflight.VERSION:
            raise ValueError("refresh-review requires a versioned final-review packet")
        if manifest.get("status") != "in_progress" and not review_recovery.is_recoverable_preflight_stop(manifest, stage=refresh_review):
            print(json.dumps({"status": "stopped", "reason": manifest.get("stop_reason", "terminal run")}))
            return 2
        try:
            if (next_stage_request(manifest) or {}).get("name") != refresh_review:
                raise ValueError("refresh-review must target the pending final-review stage")
            paths, _ = prepare_review_inputs(manifest, repo_root=REPO_ROOT, refresh_final=True)
            request = next_stage_request(manifest)
            if request and request.get("reviewer_mode") == "handoff":
                paths.append(prepare_handoff(manifest, repo_root=REPO_ROOT))
        except (ValueError, FileNotFoundError, UnicodeDecodeError) as exc:
            return _report_preflight_failure(manifest, resolved, stage=refresh_review, error=exc)
        guard._write(resolved, manifest)
        print(json.dumps({"status": "review_input_refreshed", "run_status": manifest["status"],
                          "requests": [str(p.relative_to(REPO_ROOT)) for p in paths],
                          "action": "obtain a fresh independent response, then ingest it on this same run"}, ensure_ascii=False))
        return 0
    if ingest_review and review_recovery.is_recoverable_preflight_stop(manifest, stage=ingest_review):
        try:
            review_recovery.recover_preflight_stop(
                manifest, stage=ingest_review, declared_model=declared_model,
                reviewer_agent_id=reviewer_agent_id or None, repo_root=REPO_ROOT,
                ingest=ingest_handoff_review,
            )
        except (ValueError, FileNotFoundError, UnicodeDecodeError) as exc:
            fingerprint = review_recovery.fingerprint(
                manifest, stage=ingest_review, declared_model=declared_model,
                reviewer_agent_id=reviewer_agent_id, repo_root=REPO_ROOT,
            )
            return _report_preflight_failure(manifest, resolved, stage=ingest_review,
                                             error=exc, fingerprint=fingerprint)
        guard._write(resolved, manifest)
''' + anchor)
old = '''                pending = next_stage_request(manifest)
                cycle = (REPO_ROOT / pending["output_paths"][-1 if ingest_review == "checker_passes" else 0]).parent
                fingerprint = review_preflight.digest({
                    "stage": ingest_review, "model": declared_model, "agent": reviewer_agent_id,
                    "files": {str(p.relative_to(cycle)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(cycle.rglob("*.json"))},
                    "body": _entry_body(REPO_ROOT / manifest["entry_path"]),
                })'''
new = '''                fingerprint = review_recovery.fingerprint(
                    manifest, stage=ingest_review, declared_model=declared_model,
                    reviewer_agent_id=reviewer_agent_id, repo_root=REPO_ROOT,
                )'''
s = replace(s, old, new)
s = replace(s, '''                except Exception as exc:
                    manifest["last_rejected_review"] = {"fingerprint": fingerprint, "error": str(exc)}
                    raise''', '''                except (ValueError, FileNotFoundError, UnicodeDecodeError) as exc:
                    return _report_preflight_failure(
                        manifest, resolved, stage=ingest_review, error=exc,
                        fingerprint=fingerprint,
                    )''')
s = replace(s, '        except Exception as exc:  # the guard owns every failed ingestion\n',
            '        except Exception as exc:  # actual ingestion/runtime failures retain the bounded guard\n')
s = replace(s, '''        guard.clear_review_ingest_failures(manifest)
        manifest.pop("last_rejected_review", None)''', '''        guard.clear_review_ingest_failures(manifest)
        review_recovery.resolve_validation_failure(manifest, stage=ingest_review)
        manifest.pop("last_rejected_review", None)''')
s = replace(s, '''            api_review_paths = execute_api_review_stage(manifest)
        except Exception as exc:''', '''            api_review_paths = execute_api_review_stage(manifest)
        except review_preflight.PreflightError as exc:
            return _report_preflight_failure(manifest, resolved, stage=str(stage_name), error=exc)
        except Exception as exc:''')
s = replace(s, '''        if next_request.get("reviewer_mode") == "handoff":
            handoff_path = prepare_handoff(manifest)
        else:
            review_request_paths, _ = prepare_review_inputs(manifest)''', '''        try:
            if next_request.get("reviewer_mode") == "handoff":
                handoff_path = prepare_handoff(manifest)
            else:
                review_request_paths, _ = prepare_review_inputs(manifest)
        except (ValueError, FileNotFoundError, UnicodeDecodeError) as exc:
            return _report_preflight_failure(manifest, resolved, stage=str(next_request["name"]), error=exc)''')
# Classify preparation errors before any API call; runtime errors still propagate.
s = replace(s, '''    _, packet = prepare_review_inputs(manifest, repo_root=repo_root)

    if stage == "checker_passes":''', '''    try:
        _, packet = prepare_review_inputs(manifest, repo_root=repo_root)
    except review_preflight.PreflightError:
        raise
    except (ValueError, FileNotFoundError, UnicodeDecodeError) as exc:
        raise review_preflight.PreflightError({
            "valid": False, "errors": [{"code": "input_contract", "path": stage, "message": str(exc)}],
            "blocked_checks": [],
        }) from exc

    if stage == "checker_passes":''')
s = replace(s, '    parser.add_argument("--validate-review", choices=sorted(REVIEW_STAGES))\n',
            '    parser.add_argument("--refresh-review", choices=("final_review",))\n    parser.add_argument("--validate-review", choices=sorted(REVIEW_STAGES))\n')
s = replace(s, '''    args = build_parser().parse_args()
    if args.validate_review:''', '''    args = build_parser().parse_args()
    if args.refresh_review:
        if (not args.resume or args.headword or args.dry_run or args.validate_review
                or args.ingest_review or args.call_review or args.complete_stage
                or args.record_revision or args.declared_model or args.reviewer_agent_id):
            raise SystemExit("--refresh-review requires only --resume")
        return _resume(args.resume, refresh_review=args.refresh_review)
    if args.validate_review:''')
s = replace(s, '''            print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False))''',
            '''            print(json.dumps({"valid": False, "error": str(exc), "diagnostics": getattr(exc, "report", None)}, ensure_ascii=False))''')
(ROOT / path).write_text(s, encoding='utf-8')

path = ROOT / 'AGENTS.md'
s = path.read_text(encoding='utf-8')
s = replace(s, '''検証の反復を新たな無制限の
修正ループにしない。同じ未修正応答の再投入、失敗回数を戻すための新run作成は禁止。''', '''入力・応答の契約不備は `needs_review_correction` として履歴へ分離し、
実取り込み・通信・実行失敗の停止回数へ算入しない。同じ未修正応答の再投入は拒否する。
旧事前検証エラーだけによる停止は、修正した応答の完全検証後に同じrunで復旧する。
失敗回数を戻すための新run作成は禁止。開始時刻・完了工程・累積失敗履歴を維持する。
最終レビュー依頼前に入力不整合を一括検証し、missing/extra・期待値/実値・検証不能項目を
まとめて修正する。本文が不変で依頼済みの入力だけを直した場合は
`--resume <run> --refresh-review final_review` で旧依頼・応答を保存して再依頼する。
新応答はひな形の `input_revision_id` と一致させる。本文変更は従来のrevision/recheck経路を使う。''')
s = replace(s, '''2往復中の取り込み失敗3回は `budget_exhausted` とし、並列中もheartbeat・budgetを進める。''', '''2往復中の実取り込み・通信失敗3回は `budget_exhausted` とし、事前検証の契約不備は
修正待ちとして別記録する。並列中もheartbeat・budgetを進める。''')
path.write_text(s, encoding='utf-8')
print('Applied exact-source-checked preflight/recovery changes.')
