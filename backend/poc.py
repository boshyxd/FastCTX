import asyncio
import os

import aiofiles
import structlog
from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph
from langchain_openai import ChatOpenAI

logger = structlog.stdlib.get_logger("fastctx")

MODEL = os.environ.get("LLM_MODEL", "gemini-2.0-flash")
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "gemini")


def setup_llm_transformer() -> LLMGraphTransformer:
    if LLM_PROVIDER == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")

        llm = ChatOpenAI(
            model=MODEL,
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0,
            default_headers={
                "HTTP-Referer": "http://localhost",  # Optional, for tracking
                "X-Title": "FastCTX",  # Optional, for tracking
            },
        )
        logger.info("OpenRouter LLM set up with model: %s", MODEL)
    else:  # Default to Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        llm = ChatGoogleGenerativeAI(
            model=MODEL,
            google_api_key=api_key,
            temperature=0,
        )
        logger.info("Gemini LLM set up with model: %s", MODEL)

    llm_transformer = LLMGraphTransformer(llm=llm)

    return llm_transformer


def get_neo4j_graph() -> Neo4jGraph:
    """
    Connects to Neo4j and sets up a graph context.
    """
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    # We already have env vars set up for username and password

    graph = Neo4jGraph(refresh_schema=False)

    logger.info("Connected to database at %s", uri)

    return graph


# class LoadedFile(NamedTuple):
#     contents: str
#     filename: str


async def load_document(filename: str) -> Document | None:
    """
    Loads in file from the filesystem async. Converts it to a Langchain Document
    """

    contents: str
    try:
        async with aiofiles.open(filename) as f:
            contents = await f.read()
    except UnicodeDecodeError:
        await logger.awarning("Couldn't decode %s to unicode.", filename)
        return None

    # loaded_file = LoadedFile(contents, filename)

    document = Document(page_content=contents, metadata={"filename": filename})

    await logger.ainfo(
        "Got document.", size=len(document.page_content), **document.metadata
    )
    return document


async def main():
    """Main application entry point"""
    graph = get_neo4j_graph()
    llm_transformer = setup_llm_transformer()
    document_tasks: list[asyncio.Task[Document | None]] = []
    async with asyncio.TaskGroup() as file_tg:
        # Walk the /demo directory and add load_file tasks
        demo_dir = "/demo"
        if os.path.exists(demo_dir):
            for root, _, files in os.walk(demo_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    document_task = file_tg.create_task(
                        load_document(file_path)
                    )
                    document_tasks.append(document_task)
                    await logger.ainfo("Added load_file task for %s", file_path)
        else:
            await logger.awarning("Demo directory %s does not exist", demo_dir)

    # Extract loaded documents

    documents: list[Document] = [
        doc
        for doc in [document.result() for document in document_tasks]
        if doc is not None
    ]

    await logger.ainfo("Documents loaded.", num_documents=len(documents))

    graph_documents = await llm_transformer.aconvert_to_graph_documents(
        documents
    )

    await logger.ainfo("Documents converted to graph.")

    # Why the hell are these guys using `List` and not `list`
    graph.add_graph_documents(graph_documents, include_source=True)  # pyright: ignore

    await logger.ainfo("Documents added to neo4j.")


if __name__ == "__main__":
    asyncio.run(main())
