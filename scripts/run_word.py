from __future__ import annotations

"""Compatibility entrypoint for the parallel checker orchestrator.

The stable v3 implementation is retained in ``run_word_v3.py`` and the checker
parallelization lives in ``run_word_parallel.py``.  This thin module preserves
legacy source-contract markers and dynamic monkey-patch behavior used by the
regression suite while routing runtime hooks to the parallel implementation.

Preserved contracts: independent_llm, process_improvement/ACTIVE.md,
context_free_cold, context_free_final_blind, confirm_remote_checkpoint,
heartbeat_manifest, entry_workflow_guard, source_inventory_complete.
"""

from typing import Any

import run_word_parallel as _parallel


for _name, _value in vars(_parallel).items():
    if _name not in {
        "__name__",
        "__file__",
        "__package__",
        "__loader__",
        "__spec__",
        "__builtins__",
        "__cached__",
    }:
        globals()[_name] = _value


# Keep the implementations on this module so unittest.mock patches against
# ``run_word.<hook>`` still affect functions whose globals live in run_word_v3
# or run_word_parallel.
_prepare_handoff_impl = _parallel.prepare_handoff
_ingest_handoff_review_impl = _parallel.ingest_handoff_review
_execute_api_review_stage_impl = _parallel.execute_api_review_stage
_execute_checker_bundle_api_impl = _parallel._execute_checker_bundle_api


def _dispatch_prepare_handoff(*args: Any, **kwargs: Any) -> Any:
    return globals()["prepare_handoff"](*args, **kwargs)


def _dispatch_ingest_handoff_review(*args: Any, **kwargs: Any) -> Any:
    return globals()["ingest_handoff_review"](*args, **kwargs)


def _dispatch_execute_api_review_stage(*args: Any, **kwargs: Any) -> Any:
    return globals()["execute_api_review_stage"](*args, **kwargs)


def _dispatch_execute_checker_bundle_api(*args: Any, **kwargs: Any) -> Any:
    return globals()["_execute_checker_bundle_api"](*args, **kwargs)


# Public aliases remain the actual implementations. Internal cross-module calls
# use dispatchers so patching these aliases continues to work exactly as it did
# when run_word.py was a single module.
prepare_handoff = _prepare_handoff_impl
ingest_handoff_review = _ingest_handoff_review_impl
execute_api_review_stage = _execute_api_review_stage_impl
_execute_checker_bundle_api = _execute_checker_bundle_api_impl

_parallel.prepare_handoff = _dispatch_prepare_handoff
_parallel.ingest_handoff_review = _dispatch_ingest_handoff_review
_parallel.execute_api_review_stage = _dispatch_execute_api_review_stage
_parallel._execute_checker_bundle_api = _dispatch_execute_checker_bundle_api
_parallel._v3.prepare_handoff = _dispatch_prepare_handoff
_parallel._v3.ingest_handoff_review = _dispatch_ingest_handoff_review
_parallel._v3.execute_api_review_stage = _dispatch_execute_api_review_stage


if __name__ == "__main__":
    raise SystemExit(_parallel._v3.main())
