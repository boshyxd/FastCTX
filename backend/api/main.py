from typing import Annotated, Any

import speedbeaver
import uvicorn
from fastapi import FastAPI
from fastapi.params import Depends
from fastapi_mcp import FastApiMCP
from langchain_experimental.graph_transformers.llm import LLMGraphTransformer
from langchain_neo4j.graphs.neo4j_graph import Neo4jGraph
from pydantic import BaseModel
from pydantic.functional_validators import model_validator

from api.common import get_neo4j_graph, setup_llm_transformer
from api.documents import load_github_project

LOGGER_NAME = "fastctx-api"

logger = speedbeaver.get_logger(LOGGER_NAME)

app = FastAPI(title="FastCTX API")
speedbeaver.quick_configure(app, logger_name=LOGGER_NAME)


class CypherQuery(BaseModel):
    """Request model for Cypher queries"""

    query: str
    parameters: dict[str, Any] | None = None


class NaturalLanguageQuery(BaseModel):
    """Request model for natural language queries"""

    question: str
    context: str | None = None


class ProjectSource(BaseModel):
    """Request model for the source of a loaded project"""

    github_url: str | None

    @model_validator(mode="before")
    def check_project_source(self):
        requires_one_of = self.model_dump()
        if not any(requires_one_of.values()):
            raise ValueError(
                f"Missing one of: {', '.join(requires_one_of.keys())}"
            )
        return self


@app.post("/loader", status_code=201)
async def load_codebase(
    src: ProjectSource,
    graph: Annotated[Neo4jGraph, Depends(get_neo4j_graph)],
    llm_transformer: Annotated[
        LLMGraphTransformer, Depends(setup_llm_transformer)
    ],
):
    if src.github_url:
        await load_github_project(src.github_url, llm_transformer, graph)

    return {"message": "Project loaded successfully."}


@app.post("/query/cypher")
async def query_cypher(
    query_request: CypherQuery,
    graph: Annotated[Neo4jGraph, Depends(get_neo4j_graph)],
):
    """Execute a Cypher query against the Neo4j database"""

    # Execute the query
    result = graph.query(
        query_request.query, params=query_request.parameters or {}
    )

    return {
        "query": query_request.query,
        "parameters": query_request.parameters,
        "results": result,
        "count": len(result) if isinstance(result, list) else None,
    }


@app.post("/query/natural")
async def query_natural_language(
    query_request: NaturalLanguageQuery,
    graph: Annotated[Neo4jGraph, Depends(get_neo4j_graph)],
):
    """Process a natural language query and convert it to Cypher"""

    # Use the graph's natural language query capability
    # This requires the graph to have been set up with an LLM
    prompt = f"""Based on the following question about the graph database:
        
        Question: {query_request.question}
        
        Context: {query_request.context or "No additional context provided"}
        
        Please provide a relevant Cypher query and execute it to answer the question.
        """

    return {
        "question": query_request.question,
        "context": query_request.context,
        "prompt": prompt,
    }


@app.get("/query/examples")
async def get_query_examples(
    graph: Annotated[Neo4jGraph, Depends(get_neo4j_graph)],
):
    """Get example queries for the current database schema"""
    # Get some basic information about the database
    node_count = graph.query("MATCH (n) RETURN COUNT(n) as count")[0]["count"]
    relationship_count = graph.query(
        "MATCH ()-[r]->() RETURN COUNT(r) as count"
    )[0]["count"]

    # Get node labels
    labels_result = graph.query("CALL db.labels()")
    labels = [record["label"] for record in labels_result]

    # Get relationship types
    rel_types_result = graph.query("CALL db.relationshipTypes()")
    rel_types = [record["relationshipType"] for record in rel_types_result]

    # Generate example queries
    examples = [
        {
            "description": "Get all nodes",
            "cypher": "MATCH (n) RETURN n LIMIT 10",
        },
        {
            "description": "Count nodes by label",
            "cypher": "MATCH (n) RETURN labels(n) as labels, COUNT(n) as count",
        },
        {
            "description": "Get all relationships",
            "cypher": "MATCH (a)-[r]->(b) RETURN type(r) as relationship_type, COUNT(r) as count",
        },
    ]

    # Add label-specific examples if we have labels
    if labels:
        examples.append(
            {
                "description": f"Get all {labels[0]} nodes",
                "cypher": f"MATCH (n:{labels[0]}) RETURN n LIMIT 10",
            }
        )

    return {
        "database_stats": {
            "node_count": node_count,
            "relationship_count": relationship_count,
            "labels": labels,
            "relationship_types": rel_types,
        },
        "example_queries": examples,
    }


@app.get("/schema")
async def get_schema(
    graph: Annotated[Neo4jGraph, Depends(get_neo4j_graph)],
):
    """Get the current Neo4j database schema"""
    # Refresh the schema to get the latest information
    graph.refresh_schema()

    # Get the schema information
    schema_info = {
        "structured_schema": graph.structured_schema,
        "schema": graph.schema,
    }

    return schema_info


mcp = FastApiMCP(
    app,
    name="FastCTX API",
    description="API for FastCTX - Get better context from your code.",
)
mcp.mount()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
