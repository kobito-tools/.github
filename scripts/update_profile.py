#!/usr/bin/env python3
"""Regenerate the app lineup in profile/README.md.

The lineup lists the org's repositories that carry the topic "kobito-app" and
have a valid kobito-app.json at their root (the format is described in
kobito-workspace's docs/APP_PACKAGE.md). Name, summary, kind and platforms come
from kobito-app.json.

Each app is shown with the repository's Social preview image (1280x640). If none
is set, the square icon is used: the README's right-aligned image, or a PNG whose
name contains "icon" in assets/icon/.

The latest version is the newest Release for native apps. Python apps make no
Releases and mark versions with tags only, so the newest "v*" tag is shown
(native apps without a Release fall back to tags as well).

Repositories are skipped when they are forks, archived, private, named ".github",
or carry the topic "profile-hide". kobito-workspace comes first, the rest follow
in repository-name order.

When no app is found (for example before any repository has the topic), the
README is left as it is.

Sources can be swapped so the script runs without the network:

    KOBITO_GITHUB_ORG         organization (default: kobito-tools)
    KOBITO_APP_LIST_URL       search URL for the repository list (file:// works)
    KOBITO_APP_MANIFEST_BASE  base for <base>/<repo>/<branch>/kobito-app.json
    KOBITO_GITHUB_API         REST/GraphQL base (default: https://api.github.com)
    KOBITO_GITHUB_WEB         web base used for og:image (default: https://github.com)

    python3 scripts/update_profile.py --local ..   # read sibling folders instead
    python3 scripts/update_profile.py --dry-run    # print the lineup, write nothing
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ORG = os.environ.get("KOBITO_GITHUB_ORG") or os.environ.get("ORG") or "kobito-tools"
API = os.environ.get("KOBITO_GITHUB_API", "https://api.github.com").rstrip("/")
WEB = os.environ.get("KOBITO_GITHUB_WEB", "https://github.com").rstrip("/")
LIST_URL = os.environ.get(
    "KOBITO_APP_LIST_URL",
    f"{API}/search/repositories?q=org:{ORG}+topic:kobito-app&per_page=100",
)
MANIFEST_BASE = os.environ.get(
    "KOBITO_APP_MANIFEST_BASE", f"https://raw.githubusercontent.com/{ORG}"
).rstrip("/")
README = Path(__file__).resolve().parent.parent / "profile" / "README.md"
START = "<!-- TOOLS:START -->"
END = "<!-- TOOLS:END -->"
HIDE_TOPIC = "profile-hide"
HUB = "workspace"
MANIFEST_LIMIT = 64 * 1024
PLATFORMS = {"macos": "macOS", "windows": "Windows", "linux": "Linux"}
KINDS = {"python": "Python", "native": "ネイティブ"}
VERSION_TAG = re.compile(r"^v(\d+(?:\.\d+)*)$")


def fetch(url, accept="application/vnd.github+json", data=None):
    """Return the body at url as text, or None on 404. The only network access."""
    headers = {"Accept": accept, "User-Agent": f"{ORG}-profile-updater"}
    token = os.environ.get("GITHUB_TOKEN")
    if token and url.startswith(API):
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req) as res:
            return res.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise
    except urllib.error.URLError:
        if url.startswith("file:"):
            return None
        raise


def parse_manifest(text):
    """Return the kobito-app.json dict, or None when it is missing or malformed."""
    if not text or len(text.encode("utf-8")) > MANIFEST_LIMIT:
        return None
    try:
        m = json.loads(text)
    except ValueError:
        return None
    if not isinstance(m, dict) or m.get("format") != "kobito-app" or m.get("v") != 1:
        return None
    if not (isinstance(m.get("app"), str) and re.fullmatch(r"[a-z][a-z0-9-]{0,39}", m["app"])):
        return None
    if not (isinstance(m.get("name"), str) and m["name"].strip()):
        return None
    if m.get("kind") not in KINDS or not isinstance(m.get("contracts"), int):
        return None
    for key in ("description", "repository"):
        if not isinstance(m.get(key), str):
            m.pop(key, None)
    platforms = m.get("platforms")
    m["platforms"] = [p for p in platforms if p in PLATFORMS] if isinstance(platforms, list) else []
    return m


def newest_tag(names):
    versions = [(tuple(int(n) for n in m.group(1).split(".")), t)
                for t in names if (m := VERSION_TAG.match(t))]
    return max(versions)[1] if versions else None


class GitHub:
    """Reads repositories from GitHub (or wherever the URLs above point)."""

    def __init__(self, fetch=fetch):
        self.fetch = fetch

    def repositories(self):
        text = self.fetch(LIST_URL)
        if text is None:
            raise RuntimeError(f"一覧を取り寄せられません: {LIST_URL}")
        return json.loads(text).get("items", [])

    def manifest(self, repo):
        return self.fetch(f"{MANIFEST_BASE}/{repo['name']}/{repo['default_branch']}/kobito-app.json")

    def readme(self, repo):
        return self.fetch(f"{API}/repos/{ORG}/{repo['name']}/readme",
                          accept="application/vnd.github.raw") or ""

    def icon_files(self, repo):
        listing = self.fetch(f"{API}/repos/{ORG}/{repo['name']}/contents/assets/icon")
        return [f["path"] for f in json.loads(listing) if f["type"] == "file"] if listing else []

    def latest_release(self, repo):
        release = self.fetch(f"{API}/repos/{ORG}/{repo['name']}/releases/latest")
        return json.loads(release)["tag_name"] if release else None

    def tags(self, repo):
        names, page = [], 1
        while True:
            text = self.fetch(f"{API}/repos/{ORG}/{repo['name']}/tags?per_page=100&page={page}")
            batch = json.loads(text) if text else []
            names += [t["name"] for t in batch]
            if len(batch) < 100:
                return names
            page += 1

    def social_preview(self, repo):
        """Return the custom Social preview image URL, or None if the repo has none."""
        if os.environ.get("GITHUB_TOKEN"):
            query = ("query($o:String!,$n:String!){repository(owner:$o,name:$n)"
                     "{usesCustomOpenGraphImage openGraphImageUrl}}")
            body = json.dumps({"query": query, "variables": {"o": ORG, "n": repo["name"]}}).encode()
            text = self.fetch(f"{API}/graphql", data=body)
            r = (json.loads(text).get("data") or {}).get("repository") if text else None
            return r["openGraphImageUrl"] if r and r["usesCustomOpenGraphImage"] else None

        # GraphQL needs a token; without one, read the og:image of the public repo page.
        html = self.fetch(f"{WEB}/{ORG}/{repo['name']}", accept="text/html") or ""
        m = re.search(r'<meta property="og:image" content="(https://repository-images\.githubusercontent\.com/[^"]+)"', html)
        return m.group(1) if m else None


class LocalFolder:
    """Reads app folders on this machine (each with kobito-app.json), for checking offline.

    Images are left out: nothing tells what is on GitHub yet.
    """

    def __init__(self, root):
        self.root = Path(root)
        self.folders = {}

    def repositories(self):
        repos = []
        for folder in sorted(p for p in self.root.iterdir() if p.is_dir() and not p.name.startswith(".")):
            path = folder / "kobito-app.json"
            if not path.is_file():
                continue
            m = parse_manifest(path.read_text(encoding="utf-8")) or {}
            name = m.get("repository", f"{ORG}/{folder.name}").split("/")[-1]
            self.folders[name] = folder
            repos.append({"name": name, "default_branch": "main", "html_url": f"{WEB}/{ORG}/{name}",
                          "fork": False, "archived": False, "private": False, "topics": ["kobito-app"]})
        return repos

    def manifest(self, repo):
        return (self.folders[repo["name"]] / "kobito-app.json").read_text(encoding="utf-8")

    def readme(self, repo):
        return ""

    def icon_files(self, repo):
        return []

    def latest_release(self, repo):
        return None

    def tags(self, repo):
        out = subprocess.run(["git", "-C", str(self.folders[repo["name"]]), "tag"],
                             capture_output=True, text=True)
        return out.stdout.split() if out.returncode == 0 else []

    def social_preview(self, repo):
        return None


def readme_icon(text):
    m = re.search(r'<img\s[^>]*src="([^"]+)"[^>]*align="right"', text)
    return m.group(1) if m else None


def pick_icon(files):
    icons = [f for f in files if re.search(r"icon[^/]*\.png$", f, re.I)]
    return sorted(icons, key=lambda f: ("1024" not in f, f))[0] if icons else None


def image_html(source, repo, title):
    url, name, branch = repo["html_url"], repo["name"], repo["default_branch"]
    banner = source.social_preview(repo)
    if banner:
        return f'<a href="{url}"><img src="{banner}" width="640" alt="{title}"></a>'
    icon = readme_icon(source.readme(repo)) or pick_icon(source.icon_files(repo))
    if not icon:
        return ""
    if not icon.startswith("http"):
        icon = f"https://raw.githubusercontent.com/{ORG}/{name}/{branch}/{icon.lstrip('./')}"
    return f'<a href="{url}"><img src="{icon}" width="96" alt="{title}"></a>'


def latest_version(source, repo, kind):
    url = repo["html_url"]
    if kind == "native":
        tag = source.latest_release(repo)
        if tag:
            return f"[{tag}]({url}/releases/latest)"
    tag = newest_tag(source.tags(repo))
    return f"[{tag}]({url}/tree/{tag})" if tag else "—"


def build_section(source, repo, manifest):
    title = manifest["name"]
    summary = manifest.get("description") or repo.get("description") or ""
    platforms = " · ".join(PLATFORMS[p] for p in manifest["platforms"]) or "—"
    parts = [f"### [{title}]({repo['html_url']})"]
    image = image_html(source, repo, title)
    if image:
        parts.append(image)
    if summary:
        parts.append(summary)
    parts.append(f"**種類:** {KINDS[manifest['kind']]}　**対応 OS:** {platforms}　"
                 f"**最新版:** {latest_version(source, repo, manifest['kind'])}")
    return "\n\n".join(parts)


def collect(source, log=print):
    """Return [(repo, manifest)] in display order."""
    apps = []
    for repo in source.repositories():
        if (repo.get("fork") or repo.get("archived") or repo.get("private")
                or repo["name"] == ".github" or HIDE_TOPIC in repo.get("topics", [])):
            continue
        manifest = parse_manifest(source.manifest(repo))
        if manifest is None:
            log(f"skip {repo['name']}: kobito-app.json が読めないか、形が違います")
            continue
        apps.append((repo, manifest))
    apps.sort(key=lambda a: (a[1]["app"] != HUB, a[0]["name"].lower()))
    return apps


def render(source, log=print):
    """Return (lineup markdown, app count)."""
    apps = collect(source, log)
    return "\n\n".join(build_section(source, r, m) for r, m in apps), len(apps)


def replace_lineup(content, body):
    if START not in content or END not in content:
        raise ValueError(f"{START} / {END} のマーカーがありません")
    head, rest = content.split(START, 1)
    _, tail = rest.split(END, 1)
    return f"{head}{START}\n{body}\n{END}{tail}"


def main(argv=None, readme=README):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--local", metavar="DIR", help="GitHub の代わりに DIR の直下のフォルダを読む")
    parser.add_argument("--dry-run", action="store_true", help="一覧を表示するだけで、README は書かない")
    args = parser.parse_args(argv)

    source = LocalFolder(args.local) if args.local else GitHub()
    log = (lambda s: print(s, file=sys.stderr))
    try:
        body, count = render(source, log)
    except (RuntimeError, urllib.error.URLError, ValueError) as e:
        log(f"一覧を作れません: {e}")
        return 1

    if count == 0:
        log("topic kobito-app と kobito-app.json を持つリポジトリが見つかりません。README はそのままにします。")
        return 0
    if args.dry_run:
        print(body)
        return 0

    try:
        content = replace_lineup(readme.read_text(encoding="utf-8"), body)
    except ValueError as e:
        log(f"{readme}: {e}")
        return 1
    readme.write_text(content, encoding="utf-8")
    log(f"{count} apps written to {readme}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
