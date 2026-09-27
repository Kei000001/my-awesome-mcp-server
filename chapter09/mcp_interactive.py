#!/usr/bin/env python3
"""
FastMCPを使った対話型マルチサーバークライアント (v2)
mcpServers形式（Claude Desktop準拠）に対応
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Optional
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

def extract_text(result):
    """結果からテキストを抽出"""
    sc = getattr(result, "structured_content", None)
    if isinstance(sc, dict) and "result" in sc:
        return str(sc["result"])
    content = getattr(result, "content", None)
    if isinstance(content, list) and content:
        first = content[0]
        txt = getattr(first, "text", None)
        if isinstance(txt, str):
            return txt
    data = getattr(result, "data", None)
    if data is not None:
        return str(data)
    return str(result)

class MultiServerClientV2:
    """複数のMCPサーバーを管理するクライアント（mcpServers形式対応）"""
    
    def __init__(self, config_file: str = "mcp_servers.json"):
        self.servers = {}
        self.clients = {}
        self.config_file = config_file
        self.history = []
        self.load_config()
    
    def load_config(self):
        """mcpServers形式の設定ファイルを読み込む"""
        config_path = Path(self.config_file)
        if not config_path.exists():
            console.print(f"[red]設定ファイルが見つかりません: {self.config_file}[/red]")
            return
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # mcpServers形式の設定を読み込み
        for server_name, server_config in config.get("mcpServers", {}).items():
            self.servers[server_name] = {
                "name": server_name,
                "command": server_config["command"],
                "args": server_config["args"],
                "env": server_config.get("env", {}),
                "cwd": server_config.get("cwd"),
                "description": server_config.get("meta", {}).get("description", ""),
                "chapter": server_config.get("meta", {}).get("chapter", "")
            }
    
    async def connect_server(self, name: str):
        """サーバーに接続"""
        if name not in self.servers:
            console.print(f"[red]サーバー '{name}' が見つかりません[/red]")
            return False
        
        if name in self.clients:
            console.print(f"[yellow]既に接続済み: {name}[/yellow]")
            return True
        
        server_info = self.servers[name]
        console.print(f"[cyan][接続中] {name} に接続中... ({server_info['chapter']})[/cyan]")
        
        try:
            # StdioTransportでクライアントを作成
            transport = StdioTransport(
                command=server_info["command"],
                args=server_info["args"]
            )
            client = Client(transport)
            await client.__aenter__()
            
            # ping テスト
            await client.list_tools()  # ping非対応のため代用
            
            self.clients[name] = client
            console.print(f"[green][OK] {name} に接続しました[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red][ERROR] {name} への接続に失敗: {str(e)}[/red]")
            return False
    
    async def disconnect_server(self, name: str):
        """サーバーから切断"""
        if name not in self.clients:
            console.print(f"[yellow]サーバー '{name}' は接続されていません[/yellow]")
            return
        
        try:
            await self.clients[name].__aexit__(None, None, None)
            del self.clients[name]
            console.print(f"[green][切断] {name} から切断しました[/green]")
        except Exception as e:
            console.print(f"[red][ERROR] {name} の切断に失敗: {str(e)}[/red]")
    
    async def list_servers(self):
        """サーバー一覧を表示"""
        table = Table(title="利用可能なサーバー")
        table.add_column("名前", style="cyan", no_wrap=True)
        table.add_column("状態", style="green")
        table.add_column("説明", style="yellow")
        table.add_column("章", style="magenta")
        table.add_column("コマンド", style="white")
        
        for name, info in self.servers.items():
            status = "🟢 接続中" if name in self.clients else "⚪ 未接続"
            command_display = f"{info['command']} {' '.join(info['args'][:2])}..."
            table.add_row(name, status, info['description'], info['chapter'], command_display)
        
        console.print(table)
    
    async def list_tools(self, server_name: str):
        """指定されたサーバーのツール一覧を表示"""
        if server_name not in self.clients:
            console.print(f"[red]サーバー '{server_name}' に接続されていません[/red]")
            return
        
        try:
            tools = await self.clients[server_name].list_tools()
            
            table = Table(title=f"{server_name} のツール一覧")
            table.add_column("ツール名", style="cyan", no_wrap=True)
            table.add_column("説明", style="yellow")
            
            for tool in tools:
                # 説明文を80文字で切り詰め
                desc = tool.description or "説明なし"
                if len(desc) > 80:
                    desc = desc[:77] + "..."
                table.add_row(tool.name, desc)
            
            console.print(table)
        except Exception as e:
            console.print(f"[red][ERROR] ツール一覧の取得に失敗: {str(e)}[/red]")
    
    async def execute_tool(self, server_name: str, tool_name: str, args: Dict):
        """指定されたサーバーのツールを実行"""
        if server_name not in self.clients:
            console.print(f"[red]サーバー '{server_name}' に接続されていません[/red]")
            return
        
        try:
            console.print(f"[cyan][実行中] {server_name}.{tool_name}[/cyan]")
            result = await self.clients[server_name].call_tool(tool_name, args)
            
            # 結果を表示
            output = extract_text(result)
            panel = Panel(output, title=f"実行結果: {server_name}.{tool_name}", border_style="green")
            console.print(panel)
            
            # 履歴に記録
            self.history.append({
                "server": server_name,
                "tool": tool_name,
                "args": args,
                "result": output[:200] + "..." if len(output) > 200 else output
            })
            
        except Exception as e:
            console.print(f"[red][ERROR] ツール実行に失敗: {str(e)}[/red]")
    
    async def show_history(self):
        """実行履歴を表示"""
        if not self.history:
            console.print("[yellow]実行履歴はありません[/yellow]")
            return
        
        table = Table(title="実行履歴（最新10件）")
        table.add_column("番号", style="cyan", no_wrap=True)
        table.add_column("サーバー", style="green")
        table.add_column("ツール", style="yellow")
        table.add_column("引数", style="white")
        table.add_column("結果（抜粋）", style="magenta")
        
        for i, record in enumerate(self.history[-10:], 1):
            args_str = str(record["args"])[:30] + "..." if len(str(record["args"])) > 30 else str(record["args"])
            table.add_row(
                str(i),
                record["server"],
                record["tool"],
                args_str,
                record["result"][:50] + "..." if len(record["result"]) > 50 else record["result"]
            )
        
        console.print(table)
    
    async def demo_workflow(self):
        """複数サーバーを使用したデモワークフロー"""
        console.print(Panel("🚀 デモワークフロー: 天気情報を計算する", border_style="cyan"))
        
        # 必要なサーバーに接続
        servers_needed = ["weather", "calculator", "database"]
        for server in servers_needed:
            if server in self.servers:
                await self.connect_server(server)
        
        try:
            # 1. 天気情報を取得
            if "weather" in self.clients:
                console.print("[cyan]1. 東京の天気情報を取得中...[/cyan]")
                weather_result = await self.clients["weather"].call_tool("get_weather", {"city": "Tokyo"})
                weather_data = extract_text(weather_result)
                console.print(f"[green]天気データ取得完了[/green]")
                
                # 温度を抽出（簡易パース）
                import json
                try:
                    weather_json = json.loads(weather_data)
                    temperature = weather_json.get("temperature", 25.0)
                except:
                    temperature = 25.0  # デフォルト値
                
                # 2. 華氏に変換
                if "calculator" in self.clients:
                    console.print(f"[cyan]2. 温度 {temperature}°C を華氏に変換中...[/cyan]")
                    fahrenheit_result = await self.clients["calculator"].call_tool("multiply", {"a": temperature, "b": 1.8})
                    fahrenheit_temp = float(extract_text(fahrenheit_result))
                    
                    final_fahrenheit = await self.clients["calculator"].call_tool("add", {"a": fahrenheit_temp, "b": 32})
                    final_temp = extract_text(final_fahrenheit)
                    console.print(f"[green]華氏変換完了: {final_temp}°F[/green]")
               
        
        except Exception as e:
            console.print(f"[red]デモワークフロー中にエラー: {str(e)}[/red]")
        
        console.print(Panel("✅ デモワークフロー完了", border_style="green"))
    
    async def run_interactive(self):
        """対話型モードを開始"""
        console.print("========================================")
        console.print("[デモ] Interactive MCP Client")
        console.print("========================================")
        console.print("FastMCP対話型クライアント")
        console.print()
        console.print("コマンド:")
        console.print("  connect <server>     - サーバーに接続")
        console.print("  call <server>.<tool> - ツールを呼び出す")
        console.print("  status              - 接続状態を表示")
        console.print("  tools <server>      - ツール一覧を表示")
        console.print("  history             - 実行履歴を表示")
        console.print("  demo                - 統合デモを実行")
        console.print("  exit                - 終了")
        console.print("========================================")
        console.print()
        
        while True:
            try:
                command = Prompt.ask("[bold cyan]MCP>[/bold cyan]", default="").strip()
                
                if not command:
                    continue
                
                parts = command.split()
                cmd = parts[0].lower()
                
                if cmd in ["quit", "exit"]:
                    break
                elif cmd == "status":
                    await self.list_servers()
                elif cmd == "connect" and len(parts) > 1:
                    await self.connect_server(parts[1])
                elif cmd == "tools" and len(parts) > 1:
                    await self.list_tools(parts[1])
                elif cmd == "call" and len(parts) >= 2:
                    # call <server>.<tool> 形式をパース
                    if "." in parts[1]:
                        server_tool = parts[1].split(".", 1)
                        server_name = server_tool[0]
                        tool_name = server_tool[1]
                        args = {}
                        
                        # 引数をパース（簡易版）
                        if len(parts) > 2:
                            args_str = " ".join(parts[2:])
                            if args_str.startswith("{"):
                                try:
                                    args = json.loads(args_str)
                                except:
                                    console.print("[red]JSONパースエラー[/red]")
                                    continue
                            else:
                                # key=value形式をパース
                                for arg in args_str.split():
                                    if "=" in arg:
                                        key, value = arg.split("=", 1)
                                        try:
                                            args[key] = float(value) if "." in value else int(value)
                                        except:
                                            args[key] = value
                        
                        await self.execute_tool(server_name, tool_name, args)
                    else:
                        console.print("[red]形式: call <server>.<tool> [args][/red]")
                elif cmd == "demo":
                    await self.demo_workflow()
                elif cmd == "history":
                    await self.show_history()
                else:
                    console.print("[yellow]使用可能なコマンド: connect, call, status, tools, history, demo, exit[/yellow]")
            
            except KeyboardInterrupt:
                console.print("\n[yellow]Ctrl+C で終了します[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]エラー: {str(e)}[/red]")
        
        # 全クライアントを切断
        for name in list(self.clients.keys()):
            await self.disconnect_server(name)
        
        console.print("[green]さようなら！[/green]")

async def main():
    """メイン関数"""
    client = MultiServerClientV2()
    await client.run_interactive()

if __name__ == "__main__":
    asyncio.run(main())