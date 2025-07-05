from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

app = FastAPI(title="FastCTX API")


@app.post("/query")
async def query_database():
    return {"Message:", "Hello, world"}


@app.get("/schema")
async def get_schema():
    pass


mcp = FastApiMCP(
    app,
    name="FastCTX API",
    description="API for FastCTX - Get better context from your code.",
)
mcp.mount()
