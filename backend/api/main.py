import os
from functools import cache

from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from langchain_neo4j import Neo4jGraph

app = FastAPI(title="FastCTX API")


@cache
def get_neo4j_graph() -> Neo4jGraph:
    """
    Connects to Neo4j and sets up a graph context.
    """
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    graph = Neo4jGraph(refresh_schema=True)
    return graph


@app.post("/query")
async def query_database():
    return {"Message:", "Hello, world"}


@app.get("/schema")
async def get_schema():
    """Get the current Neo4j database schema"""
    try:
        graph = get_neo4j_graph()
        # Refresh the schema to get the latest information
        graph.refresh_schema()

        # Get the schema information
        schema_info = {
            "structured_schema": graph.structured_schema,
            "schema": graph.schema,
        }

        return schema_info
    except Exception as e:
        return {"error": f"Failed to retrieve schema: {str(e)}"}


mcp = FastApiMCP(
    app,
    name="FastCTX API",
    description="API for FastCTX - Get better context from your code.",
)
mcp.mount()
