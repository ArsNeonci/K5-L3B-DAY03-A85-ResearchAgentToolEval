from __future__ import annotations

import os
from pathlib import Path


def load_dotenv(path: Path, *, override: bool = True) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        if key and (override or key not in os.environ):
            os.environ[key] = value


def load_lab_env(root: Path) -> None:
    external_path = os.getenv("DAY03_ENV_FILE")
    if external_path:
        load_dotenv(Path(external_path).expanduser())
        return
    # Accept the repository-root .env as well as starter_v0/.env.
    # The more specific starter file wins; explicit DAY03_ENV_FILE wins over both.
    load_dotenv(root.parent / ".env")
    load_dotenv(root / ".env")
