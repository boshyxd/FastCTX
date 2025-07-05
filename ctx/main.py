import logging
import os

from fastapi import FastAPI, Request, HTTPException
from modelcontextprotocol import MCPServer

from ctx.api import graph
from ctx.services.neo4j_service import Neo4jService
from ctx.services.indexing_service import IndexingService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize MCP Server
mcp_server = MCPServer()

# Initialize services (will be connected on startup)
neo4j_service = Neo4jService(
    uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    username=os.getenv("NEO4J_USERNAME", "neo4j"),
    password=os.getenv("NEO4J_PASSWORD", "password")
)
indexing_service = IndexingService(neo4j_service)

@app.on_event("startup")
async def startup_event():
    app.neo4j_service = neo4j_service
    app.indexing_service = indexing_service
    try:
        await app.neo4j_service.connect()
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j: {e}")
        # Depending on criticality, you might want to raise the exception or exit here

@app.on_event("shutdown")
async def shutdown_event():
    if app.neo4j_service:
        await app.neo4j_service.close()

# Define tool functions
@mcp_server.tool(
    name="read_file",
    description="Read the contents of a file from Neo4j.",
    parameters={
        "path": {"type": "string", "description": "The path to the file."}
    }
)
async def read_file_tool(path: str, request: Request):
    try:
        content = await request.app.neo4j_service.read_file_content(path)
        if content is None:
            raise HTTPException(status_code=404, detail=f"File not found in Neo4j: {path}")
        return {"result": content}
    except HTTPException:
        raise # Re-raise HTTPExceptions
    except Exception as e:
        logger.error(f"Error in read_file_tool for path {path}: {e}")
        raise HTTPException(status_code=500, detail=f"Error reading file from Neo4j: {e}")

@mcp_server.tool(
    name="write_file",
    description="Write content to a file in Neo4j.",
    parameters={
        "path": {"type": "string", "description": "The path to the file."},
        "content": {"type": "string", "description": "The content to write."}
    }
)
async def write_file_tool(path: str, content: str, request: Request):
    try:
        await request.app.neo4j_service.write_file_content(path, content)
        return {"result": f"Successfully wrote to {path} in Neo4j"}
    except Exception as e:
        logger.error(f"Error in write_file_tool for path {path}: {e}")
        raise HTTPException(status_code=500, detail=f"Error writing to file in Neo4j: {e}")

@mcp_server.tool(
    name="index_codebase",
    description="Index the codebase by reading files and storing their content in Neo4j.",
    parameters={
        "root_dir": {"type": "string", "description": "The root directory of the codebase to index."}
    }
)
async def index_codebase_tool(root_dir: str, request: Request):
    try:
        await request.app.indexing_service.index_codebase(root_dir)
        return {"result": f"Successfully initiated indexing for {root_dir}"}
    except Exception as e:
        logger.error(f"Error in index_codebase_tool for root_dir {root_dir}: {e}")
        raise HTTPException(status_code=500, detail=f"Error indexing codebase: {e}")

@mcp_server.tool(
    name="query_graph_rag",
    description="Process chat queries using GraphRAG retrievers to answer questions based on the indexed codebase.",
    parameters={
        "query": {"type": "string", "description": "The user's natural language query."},
        "k": {"type": "integer", "description": "The number of relevant snippets to consider for RAG (optional, default 4)."}
    }
)
async def query_graph_rag_tool(query: str, request: Request, k: int = 4):
    try:
        rag_response = await request.app.indexing_service.query_graph_rag(query, k=k)
        return {"result": rag_response}
    except Exception as e:
        logger.error(f"Error in query_graph_rag_tool for query \"{query}\": {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving context: {e}")

@mcp_server.tool(
    name="get_graph_schema",
    description="Retrieves the current schema of the Neo4j graph, including node labels and relationship types.",
    parameters={}
)
async def get_graph_schema_tool(request: Request):
    try:
        schema = await request.app.neo4j_service.get_graph_schema()
        return {"result": schema}
    except Exception as e:
        logger.error(f"Error in get_graph_schema_tool: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving graph schema: {e}")

app.include_router(mcp_server.router, prefix="/api/mcp")
app.include_router(graph.router, prefix="/api")

@app.get("/")
def read_root():
    return {"Hello": "World"}