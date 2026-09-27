#!/usr/bin/env python3
"""
Step A: 最初のMCPツール - テーブル一覧表示
"""

import sqlite3
from typing import List, Dict, Any
from fastmcp import FastMCP

# MCPサーバーを作成
mcp = FastMCP("Database Server - Step A")

# データベースのパス
DB_PATH = 'intelligent_shop.db'

def get_db_connection():
    """データベースに安全に接続する関数"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")  # 外部キー制約を有効化
    conn.row_factory = sqlite3.Row  # 列名でアクセス可能にする
    return conn

# 🔧 最初のツール：テーブル一覧を取得
@mcp.tool()
def list_tables() -> List[Dict[str, Any]]:
    """
    データベース内のすべてのテーブルを一覧表示
    
    Returns:
        テーブル名とその説明のリスト
    """
    print("[検索] データベースからテーブル一覧を取得中...")
    
    conn = get_db_connection()
    
    # SQLiteのシステムテーブルからユーザーテーブルを取得
    cursor = conn.execute('''
    SELECT name, sql 
    FROM sqlite_master 
    WHERE type='table' AND name NOT LIKE 'sqlite_%'
    ORDER BY name
    ''')
    
    tables = []
    for row in cursor.fetchall():
        tables.append({
            "table_name": row["name"],
            "creation_sql": row["sql"]
        })
    
    conn.close()
    
    print(f"[完了] {len(tables)}個のテーブルを発見しました")
    return tables

# サーバー起動
if __name__ == "__main__":
    print("[起動] MCPサーバー（Step A版）を起動します...")
    print("[ツール] 利用可能なツール: list_tables")
    mcp.run()
