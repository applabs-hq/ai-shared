#!/usr/bin/env python3
# /// script
# dependencies = [
#   "python-dotenv>=1.0.0",
#   "requests>=2.31.0",
# ]
# ///

"""
Create a LaunchDarkly feature flag via REST API.

Loads env from .cursor/.env/.env or .cursor/.env (relative to the .cursor dir
that contains this skill). Expected variables:
  - LAUNCHDARKLY_API_KEY        (required) Personal or service token
  - LAUNCHDARKLY_PROJECT_KEY    (required) Project key, e.g. "default"
  - LAUNCHDARKLY_API_VERSION    (optional) Defaults to "20240415"

Creates a boolean flag with the given key, name, description, and optional tags.
Flag is available to both client-side SDKs (JavaScript via environment ID and
mobile via mobile key). See: https://launchdarkly.com/docs/api/feature-flags/post-feature-flag

Run (use ./ so pipx treats it as a local script and installs inline deps):
  pipx run ./.cursor/skills/create-feature-flag/scripts/create_flag.py KEY "Display Name" "Optional description"
  pipx run ./.cursor/skills/create-feature-flag/scripts/create_flag.py --key KEY --name "Display Name" --description "Optional description" --tags "Kiosk,Shared"
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv


def load_cursor_env() -> None:
    # Script lives at: .cursor/skills/create-feature-flag/scripts/create_flag.py
    # parents[3] => .cursor/
    cursor_root = Path(__file__).resolve().parents[3]
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
    return {
        "Authorization": api_key,
        "Accept": "application/json",
        "Content-Type": "application/json",
        "LD-API-Version": api_version,
    }


def create_flag(
    session: requests.Session,
    project_key: str,
    api_key: str,
    api_version: str,
    key: str,
    name: str,
    description: str = "",
    tags: List[str] | None = None,
) -> Dict[str, Any]:
    """Create a feature flag. Available to client-side (JS) and mobile SDKs."""
    base_url = "https://app.launchdarkly.com"
    url = f"{base_url}/api/v2/flags/{project_key}"
    headers = ld_headers(api_key, api_version)

    payload: Dict[str, Any] = {
        "key": key,
        "name": name,
        "clientSideAvailability": {
            "usingEnvironmentId": True,
            "usingMobileKey": True,
        },
    }
    if description:
        payload["description"] = description
    if tags:
        payload["tags"] = list(tags)

    resp = session.post(url, headers=headers, json=payload, timeout=30)
    if resp.status_code == 401:
        print(
            "LaunchDarkly API returned 401 Unauthorized. Check LAUNCHDARKLY_API_KEY scope/validity.",
            file=sys.stderr,
        )
        sys.exit(1)
    if resp.status_code == 409:
        print(
            f"LaunchDarkly API returned 409 Conflict. A flag with key '{key}' may already exist.",
            file=sys.stderr,
        )
        print(resp.text, file=sys.stderr)
        sys.exit(1)

    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        print(f"LaunchDarkly API request failed: {e}", file=sys.stderr)
        print(resp.text, file=sys.stderr)
        sys.exit(1)

    return resp.json()


def main() -> int:
    load_cursor_env()

    parser = argparse.ArgumentParser(
        description="Create a LaunchDarkly feature flag (key, name, description). Flag is available to both client-side and mobile SDKs."
    )
    parser.add_argument(
        "key",
        nargs="?",
        help="Flag key (e.g. EnableNewCheckout). Used in code.",
    )
    parser.add_argument(
        "name",
        nargs="?",
        help="Human-readable flag name (e.g. Enable new checkout flow).",
    )
    parser.add_argument(
        "description",
        nargs="?",
        default="",
        help="Optional description for the flag.",
    )
    parser.add_argument("--key", dest="key_opt", metavar="KEY", help="Flag key (alternative to positional)")
    parser.add_argument("--name", dest="name_opt", metavar="NAME", help="Flag name (alternative to positional)")
    parser.add_argument(
        "--description",
        dest="description_opt",
        metavar="DESC",
        default="",
        help="Flag description (alternative to positional)",
    )
    parser.add_argument(
        "--tags",
        metavar="TAGS",
        default="",
        help="Comma-separated list of tags (e.g. Kiosk,POS,API,Shared). Applied in LaunchDarkly.",
    )
    args = parser.parse_args()

    key = args.key_opt or args.key
    name = args.name_opt or args.name
    description = (args.description_opt or args.description or "").strip()
    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []

    if not key or not name:
        parser.error("key and name are required (positional or --key / --name)")

    api_key = require_env("LAUNCHDARKLY_API_KEY")
    project_key = require_env("LAUNCHDARKLY_PROJECT_KEY")
    api_version = os.getenv("LAUNCHDARKLY_API_VERSION") or "20240415"

    with requests.Session() as session:
        flag = create_flag(
            session=session,
            project_key=project_key,
            api_key=api_key,
            api_version=api_version,
            key=key,
            name=name,
            description=description,
            tags=tags if tags else None,
        )

    print(f"Created flag: {flag.get('key')} ({flag.get('name')})")
    if tags:
        print(f"  tags: {', '.join(tags)}")
    print(f"  _links.self: {flag.get('_links', {}).get('self', {}).get('href', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
