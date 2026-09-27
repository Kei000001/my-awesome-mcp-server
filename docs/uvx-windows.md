# uvx で直接実行する（Windows 版）

GitHub の URL を指定するだけで、リポジトリをクローンせずに **My Awesome MCP Server** を Claude Desktop から使う手順です。

```
uvx --from git+https://github.com/Kei000001/my-awesome-mcp-server my-awesome-mcp-server
```

この1行で、uvx が GitHub からコードを取得し、必要なライブラリと Python を用意して、MCP サーバーを起動します。

> 対象：Windows 10 / 11、PowerShell、Claude Desktop（Windows 版）

---

## 目次

1. [仕組み](#1-仕組み)
2. [必要なもの](#2-必要なもの)
3. [準備：uv と Git をインストールする](#3-準備uv-と-git-をインストールする)
4. [ターミナルで起動を確認する](#4-ターミナルで起動を確認する)
5. [Claude Desktop に登録する](#5-claude-desktop-に登録する)
6. [API キーの渡し方](#6-api-キーの渡し方)
7. [更新・バージョンの固定](#7-更新バージョンの固定)
8. [トラブルシューティング](#8-トラブルシューティング)
9. [Windows での注意](#9-windows-での注意)

---

## 1. 仕組み

```
Claude Desktop
   │ 起動: uvx --from git+https://github.com/... my-awesome-mcp-server
   ▼
uvx
   ├─ GitHub からコードを取得（Git を使用）
   ├─ Python 3.13 と依存ライブラリを、専用の一時環境に用意（キャッシュされる）
   └─ my-awesome-mcp-server コマンドを実行
         ▼
   統合 MCP サーバー（calculator / database / external_api / universal の20ツール）
```

- 自分でクローンや `pip install` をする必要はありません。
- 2回目からはキャッシュが使われるので、すぐに起動します。
- PC の Python の環境は汚れません（uvx 専用の環境が使われます）。

---

## 2. 必要なもの

| もの | 確認コマンド（PowerShell） | 備考 |
|---|---|---|
| uv（uvx が付属） | `uvx --version` | 下の手順で入れる |
| Git for Windows | `git --version` | `git+https://` の取得に必要 |
| Claude Desktop | — | 最新版 |
| インターネット接続 | — | 初回の取得時に必要 |

Python を自分で入れる必要はありません。uvx が、必要なバージョン（3.13 以上）を自動で用意します。

---

## 3. 準備：uv と Git をインストールする

PowerShell を開いて実行します。

```powershell
# uv（uvx も一緒に入る）
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Git（入っていない場合）
winget install --id Git.Git -e
```

インストールが終わったら、**PowerShell を開き直して**確認します。

```powershell
uvx --version
git --version
(Get-Command uvx).Source    # uvx の場所。後で Claude Desktop の設定に使う
```

`(Get-Command uvx).Source` の結果は、通常 `C:\Users\<ユーザー名>\.local\bin\uvx.exe` です。メモしておいてください。

---

## 4. ターミナルで起動を確認する

Claude Desktop に登録する前に、PowerShell で一度起動しておきます。**初回はダウンロードとインストールに時間がかかる**ので、先に済ませておくと、Claude Desktop からの初回起動がタイムアウトしにくくなります。

```powershell
uvx --from git+https://github.com/Kei000001/my-awesome-mcp-server my-awesome-mcp-server --help
```

「4つのMCPサーバーを1つにまとめて起動します」と表示されれば準備完了です。

---

## 5. Claude Desktop に登録する

### 設定ファイルの場所

```
%APPDATA%\Claude\claude_desktop_config.json
```

Claude Desktop の **設定 → 開発者 → 構成を編集** からも開けます。エクスプローラーのアドレス欄に `%APPDATA%\Claude` と入力しても開けます。

### 設定を書く

**Claude Desktop を完全に終了してから**（タスクトレイのアイコンも「終了」）、`mcpServers` に追加します。

```json
{
  "mcpServers": {
    "my-awesome-mcp-server": {
      "command": "C:\\Users\\<ユーザー名>\\.local\\bin\\uvx.exe",
      "args": [
        "--from",
        "git+https://github.com/Kei000001/my-awesome-mcp-server",
        "my-awesome-mcp-server"
      ],
      "env": {
        "OPENWEATHER_API_KEY": "ここにキー",
        "NEWS_API_KEY": "ここにキー",
        "TAVILY_API_KEY": "ここにキー"
      }
    }
  }
}
```

**書くときの注意**

- `<ユーザー名>` は、手順3でメモした uvx の場所に合わせてください。
- JSON の中では、`\` を **`\\`（2つ）** と書きます。
- `command` を単に `"uvx"` と書いても動くことがありますが、Claude Desktop からは PATH が見えないことがあるので、フルパスをおすすめします。
- 使わない API のキーの行は、消して構いません（電卓・DB・IP 情報・Python 実行はキーなしで使えます）。
- すでに `mcpServers` にほかのサーバーがある場合は、`{ }` の中に**追加**してください。

### 起動して確認する

1. Claude Desktop を起動します。
2. **設定 → 開発者**で `my-awesome-mcp-server` が **running** になっているか確認します。
3. チャットで「12×34 は？」と聞き、`calculator_multiply` が使われれば成功です。

一部のサーバーだけを使いたいときは、`args` の最後に `"--only", "calculator", "database"` のように足します。

---

## 6. API キーの渡し方

| 方法 | 書き方 | 向いている場面 |
|---|---|---|
| **設定の `env` に書く（おすすめ）** | 上の例のとおり | Claude Desktop から使う |
| Windows の環境変数に登録 | `setx TAVILY_API_KEY "キー"`（登録後は Claude Desktop を再起動） | 複数のアプリで同じキーを使う |
| 起動したフォルダの `.env` | ターミナルで起動するときだけ有効 | ターミナルで試す |

- `env` に書いたキーは、`claude_desktop_config.json` に**平文で保存**されます。このファイルを人に送ったり、画面共有で見せたりしないでください。
- Claude Desktop から起動するとき、「どのフォルダで起動されるか」は決まっていないので、`.env` ファイルには頼らない方が確実です。

---

## 7. 更新・バージョンの固定

uvx はキャッシュを使うので、GitHub を更新しても、**自動では新しい版になりません**。

```powershell
# 最新版を取り直す（そのあと Claude Desktop を再起動）
uvx --refresh --from git+https://github.com/Kei000001/my-awesome-mcp-server my-awesome-mcp-server --help
```

動作が変わると困る場合は、**特定の版に固定**できます。`args` の URL の後ろに `@` を付けます。

```text
"git+https://github.com/Kei000001/my-awesome-mcp-server@main"      // ブランチ
"git+https://github.com/Kei000001/my-awesome-mcp-server@v0.1.0"    // タグ（作成した場合）
"git+https://github.com/Kei000001/my-awesome-mcp-server@a5077d5"   // コミット
```

---

## 8. トラブルシューティング

**ログの場所**：`%APPDATA%\Claude\logs\mcp-server-my-awesome-mcp-server.log`

| 症状 | 原因と対処 |
|---|---|
| `failed` になる・初回だけ失敗する | 初回のダウンロードでタイムアウトした。手順4を PowerShell で実行してから、Claude Desktop を再起動 |
| `'uvx' is not recognized` / `spawn uvx ENOENT` | uvx が見つからない。`command` を uvx.exe のフルパスにする |
| `git` に関するエラー | Git for Windows が入っていない。`winget install --id Git.Git -e` |
| JSON のエラーで Claude Desktop が起動しない | `\` を `\\` にしていない、カンマの過不足など |
| 天気・ニュース・検索が認証エラー | `env` のキーが間違っている、または書いていない |
| ログに `[エラー] <サーバー名>` | そのサーバーだけ読み込みに失敗（ほかは使える）。メッセージを確認 |
| 社内ネットワークでダウンロードできない | プロキシが必要な場合がある。環境変数 `HTTPS_PROXY` の設定を情報システム部門に確認 |

---

## 9. Windows での注意

- **Python 実行ツール（`universal_execute_python`）**：CPU 時間やメモリの上限を設定する仕組み（`resource`）は Linux 専用のため、**Windows では上限なしで動きます**（危険なコードを拒否するチェックは動きます）。AI が書いたコードを実行する前に、Claude Desktop の確認画面で中身を見てください。
- **会社の PC**：ツールの実行結果（DB の中身など）は AI の提供元に送られます。業務の PC で使う前に、社内の規程を確認してください。

---

参考：[README](../README.md) ／ [Linux・Copilot 版](uvx-linux-copilot.md)
