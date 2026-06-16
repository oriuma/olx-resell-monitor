"""
State management — persists seen listing IDs locally and
syncs to GitHub repo via Contents API (same approach as oriuma/otmt state.py).
This allows GitHub Actions runs to remember which listings were already sent.
"""

import base64
import json
import logging
import os

import requests

logger = logging.getLogger(__name__)
GITHUB_API = "https://api.github.com"


def _gh_headers() -> dict:
    token = os.environ.get("GITHUB_TOKEN", "")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _get_remote_file(repo: str, path: str) -> tuple[str | None, str | None]:
    """
    Returns (content_str, sha) of a file in the repo.
    content_str is None if file doesn't exist.
    """
    url  = f"{GITHUB_API}/repos/{repo}/contents/{path}"
    resp = requests.get(url, headers=_gh_headers(), timeout=10)
    if resp.status_code == 200:
        data    = resp.json()
        content = base64.b64decode(data["content"]).decode("utf-8")
        return content, data["sha"]
    return None, None


def load_sent_ids(local_path: str, repo: str, remote_path: str) -> set:
    """
    Load sent IDs — prefers remote GitHub state so Actions runs stay in sync.
    Falls back to local file if remote is unavailable.
    """
    # Try remote first
    content, _ = _get_remote_file(repo, remote_path)
    if content:
        try:
            data = json.loads(content)
            ids  = set(str(x) for x in data) if isinstance(data, list) else set()
            logger.info("[state] Loaded %d sent IDs from remote.", len(ids))
            # Sync to local so we have a fresh copy
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, "w", encoding="utf-8") as f:
                json.dump(sorted(ids), f, ensure_ascii=False, indent=2)
            return ids
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning("[state] Remote parse error: %s", e)

    # Fallback: local file
    try:
        with open(local_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        ids = set(str(x) for x in data) if isinstance(data, list) else set()
        logger.info("[state] Loaded %d sent IDs from local file.", len(ids))
        return ids
    except FileNotFoundError:
        logger.info("[state] No local state file found — starting fresh.")
        return set()


def save_sent_ids(local_path: str, sent_ids: set) -> None:
    """Persist sent IDs to local file."""
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    with open(local_path, "w", encoding="utf-8") as f:
        json.dump(sorted(sent_ids), f, ensure_ascii=False, indent=2)


def push_state_to_github(local_path: str, repo: str, remote_path: str) -> None:
    """
    Atomically update state file in GitHub via Contents API.
    No git push needed — safe for Actions.
    """
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        logger.warning("[state] No GITHUB_TOKEN — skipping remote push.")
        return

    with open(local_path, "r", encoding="utf-8") as f:
        content = f.read()

    encoded  = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    _, sha   = _get_remote_file(repo, remote_path)

    payload: dict = {
        "message": "chore: update OLX sent_ids state",
        "content": encoded,
        "branch":  "main",
    }
    if sha:
        payload["sha"] = sha

    resp = requests.put(
        f"{GITHUB_API}/repos/{repo}/contents/{remote_path}",
        headers=_gh_headers(),
        json=payload,
        timeout=15,
    )
    if resp.status_code in (200, 201):
        logger.info("[state] Remote state updated (%s).", resp.status_code)
    else:
        logger.error("[state] Remote update failed: %s %s",
                     resp.status_code, resp.text[:200])
