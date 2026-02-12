#!/usr/bin/env python3
# /// script
# dependencies = [
#   "python-dotenv>=1.0.0",
#   "requests>=2.31.0",
# ]
# ///

"""
List LaunchDarkly feature flags via REST API and print them.

Loads env from .cursor/.env/.env or .cursor/.env (relative to the .cursor dir
that contains this skill). Expected variables:
  - LAUNCHDARKLY_API_KEY        (required) Personal or service token
  - LAUNCHDARKLY_PROJECT_KEY    (required) Project key, e.g. "default"
  - LAUNCHDARKLY_ENV_KEY        (optional) Environment key to include env-specific config, e.g. "production"
  - LAUNCHDARKLY_API_VERSION    (optional) Defaults to "20240415"

Run (use ./ so pipx treats it as a local script and installs inline deps):
  pipx run ./.cursor/skills/create-feature-flag/scripts/list_flags.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv


def load_cursor_env() -> None:
    # list_flags.py lives at:
    #   .cursor/skills/create-feature-flag/scripts/list_flags.py
    # parents[3] => .cursor/
    cursor_root = Path(__file__).resolve().parents[3]
    # Prefer .cursor/.env/.env then .cursor/.env
    candidates = [cursor_root / ".env" / ".env", cursor_root / ".env"]
    env_path = None
    for p in candidates:
        if p.exists():
            env_path = p
            break
    if not env_path:
        print(
            f".env file not found. Tried: {[str(c) for c in candidates]}",
            file=sys.stderr,
        )
        sys.exit(1)

    load_dotenv(env_path)


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        print(f"Missing required environment variable: {name}", file=sys.stderr)
        sys.exit(1)
    return value


def ld_headers(api_key: str, api_version: str) -> Dict[str, str]:
    # LaunchDarkly REST API uses an Authorization header with your API access token.
    # You can also set the REST API version with the LD-API-Version header. citeturn2view0turn0search4
    return {
        "Authorization": api_key,
        "Accept": "application/json",
        "LD-API-Version": api_version,
    }


def fetch_flags(
    session: requests.Session,
    project_key: str,
    env_key: Optional[str],
    api_key: str,
    api_version: str,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    # Endpoint: GET /api/v2/flags/{projectKey} citeturn1view0
    base_url = "https://app.launchdarkly.com"
    url = f"{base_url}/api/v2/flags/{project_key}"

    headers = ld_headers(api_key, api_version)

    all_items: List[Dict[str, Any]] = []
    offset = 0

    while True:
        params: Dict[str, Any] = {"limit": limit, "offset": offset}
        if env_key:
            params["env"] = env_key

        resp = session.get(url, headers=headers, params=params, timeout=30)
        if resp.status_code == 401:
            print(
                "LaunchDarkly API returned 401 Unauthorized. Check LAUNCHDARKLY_API_KEY scope/validity.",
                file=sys.stderr,
            )
            sys.exit(1)

        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            print(f"LaunchDarkly API request failed: {e}", file=sys.stderr)
            print(resp.text, file=sys.stderr)
            sys.exit(1)

        data = resp.json()
        items = data.get("items") or []
        if not isinstance(items, list):
            print("Unexpected response shape: 'items' is not a list", file=sys.stderr)
            sys.exit(1)

        all_items.extend(items)

        # If fewer than limit returned, we're done.
        if len(items) < limit:
            break

        offset += limit

    return all_items


def format_flag_summary(flag: Dict[str, Any], env_key: Optional[str]) -> Dict[str, Any]:
    key = flag.get("key")
    name = flag.get("name")
    description = flag.get("description")

    out: Dict[str, Any] = {
        "key": key,
        "name": name,
    }

    if description:
        out["description"] = description

    # If env was requested, include a small, useful slice of env config when present.
    if env_key:
        envs = flag.get("environments") or {}
        env_cfg = envs.get(env_key) if isinstance(envs, dict) else None
        if isinstance(env_cfg, dict):
            out["env"] = env_key
            out["on"] = env_cfg.get("on")
            out["archived"] = env_cfg.get("archived")
            # "isOff" appears in summary responses for some shapes; include if present.
            if "isOff" in env_cfg:
                out["isOff"] = env_cfg.get("isOff")

    return out


def main() -> int:
    load_cursor_env()

    api_key = require_env("LAUNCHDARKLY_API_KEY")
    project_key = require_env("LAUNCHDARKLY_PROJECT_KEY")
    env_key = os.getenv("LAUNCHDARKLY_ENV_KEY") or None
    api_version = os.getenv("LAUNCHDARKLY_API_VERSION") or "20240415"

    with requests.Session() as session:
        flags = fetch_flags(
            session=session,
            project_key=project_key,
            env_key=env_key,
            api_key=api_key,
            api_version=api_version,
        )

    # Print a concise JSON list that is easy to pipe/parse.
    summaries = [format_flag_summary(f, env_key) for f in flags]
    print(json.dumps(summaries, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())