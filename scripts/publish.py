#!/usr/bin/env python3
"""Publish a validated, committed site to the Phygital AI organization."""

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OWNER = "Phygital-AI"
REPO = "agentic-world-simulation-and-mapping"
REMOTE_NAME = "phygital"
REMOTE_URL = f"https://github.com/{OWNER}/{REPO}.git"
SITE_URL = f"https://{OWNER.lower()}.github.io/{REPO}/"


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], check=True, capture_output=True, text=True).stdout.strip()


def api(path, method="GET", body=None):
    command = ["gh", "api", path, "--method", method]
    if body is not None:
        command.extend(["--input", "-"])
    result = subprocess.run(command, input=json.dumps(body) if body is not None else None, capture_output=True, text=True)
    try:
        response = json.loads(result.stdout) if result.stdout.strip() else {}
    except json.JSONDecodeError:
        raise SystemExit(f"GitHub API returned an invalid response for {path}")
    return result.returncode, response


def require_api(path, method="GET", body=None):
    code, response = api(path, method, body)
    if code:
        raise SystemExit(f"GitHub API failed for {path}: {response.get('message', 'request failed')}")
    return response


def main():
    subprocess.run([sys.executable, str(ROOT / "scripts/render.py"), "--check"], check=True)
    subprocess.run([sys.executable, str(ROOT / "scripts/validate.py")], check=True)
    if git("status", "--porcelain"):
        raise SystemExit("Commit the validated revision before publishing.")
    user = require_api("user")
    if user.get("login") != "Yaofang-Liu":
        raise SystemExit("Authenticate GitHub CLI as Yaofang-Liu before publishing.")
    path = f"repos/{OWNER}/{REPO}"
    code, repository = api(path)
    if code and str(repository.get("status")) == "404":
        repository = require_api(f"orgs/{OWNER}/repos", "POST", {
            "name": REPO,
            "description": "Geometry-grounded agentic scene reconstruction, map-based embodied execution, and persistent spatial representations for memory, interaction, and simulation.",
            "private": False,
            "auto_init": False,
            "homepage": SITE_URL,
        })
    elif code:
        raise SystemExit("Cannot inspect the intended organization repository.")
    if repository.get("full_name") != f"{OWNER}/{REPO}" or repository.get("private") or not repository.get("permissions", {}).get("push"):
        raise SystemExit("Repository identity, visibility, or push permissions do not match the publication target.")
    if REMOTE_NAME not in git("remote").splitlines():
        git("remote", "add", REMOTE_NAME, REMOTE_URL)
    if git("remote", "get-url", REMOTE_NAME) != REMOTE_URL:
        raise SystemExit("Unexpected publication remote; no push attempted.")
    push = subprocess.run([
        "git", "-C", str(ROOT), "-c", "credential.helper=", "-c", "credential.helper=!gh auth git-credential",
        "push", "-u", REMOTE_NAME, "HEAD:main",
    ], capture_output=True, text=True, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
    if push.returncode:
        raise SystemExit("Non-force push failed. Inspect branch state and GitHub CLI authentication; no forced overwrite was attempted.")
    require_api(path, "PATCH", {"homepage": SITE_URL, "default_branch": "main"})
    code, pages = api(path + "/pages")
    configuration = {"build_type": "legacy", "source": {"branch": "main", "path": "/"}}
    if code and str(pages.get("status")) == "404":
        require_api(path + "/pages", "POST", configuration)
    elif code:
        raise SystemExit("Code pushed, but GitHub Pages configuration could not be inspected.")
    elif pages.get("build_type") != "legacy" or pages.get("source") != configuration["source"]:
        require_api(path + "/pages", "PUT", configuration)
    build_code, build = api(path + "/pages/builds", "POST", {})
    record = {
        "repository": REMOTE_URL.removesuffix(".git"),
        "commit": git("rev-parse", "HEAD"),
        "url": SITE_URL,
        "pages_build_requested": build_code == 0,
        "pages_build_url": build.get("url"),
    }
    (ROOT / ".publication.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record))


if __name__ == "__main__":
    main()
