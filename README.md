# Origin Twitter Neo

![GitHub Downloads](https://img.shields.io/github/downloads/YuzuMikan404/Origin-Twitter-Neo/total?color=green&style=for-the-badge&logo=github)
![GitHub Issues](https://img.shields.io/github/stars/YuzuMikan404/Origin-Twitter-Neo?style=for-the-badge&logo=github)

## 概要
<!-- **Origin Twitter Neo**は、[monefiera](https://github.com/monefiera)さんの[Origin-Twitter](https://github.com/monefiera/Origin-Twitter)をベースに、参照元を更新して自動ビルドするようにした自分用ビルドリポジトリです。-->
参照元であったcrimeraさんのAPK更新が停止しているため、独自に参照元を[piko/twitter-apk](https://github.com/crimera/twitter-apk/releases)から[monsivamon/twitter-apk](https://github.com/monsivamon/twitter-apk/releases)にに変更してビルドしています。
**自己責任**にてご使用ください。

## 📢 アナウンス
- **ログイン不具合の解決策 (2026/01/05更新)**
  元パッチの影響でログインできない不具合がありましたが、応急的な解決策が判明しました。[こちらの手順](https://github.com/crimera/piko/issues/714#issuecomment-3706542446)を実施することでログインができるようになるかもしれません。私の環境ではこの方法でログインできました。
- **署名の変更について (2025/12/27更新)**
  署名がされていない不具合を修正しました。これに伴い署名キーが変更されたため、以前のバージョンからは上書きアップデートができない場合があります。その際は一度アンインストールしてから再インストールしてください。それに伴い、これ以前のリリースは削除しています。これ以降、署名は変更しません。
- **Blueskyでのご紹介について**
  monefieraさんがご自身のBlueskyでこのリポジトリを紹介してくださっていました。勝手にフォークして作成したにも関わらず、ありがとうございます！🙇🏻
  [該当ポストはこちら](https://bsky.app/profile/forsaken-love02.bsky.social/post/3m7nixn7t4k2a)

## 📥 ダウンロード
[Obtainium](https://github.com/ImranR98/Obtainium)を使用して、更新を自動で追跡・インストールすることをお勧めします。

[<img src="badge_obtainium.png" alt="Get it on Obtainium" height="45">](https://apps.obtainium.imranr.dev/redirect?r=obtainium://app/%7B%22id%22%3A%22com.twitter.android%22%2C%22url%22%3A%22https%3A%2F%2Fgithub.com%2FYuzuMikan404%2FOrigin-Twitter-Neo%22%2C%22author%22%3A%22YuzuMikan404%22%2C%22name%22%3A%22Twitter%22%2C%22preferredApkIndex%22%3A9%2C%22additionalSettings%22%3A%22%7B%5C%22includePrereleases%5C%22%3Afalse%2C%5C%22fallbackToOlderReleases%5C%22%3Atrue%2C%5C%22filterReleaseTitlesByRegEx%5C%22%3A%5C%22%5C%22%2C%5C%22filterReleaseNotesByRegEx%5C%22%3A%5C%22%5C%22%2C%5C%22verifyLatestTag%5C%22%3Afalse%2C%5C%22sortMethodChoice%5C%22%3A%5C%22date%5C%22%2C%5C%22useLatestAssetDateAsReleaseDate%5C%22%3Afalse%2C%5C%22releaseTitleAsVersion%5C%22%3Afalse%2C%5C%22trackOnly%5C%22%3Afalse%2C%5C%22versionExtractionRegEx%5C%22%3A%5C%22%5C%22%2C%5C%22matchGroupToUse%5C%22%3A%5C%22%5C%22%2C%5C%22versionDetection%5C%22%3Afalse%2C%5C%22releaseDateAsVersion%5C%22%3Afalse%2C%5C%22useVersionCodeAsOSVersion%5C%22%3Afalse%2C%5C%22apkFilterRegEx%5C%22%3A%5C%22%5C%22%2C%5C%22invertAPKFilter%5C%22%3Afalse%2C%5C%22autoApkFilterByArch%5C%22%3Atrue%2C%5C%22appName%5C%22%3A%5C%22%5C%22%2C%5C%22appAuthor%5C%22%3A%5C%22%5C%22%2C%5C%22shizukuPretendToBeGooglePlay%5C%22%3Afalse%2C%5C%22allowInsecure%5C%22%3Afalse%2C%5C%22exemptFromBackgroundUpdates%5C%22%3Afalse%2C%5C%22skipUpdateNotifications%5C%22%3Afalse%2C%5C%22about%5C%22%3A%5C%22%5C%22%2C%5C%22refreshBeforeDownload%5C%22%3Afalse%2C%5C%22includeZips%5C%22%3Afalse%2C%5C%22zippedApkFilterRegEx%5C%22%3A%5C%22%5C%22%7D%22%2C%22overrideSource%22%3Anull%7D)

または [リリース](https://github.com/YuzuMikan404/Origin-Twitter-Ne/releases) ページから直接APKをダウンロードしてください。

## 🎨 カラーバリエーション
お好みに合わせて、以下の10色から選べます。
※すべての署名は共通化されているため、アプリを再インストールすることで色のみを変更可能です。

### ① Twitter Web準拠カラー
| 色名 | カラーコード | 備考 |
| :--- | :--- | :--- |
| 💧 **Origin Blue** | `#1d9bf0` | オリジナルに近いですが微調整されています |
| ⭐ **Star Gold** | `#fed400` | |
| 🌸 **Sakura Red** | `#f91880` | |
| 🐙 **Octopus Purple** | `#7856ff` | |
| 🔥 **Flare Orange** | `#ff7a00` | |
| 🥑 **Avocado Green** | `#31c88e` | |

### ② FIERAのオリジナルカラー
| 色名 | カラーコード | 備考 |
| :--- | :--- | :--- |
| 🌹 **Crimsonate** | `#c20024` | 眼に広がる深紅の彩 |
| 💎 **Izumo Lazurite** | `#1e50a2` | 落ち着いた瑠璃色 |
| ☁ **Monotone** | `#808080` | グレー基調 |
| 🩷 **MateChan Pink** | `#ffadc0` | [あるユーザー](https://matechan.com/)用の淡いピンク |

## 💐 クレジット
- **[crimera](https://github.com/crimera)**: Base Mod (Piko) Developer
- **[monefiera](https://github.com/monefiera)**: Original "Origin Twitter" Developer
- **[kitadai31](https://github.com/kitadai31)**: Language patch implementation
- **[Risa Yuzuki](https://yuzu-risa.com)**: Crimsonate name holder
- **[Twitter Inc.](https://twitter.com)**: Original App Developer

Based on [Piko Patches](https://github.com/crimera/piko)
