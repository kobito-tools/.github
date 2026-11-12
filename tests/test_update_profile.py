"""Tests for scripts/update_profile.py. Nothing here touches the network."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import update_profile as up  # noqa: E402

ORG = up.ORG
API = up.API
RAW = f"https://raw.githubusercontent.com/{ORG}"
# kobito-workspace next to this repository, for comparing with its kit.package (skipped if absent).
WORKSPACE = Path(os.environ.get("KOBITO_WORKSPACE_DIR")
                 or Path(__file__).resolve().parent.parent.parent / "kobito-workspace")


def repo(name, **extra):
    return {"name": name, "default_branch": "main", "html_url": f"https://github.com/{ORG}/{name}",
            "fork": False, "archived": False, "private": False, "topics": ["kobito-app"],
            "description": f"{name} description", **extra}


def manifest(app, name, kind="python", **extra):
    return json.dumps({"format": "kobito-app", "v": 1, "app": app, "name": name, "kind": kind,
                       "contracts": 1, **extra})


def listing(*files, size=1000):
    return json.dumps([{"path": f"kobito/{f}", "type": "file", "size": size} for f in files])


class FakeFetch:
    """Answers from a dict of URL -> body; anything else is a 404 (None)."""

    def __init__(self, responses):
        self.responses = responses
        self.urls = []

    def __call__(self, url, accept=None, data=None):
        self.urls.append(url)
        return self.responses.get(url)


def list_url(page=1):
    return f"{up.LIST_URL}&page={page}"


def site(repos, extra=None):
    responses = {list_url(): json.dumps(repos)}
    responses.update(extra or {})
    return FakeFetch(responses)


def manifest_url(name):
    return f"{up.MANIFEST_BASE}/{name}/main/kobito-app.json"


def kobito_url(name, folder="kobito"):
    return f"{API}/repos/{ORG}/{name}/contents/{folder}?ref=main"


def assets(*files, size=1000):
    return json.dumps([{"path": f"assets/{f}", "type": "file", "size": size} for f in files])


class ParseManifestTest(unittest.TestCase):
    def test_accepts_valid(self):
        m = up.parse_manifest(manifest("popnote", "PopNote!", platforms=["macos", "beos"]))
        self.assertEqual(m["name"], "PopNote!")
        self.assertEqual(m["platforms"], ["macos"])

    def test_rejects_broken(self):
        for text in (None, "", "{", "[]",
                     manifest("popnote", "PopNote!", kind="java"),
                     manifest("Pop Note", "PopNote!"),
                     manifest("popnote", "  "),
                     manifest("popnote", "PopNote!", entry="popnote.py"),
                     manifest("popnote", "PopNote!", setup="../setup.sh"),
                     manifest("popnote", "PopNote!", contracts=True),
                     json.dumps({"format": "kobito-app", "v": 2, "app": "a", "name": "A",
                                 "kind": "python", "contracts": 1}),
                     "{" + " " * up.MANIFEST_LIMIT + "}"):
            self.assertIsNone(up.parse_manifest(text), text and text[:40])

    def test_drops_only_wrong_optional_items(self):
        m = up.parse_manifest(manifest("sample", "Sample", tagline="x" * 81, tagline_en="two\nlines",
                                       version="one", repository="not a repo", description=" "))
        for key in ("tagline", "tagline_en", "version", "repository", "description"):
            self.assertNotIn(key, m)
        self.assertEqual(m["name"], "Sample")


class CardTest(unittest.TestCase):
    def test_fields_and_images(self):
        m = up.parse_manifest(manifest("sample", "Sample", tagline="ひとこと", version="0.2.0", bundle_id="x"))
        c = up.card(m, {"kobito/icon.svg": 10, "kobito/icon-1024.png": 10, "kobito/screenshot.png": 10})
        self.assertEqual(c["icon"], "kobito/icon-1024.png")
        self.assertEqual(c["screenshot"], "kobito/screenshot.png")
        self.assertEqual(c["tagline"], "ひとこと")
        self.assertNotIn("bundle_id", c)

    def test_missing_or_too_large_images(self):
        m = up.parse_manifest(manifest("sample", "Sample"))
        c = up.card(m, {"kobito/icon.svg": 10, "kobito/screenshot.png": 3 * 1024 * 1024})
        self.assertEqual(c["icon"], "kobito/icon.svg")
        self.assertIsNone(c["screenshot"])
        self.assertIsNone(up.card(m, {"kobito/other.png": 10})["icon"])

    def test_tagline_falls_back_to_description(self):
        self.assertEqual(up.tagline({"tagline": "a", "description": "b"}), "a")
        self.assertEqual(up.tagline({"description": "b"}), "b")
        self.assertEqual(up.tagline({}), "")

    def test_english_text_falls_back_to_japanese(self):
        c = {"name": "名前", "tagline": "ひとこと", "description_en": "In English"}
        self.assertEqual(up.tagline(c, "en"), "In English")
        self.assertEqual(up.tagline({"tagline": "ひとこと"}, "en"), "ひとこと")
        self.assertEqual(up.tagline({"tagline_en": "One line"}, "ja"), "One line")
        self.assertEqual(up.name(c, "en"), "名前")
        self.assertEqual(up.name({"name": "名前", "name_en": "Name"}, "en"), "Name")

    @unittest.skipUnless((WORKSPACE / "kobito_workspace" / "kit" / "package.py").is_file(),
                         "kobito-workspace is not next to this repository")
    def test_same_card_as_kit_package(self):
        sys.path.insert(0, str(WORKSPACE))
        try:
            from kobito_workspace.kit import package
        finally:
            sys.path.remove(str(WORKSPACE))
        samples = {
            "Sample": (manifest("sample", "Sample", tagline="すぐ書きとめる", description="メモ",
                                version="0.1.0", repository=f"{ORG}/Sample", platforms=["macos"],
                                tagline_en="x" * 81), ["icon-1024.png", "screenshot.png"]),
            "SampleNative": (manifest("sample-native", "Sample Native", kind="native", description="常駐",
                                      bundle_id="b", version="v1"), ["icon-1024.png"]),
        }
        with tempfile.TemporaryDirectory() as tmp:
            for folder, (text, images) in samples.items():
                d = Path(tmp) / folder
                (d / "kobito").mkdir(parents=True)
                (d / "kobito-app.json").write_text(text, encoding="utf-8")
                for image in images:
                    (d / "kobito" / image).write_bytes(b"x")
                files = {f"kobito/{f.name}": f.stat().st_size for f in (d / "kobito").iterdir()}
                theirs = package.AppPackage.read(d).card()
                ours = up.card(up.parse_manifest(text), files)
                # Same items with the same meaning; the icon is the PNG on both since there is no SVG.
                self.assertEqual(ours, theirs, folder)


class RenderTest(unittest.TestCase):
    """Two sample repositories, one Python and one native, as the card standard lays them out."""

    def setUp(self):
        env = mock.patch.dict(os.environ)
        env.start()
        self.addCleanup(env.stop)
        os.environ.pop("GITHUB_TOKEN", None)

    def sample_site(self):
        return site(
            [repo("SampleNative"), repo("Sample"), repo("kobito-workspace"),
             repo("Hidden", topics=["kobito-app", "profile-hide"]),
             repo("Old", archived=True), repo("NoManifest"), repo(".github")],
            {
                # Python: tagline, icon and screenshot, versions marked by tags only.
                manifest_url("Sample"): manifest(
                    "sample", "Sample", tagline="思いついたことを、すぐ書きとめる",
                    description="説明のための架空のメモのアプリ", version="0.1.0",
                    platforms=["macos", "windows"]),
                kobito_url("Sample"): listing("icon.svg", "icon-1024.png", "screenshot.png"),
                kobito_url("Sample", "assets"): assets("social-preview.png", "social-preview.ja.png", "other.svg"),
                f"{API}/repos/{ORG}/Sample/tags?per_page=100&page=1":
                    json.dumps([{"name": "v0.1.0"}, {"name": "v0.10.0"}, {"name": "contracts-v1"}]),
                # Native: no tagline, no assets/social-preview.png (the Social preview is used), a tag.
                manifest_url("SampleNative"): manifest(
                    "sample-native", "Sample Native", kind="native", description="説明のための架空の常駐アプリ",
                    description_en="A made-up resident app", version="1.0.0", platforms=["macos"]),
                kobito_url("SampleNative"): listing("icon.svg", "icon-1024.png"),
                f"{API}/repos/{ORG}/SampleNative/tags?per_page=100&page=1": json.dumps([{"name": "v1.0.0"}]),
                f"https://github.com/{ORG}/SampleNative":
                    '<meta property="og:image" content="https://repository-images.githubusercontent.com/1/abc">',
                # The hub: no images yet, no tags; the manifest's version is shown as it is.
                manifest_url("kobito-workspace"): manifest("workspace", "kobito-workspace", version="0.1.0"),
                manifest_url("Hidden"): manifest("hidden", "Hidden"),
                manifest_url("Old"): manifest("old", "Old"),
            },
        )

    def test_lineup_from_cards(self):
        fetch = self.sample_site()
        skipped = []
        bodies, count = up.render(up.GitHub(fetch), skipped.append, ("ja", "en"))

        self.assertEqual(count, 3)
        sections = bodies["ja"].split("\n\n### ")
        self.assertEqual(len(sections), 3)
        hub, python, native = sections

        self.assertEqual(hub, "\n\n".join([
            f"### [kobito-workspace](https://github.com/{ORG}/kobito-workspace)",
            "**種類:** Python　**対応 OS:** —　**最新版:** 0.1.0",
        ]))
        self.assertEqual(native, "\n\n".join([
            f'<img src="{RAW}/SampleNative/main/kobito/icon-1024.png" width="32" height="32" alt="">'
            f" [Sample Native](https://github.com/{ORG}/SampleNative)",
            "説明のための架空の常駐アプリ",
            f'<a href="https://github.com/{ORG}/SampleNative">'
            '<img src="https://repository-images.githubusercontent.com/1/abc" width="640" alt="Sample Native"></a>',
            f"**種類:** ネイティブ　**対応 OS:** macOS　"
            f"**最新版:** [v1.0.0](https://github.com/{ORG}/SampleNative/tree/v1.0.0)",
        ]))
        self.assertEqual(python, "\n\n".join([
            f'<img src="{RAW}/Sample/main/kobito/icon-1024.png" width="32" height="32" alt="">'
            f" [Sample](https://github.com/{ORG}/Sample)",
            "思いついたことを、すぐ書きとめる",
            f'<a href="https://github.com/{ORG}/Sample">'
            f'<img src="{RAW}/Sample/main/assets/social-preview.ja.png" width="640" alt="Sample"></a>',
            f"**種類:** Python　**対応 OS:** macOS · Windows　"
            f"**最新版:** [v0.10.0](https://github.com/{ORG}/Sample/tree/v0.10.0)",
        ]))

        # English: same order and images, English labels and text (Japanese when there is no English).
        en_hub, en_python, en_native = bodies["en"].split("\n\n### ")
        self.assertTrue(en_hub.endswith("**Type:** Python &nbsp;·&nbsp; **Platforms:** — &nbsp;·&nbsp; **Latest:** 0.1.0"))
        self.assertIn("\n\nA made-up resident app\n\n", en_native)
        self.assertIn("**Type:** Native", en_native)
        self.assertIn("\n\n思いついたことを、すぐ書きとめる\n\n", en_python)
        self.assertIn(f"{RAW}/Sample/main/assets/social-preview.png\"", en_python)
        self.assertNotIn("social-preview.ja.png", bodies["en"])

        self.assertNotIn("Hidden", bodies["ja"])
        self.assertNotIn("description", bodies["ja"])  # GitHub's Description is not part of the card
        self.assertEqual(len(skipped), 1)
        self.assertIn("NoManifest", skipped[0])
        self.assertFalse(any("/Old" in u for u in fetch.urls if u != manifest_url("Old")))
        # The Social preview is only looked up when there is no assets/social-preview.png,
        # and each repository is read once for both languages.
        self.assertNotIn(f"https://github.com/{ORG}/Sample", fetch.urls)
        self.assertEqual(fetch.urls.count(f"https://github.com/{ORG}/SampleNative"), 1)
        self.assertNotIn(f"{RAW}/Sample/main/kobito/screenshot.png", bodies["ja"])

    def test_japanese_uses_english_image_when_it_has_none(self):
        fetch = site([repo("Sample")], {
            manifest_url("Sample"): manifest("sample", "Sample"),
            kobito_url("Sample", "assets"): assets("social-preview.png"),
        })
        bodies, _ = up.render(up.GitHub(fetch), lambda s: None, ("ja", "en"))
        for lang in ("ja", "en"):
            self.assertIn(f'src="{RAW}/Sample/main/assets/social-preview.png"', bodies[lang])
        self.assertNotIn(f"https://github.com/{ORG}/Sample", fetch.urls)

    def test_only_japanese_image_leaves_english_on_social_preview(self):
        fetch = site([repo("Sample")], {
            manifest_url("Sample"): manifest("sample", "Sample"),
            kobito_url("Sample", "assets"): assets("social-preview.ja.png"),
            f"https://github.com/{ORG}/Sample":
                '<meta property="og:image" content="https://repository-images.githubusercontent.com/3/og">',
        })
        bodies, _ = up.render(up.GitHub(fetch), lambda s: None, ("ja", "en"))
        self.assertIn(f'src="{RAW}/Sample/main/assets/social-preview.ja.png"', bodies["ja"])
        self.assertIn('src="https://repository-images.githubusercontent.com/3/og"', bodies["en"])

    def test_too_large_social_preview_falls_back(self):
        fetch = site([repo("Sample")], {
            manifest_url("Sample"): manifest("sample", "Sample"),
            kobito_url("Sample", "assets"): assets("social-preview.png", size=3 * 1024 * 1024),
            f"https://github.com/{ORG}/Sample":
                '<meta property="og:image" content="https://repository-images.githubusercontent.com/2/og">',
        })
        bodies, _ = up.render(up.GitHub(fetch), lambda s: None)
        self.assertIn('src="https://repository-images.githubusercontent.com/2/og"', bodies["ja"])

    def test_lists_every_page_of_repositories(self):
        first = [repo(f"Other{i:03}") for i in range(100)]
        fetch = FakeFetch({
            list_url(1): json.dumps(first),
            list_url(2): json.dumps([repo("Sample")]),
            manifest_url("Sample"): manifest("sample", "Sample"),
        })
        bodies, count = up.render(up.GitHub(fetch), lambda s: None)
        self.assertEqual(count, 1)
        self.assertTrue(bodies["ja"].startswith("### [Sample]"))

    def test_native_uses_tags_not_releases(self):
        fetch = site([repo("SampleNative")], {
            manifest_url("SampleNative"): manifest("sample-native", "Sample Native", kind="native"),
            f"{API}/repos/{ORG}/SampleNative/tags?per_page=100&page=1": json.dumps([{"name": "v0.1.4"}]),
            # A leftover Release must not win over the tags.
            f"{API}/repos/{ORG}/SampleNative/releases/latest": json.dumps({"tag_name": "v9.9.9"}),
        })
        body = up.render(up.GitHub(fetch), lambda s: None)[0]["ja"]
        self.assertIn(f"[v0.1.4](https://github.com/{ORG}/SampleNative/tree/v0.1.4)", body)
        self.assertNotIn("v9.9.9", body)
        self.assertFalse(any("/releases" in url for url in fetch.urls))
        self.assertTrue(body.startswith("### [Sample Native]"))  # no icon, no tagline
        self.assertEqual(body.count("\n\n"), 1)

    def test_ignores_links_and_unknown_files_in_kobito(self):
        fetch = site([repo("Sample")], {
            manifest_url("Sample"): manifest("sample", "Sample"),
            kobito_url("Sample"): json.dumps([
                {"path": "kobito/icon-1024.png", "type": "symlink", "size": 10},
                {"path": "kobito/screenshot.png", "type": "file", "size": 3 * 1024 * 1024},
                {"path": "kobito/banner.png", "type": "file", "size": 10},
            ]),
            kobito_url("Sample", "assets"): json.dumps([
                {"path": "assets/social-preview.png", "type": "symlink", "size": 10},
            ]),
        })
        body = up.render(up.GitHub(fetch), lambda s: None)[0]["ja"]
        self.assertNotIn("<img", body)

    def test_token_reads_social_preview_with_graphql(self):
        fetch = site([repo("SampleNative")], {
            manifest_url("SampleNative"): manifest("sample-native", "Sample Native", kind="native"),
            f"{API}/graphql": json.dumps({"data": {"repository": {
                "usesCustomOpenGraphImage": True, "openGraphImageUrl": "https://example.com/og.png"}}}),
        })
        os.environ["GITHUB_TOKEN"] = "test"
        body = up.render(up.GitHub(fetch), lambda s: None)[0]["ja"]
        self.assertIn('src="https://example.com/og.png" width="640"', body)

    def test_list_failure_raises(self):
        with self.assertRaises(RuntimeError):
            up.GitHub(FakeFetch({})).repositories()


class MainTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.readmes = {"en": self.root / "README.md", "ja": self.root / "README.ja.md"}
        for readme in self.readmes.values():
            readme.write_text(f"intro\n{up.START}\nhand-written\n{up.END}\noutro\n", encoding="utf-8")
        self.readme = self.readmes["ja"]

    def tearDown(self):
        self.tmp.cleanup()

    def app(self, folder, text, tags=()):
        d = self.root / "apps" / folder
        (d / "kobito").mkdir(parents=True)
        (d / "kobito-app.json").write_text(text, encoding="utf-8")
        (d / "kobito" / "icon-1024.png").write_bytes(b"x")
        if tags:
            git = ["git", "-C", str(d), "-c", "user.name=t", "-c", "user.email=t@example.com"]
            subprocess.run(git + ["init", "-q"], check=True)
            subprocess.run(git + ["commit", "-q", "--allow-empty", "-m", "x"], check=True)
            for t in tags:
                subprocess.run(git + ["tag", t], check=True)

    def test_local_replaces_hand_written_list(self):
        self.app("Sample", manifest("sample", "Sample", tagline="ひとこと", tagline_en="One line",
                                    repository=f"{ORG}/Sample"), tags=["v0.2.1"])
        self.app("broken", "{")
        self.assertEqual(up.main(["--local", str(self.root / "apps")], readmes=self.readmes), 0)
        english = self.readmes["en"].read_text(encoding="utf-8")
        self.assertIn("One line", english)
        self.assertIn("**Latest:**", english)
        text = self.readme.read_text(encoding="utf-8")
        self.assertNotIn("hand-written", text)
        self.assertIn("### [Sample]", text)  # local images are not linked: GitHub may not have them yet
        self.assertIn("ひとこと", text)
        self.assertIn("v0.2.1", text)
        self.assertTrue(text.startswith("intro\n") and text.endswith("outro\n"))

    def test_nothing_found_keeps_readme(self):
        (self.root / "apps").mkdir()
        before = self.readme.read_text(encoding="utf-8")
        self.assertEqual(up.main(["--local", str(self.root / "apps")], readmes=self.readmes), 0)
        self.assertEqual(self.readme.read_text(encoding="utf-8"), before)

    def test_missing_markers_fails_without_writing_either(self):
        self.app("Sample", manifest("sample", "Sample"))
        self.readme.write_text("no markers\n", encoding="utf-8")
        self.assertEqual(up.main(["--local", str(self.root / "apps")], readmes=self.readmes), 1)
        self.assertIn("hand-written", self.readmes["en"].read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
