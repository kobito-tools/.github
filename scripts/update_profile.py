#!/usr/bin/env python3
"""Regenerate the tool lineup in profile/README.md from the org's public repositories.

Each repository's README is expected to follow the kobito-tools convention:

    # Tool Name
    <img src="path/to/icon.png" width="96" align="right" alt="">
    One-paragraph summary.
    ...
    ## 動作環境
    - macOS ...

If the README has no right-aligned icon, a PNG whose name contains "icon" in
assets/icon/ is used instead.

Repositories are skipped when they are forks, archived, private, named ".github",
or carry the topic "profile-hide".
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ORG = os.environ.get("ORG", "kobito-tools")
README = Path(__file__).resolve().parent.parent / "profile" / "README.md"
START = "<!-- TOOLS:START -->"
END = "<!-- TOOLS:END -->"
HIDE_TOPIC = "profile-hide"
PLATFORMS = ["macOS", "Windows", "Linux", "iOS", "Android", "Web"]
API = "https://api.github.com"


def request(path, accept="application/vnd.github+json"):
    headers = {"Accept": accept, "User-Agent": f"{ORG}-profile-updater"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{API}{path}", headers=headers)
    try:
        with urllib.request.urlopen(req) as res:
            return res.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def list_repos():
    repos, page = [], 1
    while True:
        batch = json.loads(request(f"/orgs/{ORG}/repos?type=public&per_page=100&page={page}"))
        repos += batch
        if len(batch) < 100:
            return repos
        page += 1


def parse_readme(text):
    lines = text.splitlines()
    title = next((l[2:].strip() for l in lines if l.startswith("# ")), None)

    icon = re.search(r'<img\s[^>]*src="([^"]+)"[^>]*align="right"', text)
    icon = icon.group(1) if icon else None

    # First plain-text paragraph after the H1.
    summary, started = [], False
    for line in lines:
        if not started:
            started = line.startswith("# ")
            continue
        s = line.strip()
        if not s:
            if summary:
                break
            continue
        if s.startswith(("<", "!", "#", "|", "-", ">", "```")):
            if summary:
                break
            continue
        summary.append(s)

    section = re.search(r"^## 動作環境\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    section = section.group(1) if section else ""
    platforms = [p for p in PLATFORMS if re.search(rf"\b{p}\b", section)]

    return title, icon, " ".join(summary), platforms


def find_icon(name):
    listing = request(f"/repos/{ORG}/{name}/contents/assets/icon")
    if not listing:
        return None
    files = [f["path"] for f in json.loads(listing) if f["type"] == "file"]
    icons = [f for f in files if re.search(r"icon[^/]*\.png$", f, re.I)]
    return sorted(icons, key=lambda f: ("1024" not in f, f))[0] if icons else None


def build_row(repo):
    name, branch, url = repo["name"], repo["default_branch"], repo["html_url"]
    readme = request(f"/repos/{ORG}/{name}/readme", accept="application/vnd.github.raw") or ""
    title, icon, summary, platforms = parse_readme(readme)

    title = title or name
    icon = icon or find_icon(name)
    summary = summary or repo.get("description") or ""
    summary = summary.replace("|", "\\|")
    # Make relative links in the summary point at the tool's own repository.
    summary = re.sub(r"\]\((?!https?://|#)([^)]+)\)", rf"]({url}/blob/{branch}/\1)", summary)

    if icon and not icon.startswith("http"):
        icon = f"https://raw.githubusercontent.com/{ORG}/{name}/{branch}/{icon.lstrip('./')}"
    icon_cell = f'<a href="{url}"><img src="{icon}" width="64" alt="{title}"></a>' if icon else ""

    release = request(f"/repos/{ORG}/{name}/releases/latest")
    if release:
        tag = json.loads(release)["tag_name"]
        dl = f"[{tag}]({url}/releases/latest)"
    else:
        dl = "—"

    return f"| {icon_cell} | **[{title}]({url})** | {summary} | {' · '.join(platforms) or '—'} | {dl} |"


def main():
    repos = [
        r for r in list_repos()
        if not (r["fork"] or r["archived"] or r["private"] or r["name"] == ".github"
                or HIDE_TOPIC in r.get("topics", []))
    ]
    repos.sort(key=lambda r: r["created_at"])

    table = "\n".join(
        ["|  | ツール | 概要 | 対応 OS | 最新版 |", "|:-:|---|---|---|:-:|"]
        + [build_row(r) for r in repos]
    )

    content = README.read_text(encoding="utf-8")
    if START not in content or END not in content:
        sys.exit(f"{README} に {START} / {END} のマーカーがありません")
    head, rest = content.split(START, 1)
    _, tail = rest.split(END, 1)
    README.write_text(f"{head}{START}\n{table}\n{END}{tail}", encoding="utf-8")
    print(f"{len(repos)} repositories: {', '.join(r['name'] for r in repos)}")


if __name__ == "__main__":
    main()
