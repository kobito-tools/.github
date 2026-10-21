# .github

[kobito-tools](https://github.com/kobito-tools) organization のプロフィールページを管理するリポジトリです。organization のページには [profile/README.md](profile/README.md) が表示されます。kobito シリーズ全体の紹介は、ここに集めています（各アプリのリポジトリは、ほかのアプリのことを書きません）。

## アプリ一覧の自動更新

`profile/README.md` の `<!-- TOOLS:START -->` 〜 `<!-- TOOLS:END -->` の間は、[scripts/update_profile.py](scripts/update_profile.py) が自動で作ります。手で書き換えても上書きされるので、それ以外の部分を編集してください。

GitHub Actions（[update-profile.yml](.github/workflows/update-profile.yml)）が毎日 0:00 (JST) と、スクリプト・テスト・ワークフローが `main` に入ったときに動きます。すぐに反映したいときは、Actions タブから「Update profile README」を手で動かしてください。動かす前に、テスト（`tests/`）を通します。

### 一覧に並ぶリポジトリ

1. organization のリポジトリのうち、GitHub の topic `kobito-app` が付いたものを探します（GitHub の検索。kobito-workspace の `install.sh` と同じ探し方）。
2. フォーク・しまわれた（archived）・非公開のリポジトリ、`.github`、topic `profile-hide` が付いたものは飛ばします。
3. 既定のブランチの直下の `kobito-app.json` を読みます。読めない・形が違うものは飛ばします（形は kobito-workspace の [APP_PACKAGE.md](https://github.com/kobito-tools/kobito-workspace/blob/main/kobito_workspace/kit/docs/APP_PACKAGE.md) の §2）。読み方は kobito-workspace の共通部品 `kit.manifest` と同じです。
4. kobito-workspace を先頭に、残りをリポジトリ名の順に並べます。

1つも見つからないとき（まだどこにも topic を付けていないときなど）は、README を書き換えません。

### 各リポジトリから読む内容（紹介のカード）

1つのアプリは、シリーズの「紹介のカード」（[APP_PACKAGE.md](https://github.com/kobito-tools/kobito-workspace/blob/main/kobito_workspace/kit/docs/APP_PACKAGE.md) の §6）として並べます。kobito-workspace の画面・`install.sh` と同じ項目です。読むのは `kobito-app.json` と、`kobito/` の決まった名前の画像だけで、リポジトリの中の物は何も動かしません。

| カードの部分 | 読む所 | 無いとき |
|---|---|---|
| アイコン | 既定のブランチの `kobito/icon-1024.png`（2 MB まで） | `kobito/icon.svg`（256 KB まで）。それも無ければ出さない |
| 名前 | `kobito-app.json` の `name` | — |
| ひとこと | `kobito-app.json` の `tagline`（1行、80文字まで） | `description`。それも無ければ出さない |
| 画像 | 既定のブランチの `kobito/screenshot.png`（2 MB まで） | リポジトリの Social preview（1280×640）。それも無ければ出さない |
| 種類・対応 OS | `kobito-app.json` の `kind`（Python・ネイティブ）と `platforms` | 対応 OS は「—」 |
| 最新版 | ネイティブのアプリは最新の Release。Python のアプリは Release を作らないので、いちばん新しい `v…` のタグ（Release の無いネイティブのアプリもタグ） | `kobito-app.json` の `version` をそのまま（リンクなし）。それも無ければ「—」 |

- `kobito/` の中にあるかどうかは、GitHub の API（`contents/kobito`）の一覧で調べます。ふつうのファイルだけを使い、シンボリックリンク・大きすぎるファイル・決まっていない名前のファイルは使いません。
- アイコンは、§6 では `icon.svg` が先ですが、ここでは `icon-1024.png` を先に使います（GitHub の README では、PNG がどこでも同じに見えるため）。
- 画像は、`https://raw.githubusercontent.com/<organization>/<リポジトリ名>/<ブランチ>/kobito/…` を README から指します。
- GitHub のリポジトリの Description は使いません（カードの文字は `kobito-app.json` だけから作る）。

### 手元で動かす

```bash
python3 scripts/update_profile.py            # GitHub から作って README を書き換える
python3 scripts/update_profile.py --dry-run  # 一覧を表示するだけ
python3 scripts/update_profile.py --local .. # GitHub の代わりに、隣のフォルダの kobito-app.json を読む（画像なし）
python3 -m unittest discover -s tests        # テスト（ネットにつながらない）
```

テストは、見本のリポジトリ2つ（Python とネイティブ）の取り寄せ先を差し替えて、一覧の見え方を確かめます。隣に kobito-workspace のフォルダがあれば（または `KOBITO_WORKSPACE_DIR` で指せば）、共通部品 `kit.package` のカードと同じ項目になるかも比べます（無ければ、その1つは飛ばします）。

`--local` は、topic を付ける前の仮の一覧を作るためのものです。GitHub にまだ画像があるか分からないので、画像は出しません。

取り寄せ先は、環境変数で差し替えられます。

| 環境変数 | 既定 | 用途 |
|---|---|---|
| `KOBITO_GITHUB_ORG` | `kobito-tools` | organization |
| `KOBITO_APP_LIST_URL` | `https://api.github.com/search/repositories?q=org:<organization>+topic:kobito-app&per_page=100` | 一覧の取得先（`file://…` も指せる） |
| `KOBITO_APP_MANIFEST_BASE` | `https://raw.githubusercontent.com/<organization>` | `<ここ>/<リポジトリ名>/<ブランチ>/kobito-app.json` を読む |
| `KOBITO_GITHUB_API` | `https://api.github.com` | `kobito/` の一覧・Release・タグ・GraphQL の取得先 |
| `KOBITO_GITHUB_WEB` | `https://github.com` | トークンが無いときに Social preview を読むページ |
| `GITHUB_TOKEN` | なし | あれば API に使う（Actions では自動で入る） |
