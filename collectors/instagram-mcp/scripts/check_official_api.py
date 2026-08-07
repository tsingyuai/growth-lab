#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

COLLECTORS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COLLECTORS))

from official_social_api import probe_instagram  # noqa: E402


if __name__ == "__main__":
    result = probe_instagram(Path(__file__).resolve().parents[3], os.environ)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "verified" else 2)
