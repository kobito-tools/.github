# kobito-tools

[English](https://github.com/kobito-tools) | **日本語**

毎日の作業を、ちょっとだけ楽にする小さな道具たち。

kobito-tools は、小人（kobito）のように手を貸してくれる、デスクトップ用の小さなアプリのシリーズです。

## 考え方

- **どのアプリも単体で使えます。** ほしいアプリだけを入れて、ふつうのアプリとして開けます。
- **[kobito-workspace](https://github.com/kobito-tools/kobito-workspace) に並べると、1つのウインドウで使えます。** 入れたアプリが workspace に並び、切り替えながら使えて、横断検索もできます。
- **どのアプリも、同じ形のリポジトリです。** 直下に名乗り `kobito-app.json` を、`kobito/` にアイコンを、`assets/social-preview.png`（日本語は `social-preview.ja.png`）に紹介の画像を、決まった名前で置きます。`kobito-app.json` を持つ公開リポジトリは、下の一覧に自動で並びます。決まりは kobito-workspace の [APP_PACKAGE.md](https://github.com/kobito-tools/kobito-workspace/blob/main/kobito_workspace/kit/docs/APP_PACKAGE.md) にあります。

## 入れ方

シリーズをまとめて入れるときは、ターミナルで次を動かします。一覧から入れたいアプリを選べます。

```bash
zsh -c "$(curl -fsSL https://raw.githubusercontent.com/kobito-tools/kobito-workspace/main/install.sh)"
```

アプリを1つずつ入れるときは、そのアプリのソースを入手して（`git clone` か「Code → Download ZIP」）、フォルダの中で `./setup.sh` を実行します。詳しくは各アプリの README を見てください。インストーラー（dmg など）は配っていません。

## アプリ一覧

<!-- TOOLS:START -->
### <img src="https://raw.githubusercontent.com/kobito-tools/CrokClip/main/kobito/icon-1024.png" width="32" height="32" alt=""> [CorkClip](https://github.com/kobito-tools/CrokClip)

コピーした物を、コルクボードに留めておく

<a href="https://github.com/kobito-tools/CrokClip"><img src="https://raw.githubusercontent.com/kobito-tools/CrokClip/main/assets/social-preview.png" width="640" alt="CorkClip"></a>

**種類:** ネイティブ　**対応 OS:** macOS　**最新版:** [v0.2.0](https://github.com/kobito-tools/CrokClip/tree/v0.2.0)

### <img src="https://raw.githubusercontent.com/kobito-tools/OpenSesame/main/kobito/icon-1024.png" width="32" height="32" alt=""> [OpenSesame!](https://github.com/kobito-tools/OpenSesame)

キーを押している間だけ、アプリやファイルへの扉が開く

<a href="https://github.com/kobito-tools/OpenSesame"><img src="https://repository-images.githubusercontent.com/1382855232/03a62c13-b261-42ac-898c-e7c8617d9ca8" width="640" alt="OpenSesame!"></a>

**種類:** ネイティブ　**対応 OS:** macOS · Windows　**最新版:** [v1.0.0](https://github.com/kobito-tools/OpenSesame/tree/v1.0.0)

### <img src="https://raw.githubusercontent.com/kobito-tools/PopNote/main/kobito/icon-1024.png" width="32" height="32" alt=""> [PopNote!](https://github.com/kobito-tools/PopNote)

ポンッと開いて、すぐ書けるメモと日記

<a href="https://github.com/kobito-tools/PopNote"><img src="https://repository-images.githubusercontent.com/1385164626/c451f484-88a4-4d0b-9806-b493c2dc53e4" width="640" alt="PopNote!"></a>

**種類:** Python　**対応 OS:** macOS · Windows　**最新版:** [v0.3.0](https://github.com/kobito-tools/PopNote/tree/v0.3.0)
<!-- TOOLS:END -->

---

<sub>「アプリ一覧」は、GitHub Actions が、`kobito-app.json` を持つ公開リポジトリの紹介のカード（`kobito-app.json`・`kobito/` のアイコン・`assets/social-preview.ja.png`）から自動で作っています。</sub>
