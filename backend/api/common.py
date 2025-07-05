import os
from functools import cache

import speedbeaver
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_neo4j import Neo4jGraph

LOGGER_NAME = "fastctx-api"
MODEL = os.environ.get("LLM_MODEL", "gemini-2.0-flash")

logger = speedbeaver.get_logger(LOGGER_NAME)


@cache
def get_neo4j_graph() -> Neo4jGraph:
    """
    Connects to Neo4j and sets up a graph context.
    """
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    graph = Neo4jGraph(url=uri, refresh_schema=True)
    logger.info("Connected to Neo4J database at %s", uri)
    return graph


def setup_llm_transformer() -> LLMGraphTransformer:
    """
    Sets up a graph transformer with an LLM.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    llm = ChatGoogleGenerativeAI(
        model=MODEL,
        google_api_key=api_key,  # or pass directly
        temperature=0,
    )

    llm_transformer = LLMGraphTransformer(llm=llm)

    logger.info("LLM set up.")

    return llm_transformer
