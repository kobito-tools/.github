#!/usr/bin/env python3
"""Regenerate the app lineup in profile/README.md.

The lineup lists the org's repositories that carry the topic "kobito-app" and
have a valid kobito-app.json at their root. Each app is shown as its card
(kobito-workspace's kobito_workspace/kit/docs/APP_PACKAGE.md, section 6), made
only from kobito-app.json and the fixed-name images in kobito/ on the default
branch. Nothing from the repositories is run.

    icon         kobito/icon-1024.png (kobito/icon.svg if there is no PNG); none if neither
    name         "name"
    tagline      "tagline", else "description"; none if neither
    kind         "kind" (Python / ネイティブ), with "platforms"
    image        kobito/screenshot.png, else the repository's Social preview; none if neither
    version      the newest Release (native) or "v*" tag; else "version" as written

Repositories are skipped when they are forks, archived, private, named ".github",
or carry the topic "profile-hide". kobito-workspace comes first, the rest follow
in repository-name order. When no app is found (for example before any
repository has the topic), the README is left as it is.

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
import urllib.parse
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
# Images are linked from the README, so they always point at the public files.
IMAGE_BASE = f"https://raw.githubusercontent.com/{ORG}"
README = Path(__file__).resolve().parent.parent / "profile" / "README.md"
START = "<!-- TOOLS:START -->"
END = "<!-- TOOLS:END -->"
HIDE_TOPIC = "profile-hide"
HUB = "workspace"

# The repository shape (APP_PACKAGE.md sections 0 and 2), read the same way as
# kobito-workspace's kit.manifest and kit.package.
MANIFEST_LIMIT = 64 * 1024
APP_ID = re.compile(r"^[a-z][a-z0-9-]{0,39}$")
REPOSITORY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]{0,38}/[A-Za-z0-9._-]{1,100}$")
FILE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")
APP_VERSION = re.compile(r"^\d+(\.\d+){0,2}([-+][0-9A-Za-z.-]+)?$")
TAGLINE_MAX = 80
ICON = "kobito/icon.svg"
ICON_PNG = "kobito/icon-1024.png"
SCREENSHOT = "kobito/screenshot.png"
IMAGE_LIMITS = {ICON: 256 * 1024, ICON_PNG: 2 * 1024 * 1024, SCREENSHOT: 2 * 1024 * 1024}
CARD_ITEMS = ("app", "name", "name_en", "tagline", "tagline_en", "description", "description_en",
              "kind", "version", "repository", "platforms")
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


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def parse_manifest(text):
    """Return the kobito-app.json dict, or None when it is missing or malformed.

    Required items that are missing or wrong drop the whole file; optional items
    that are wrong drop only that item.
    """
    if not text or len(text.encode("utf-8")) > MANIFEST_LIMIT:
        return None
    try:
        m = json.loads(text)
    except ValueError:
        return None
    if not isinstance(m, dict) or m.get("format") != "kobito-app" or m.get("v") != 1:
        return None
    contracts = m.get("contracts")
    if not (isinstance(m.get("app"), str) and APP_ID.match(m["app"])) or not _text(m.get("name")):
        return None
    if m.get("kind") not in KINDS:
        return None
    if not isinstance(contracts, int) or isinstance(contracts, bool) or contracts < 1:
        return None
    if m["kind"] == "python" and m.get("entry", "launch.py") != "launch.py":
        return None
    setup = m.get("setup", "setup.sh")
    if not isinstance(setup, str) or not FILE_NAME.match(setup):
        return None
    for key in ("name_en", "description", "description_en"):
        if key in m and not _text(m[key]):
            m.pop(key)
    for key in ("tagline", "tagline_en"):
        if key in m and not (_text(m[key]) and len(m[key]) <= TAGLINE_MAX and "\n" not in m[key]):
            m.pop(key)
    if "version" in m and not (isinstance(m["version"], str) and APP_VERSION.match(m["version"])):
        m.pop("version")
    if "repository" in m and not (isinstance(m["repository"], str) and REPOSITORY.match(m["repository"])):
        m.pop("repository")
    if "platforms" in m:
        platforms = m["platforms"]
        m["platforms"] = [p for p in platforms if p in PLATFORMS] if isinstance(platforms, list) else []
    return m


def card(manifest, files):
    """The app's card, as kit.package.AppPackage.card() gives it.

    files maps the regular files in kobito/ ("kobito/<name>") to their size.
    icon and screenshot are fixed-name paths in the repository, or None.
    """
    c = {key: manifest[key] for key in CARD_ITEMS if key in manifest}
    usable = {p for p, size in files.items() if p in IMAGE_LIMITS and size <= IMAGE_LIMITS[p]}
    # GitHub shows the PNG the same everywhere, so it comes before the SVG here.
    c["icon"] = next((p for p in (ICON_PNG, ICON) if p in usable), None)
    c["screenshot"] = SCREENSHOT if SCREENSHOT in usable else None
    return c


def tagline(c):
    return c.get("tagline") or c.get("description") or ""


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

    def kobito_files(self, repo):
        """{path: size} of the regular files in kobito/ on the default branch."""
        ref = urllib.parse.quote(repo["default_branch"], safe="")
        listing = self.fetch(f"{API}/repos/{ORG}/{repo['name']}/contents/kobito?ref={ref}")
        items = json.loads(listing) if listing else []
        if not isinstance(items, list):
            return {}
        return {f["path"]: f.get("size", 0) for f in items if f.get("type") == "file"}

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

    Images are left out: the README links to the files on GitHub, which may not be there yet.
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

    def kobito_files(self, repo):
        return {}

    def latest_release(self, repo):
        return None

    def tags(self, repo):
        out = subprocess.run(["git", "-C", str(self.folders[repo["name"]]), "tag"],
                             capture_output=True, text=True)
        return out.stdout.split() if out.returncode == 0 else []

    def social_preview(self, repo):
        return None


def image_url(repo, path):
    return f"{IMAGE_BASE}/{repo['name']}/{urllib.parse.quote(repo['default_branch'])}/{path}"


def escape(text):
    return text.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def latest_version(source, repo, c):
    url = repo["html_url"]
    if c["kind"] == "native":
        tag = source.latest_release(repo)
        if tag:
            return f"[{tag}]({url}/releases/latest)"
    tag = newest_tag(source.tags(repo))
    if tag:
        return f"[{tag}]({url}/tree/{tag})"
    return c.get("version") or "—"


def build_section(source, repo, c):
    url, title = repo["html_url"], c["name"]
    heading = f"### [{title}]({url})"
    if c["icon"]:
        heading = f'### <img src="{image_url(repo, c["icon"])}" width="32" height="32" alt=""> [{title}]({url})'
    parts = [heading]
    if tagline(c):
        parts.append(tagline(c))
    picture = image_url(repo, c["screenshot"]) if c["screenshot"] else source.social_preview(repo)
    if picture:
        parts.append(f'<a href="{url}"><img src="{picture}" width="640" alt="{escape(title)}"></a>')
    platforms = " · ".join(PLATFORMS[p] for p in c.get("platforms", [])) or "—"
    parts.append(f"**種類:** {KINDS[c['kind']]}　**対応 OS:** {platforms}　"
                 f"**最新版:** {latest_version(source, repo, c)}")
    return "\n\n".join(parts)


def collect(source, log=print):
    """Return [(repo, card)] in display order."""
    apps = []
    for repo in source.repositories():
        if (repo.get("fork") or repo.get("archived") or repo.get("private")
                or repo["name"] == ".github" or HIDE_TOPIC in repo.get("topics", [])):
            continue
        manifest = parse_manifest(source.manifest(repo))
        if manifest is None:
            log(f"skip {repo['name']}: kobito-app.json が読めないか、形が違います")
            continue
        apps.append((repo, card(manifest, source.kobito_files(repo))))
    apps.sort(key=lambda a: (a[1]["app"] != HUB, a[0]["name"].lower()))
    return apps


def render(source, log=print):
    """Return (lineup markdown, app count)."""
    apps = collect(source, log)
    return "\n\n".join(build_section(source, r, c) for r, c in apps), len(apps)


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
