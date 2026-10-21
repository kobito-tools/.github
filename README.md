# .github

[kobito-tools](https://github.com/kobito-tools) organization のプロフィールページを管理するリポジトリです。organization のページには [profile/README.md](profile/README.md) が表示されます。kobito シリーズ全体の紹介は、ここに集めています（各アプリのリポジトリは、ほかのアプリのことを書きません）。

## アプリ一覧の自動更新

`profile/README.md` の `<!-- TOOLS:START -->` 〜 `<!-- TOOLS:END -->` の間は、[scripts/update_profile.py](scripts/update_profile.py) が自動で作ります。手で書き換えても上書きされるので、それ以外の部分を編集してください。

GitHub Actions（[update-profile.yml](.github/workflows/update-profile.yml)）が毎日 0:00 (JST) に動きます。すぐに反映したいときは、Actions タブから「Update profile README」を手で動かしてください。動かす前に、テスト（`tests/`）を通します。

### 一覧に並ぶリポジトリ

1. organization のリポジトリのうち、GitHub の topic `kobito-app` が付いたものを探します（GitHub の検索。kobito-workspace の `install.sh` と同じ探し方）。
2. フォーク・しまわれた（archived）・非公開のリポジトリ、`.github`、topic `profile-hide` が付いたものは飛ばします。
3. 既定のブランチの直下の `kobito-app.json` を読みます。読めない・形が違うものは飛ばします（形は kobito-workspace の [docs/APP_PACKAGE.md](https://github.com/kobito-tools/kobito-workspace/blob/main/docs/APP_PACKAGE.md)）。
4. kobito-workspace を先頭に、残りをリポジトリ名の順に並べます。

1つも見つからないとき（まだどこにも topic を付けていないときなど）は、README を書き換えません。

### 各リポジトリから読む内容

| 項目 | 読む所 |
|---|---|
| 名前 | `kobito-app.json` の `name` |
| 説明 | `kobito-app.json` の `description`（なければリポジトリの Description） |
| 種類 | `kobito-app.json` の `kind`（`python` は「Python」、`native` は「ネイティブ」） |
| 対応 OS | `kobito-app.json` の `platforms` |
| 画像 | リポジトリの Social preview（1280×640）。設定がなければ README の `<img src="..." align="right">`、それもなければ `assets/icon/` の中の名前に icon を含む PNG |
| 最新版 | ネイティブのアプリは最新の Release。Python のアプリは Release を作らないので、いちばん新しい `v…` のタグ（Release の無いネイティブのアプリもタグ） |

### 手元で動かす

```bash
python3 scripts/update_profile.py            # GitHub から作って README を書き換える
python3 scripts/update_profile.py --dry-run  # 一覧を表示するだけ
python3 scripts/update_profile.py --local .. # GitHub の代わりに、隣のフォルダの kobito-app.json を読む（画像なし）
python3 -m unittest discover -s tests        # テスト（ネットにつながらない）
```

取り寄せ先は、環境変数で差し替えられます。

| 環境変数 | 既定 | 用途 |
|---|---|---|
| `KOBITO_GITHUB_ORG` | `kobito-tools` | organization |
| `KOBITO_APP_LIST_URL` | `https://api.github.com/search/repositories?q=org:<organization>+topic:kobito-app&per_page=100` | 一覧の取得先（`file://…` も指せる） |
| `KOBITO_APP_MANIFEST_BASE` | `https://raw.githubusercontent.com/<organization>` | `<ここ>/<リポジトリ名>/<ブランチ>/kobito-app.json` を読む |
| `KOBITO_GITHUB_API` | `https://api.github.com` | Release・タグ・README・GraphQL の取得先 |
| `KOBITO_GITHUB_WEB` | `https://github.com` | トークンが無いときに Social preview を読むページ |
| `GITHUB_TOKEN` | なし | あれば API に使う（Actions では自動で入る） |
