from fastapi import APIRouter, Request, HTTPException
from typing import List, Dict, Any
import logging

from ctx.services.neo4j_service import Neo4jService

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/graph")
async def get_graph(request: Request):
    neo4j_service: Neo4jService = request.app.neo4j_service
    if not neo4j_service:
        raise HTTPException(status_code=500, detail="Neo4j service not initialized.")

    try:
        nodes_result = await neo4j_service.run_query("MATCH (n) RETURN n")
        relationships_result = await neo4j_service.run_query("MATCH (n)-[r]->(m) RETURN n, r, m")

        nodes = []
        async for record in nodes_result:
            node = record["n"]
            nodes.append({"id": node.id, "labels": list(node.labels), "properties": dict(node.items())})

        relationships = []
        async for record in relationships_result:
            start_node = record["n"]
            relationship = record["r"]
            end_node = record["m"]
            relationships.append({
                "id": relationship.id,
                "type": relationship.type,
                "start_node": start_node.id,
                "end_node": end_node.id,
                "properties": dict(relationship.items())
            })

        return {"nodes": nodes, "relationships": relationships}
    except Exception as e:
        logger.error(f"Error retrieving graph data: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving graph data: {e}")