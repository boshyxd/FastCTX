from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("TimeServer")


@mcp.tool()
def get_current_time() -> str:
    """Get the current date and time"""
    return datetime.now().isoformat()


@mcp.tool()
def get_current_timestamp() -> float:
    """Get the current Unix timestamp"""
    return datetime.now().timestamp()


@mcp.resource("time://current")
def current_time() -> str:
    """Current time as a resource"""
    return f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


if __name__ == "__main__":
    import uvicorn
    
    app = mcp.sse_app()
    uvicorn.run(app, host="0.0.0.0", port=3001)
