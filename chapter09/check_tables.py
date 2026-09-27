#!/usr/bin/env python3
"""テーブル構造を確認するスクリプト"""

import asyncio
from fastmcp import Client

async def main():
    client = Client(r"/home/kei/MCP_Learning/chapter06/database_server.py")
    
    async with client:
        await client.list_tools()  # ping非対応のため代用
        print("[OK] データベースサーバーに接続しました\n")
        
        # テーブル一覧を取得
        tables = await client.call_tool("list_tables", {})
        print("[LIST] 利用可能なテーブル:")
        print(tables)

if __name__ == "__main__":
    asyncio.run(main())