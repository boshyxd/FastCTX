import os

import aiofiles
import structlog
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_neo4j import Neo4jGraph

logger = structlog.stdlib.get_logger("neo4j-bullshit")


def setup_llm_transformer():
    api_key = os.getenv("GEMINI_API_KEY")
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=api_key,  # or pass directly
        temperature=0,
    )

    llm_transformer = LLMGraphTransformer(llm=llm)

    logger.info("LLM set up.")

    return llm_transformer


def get_neo4j_graph():
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    # We already have env vars set up for username and password

    graph_db = Neo4jGraph(refresh_schema=False)

    logger.info("Connected to database at %s", uri)


async def load_file(filename: str):
    contents: str
    async with aiofiles.open("filename") as f:
        contents = await f.read()

    return contents


def main():
    """Main application entry point"""
    get_neo4j_graph()
    llm_transformer = setup_llm_transformer()


if __name__ == "__main__":
    main()
