#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

COLLECTORS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COLLECTORS))

from social_browser_collector import PlatformSpec, main_for  # noqa: E402


SPEC = PlatformSpec(
    platform="instagram",
    endpoint_env="INSTAGRAM_MCP_ENDPOINT",
    default_endpoint="http://127.0.0.1:18065",
    public_hosts=("instagram.com",),
)


if __name__ == "__main__":
    raise SystemExit(main_for(SPEC, Path(__file__).resolve().parents[3]))
