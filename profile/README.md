# kobito-tools

毎日の作業を、ちょっとだけ楽にする小さな道具たち。

kobito-tools は、小人（kobito）のように手を貸してくれる、デスクトップ用の小さなアプリのシリーズです。

## 考え方

- **どのアプリも単体で使えます。** ほしいアプリだけを入れて、ふつうのアプリとして開けます。
- **[kobito-workspace](https://github.com/kobito-tools/kobito-workspace) に並べると、1つのウインドウで使えます。** 入れたアプリが workspace に並び、切り替えながら使えて、横断検索もできます。
- **どのアプリも、同じ形のリポジトリです。** 直下に名乗り `kobito-app.json` を、`kobito/` にアイコンと画像を、決まった名前で置きます。GitHub の topic `kobito-app` を付けると、workspace と下の一覧に、同じ紹介のカードで並びます。決まりは kobito-workspace の [APP_PACKAGE.md](https://github.com/kobito-tools/kobito-workspace/blob/main/kobito_workspace/kit/docs/APP_PACKAGE.md) にあります。

## 入れ方

シリーズをまとめて入れるときは、ターミナルで次を動かします。一覧から入れたいアプリを選べます。

```bash
zsh -c "$(curl -fsSL https://raw.githubusercontent.com/kobito-tools/kobito-workspace/main/install.sh)"
```

アプリを1つずつ入れるときは、各アプリの README を見てください。CorkClip・OpenSesame! などのネイティブのアプリは、[Homebrew](https://github.com/kobito-tools/homebrew-tap) でも入れられます。

## アプリ一覧

<!-- TOOLS:START -->
<!-- 今は、手元のフォルダの kobito-app.json から作った仮の一覧です（画像なし）。topic を付けて scripts/update_profile.py を動かすと、GitHub から作った一覧（アイコン・画像つき）に置き換わります。 -->
### [kobito-workspace](https://github.com/kobito-tools/kobito-workspace)

シリーズのアプリを1つの窓に並べる

**種類:** Python　**対応 OS:** macOS　**最新版:** 0.1.0

### [CorkClip](https://github.com/kobito-tools/CorkClip)

コピーした物をピンで留めるように取っておく、クリップボード履歴

**種類:** ネイティブ　**対応 OS:** macOS　**最新版:** [v0.1.0](https://github.com/kobito-tools/CorkClip/tree/v0.1.0)

### [Daycierge](https://github.com/kobito-tools/Daycierge)

今日の予定とやることを、ひと目で

**種類:** Python　**対応 OS:** macOS · Windows　**最新版:** 0.1.0

### [Filepantry](https://github.com/kobito-tools/Filepantry)

ファイルを見て、しまって、届いたら振り分ける

**種類:** Python　**対応 OS:** macOS · Windows　**最新版:** 0.1.0

### [GitTrain](https://github.com/kobito-tools/GitTrain)

Git の履歴を、線路と電車で見る

**種類:** Python　**対応 OS:** macOS　**最新版:** 0.1.0

### [OpenSesame!](https://github.com/kobito-tools/OpenSesame)

キーを押している間だけ出るランチャー

**種類:** ネイティブ　**対応 OS:** macOS · Windows　**最新版:** [v0.1.4](https://github.com/kobito-tools/OpenSesame/tree/v0.1.4)

### [PopNote!](https://github.com/kobito-tools/PopNote)

ポンッと開いて、すぐ書けるメモと日記

**種類:** Python　**対応 OS:** macOS · Windows　**最新版:** [v0.2.1](https://github.com/kobito-tools/PopNote/tree/v0.2.1)

### [PyMaison](https://github.com/kobito-tools/PyMaison)

uv のコマンドを、マンションの絵で学ぶ

**種類:** Python　**対応 OS:** macOS · Windows · Linux　**最新版:** 0.3.0

### [ScreenDresser](https://github.com/kobito-tools/ScreenDresser)

仕事・会議・発表に合わせて、画面をワンクリックで着替える

**種類:** Python　**対応 OS:** macOS　**最新版:** 0.1.0
<!-- TOOLS:END -->

以前の Pastephant を使っていた方は、CorkClip の README の「[Pastephant から乗り換える場合](https://github.com/kobito-tools/CorkClip#pastephant-から乗り換える場合)」を見てください。

---

<sub>「アプリ一覧」は、GitHub Actions が、topic `kobito-app` の付いたリポジトリの紹介のカード（`kobito-app.json` と `kobito/` の画像）から自動で作っています。</sub>
