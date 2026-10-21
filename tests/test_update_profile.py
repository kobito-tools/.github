"""Tests for scripts/update_profile.py. Nothing here touches the network."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import update_profile as up  # noqa: E402

ORG = up.ORG
API = up.API


def repo(name, **extra):
    return {"name": name, "default_branch": "main", "html_url": f"https://github.com/{ORG}/{name}",
            "fork": False, "archived": False, "private": False, "topics": ["kobito-app"],
            "description": f"{name} description", **extra}


def manifest(app, name, kind="python", **extra):
    return json.dumps({"format": "kobito-app", "v": 1, "app": app, "name": name, "kind": kind,
                       "contracts": 1, **extra})


class FakeFetch:
    """Answers from a dict of URL -> body; anything else is a 404 (None)."""

    def __init__(self, responses):
        self.responses = responses
        self.urls = []

    def __call__(self, url, accept=None, data=None):
        self.urls.append(url)
        return self.responses.get(url)


def site(repos, extra=None):
    responses = {up.LIST_URL: json.dumps({"items": repos})}
    responses.update(extra or {})
    return FakeFetch(responses)


def manifest_url(name):
    return f"{up.MANIFEST_BASE}/{name}/main/kobito-app.json"


class ParseManifestTest(unittest.TestCase):
    def test_accepts_valid(self):
        m = up.parse_manifest(manifest("popnote", "PopNote!", platforms=["macos", "beos"]))
        self.assertEqual(m["name"], "PopNote!")
        self.assertEqual(m["platforms"], ["macos"])

    def test_rejects_broken(self):
        for text in (None, "", "{", "[]",
                     manifest("popnote", "PopNote!", kind="java"),
                     manifest("Pop Note", "PopNote!"),
                     json.dumps({"format": "kobito-app", "v": 2, "app": "a", "name": "A",
                                 "kind": "python", "contracts": 1}),
                     "{" + " " * up.MANIFEST_LIMIT + "}"):
            self.assertIsNone(up.parse_manifest(text), text and text[:40])


class NewestTagTest(unittest.TestCase):
    def test_compares_numerically(self):
        self.assertEqual(up.newest_tag(["v0.9.0", "v0.10.0", "contracts-v1", "v0.2"]), "v0.10.0")
        self.assertIsNone(up.newest_tag(["contracts-v1"]))


class RenderTest(unittest.TestCase):
    def test_lineup_from_topic_and_manifest(self):
        fetch = site(
            [repo("PopNote"), repo("kobito-workspace"), repo("CorkClip"),
             repo("Hidden", topics=["kobito-app", "profile-hide"]),
             repo("Old", archived=True), repo("NoManifest"), repo(".github")],
            {
                manifest_url("PopNote"): manifest("popnote", "PopNote!", description="メモ",
                                                  platforms=["macos", "windows"]),
                manifest_url("kobito-workspace"): manifest("workspace", "kobito-workspace"),
                manifest_url("CorkClip"): manifest("corkclip", "CorkClip", kind="native",
                                                   description="クリップボード履歴"),
                manifest_url("Hidden"): manifest("hidden", "Hidden"),
                manifest_url("Old"): manifest("old", "Old"),
                # Python app: tags only, no Release.
                f"{API}/repos/{ORG}/PopNote/tags?per_page=100&page=1":
                    json.dumps([{"name": "v0.2.0"}, {"name": "v0.2.1"}]),
                # Native app: the Release wins.
                f"{API}/repos/{ORG}/CorkClip/releases/latest": json.dumps({"tag_name": "v0.1.0"}),
                f"https://github.com/{ORG}/CorkClip":
                    '<meta property="og:image" content="https://repository-images.githubusercontent.com/1/abc">',
                f"{API}/repos/{ORG}/kobito-workspace/readme":
                    '# kobito-workspace\n<img src="assets/icon.png" width="96" align="right">\n',
            },
        )
        skipped = []
        body, count = up.render(up.GitHub(fetch), skipped.append)

        self.assertEqual(count, 3)
        self.assertEqual([l for l in body.splitlines() if l.startswith("### ")], [
            f"### [kobito-workspace](https://github.com/{ORG}/kobito-workspace)",
            f"### [CorkClip](https://github.com/{ORG}/CorkClip)",
            f"### [PopNote!](https://github.com/{ORG}/PopNote)",
        ])
        self.assertIn(f"[v0.2.1](https://github.com/{ORG}/PopNote/tree/v0.2.1)", body)
        self.assertIn(f"[v0.1.0](https://github.com/{ORG}/CorkClip/releases/latest)", body)
        self.assertIn("**種類:** Python　**対応 OS:** macOS · Windows", body)
        self.assertIn("**種類:** ネイティブ", body)
        self.assertIn('src="https://repository-images.githubusercontent.com/1/abc" width="640"', body)
        self.assertIn(f'src="https://raw.githubusercontent.com/{ORG}/kobito-workspace/main/assets/icon.png"', body)
        self.assertIn("メモ", body)
        self.assertNotIn("Hidden", body)
        self.assertEqual(len(skipped), 1)
        self.assertIn("NoManifest", skipped[0])
        self.assertFalse(any("/Old/" in u or u.endswith("/Old") for u in fetch.urls if "tags" in u))

    def test_native_without_release_falls_back_to_tags(self):
        fetch = site([repo("OpenSesame")], {
            manifest_url("OpenSesame"): manifest("opensesame", "OpenSesame!", kind="native"),
            f"{API}/repos/{ORG}/OpenSesame/tags?per_page=100&page=1": json.dumps([{"name": "v0.1.4"}]),
            f"{API}/repos/{ORG}/OpenSesame/contents/assets/icon":
                json.dumps([{"path": "assets/icon/icon-1024.png", "type": "file"},
                            {"path": "assets/icon/icon.svg", "type": "file"}]),
        })
        body, _ = up.render(up.GitHub(fetch), lambda s: None)
        self.assertIn(f"[v0.1.4](https://github.com/{ORG}/OpenSesame/tree/v0.1.4)", body)
        self.assertIn("assets/icon/icon-1024.png", body)
        self.assertIn("OpenSesame description", body)  # repo description when the manifest has none

    def test_list_failure_raises(self):
        with self.assertRaises(RuntimeError):
            up.GitHub(FakeFetch({})).repositories()


class MainTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.readme = self.root / "README.md"
        self.readme.write_text(f"intro\n{up.START}\nhand-written\n{up.END}\noutro\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def app(self, folder, text, tags=()):
        d = self.root / "apps" / folder
        d.mkdir(parents=True)
        (d / "kobito-app.json").write_text(text, encoding="utf-8")
        if tags:
            git = ["git", "-C", str(d), "-c", "user.name=t", "-c", "user.email=t@example.com"]
            subprocess.run(git + ["init", "-q"], check=True)
            subprocess.run(git + ["commit", "-q", "--allow-empty", "-m", "x"], check=True)
            for t in tags:
                subprocess.run(git + ["tag", t], check=True)

    def test_local_replaces_hand_written_list(self):
        self.app("PopNote", manifest("popnote", "PopNote!", repository=f"{ORG}/PopNote"), tags=["v0.2.1"])
        self.app("broken", "{")
        self.assertEqual(up.main(["--local", str(self.root / "apps")], readme=self.readme), 0)
        text = self.readme.read_text(encoding="utf-8")
        self.assertNotIn("hand-written", text)
        self.assertIn("### [PopNote!]", text)
        self.assertIn("v0.2.1", text)
        self.assertTrue(text.startswith("intro\n") and text.endswith("outro\n"))

    def test_nothing_found_keeps_readme(self):
        (self.root / "apps").mkdir()
        before = self.readme.read_text(encoding="utf-8")
        self.assertEqual(up.main(["--local", str(self.root / "apps")], readme=self.readme), 0)
        self.assertEqual(self.readme.read_text(encoding="utf-8"), before)

    def test_missing_markers_fails(self):
        self.app("PopNote", manifest("popnote", "PopNote!"))
        self.readme.write_text("no markers\n", encoding="utf-8")
        self.assertEqual(up.main(["--local", str(self.root / "apps")], readme=self.readme), 1)


if __name__ == "__main__":
    unittest.main()
