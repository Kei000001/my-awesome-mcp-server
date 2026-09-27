#!/usr/bin/env python3
"""
My Awesome MCP Server - 統合サーバー

4つのMCPサーバーを、FastMCPの mount で1つにまとめて起動する。
Claude Desktop や GitHub Copilot には、このサーバーを1つ登録するだけで全ツールが使える。

  calculator      ← mcp_learning/servers/calculator.py   （chapter03）
  database        ← mcp_learning/servers/database.py     （chapter06）
  external_api    ← mcp_learning/servers/external_api.py （chapter07）
  universal       ← mcp_learning/servers/universal.py    （chapter08）

ツール名には、どのサーバーのツールかが分かるように名前空間が付く。
（例：calculator の add → calculator_add）

使い方:
    uv run my-awesome-mcp-server                                  # リポジトリをクローンした場合
    uvx --from git+https://github.com/Kei000001/my-awesome-mcp-server my-awesome-mcp-server
    my-awesome-mcp-server --transport http --port 8000
    my-awesome-mcp-server --only calculator database
"""

from __future__ import annotations

import argparse
import importlib
import sys

from dotenv import find_dotenv, load_dotenv
from fastmcp import FastMCP

# 名前空間 → パッケージ内のモジュール
SERVERS: dict[str, str] = {
    "calculator": "mcp_learning.servers.calculator",
    "database": "mcp_learning.servers.database",
    "external_api": "mcp_learning.servers.external_api",
    "universal": "mcp_learning.servers.universal",
}


def log(message: str) -> None:
    """stdio通信ではstdoutがMCPの通信路になるので、メッセージはstderrに出す"""
    print(message, file=sys.stderr, flush=True)


def load_env() -> None:
    """APIキーを読み込む。

    1. MCPの設定（env）などで渡された環境変数（最優先。上書きしない）
    2. 起動したフォルダ（またはその上のフォルダ）にある .env
    uvx で起動するとパッケージはキャッシュに置かれるので、
    「起動したフォルダから探す」（usecwd=True）ようにしている。
    """
    path = find_dotenv(usecwd=True)
    if path:
        load_dotenv(path, override=False)
        log(f"[設定] .env を読み込みました: {path}")


def build_server(only: list[str] | None = None) -> FastMCP:
    """各サーバーを読み込み、1つのサーバーにまとめる"""
    main_server = FastMCP("My Awesome MCP Server")

    for namespace, module_name in SERVERS.items():
        if only and namespace not in only:
            continue
        try:
            module = importlib.import_module(module_name)
            main_server.mount(module.mcp, namespace=namespace)
            log(f"[読み込み] {namespace}")
        except Exception as e:  # 1つ失敗しても、ほかのサーバーは使えるようにする
            log(f"[エラー] {namespace}: {type(e).__name__}: {e}")

    return main_server


def main() -> None:
    """コマンド my-awesome-mcp-server の入口"""
    parser = argparse.ArgumentParser(
        prog="my-awesome-mcp-server",
        description="4つのMCPサーバーを1つにまとめて起動します",
    )
    parser.add_argument(
        "--transport", choices=["stdio", "http"], default="stdio",
        help="通信方式（既定: stdio。Claude Desktop や Copilot から使うときは stdio）",
    )
    parser.add_argument("--host", default="127.0.0.1", help="HTTPのときの待ち受けアドレス")
    parser.add_argument("--port", type=int, default=8000, help="HTTPのときのポート番号")
    parser.add_argument(
        "--only", nargs="+", choices=list(SERVERS), metavar="NAME",
        help=f"指定したサーバーだけを読み込む（{', '.join(SERVERS)}）",
    )
    args = parser.parse_args()

    load_env()  # 各サーバーを import する前に読み込む
    server = build_server(args.only)
    log(f"[起動] My Awesome MCP Server（transport={args.transport}）")

    if args.transport == "http":
        server.run(transport="http", host=args.host, port=args.port, show_banner=False)
    else:
        server.run(show_banner=False)


if __name__ == "__main__":
    main()
