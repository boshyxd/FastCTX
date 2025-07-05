from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Neo4jVector
from langchain_openai import ChatOpenAI
from langchain_community.graphs import Neo4jGraph
from langchain.chains import GraphCypherQAChain
import os
import logging

from ctx.services.neo4j_service import Neo4jService

logger = logging.getLogger(__name__)

class IndexingService:
    def __init__(self, neo4j_service: Neo4jService):
        self.neo4j_service = neo4j_service
        self.llm = ChatOpenAI(temperature=0, model_name="deepseek-v2", openai_api_base="https://openrouter.ai/api/v1") # Using deepseek-v2 via OpenRouter

    async def index_codebase(self, root_dir: str):
        logger.info(f"Starting codebase indexing for: {root_dir}")
        # Load documents
        loader = DirectoryLoader(root_dir, glob="**/*", show_progress=True, use_multithreading=True)
        documents = loader.load()

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)

        # Initialize embeddings
        embeddings = OpenAIEmbeddings(openai_api_base="https://openrouter.ai/api/v1")

        # Initialize Neo4jVector for semantic search on chunks
        vectorstore = Neo4jVector.from_existing_graph(
            embedding=embeddings,
            url=self.neo4j_service.uri,
            username=self.neo4j_service.username,
            password=self.neo4j_service.password,
            index_name="code_embeddings",
            node_label="Chunk", # Index chunks for vector search
            text_node_property="text",
            embedding_node_property="embedding",
        )

        # Add chunks to Neo4jVector (this also stores them as Chunk nodes)
        await vectorstore.add_documents(chunks)
        logger.info(f"Successfully indexed {len(chunks)} chunks from {root_dir} into Neo4jVector.")

        # Initialize Neo4jGraph for entity/relationship extraction
        graph = Neo4jGraph(
            url=self.neo4j_service.uri,
            username=self.neo4j_service.username,
            password=self.neo4j_service.password,
        )

        # Create Document nodes and link to Chunks
        async with self.neo4j_service._driver.session() as session:
            for doc in documents:
                doc_path = doc.metadata.get('source')
                await session.run("MERGE (d:Document {path: $path})", path=doc_path)
                # Link chunks to their parent document
                for chunk in chunks:
                    if chunk.metadata.get('source') == doc_path:
                        await session.run(
                            "MATCH (d:Document {path: $doc_path}), (c:Chunk {text: $chunk_text}) MERGE (c)-[:PART_OF_DOCUMENT]->(d)",
                            doc_path=doc_path, chunk_text=chunk.page_content
                        )
            logger.info("Created Document nodes and PART_OF_DOCUMENT relationships.")

        # LLM-based entity and relationship extraction (for Entity Graph)
        # This part needs a custom LLMGraphTransformer or similar logic
        # For now, we'll just log that this step would occur.
        logger.info("Skipping LLM-based entity and relationship extraction for now. This would be the next step for a full LLM Graph Builder integration.")

    async def query_graph_rag(self, query: str, k: int = 4):
        logger.info(f"Retrieving context for query: {query} (k={k})")

        # Initialize Neo4jGraph for GraphRAG
        graph = Neo4jGraph(
            url=self.neo4j_service.uri,
            username=self.neo4j_service.username,
            password=self.neo4j_service.password,
        )

        # Use GraphCypherQAChain for RAG
        chain = GraphCypherQAChain.from_llm(self.llm, graph=graph, verbose=True)
        result = await chain.ainvoke({"query": query})

        logger.info(f"Retrieved RAG response for query: {query}")
        return {"answer": result["result"], "intermediate_steps": result["intermediate_steps"]}
