"""Shared runtime configuration and sanitized, atomic evidence storage."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from urllib.parse import quote, quote_plus

ROOT = Path(__file__).resolve().parent
VERSION = "v7-final"
COMMERCE_TOOLS = {"get_my_profile", "update_profile", "preview_order", "place_order", "get_order_status", "cancel_order"}


def redact(value):
    if isinstance(value, dict):
        return {key: "[redacted]" if key in {"confirmation_key", "token"} else redact(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, str):
        for name, secret in os.environ.items():
            if secret and name.endswith(("_API_KEY", "_TOKEN", "_CHAT_ID")):
                for variant in {secret, quote(secret, safe=""), quote_plus(secret)}:
                    value = value.replace(variant, "[redacted]")
    return value


def atomic_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(redact(payload), handle, ensure_ascii=False, indent=2, default=str)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def transcript_directory() -> Path:
    return Path(os.getenv("DAY03_TRANSCRIPTS_DIR", str(ROOT / "transcripts")))
