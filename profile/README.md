# kobito-tools

毎日の作業を、ちょっとだけ楽にする小さな道具たち。

kobito-tools は、小人（kobito）のように手を貸してくれる、デスクトップ用の小さなアプリのシリーズです。

## 考え方

- **どのアプリも単体で使えます。** ほしいアプリだけを入れて、ふつうのアプリとして開けます。
- **[kobito-workspace](https://github.com/kobito-tools/kobito-workspace) に並べると、1つのウインドウで使えます。** 入れたアプリが workspace に並び、切り替えながら使えて、横断検索もできます。
- **アプリは、決まりを守れば誰でも足せます。** リポジトリの直下に目印 `kobito-app.json` を置き、GitHub の topic `kobito-app` を付けると、workspace と下の一覧に並びます。決まりは kobito-workspace の [docs/APP_PACKAGE.md](https://github.com/kobito-tools/kobito-workspace/blob/main/docs/APP_PACKAGE.md) にあります。

## 入れ方

シリーズをまとめて入れるときは、ターミナルで次を動かします。一覧から入れたいアプリを選べます。

```bash
zsh -c "$(curl -fsSL https://raw.githubusercontent.com/kobito-tools/kobito-workspace/main/install.sh)"
```

アプリを1つずつ入れるときは、各アプリの README を見てください。CorkClip・OpenSesame! などのネイティブのアプリは、[Homebrew](https://github.com/kobito-tools/homebrew-tap) でも入れられます。

## アプリ一覧

<!-- TOOLS:START -->
<!-- 今は、手元のフォルダの kobito-app.json から作った一覧です（画像なし）。scripts/update_profile.py を動かすと、GitHub から作った一覧に置き換わります。 -->
### [kobito-workspace](https://github.com/kobito-tools/kobito-workspace)

各アプリを並べる枠、HOME、横断検索

**種類:** Python　**対応 OS:** macOS　**最新版:** —

### [CorkClip](https://github.com/kobito-tools/CorkClip)

コピーした物をピンで留めるように取っておく、クリップボード履歴

**種類:** ネイティブ　**対応 OS:** macOS　**最新版:** [v0.1.0](https://github.com/kobito-tools/CorkClip/tree/v0.1.0)

### [Daycierge](https://github.com/kobito-tools/Daycierge)

予定・Todo・時間割・作業の記録・タイマーを1つにまとめたアプリ

**種類:** Python　**対応 OS:** macOS · Windows　**最新版:** —

### [Filepantry](https://github.com/kobito-tools/Filepantry)

ディスク全体のファイラーに、書籍・文書の管理とダウンロードの振り分けを組み合わせたアプリ

**種類:** Python　**対応 OS:** macOS · Windows　**最新版:** —

### [GitTrain](https://github.com/kobito-tools/GitTrain)

Git の履歴を、マス目の地面に敷いた線路と電車で見せる Git の GUI

**種類:** Python　**対応 OS:** macOS　**最新版:** —

### [OpenSesame!](https://github.com/kobito-tools/OpenSesame)

キーを押している間だけ出るランチャー

**種類:** ネイティブ　**対応 OS:** macOS · Windows　**最新版:** [v0.1.4](https://github.com/kobito-tools/OpenSesame/tree/v0.1.4)

### [PopNote!](https://github.com/kobito-tools/PopNote)

押したらすぐ書けるメモと日記

**種類:** Python　**対応 OS:** macOS · Windows　**最新版:** [v0.2.1](https://github.com/kobito-tools/PopNote/tree/v0.2.1)

### [PyMaison](https://github.com/kobito-tools/PyMaison)

uv のコマンドを、マンションのイラストで学ぶ GUI

**種類:** Python　**対応 OS:** macOS · Windows · Linux　**最新版:** —

### [ScreenDresser](https://github.com/kobito-tools/ScreenDresser)

作業・ミーティング・発表などのモードを1クリックで切り替える、画面の着せ替え係

**種類:** Python　**対応 OS:** macOS　**最新版:** —
<!-- TOOLS:END -->

以前の Pastephant を使っていた方は、CorkClip の README の「[Pastephant から乗り換える場合](https://github.com/kobito-tools/CorkClip#pastephant-から乗り換える場合)」を見てください。

---

<sub>「アプリ一覧」は、GitHub Actions が、topic `kobito-app` の付いたリポジトリの `kobito-app.json` から自動で作っています。</sub>
