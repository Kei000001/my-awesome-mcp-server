from fastmcp import FastMCP

mcp = FastMCP("My Greeter")

@mcp.tool()
def greet(name: str) -> str:
    """名前を受け取って挨拶を返す"""
    return f"こんにちは、{name}さん！"

if __name__ == "__main__":
    mcp.run()
