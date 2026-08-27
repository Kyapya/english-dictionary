from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SUPPORTED_PROVIDERS = {"openai", "anthropic"}


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def call_provider(
    provider: str,
    *,
    model: str,
    api_key: str,
    prompt: str,
    request_payload: dict[str, Any],
    endpoint: str | None = None,
) -> dict[str, Any]:
    """The only provider-specific network boundary used by review stages."""
    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(f"unsupported review provider: {provider}")
    user_text = json.dumps(request_payload, ensure_ascii=False, indent=2)
    if provider == "openai":
        url = endpoint or "https://api.openai.com/v1/responses"
        body = {
            "model": model,
            "instructions": prompt,
            "input": user_text,
            "text": {"format": {"type": "json_object"}},
            "store": False,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
    else:
        url = endpoint or "https://api.anthropic.com/v1/messages"
        body = {
            "model": model,
            "max_tokens": 16_384,
            "system": prompt,
            "messages": [{"role": "user", "content": user_text}],
        }
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
    http_request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(http_request, timeout=180) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"review provider returned HTTP {exc.code}: {detail}") from exc
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("review provider response must be a JSON object")
    return value


def _extract_text(provider: str, raw: dict[str, Any]) -> str:
    if provider == "openai":
        if isinstance(raw.get("output_text"), str):
            return raw["output_text"]
        for output in raw.get("output", []):
            if not isinstance(output, dict):
                continue
            for content in output.get("content", []):
                if isinstance(content, dict) and isinstance(content.get("text"), str):
                    return content["text"]
    else:
        for content in raw.get("content", []):
            if isinstance(content, dict) and isinstance(content.get("text"), str):
                return content["text"]
    raise ValueError("review provider response contains no text output")


def _parse_json_text(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    value = json.loads(stripped)
    if not isinstance(value, dict):
        raise ValueError("review response payload must be a JSON object")
    return value


def normalize_response(
    provider: str,
    model: str,
    raw: dict[str, Any],
    request_payload: dict[str, Any],
    *,
    generation_model: str | None = None,
    recorded_at: str | None = None,
) -> dict[str, Any]:
    result = _parse_json_text(_extract_text(provider, raw))
    response_id = str(raw.get("id") or raw.get("request_id") or "")
    if not response_id:
        raise ValueError("review provider response is missing its response id")
    reviewer: dict[str, Any] = {
        "mode": "api",
        "provider": provider,
        "model": model,
        "response_id": response_id,
        "request_sha256": canonical_sha256(request_payload),
    }
    if generation_model and model.strip().casefold() == generation_model.strip().casefold():
        reviewer["same_model_as_generation"] = True
    metadata = request_payload.get("_output_metadata")
    if isinstance(metadata, dict):
        result.update(metadata)
        result["recorded_at"] = recorded_at or datetime.now(timezone.utc).isoformat()
    result["reviewer"] = reviewer
    return result


def execute_review(
    *,
    stage: str,
    request_path: Path,
    prompt_path: Path,
    cycle_dir: Path,
    output_path: Path,
    provider: str,
    model: str,
    api_key: str,
    endpoint: str | None = None,
    generation_model: str | None = None,
) -> dict[str, Any]:
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", stage) is None:
        raise ValueError("review stage must be a safe artifact name")
    request_payload = json.loads(request_path.read_text(encoding="utf-8"))
    if not isinstance(request_payload, dict):
        raise ValueError("review request must be a JSON object")
    prompt = prompt_path.read_text(encoding="utf-8")
    raw = call_provider(
        provider,
        model=model,
        api_key=api_key,
        prompt=prompt,
        request_payload=request_payload,
        endpoint=endpoint,
    )
    raw_path = cycle_dir / "raw" / f"{stage}.response.json"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(
        json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    normalized = normalize_response(
        provider,
        model,
        raw,
        request_payload,
        generation_model=generation_model,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(normalized, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return normalized


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Call an independent dictionary reviewer")
    parser.add_argument("stage")
    parser.add_argument("request", type=Path)
    parser.add_argument("prompt", type=Path)
    parser.add_argument("--cycle-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--generation-model")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    provider = os.environ.get("DICT_REVIEW_PROVIDER", "openai").strip().lower()
    model = os.environ.get("DICT_REVIEW_MODEL", "").strip()
    api_key = os.environ.get("DICT_REVIEW_API_KEY", "").strip()
    endpoint = os.environ.get("DICT_REVIEW_ENDPOINT", "").strip() or None
    if provider not in SUPPORTED_PROVIDERS:
        raise SystemExit(f"DICT_REVIEW_PROVIDER must be one of {sorted(SUPPORTED_PROVIDERS)}")
    if not model or not api_key:
        raise SystemExit("review API mode requires DICT_REVIEW_MODEL and DICT_REVIEW_API_KEY")
    execute_review(
        stage=args.stage,
        request_path=args.request,
        prompt_path=args.prompt,
        cycle_dir=args.cycle_dir,
        output_path=args.output,
        provider=provider,
        model=model,
        api_key=api_key,
        endpoint=endpoint,
        generation_model=args.generation_model,
    )
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
