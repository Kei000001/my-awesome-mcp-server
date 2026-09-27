# My Awesome MCP Server

電卓・SQLiteデータベース分析・天気/ニュース/IP情報の取得・Web検索とPython実行を、Claude Desktop などの AI から使えるようにする MCP サーバー集です。

> **想定環境：Linux（Ubuntu 22.04 で動作確認）**
> Windows / macOS でも動く可能性はありますが、パスの書き方などが異なります。このREADMEのコマンドとパスはすべて Linux 用です。

---

## 目次

1. [できること](#できること)
2. [必要な環境](#必要な環境)
3. [インストール方法](#インストール方法)
4. [Claude Desktop の設定](#claude-desktop-の設定)
5. [利用可能なツール](#利用可能なツール)
6. [動作確認とトラブルシューティング](#動作確認とトラブルシューティング)
7. [フォルダ構成](#フォルダ構成)
8. [セキュリティの注意](#セキュリティの注意)
9. [貢献方法](#貢献方法)
10. [ライセンス](#ライセンス)

---

## できること

Claude Desktop に次のように話しかけると、AI がこのリポジトリのツールを選んで実行します。

| 話しかける例 | 使われるサーバー |
|---|---|
| 「12×34 は？」 | `calculator` |
| 「在庫が5個以下の商品をカテゴリ別に教えて」 | `database` |
| 「東京の天気は？」「AI のニュースを教えて」 | `external_api` |
| 「Python について検索して」「フィボナッチ数列を20個計算して」 | `universal-tools` |

---

## 必要な環境

| ソフトウェア | バージョン | 用途 | 確認コマンド |
|---|---|---|---|
| Linux（Ubuntu 22.04 推奨） | — | 動作環境 | `lsb_release -a` |
| Python | 3.13 以上 | サーバーの実行 | `python3 --version` |
| [uv](https://docs.astral.sh/uv/) | 最新版 | Python の環境とライブラリの管理 | `uv --version` |
| Node.js | 18 以上 | MCP Inspector（動作確認用） | `node -v` |
| Git | — | リポジトリのクローン | `git --version` |
| Claude Desktop | 最新版 | MCP サーバーを使う AI アプリ | — |

`uv` が入っていない場合は、次のコマンドでインストールできます。

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### API キー（使うツールに応じて）

| キー | 使うツール | 取得先 | 必須か |
|---|---|---|---|
| `OPENWEATHER_API_KEY` | 天気 | [OpenWeatherMap](https://openweathermap.org/api) | 天気を使う場合 |
| `NEWS_API_KEY` | ニュース | [NewsAPI](https://newsapi.org/) | ニュースを使う場合 |
| `TAVILY_API_KEY` | Web 検索 | [Tavily](https://tavily.com/) | Web 検索を使う場合 |
| `OPENAI_API_KEY` | `chapter09` / `chapter10` の自作クライアント | [OpenAI Platform](https://platform.openai.com/api-keys) | クライアントを使う場合 |

電卓・データベース・IP 情報・Python 実行は、API キーなしで使えます。

---

## インストール方法

> **クローンせずに使いたい場合**：`uvx` を使えば、GitHub の URL を指定するだけで起動できます。
> ```bash
> uvx --from git+https://github.com/yourname/my-awesome-mcp-server my-awesome-mcp-server
> ```
> 詳しい手順は [Windows 版](docs/uvx-windows.md) ／ [Linux・venv ＋ GitHub Copilot 版](docs/uvx-linux-copilot.md) を参照してください。
> 以下は、リポジトリをクローンして使う手順です。

### 1. リポジトリをクローンする

```bash
cd ~
git clone https://github.com/yourname/my-awesome-mcp-server.git
cd my-awesome-mcp-server
```

`yourname` は、自分の GitHub のユーザー名に置き換えてください。

### 2. ライブラリをインストールする

```bash
uv sync
```

`.venv` フォルダが作られ、必要なライブラリ（`fastmcp`、`requests`、`python-dotenv`、`beautifulsoup4`、`openai`）がまとめて入ります。

### 3. API キーを設定する（必要な場合）

リポジトリの直下に `.env` ファイルを作ります。

```bash
cat > .env <<'EOF'
OPENWEATHER_API_KEY=your_openweather_api_key_here
NEWS_API_KEY=your_news_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
EOF
chmod 600 .env    # 自分だけが読み書きできるようにする
nano .env         # your_..._here を実際のキーに書き換える
```

- `.env` は `.gitignore` で Git の対象外にしてあります。**API キーを GitHub に上げないでください。**
- `.env` は隠しファイルなので、`ls` ではなく `ls -a` で表示されます。

### 4. サーバー単体で起動できるか確認する

```bash
uv run python chapter03/calculator_server.py
```

エラーが出ずに待ち受け状態になれば OK です。`Ctrl + C` で止めます。

---

## Claude Desktop の設定

### 1. 設定ファイルの場所

```
~/.config/Claude/claude_desktop_config.json
```

Claude Desktop の **設定 → 開発者（Developer）→ 構成を編集（Edit Config）** からも開けます。

### 2. `uv` の場所を確認する

Claude Desktop はターミナルと同じ PATH を使わないことがあるので、`uv` はフルパスで書きます。

```bash
which uv    # 例: /home/yourname/.local/bin/uv
```

### 3. 設定を書く

登録のしかたは2通りあります。**どちらか一方**を選んでください。両方を登録すると、同じツールが2つずつ見えて、AI がどちらを使うか迷います。

| 方法 | 登録するサーバーの数 | 向いている場面 |
|---|---|---|
| **A. 統合サーバー（おすすめ）** | 1つ | 全部のツールをまとめて使いたい |
| B. サーバーを個別に登録 | 4つ | 必要なサーバーだけ使いたい、章ごとに動きを確かめたい |

どちらの場合も、**Claude Desktop を完全に終了してから**、`mcpServers` に追加します。`/home/yourname/` の部分は、自分のホームフォルダに置き換えてください。

#### A. 統合サーバーを1つ登録する（おすすめ）

`my-awesome-mcp-server` コマンド（`src/mcp_learning/server.py` の `main()`）が、4つのサーバーを1つにまとめて起動します。

```json
{
  "mcpServers": {
    "my-awesome-mcp-server": {
      "command": "/home/yourname/.local/bin/uv",
      "args": ["--directory", "/home/yourname/my-awesome-mcp-server", "run", "my-awesome-mcp-server"]
    }
  }
}
```

- `--directory` には、章のフォルダではなく、**リポジトリの直下**（`pyproject.toml` がある場所）を指定します。
- ツール名の前に、どのサーバーのツールかを表す名前が付きます（例：`add` → `calculator_add`、`get_weather` → `external_api_get_weather`）。
- 一部のサーバーだけを使いたいときは、`args` の最後に `--only` を付けます。
  ```json
  "args": ["--directory", "/home/yourname/my-awesome-mcp-server", "run", "my-awesome-mcp-server", "--only", "calculator", "database"]
  ```
- 登録する前に、ターミナルで起動できるか確認しておくと安心です。
  ```bash
  cd ~/my-awesome-mcp-server
  uv run my-awesome-mcp-server --help    # 使い方が表示されれば OK
  ```

#### B. サーバーを個別に登録する

```json
{
  "mcpServers": {
    "calculator": {
      "command": "/home/yourname/.local/bin/uv",
      "args": ["--directory", "/home/yourname/my-awesome-mcp-server/chapter03", "run", "calculator_server.py"]
    },
    "database": {
      "command": "/home/yourname/.local/bin/uv",
      "args": ["--directory", "/home/yourname/my-awesome-mcp-server/chapter06", "run", "database_server_prompt.py"]
    },
    "external_api": {
      "command": "/home/yourname/.local/bin/uv",
      "args": ["--directory", "/home/yourname/my-awesome-mcp-server/chapter07", "run", "external_api_server.py"]
    },
    "universal-tools": {
      "command": "/home/yourname/.local/bin/uv",
      "args": ["--directory", "/home/yourname/my-awesome-mcp-server/chapter08", "run", "universal_tools_server.py"]
    }
  }
}
```

**書くときの注意**

- パスに `~` は使えません。`/home/yourname/...` のように、最初から書いてください。
- Windows 用のパス（`C:\...`）は Linux では動きません。
- すでに `mcpServers` に別のサーバーがある場合は、`{ }` の中に**追加**してください（上書きしない）。
- 書き換える前に、バックアップを取っておくと安心です。
  ```bash
  cp ~/.config/Claude/claude_desktop_config.json ~/.config/Claude/claude_desktop_config.json.bak
  ```

### 4. 起動して確認する

1. Claude Desktop を起動します。
2. **設定 → 開発者** で、登録したサーバーが **running** になっているか確認します（A なら1つ、B なら4つ）。
3. チャットで「12×34 は？」と聞いて、掛け算のツール（A なら `calculator_multiply`、B なら `multiply`）が使われれば成功です。

---

## 利用可能なツール

以下は、サーバーを個別に登録したとき（方法 B）の名前です。統合サーバー（方法 A）では、名前の前に `calculator_`・`database_`・`external_api_`・`universal_` が付きます。

### `calculator`（`chapter03/calculator_server.py`）

| 種類 | 名前 | 引数 | 内容 |
|---|---|---|---|
| ツール | `add` | `a`, `b` | 足し算 |
| ツール | `subtract` | `a`, `b` | 引き算 |
| ツール | `multiply` | `a`, `b` | 掛け算 |
| ツール | `divide` | `a`, `b` | 割り算（0で割るとエラーを返す） |
| ツール | `power` | `a`, `b` | 累乗（a の b 乗） |
| ツール | `square_root` | `a` | 平方根（負の数はエラーを返す） |
| ツール | `circle_area` | `radius` | 円の面積 |
| ツール | `log_demo` | `value` | INFO / WARNING / ERROR のログ送信のテスト用 |
| リソース | `config://calculator/settings` | — | 電卓の設定値（JSON） |
| プロンプト | `financial_analysis` | `period` | 財務データ分析の定型プロンプト |

### `database`（`chapter06/database_server_prompt.py`）

サンプルの SQLite データベース `intelligent_shop.db`（顧客・商品・売上）を、**読み取り専用**で扱います。

| 種類 | 名前 | 引数 | 内容 |
|---|---|---|---|
| ツール | `list_tables` | — | テーブルの一覧と CREATE 文 |
| ツール | `get_table_schema` | `table_name` | 列の情報・外部キー・件数 |
| ツール | `execute_safe_query` | `sql` | SELECT 文だけを実行（INSERT / UPDATE / DELETE などは拒否） |
| プロンプト | `sales_analysis_prompt` | `month`, `focus_category` | 月次の売上分析 |
| プロンプト | `inventory_alert_prompt` | `threshold` | 在庫アラートのレポート |
| プロンプト | `customer_behavior_prompt` | `period`, `segment` | 顧客の購買行動の分析 |

### `external_api`（`chapter07/external_api_server.py`）

| 名前 | 引数 | 内容 | API キー |
|---|---|---|---|
| `get_weather` | `city`, `country_code` | 現在の天気 | `OPENWEATHER_API_KEY` |
| `get_weather_forecast` | `city`, `days`, `country_code` | 天気予報（1〜5日） | `OPENWEATHER_API_KEY` |
| `get_latest_news` | `category`, `country`, `limit` | 最新ニュース | `NEWS_API_KEY` |
| `search_news` | `query`, `language`, `limit` | キーワードでニュース検索 | `NEWS_API_KEY` |
| `get_ip_info` | `ip_address` | IP アドレスの位置情報（省略すると自分の IP） | 不要 |

### `universal-tools`（`chapter08/universal_tools_server.py`）

| 名前 | 引数 | 内容 | API キー |
|---|---|---|---|
| `web_search` | `query`, `num_results` | Web 検索（Tavily） | `TAVILY_API_KEY` |
| `get_webpage_content` | `url` | Web ページの本文をテキストで取得 | 不要 |
| `execute_python` | `code` | 安全チェック付きで Python を実行（危険なコードを拒否） | 不要 |
| `execute_python_basic` | `code` | 基本版の Python 実行（5秒で打ち切り） | 不要 |

---

## 動作確認とトラブルシューティング

### MCP Inspector で確認する

Claude Desktop を使わずに、ブラウザでツールを試せます。

```bash
cd ~/my-awesome-mcp-server/chapter03
npx @modelcontextprotocol/inspector uv run calculator_server.py
```

表示された URL をブラウザで開き、**Connect** → **Tools** タブでツールを実行できます。

### よくあるエラー

| 症状 | 原因と対処 |
|---|---|
| Claude Desktop でサーバーが `failed` になる | 設定のパスを確認。ログは `~/.config/Claude/logs/mcp-server-<名前>.log` |
| `No such file or directory` | パスの誤り、または Windows のパス（`C:\...`）が残っている |
| `ModuleNotFoundError: No module named 'bs4'` など | `uv sync` をもう一度実行 |
| 天気・ニュース・検索が認証エラーになる | `.env` のキーを確認（`your_..._here` のままになっていないか） |
| 自作クライアントで `ping` が `Method not found` | FastMCP 4 と `mcp` 2.x の組み合わせでは `ping()` が使えない。`list_tools()` で代用 |
| `.env` が見つからない | `.env` はリポジトリの直下に置く。`ls -a` で存在を確認 |
| 統合サーバーで一部のツールが出ない | stderr に `[エラー] <サーバー名>` と出ていないか確認（Claude Desktop なら `~/.config/Claude/logs/mcp-server-my-awesome-mcp-server.log`）。1つのサーバーが失敗しても、ほかのサーバーは使える |
| 同じツールが2つずつ見える | 統合サーバー（A）と個別のサーバー（B）を両方登録している。どちらか一方だけにする |

---

## フォルダ構成

```
my-awesome-mcp-server/
├── chapter01/   # MCP の基本（ファイル操作の練習用ファイル）
├── chapter03/   # 電卓サーバー（calculator_server.py）、HTTP 版の起動例
├── chapter05/   # HTTP トランスポートの例
├── chapter06/   # データベースサーバー（database_server_prompt.py）とサンプル DB
├── chapter07/   # 外部 API サーバー（天気・ニュース・IP 情報）
├── chapter08/   # 汎用ツールサーバー（Web 検索・Python 実行）
├── chapter09/   # 自作の MCP クライアント（CLI・対話型・OpenAI 連携）
├── chapter10/   # MCP エージェント（専用の pyproject.toml あり）
├── docs/        # uvx での直接実行の手順（Windows 版・Linux＋Copilot 版）
├── src/
│   └── mcp_learning/
│       ├── server.py   # 統合サーバー（my-awesome-mcp-server コマンドの本体）
│       └── servers/    # 統合サーバーに組み込む4つのサーバー（各章の完成版のコピー）と DB
├── pyproject.toml
├── uv.lock
├── LICENSE
└── README.md
```

各章には、途中段階のファイル（`_step1`、`_web_1` など）も含まれています。Claude Desktop には、上の設定にある完成版を登録してください。

---

## セキュリティの注意

- **API キー**：`.env` に保存し、GitHub や画面共有、チャットに貼らないでください。漏れた場合は、各サービスでキーを削除して作り直してください。
- **Python 実行ツール**：`execute_python` と `execute_python_basic` は、AI が書いたコードを**あなたの PC 上で**実行します。Claude Desktop から実行の許可を求められたら、コードの内容を確認してから許可してください。
- **会社の PC での利用**：ツールの実行結果（DB の中身、ファイルの内容など）は、AI の提供元に送られます。業務の PC やデータで使う前に、社内の規程を確認してください。

---

## 貢献方法

バグの報告、改善の提案、プルリクエストを歓迎します。

### バグの報告・提案

[Issues](https://github.com/yourname/my-awesome-mcp-server/issues) に、次の情報を書いてください。

- OS とバージョン（例：Ubuntu 22.04）
- Python・uv・FastMCP のバージョン（`uv pip list | grep -i fastmcp`）
- 実行したコマンドと、エラーメッセージの全文
- 期待した動きと、実際の動き

### プルリクエストの手順

1. このリポジトリを **Fork** します。
2. 自分の Fork をクローンし、作業用のブランチを作ります。
   ```bash
   git clone https://github.com/yourname/my-awesome-mcp-server.git
   cd my-awesome-mcp-server
   git checkout -b feature/add-new-tool
   ```
3. 変更して、動作を確認します（MCP Inspector での確認を推奨）。
4. コミットして、Fork にプッシュします。
   ```bash
   git add .
   git commit -m "Add: 新しいツール xxx を追加"
   git push origin feature/add-new-tool
   ```
5. GitHub で **Pull Request** を作成し、変更内容と確認方法を書いてください。

### お願い

- `.env` や API キーをコミットに含めないでください。
- ツールを追加したら、このREADMEの「利用可能なツール」も更新してください。
- ツールの docstring（説明文）は、AI がツールを選ぶ手がかりになるので、具体的に書いてください。
- stdio で動くサーバーでは、`print()` は `file=sys.stderr` にしてください（stdout は MCP の通信に使われます）。

---

## ライセンス

このプロジェクトは **MIT License** のもとで公開しています。全文は [LICENSE](LICENSE) を参照してください。
