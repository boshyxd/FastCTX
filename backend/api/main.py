import os
from functools import cache
from typing import Any

import structlog
from fastapi import FastAPI, HTTPException
from fastapi_mcp import FastApiMCP
from langchain_neo4j import Neo4jGraph
from pydantic import BaseModel

logger = structlog.stdlib.get_logger("fastctx-api")

app = FastAPI(title="FastCTX API")


class CypherQuery(BaseModel):
    """Request model for Cypher queries"""

    query: str
    parameters: dict[str, Any] | None = None


class NaturalLanguageQuery(BaseModel):
    """Request model for natural language queries"""

    question: str
    context: str | None = None


@cache
def get_neo4j_graph() -> Neo4jGraph:
    """
    Connects to Neo4j and sets up a graph context.
    """
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    graph = Neo4jGraph(refresh_schema=True)
    logger.info("Connected to Neo4J database at %s", uri)
    return graph


@app.post("/query/cypher")
async def query_cypher(query_request: CypherQuery):
    """Execute a Cypher query against the Neo4j database"""
    try:
        graph = get_neo4j_graph()

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
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Query failed: {str(e)}"
        ) from e


@app.post("/query/natural")
async def query_natural_language(query_request: NaturalLanguageQuery):
    """Process a natural language query and convert it to Cypher"""
    try:
        graph = get_neo4j_graph()

        # Use the graph's natural language query capability
        # This requires the graph to have been set up with an LLM
        result = graph.query(
            f"""Based on the following question about the graph database:
            
            Question: {query_request.question}
            
            Context: {query_request.context or "No additional context provided"}
            
            Please provide a relevant Cypher query and execute it to answer the question.
            """
        )

        return {
            "question": query_request.question,
            "context": query_request.context,
            "results": result,
            "count": len(result) if isinstance(result, list) else None,
        }
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Natural language query failed: {str(e)}"
        ) from e


@app.get("/query/examples")
async def get_query_examples():
    """Get example queries for the current database schema"""
    try:
        graph = get_neo4j_graph()

        # Get some basic information about the database
        node_count = graph.query("MATCH (n) RETURN COUNT(n) as count")[0][
            "count"
        ]
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
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate examples: {str(e)}"
        ) from e


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
