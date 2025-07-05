from neo4j import AsyncGraphDatabase
from neo4j.exceptions import ServiceUnavailable
import os
import logging

logger = logging.getLogger(__name__)

class Neo4jService:
    def __init__(self, uri, username, password):
        self._driver = None
        self.uri = uri
        self.username = username
        self.password = password

    async def connect(self):
        if self._driver is None:
            self._driver = AsyncGraphDatabase.driver(self.uri, auth=(self.username, self.password))
        try:
            await self._driver.verify_connectivity()
            logger.info("Neo4j connection established.")
        except ServiceUnavailable as e:
            logger.error(f"Neo4j connection failed: {e}")
            raise

    async def close(self):
        if self._driver:
            await self._driver.close()
            logger.info("Neo4j connection closed.")
            self._driver = None

    async def get_driver(self):
        if self._driver is None:
            await self.connect()
        return self._driver

    async def run_query(self, query, parameters=None):
        driver = await self.get_driver()
        async with driver.session() as session:
            result = await session.run(query, parameters)
            return result

    async def read_file_content(self, path: str):
        query = "MATCH (f:File {path: $path}) RETURN f.content AS content"
        result = await self.run_query(query, {"path": path})
        record = await result.single()
        return record["content"] if record else None

    async def write_file_content(self, path: str, content: str):
        query = "MERGE (f:File {path: $path}) SET f.content = $content"
        await self.run_query(query, {"path": path, "content": content})

    async def get_graph_schema(self):
        labels_query = "CALL db.labels() YIELD label RETURN label"
        relationships_query = "CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType"

        labels_result = await self.run_query(labels_query)
        relationship_types_result = await self.run_query(relationships_query)

        labels = [record["label"] async for record in labels_result]
        relationship_types = [record["relationshipType"] async for record in relationship_types_result]

        return {"labels": labels, "relationship_types": relationship_types}

