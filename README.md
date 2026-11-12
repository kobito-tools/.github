# .github

[kobito-tools](https://github.com/kobito-tools) organization のプロフィールページを管理するリポジトリです。organization のページには、英語の [profile/README.md](profile/README.md) が表示されます。日本語は [profile/README.ja.md](profile/README.ja.md) で、どちらも先頭のリンクで切り替えられます。kobito シリーズ全体の紹介は、ここに集めています（各アプリのリポジトリは、ほかのアプリのことを書きません）。

## アプリ一覧の自動更新

`profile/README.md`（英語）と `profile/README.ja.md`（日本語）の `<!-- TOOLS:START -->` 〜 `<!-- TOOLS:END -->` の間は、[scripts/update_profile.py](scripts/update_profile.py) が自動で作ります。手で書き換えても上書きされるので、それ以外の部分を編集してください。文章を直すときは、両方の言語をそろえてください。どちらかのマーカーが無いときは、どちらも書き換えません。

GitHub Actions（[update-profile.yml](.github/workflows/update-profile.yml)）が毎日 0:00 (JST) と、スクリプト・テスト・ワークフローが `main` に入ったときに動きます。すぐに反映したいときは、Actions タブから「Update profile README」を手で動かしてください。動かす前に、テスト（`tests/`）を通します。

### 一覧に並ぶリポジトリ

1. organization の公開リポジトリをすべて取り寄せます（`GET /orgs/<organization>/repos?type=public`。100件ずつ、全ページ）。topic は要りません。
2. フォーク・しまわれた（archived）・非公開のリポジトリ、`.github`、topic `profile-hide` が付いたものは飛ばします。
3. 既定のブランチの直下の `kobito-app.json` を読みます。無い・読めない・形が違うものは飛ばします（形は kobito-workspace の [APP_PACKAGE.md](https://github.com/kobito-tools/kobito-workspace/blob/main/kobito_workspace/kit/docs/APP_PACKAGE.md) の §2）。読み方は kobito-workspace の共通部品 `kit.manifest` と同じです。
4. kobito-workspace を先頭に、残りをリポジトリ名の順に並べます。

1つも見つからないときは、README を書き換えません。リポジトリを一覧から外したいときは、非公開にするか、topic `profile-hide` を付けます。

### 各リポジトリから読む内容（紹介のカード）

1つのアプリは、シリーズの「紹介のカード」（[APP_PACKAGE.md](https://github.com/kobito-tools/kobito-workspace/blob/main/kobito_workspace/kit/docs/APP_PACKAGE.md) の §6）として並べます。kobito-workspace の画面・`install.sh` と同じ項目です。読むのは `kobito-app.json` と、決まった名前の画像だけで、リポジトリの中の物は何も動かしません。1つのリポジトリは1回だけ読み、英語と日本語の両方の一覧を作ります。

| カードの部分 | 読む所 | 無いとき |
|---|---|---|
| アイコン | 既定のブランチの `kobito/icon-1024.png`（2 MB まで） | `kobito/icon.svg`（256 KB まで）。それも無ければ出さない |
| 名前 | 英語は `name_en`、日本語は `name` | もう一方の言語 |
| ひとこと | 英語は `tagline_en`、日本語は `tagline`（1行、80文字まで） | 同じ言語の `description_en`・`description`、次にもう一方の言語。どれも無ければ出さない |
| 画像 | 既定のブランチの `assets/social-preview.png`（1280×640、2 MB まで） | リポジトリの Settings で設定した Social preview。それも無ければ出さない |
| 種類・対応 OS | `kobito-app.json` の `kind`（Python・ネイティブ）と `platforms` | 対応 OS は「—」 |
| 最新版 | いちばん新しい `v…` のタグ（どのアプリも Release では配らず、ソースを入手して `./setup.sh` で入れる） | `kobito-app.json` の `version` をそのまま（リンクなし）。それも無ければ「—」 |

- `kobito/`・`assets/` の中にあるかどうかは、GitHub の API（`contents/kobito`・`contents/assets`）の一覧で調べます。ふつうのファイルだけを使い、シンボリックリンク・大きすぎるファイル・決まっていない名前のファイルは使いません。
- アイコンは、§6 では `icon.svg` が先ですが、ここでは `icon-1024.png` を先に使います（GitHub の README では、PNG がどこでも同じに見えるため）。
- `kobito/screenshot.png` は使いません（一覧の画像は `assets/social-preview.png` にそろえた）。
- 画像は、`https://raw.githubusercontent.com/<organization>/<リポジトリ名>/<ブランチ>/…` を README から指します。リンクは GitHub の実際のリポジトリ名で作ります（`kobito-app.json` の `repository` は使わない）。
- GitHub のリポジトリの Description は使いません（カードの文字は `kobito-app.json` だけから作る）。

### 手元で動かす

```bash
python3 scripts/update_profile.py            # GitHub から作って README（英語・日本語）を書き換える
python3 scripts/update_profile.py --dry-run  # 一覧を表示するだけ
python3 scripts/update_profile.py --local .. # GitHub の代わりに、隣のフォルダの kobito-app.json を読む（画像なし）
python3 -m unittest discover -s tests        # テスト（ネットにつながらない）
```

テストは、見本のリポジトリ（Python とネイティブ）の取り寄せ先を差し替えて、一覧の見え方を確かめます。隣に kobito-workspace のフォルダがあれば（または `KOBITO_WORKSPACE_DIR` で指せば）、共通部品 `kit.package` のカードと同じ項目になるかも比べます（無ければ、その1つは飛ばします）。

`--local` は、公開する前のアプリも含めた仮の一覧を、手元で確かめるためのものです。GitHub にまだ画像があるか分からないので、画像は出しません。

取り寄せ先は、環境変数で差し替えられます。

| 環境変数 | 既定 | 用途 |
|---|---|---|
| `KOBITO_GITHUB_ORG` | `kobito-tools` | organization |
| `KOBITO_APP_LIST_URL` | `https://api.github.com/orgs/<organization>/repos?type=public&per_page=100` | 一覧の取得先。後ろに `&page=<n>` を付けて読む |
| `KOBITO_APP_MANIFEST_BASE` | `https://raw.githubusercontent.com/<organization>` | `<ここ>/<リポジトリ名>/<ブランチ>/kobito-app.json` を読む |
| `KOBITO_GITHUB_API` | `https://api.github.com` | `kobito/`・`assets/` の一覧・タグ・GraphQL の取得先 |
| `KOBITO_GITHUB_WEB` | `https://github.com` | トークンが無いときに Social preview を読むページ |
| `GITHUB_TOKEN` | なし | あれば API に使う（Actions では自動で入る） |
