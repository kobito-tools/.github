# .github

[kobito-tools](https://github.com/kobito-tools) organization のプロフィールページを管理するリポジトリです。organization のページには [profile/README.md](profile/README.md) が表示されます。

## ツール一覧の自動更新

`profile/README.md` の `<!-- TOOLS:START -->` 〜 `<!-- TOOLS:END -->` の間は、[scripts/update_profile.py](scripts/update_profile.py) が organization の公開リポジトリから自動生成します。手で編集しても上書きされるので、それ以外の部分を編集してください。

GitHub Actions（[update-profile.yml](.github/workflows/update-profile.yml)）が毎日 0:00 (JST) に実行します。すぐに反映したいときは Actions タブから「Update profile README」を手動実行してください。

### 各リポジトリから読み取る内容

| 項目 | 読み取り元 |
|---|---|
| ツール名 | README の最初の `# 見出し` |
| アイコン | README 冒頭の `<img src="..." align="right">`（なければ `assets/icon/` 内の名前に icon を含む PNG） |
| 概要 | 見出しの次の最初の段落（なければリポジトリの Description） |
| 対応 OS | README の `## 動作環境` に書かれた macOS / Windows など |
| 最新版 | 最新の Release のタグ |

並び順はリポジトリの作成順です。フォーク・アーカイブ済み・非公開のリポジトリは表示されません。公開したまま一覧から外したい場合は、そのリポジトリに `profile-hide` トピックを付けてください。

### ローカルで実行

```bash
python3 scripts/update_profile.py
```
