# uvx で直接実行する（Linux・venv 環境 ＋ GitHub Copilot 版）

GitHub の URL を指定するだけで、リポジトリをクローンせずに **My Awesome MCP Server** を VS Code の GitHub Copilot（エージェントモード）から使う手順です。

```bash
uvx --from git+https://github.com/Kei000001/my-awesome-mcp-server my-awesome-mcp-server
```

> 対象：Linux（Ubuntu 22.04 で確認）、WSL2、そのほか Linux 系の環境
> uv を PC 全体に入れられない環境向けに、**プロジェクトの venv の中に uv を入れて使う方法**も説明します。

---

## 目次

1. [仕組み](#1-仕組み)
2. [必要なもの](#2-必要なもの)
3. [uv を用意する（2通り）](#3-uv-を用意する2通り)
4. [ターミナルで起動を確認する](#4-ターミナルで起動を確認する)
5. [VS Code（GitHub Copilot）に登録する](#5-vs-codegithub-copilotに登録する)
6. [API キーの渡し方](#6-api-キーの渡し方)
7. [Copilot から使う](#7-copilot-から使う)
8. [ほかのクライアントから使う](#8-ほかのクライアントから使う)
9. [更新・バージョンの固定](#9-更新バージョンの固定)
10. [トラブルシューティング](#10-トラブルシューティング)
11. [会社の環境で使うときの注意](#11-会社の環境で使うときの注意)

---

## 1. 仕組み

```
VS Code（GitHub Copilot エージェントモード）
   │ .vscode/mcp.json に従って起動
   │   uvx --from git+https://github.com/... my-awesome-mcp-server
   ▼
uvx
   ├─ GitHub からコードを取得（Git を使用）
   ├─ Python 3.13 と依存ライブラリを専用の環境に用意（キャッシュされる）
   └─ my-awesome-mcp-server を実行（作業フォルダ ＝ VS Code で開いたフォルダ）
         ▼
   統合 MCP サーバー（calculator / database / external_api / universal の20ツール）
```

- サーバーは、**VS Code で開いているフォルダ**を作業フォルダとして起動されます。そのフォルダに `.env` を置けば、API キーが自動で読み込まれます。
- プロジェクト自身の venv（`.venv`）とは別の環境で動くので、プロジェクトのライブラリとぶつかりません。

---

## 2. 必要なもの

| もの | 確認コマンド | 備考 |
|---|---|---|
| uv（uvx が付属） | `uvx --version` | 次の手順で用意 |
| Git | `git --version` | `sudo apt install git` |
| VS Code | `code --version` | |
| GitHub Copilot（Chat） | — | **エージェントモード**を使用 |

Python を自分で入れる必要はありません。uvx が必要なバージョン（3.13 以上）を用意します。

**会社のアカウント（Copilot Business / Enterprise）の場合**：組織の管理者がポリシーで「MCP servers in Copilot」を有効にしていないと、MCP サーバーを使えません。

---

## 3. uv を用意する（2通り）

### 方法A：PC（ユーザー）に入れる（おすすめ）

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc          # または、ターミナルを開き直す
uvx --version
which uvx                 # 例: /home/<ユーザー名>/.local/bin/uvx
```

### 方法B：プロジェクトの venv の中に入れる

インストーラーを実行できない環境や、PC 全体の設定を変えたくない場合の方法です。uv は pip からも入れられます。

```bash
cd ~/work/my-project              # Copilot で開くプロジェクトのフォルダ
python3 -m venv .venv
source .venv/bin/activate
pip install uv
uvx --version
```

uvx は `.venv/bin/uvx` に入ります。VS Code の設定では、このパスを指定します（手順5）。

> venv の中の Python のバージョンは何でも構いません。uvx は、サーバー用に Python 3.13 を別に用意します（初回に自動でダウンロード）。

---

## 4. ターミナルで起動を確認する

VS Code に登録する前に、一度起動しておきます。**初回はダウンロードに時間がかかる**ので、先に済ませておくと、VS Code からの初回起動がタイムアウトしにくくなります。

```bash
uvx --from git+https://github.com/Kei000001/my-awesome-mcp-server my-awesome-mcp-server --help
```

「4つのMCPサーバーを1つにまとめて起動します」と表示されれば準備完了です。

---

## 5. VS Code（GitHub Copilot）に登録する

プロジェクトのフォルダに `.vscode/mcp.json` を作ります。VS Code の MCP 設定は、Claude Desktop とは形式が少し違います（トップのキーが `servers`、`type` の指定がある）。

### 方法A（uvx を PC に入れた場合）

```json
{
  "servers": {
    "my-awesome-mcp-server": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/Kei000001/my-awesome-mcp-server",
        "my-awesome-mcp-server"
      ],
      "envFile": "${workspaceFolder}/.env"
    }
  }
}
```

`uvx` が見つからないと言われる場合は、`command` を `which uvx` の結果（フルパス）にしてください。

### 方法B（venv に uv を入れた場合）

`command` だけを venv の中の uvx に変えます。

```json
{
  "servers": {
    "my-awesome-mcp-server": {
      "type": "stdio",
      "command": "${workspaceFolder}/.venv/bin/uvx",
      "args": [
        "--from",
        "git+https://github.com/Kei000001/my-awesome-mcp-server",
        "my-awesome-mcp-server"
      ],
      "envFile": "${workspaceFolder}/.env"
    }
  }
}
```

### 起動する

1. `mcp.json` を保存すると、ファイルの上に **「Start」** が表示されるので押します。
   コマンドパレット（`Ctrl+Shift+P`）の **「MCP: List Servers」** からも起動・停止できます。
2. Copilot Chat を開き、モードを **Agent（エージェント）** にします。
3. チャット欄のツールのアイコンを押し、`my-awesome-mcp-server` の20個のツールが出ていれば成功です。

一部のサーバーだけ使いたいときは、`args` の最後に `"--only", "calculator", "database"` のように足します。ツールの数が少ないほど、Copilot がツールを選び間違えにくくなります。

---

## 6. API キーの渡し方

| 方法 | 書き方 | 向いている場面 |
|---|---|---|
| **`.env` ＋ `envFile`（おすすめ）** | 下の `.env` を作る | 個人の開発 |
| `inputs`（起動時に入力） | 下の例 | キーをファイルに残したくない |
| シェルの環境変数 | `export TAVILY_API_KEY=...` | ターミナルから試す |

### `.env` を使う

プロジェクトのフォルダ（`.vscode` と同じ階層）に作ります。

```bash
cat > .env <<'EOF'
OPENWEATHER_API_KEY=ここにキー
NEWS_API_KEY=ここにキー
TAVILY_API_KEY=ここにキー
EOF
chmod 600 .env
grep -qx ".env" .gitignore 2>/dev/null || echo ".env" >> .gitignore    # Git に入れない
```

サーバーも、起動したフォルダ（＝VS Code で開いたフォルダ）の `.env` を自分で読み込みます。`envFile` と二重になっても問題ありません。

### `inputs` を使う（キーをファイルに書かない）

VS Code が初回の起動時にキーの入力を求め、安全な場所に保存します。

```json
{
  "inputs": [
    { "type": "promptString", "id": "tavily-key", "description": "Tavily API Key", "password": true }
  ],
  "servers": {
    "my-awesome-mcp-server": {
      "type": "stdio",
      "command": "uvx",
      "args": ["--from", "git+https://github.com/Kei000001/my-awesome-mcp-server", "my-awesome-mcp-server"],
      "env": { "TAVILY_API_KEY": "${input:tavily-key}" }
    }
  }
}
```

`.vscode/mcp.json` はチームで Git に入れて共有しても、キーが含まれないので安全です。

---

## 7. Copilot から使う

エージェントモードで、例えば次のように頼みます。

| 頼み方 | 使われるツール |
|---|---|
| 「12×34 を計算して」 | `calculator_multiply` |
| 「在庫が5個以下の商品をカテゴリ別に」 | `database_execute_safe_query` |
| 「8.8.8.8 の情報を調べて」 | `external_api_get_ip_info` |
| 「MCP の最新情報を検索して」 | `universal_web_search` |
| 「フィボナッチ数列を20個計算して」 | `universal_execute_python` |

ツールを実行する前に、Copilot が確認を求めます。特にコードの実行は、中身を見てから **Continue** を押してください。

---

## 8. ほかのクライアントから使う

同じ uvx のコマンドは、ほかのクライアントでも使えます。

**Claude Desktop（Linux）**：`~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "my-awesome-mcp-server": {
      "command": "/home/<ユーザー名>/.local/bin/uvx",
      "args": ["--from", "git+https://github.com/Kei000001/my-awesome-mcp-server", "my-awesome-mcp-server"],
      "env": { "TAVILY_API_KEY": "ここにキー" }
    }
  }
}
```

**MCP Inspector（動作確認）**

```bash
npx @modelcontextprotocol/inspector uvx --from git+https://github.com/Kei000001/my-awesome-mcp-server my-awesome-mcp-server
```

---

## 9. 更新・バージョンの固定

uvx はキャッシュを使うので、GitHub を更新しても**自動では新しい版になりません**。

```bash
# 最新版を取り直す（そのあと VS Code で「MCP: List Servers」→ Restart）
uvx --refresh --from git+https://github.com/Kei000001/my-awesome-mcp-server my-awesome-mcp-server --help
```

チームで同じ動きにそろえたい場合は、**特定の版に固定**します。`args` の URL の後ろに `@` を付けます。

```text
git+https://github.com/Kei000001/my-awesome-mcp-server@main      # ブランチ
git+https://github.com/Kei000001/my-awesome-mcp-server@v0.1.0    # タグ（作成した場合）
git+https://github.com/Kei000001/my-awesome-mcp-server@a5077d5   # コミット
```

---

## 10. トラブルシューティング

**ログの見方**：コマンドパレット →「**MCP: List Servers**」→ サーバーを選ぶ →「**Show Output**」。サーバーが stderr に出すメッセージ（`[読み込み] calculator` など）もここに出ます。

| 症状 | 原因と対処 |
|---|---|
| 初回の起動だけ失敗する | ダウンロード中にタイムアウト。手順4をターミナルで実行してから Restart |
| `spawn uvx ENOENT` | uvx が見つからない。`command` をフルパス（`which uvx` の結果、または `${workspaceFolder}/.venv/bin/uvx`）に |
| `git` に関するエラー | Git が入っていない。`sudo apt install git` |
| ツールが出てこない | エージェントモードになっているか、ツールのアイコンでサーバーが有効か確認 |
| 会社のアカウントで MCP が使えない | 組織のポリシーで MCP が無効。管理者に確認 |
| 天気・ニュース・検索が認証エラー | `.env` の場所（VS Code で開いたフォルダの直下か）とキーを確認 |
| 出力に `[エラー] <サーバー名>` | そのサーバーだけ読み込みに失敗（ほかは使える）。メッセージを確認 |
| プロキシの内側でダウンロードできない | `export HTTPS_PROXY=http://proxy.example:8080` などを設定（値は情報システム部門に確認）。VS Code から起動する場合は `mcp.json` の `env` にも書く |

---

## 11. 会社の環境で使うときの注意

- **データの送り先**：ツールの実行結果（DB の中身、ファイルの内容、Web ページの本文など）は、Copilot の LLM に送られます。社外秘のデータを扱う前に、社内の規程と、Copilot の利用範囲を確認してください。
- **コードの実行**：`universal_execute_python` は、AI が書いたコードをあなたの PC で実行します（Linux では CPU・メモリの上限と危険なコードのチェックあり）。社内のネットワークやファイル共有にも届く可能性があるので、確認画面でコードを見てから実行してください。
- **使うツールを絞る**：業務では `--only calculator database` のように、必要なサーバーだけを読み込むと安全です。
- **取得元の固定**：GitHub の内容が変わると、次に取り直したときにサーバーの動きも変わります。業務では、コミットやタグで版を固定してください（手順9）。

---

参考：[README](../README.md) ／ [Windows 版](uvx-windows.md) ／ [VS Code MCP 設定リファレンス](https://code.visualstudio.com/docs/agents/reference/mcp-configuration)
