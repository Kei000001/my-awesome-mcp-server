#!/usr/bin/env python3
"""
My Awesome MCP Server - 統合サーバー

各章で作った4つのMCPサーバーを、FastMCPの mount で1つにまとめて起動する。
Claude Desktop には、このサーバーを1つ登録するだけで全ツールが使える。

  calculator      ← chapter03/calculator_server.py
  database        ← chapter06/database_server_prompt.py
  external_api    ← chapter07/external_api_server.py
  universal       ← chapter08/universal_tools_server.py

ツール名には、どのサーバーのツールかが分かるように名前空間が付く。
（例：calculator の add → calculator_add）

使い方:
    uv run my-awesome-mcp-server                          # stdio（Claude Desktop 用）
    uv run my-awesome-mcp-server --transport http --port 8000
    uv run my-awesome-mcp-server --only calculator database
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType

from fastmcp import FastMCP

# リポジトリのルート（src/mcp_learning/server.py から2つ上）
# 環境変数 MCP_LEARNING_ROOT で上書きできる
REPO_ROOT = Path(
    os.environ.get("MCP_LEARNING_ROOT", Path(__file__).resolve().parents[2])
).resolve()

# 名前空間 → サーバーファイル（リポジトリのルートからの相対パス）
SERVERS: dict[str, str] = {
    "calculator": "chapter03/calculator_server.py",
    "database": "chapter06/database_server_prompt.py",
    "external_api": "chapter07/external_api_server.py",
    "universal": "chapter08/universal_tools_server.py",
}


def log(message: str) -> None:
    """stdio通信ではstdoutがMCPの通信路になるので、メッセージはstderrに出す"""
    print(message, file=sys.stderr, flush=True)


def load_module(name: str, path: Path) -> ModuleType:
    """ファイルのパスを指定してPythonモジュールとして読み込む"""
    spec = importlib.util.spec_from_file_location(f"mams_{name}", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"読み込めません: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def build_server(only: list[str] | None = None) -> FastMCP:
    """各章のサーバーを読み込み、1つのサーバーにまとめる"""
    main_server = FastMCP("My Awesome MCP Server")

    for namespace, rel_path in SERVERS.items():
        if only and namespace not in only:
            continue
        path = REPO_ROOT / rel_path
        if not path.exists():
            log(f"[スキップ] {namespace}: ファイルがありません ({path})")
            continue
        try:
            module = load_module(namespace, path)
            sub_server = getattr(module, "mcp")
            main_server.mount(sub_server, namespace=namespace)
            log(f"[読み込み] {namespace}: {rel_path}")
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
        help="通信方式（既定: stdio。Claude Desktop から使うときは stdio）",
    )
    parser.add_argument("--host", default="127.0.0.1", help="HTTPのときの待ち受けアドレス")
    parser.add_argument("--port", type=int, default=8000, help="HTTPのときのポート番号")
    parser.add_argument(
        "--only", nargs="+", choices=list(SERVERS), metavar="NAME",
        help=f"指定したサーバーだけを読み込む（{', '.join(SERVERS)}）",
    )
    args = parser.parse_args()

    server = build_server(args.only)
    log(f"[起動] My Awesome MCP Server（transport={args.transport}）")

    if args.transport == "http":
        server.run(transport="http", host=args.host, port=args.port, show_banner=False)
    else:
        server.run(show_banner=False)


if __name__ == "__main__":
    main()
