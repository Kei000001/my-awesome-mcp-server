#!/usr/bin/env python3
"""Claude Desktop の "external_api" サーバーを、第7章の指定ステップに切り替える。

使い方（Claude Desktop を完全に終了してから実行）:
    python3 set_external_api_step.py base      # ステップ1: 土台（ツールなし）
    python3 set_external_api_step.py weather   # ステップ2: 天気
    python3 set_external_api_step.py news      # ステップ3: 天気＋ニュース
    python3 set_external_api_step.py ipinfo    # ステップ4: 天気＋ニュース＋IP位置情報
    python3 set_external_api_step.py full      # 完成版 (external_api_server.py)
    python3 set_external_api_step.py off       # 登録を外す
"""
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

STEPS = {
    "base": "external_api_server_base.py",
    "weather": "external_api_server_weather.py",
    "news": "external_api_server_news.py",
    "ipinfo": "external_api_server_ipinfo.py",
    "full": "external_api_server.py",
}
CHAPTER_DIR = Path(__file__).resolve().parent
CONFIG = Path.home() / ".config" / "Claude" / "claude_desktop_config.json"


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in [*STEPS, "off"]:
        print(__doc__)
        sys.exit(1)
    step = sys.argv[1]

    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    backup = CONFIG.with_name(f"claude_desktop_config.json.bak_{datetime.now():%Y%m%d_%H%M%S}")
    shutil.copy2(CONFIG, backup)

    servers = cfg.setdefault("mcpServers", {})
    before = servers.get("external_api", {}).get("args", ["未登録"])[-1]

    if step == "off":
        servers.pop("external_api", None)
        after = "未登録"
    else:
        script = CHAPTER_DIR / STEPS[step]
        if not script.exists():
            sys.exit(f"ファイルがありません: {script}")
        servers["external_api"] = {
            "command": shutil.which("uv") or str(Path.home() / ".local/bin/uv"),
            "args": ["--directory", str(CHAPTER_DIR), "run", script.name],
        }
        after = script.name

    CONFIG.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"external_api: {before} → {after}")
    print(f"バックアップ: {backup.name}")
    print("Claude Desktop を起動して、設定 → 開発者 で running を確認してください。")


if __name__ == "__main__":
    main()
