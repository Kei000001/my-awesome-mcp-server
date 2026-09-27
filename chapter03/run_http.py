from calculator_server import mcp

try:
    # FastMCP 2.x（本の書き方）
    mcp.run(transport="http", host="127.0.0.1", port=8000)
except (TypeError, ValueError):
    # 公式SDK (mcp.server.fastmcp)
    mcp.settings.host = "127.0.0.1"
    mcp.settings.port = 8000
    mcp.run(transport="streamable-http")
