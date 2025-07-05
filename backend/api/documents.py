import asyncio
import os
import shutil
import tempfile
from pathlib import Path
from typing import Annotated  # pyright: ignore

import aiofiles
import httpx
import structlog
from fastapi.exceptions import HTTPException
from fastapi.params import Depends
from langchain_core.documents import Document
from langchain_experimental.graph_transformers.llm import LLMGraphTransformer
from langchain_neo4j.graphs.neo4j_graph import Neo4jGraph

from api.common import get_neo4j_graph, logger, setup_llm_transformer


async def load_document(filename: str, **kwargs) -> Document | None:
    """
    Loads in file from the filesystem async. Converts it to a Langchain Document

    kwargs specify metadata to be added to the document.
    """

    contents: str
    try:
        async with aiofiles.open(filename) as f:
            contents = await f.read()
    except UnicodeDecodeError:
        await logger.awarning("Couldn't decode %s to unicode.", filename)
        return None

    # TODO: Set up more metadata
    document = Document(page_content=contents, metadata={"filename": filename})

    await logger.ainfo(
        "Got document.", size=len(document.page_content), **document.metadata
    )
    return document


async def load_documents(root_dir: os.PathLike, **metadata) -> list[Document]:
    """
    Converts a tree of files at a given `root_dir` into Langchain documents.

    metadata specifies metadata to add to each document.
    """
    if not os.path.exists(root_dir):
        await logger.awarning("%s is nonexistent.", root_dir)
        return []
    document_tasks: list[asyncio.Task[Document | None]] = []
    async with asyncio.TaskGroup() as file_tg:
        # Walk the /demo directory and add load_file tasks
        for root, _, files in os.walk(root_dir):
            for file in files:
                file_path = os.path.join(root, file)
                document_task = file_tg.create_task(
                    load_document(file_path, **metadata)
                )
                document_tasks.append(document_task)
                await logger.adebug("Added load_file task for %s", file_path)

    # Extract loaded documents

    documents: list[Document] = [
        doc
        for doc in [document.result() for document in document_tasks]
        if doc is not None
    ]

    await logger.adebug("Documents loaded.", num_documents=len(documents))

    return documents


async def insert_documents(
    documents: list[Document],  # pyright: ignore
    llm_transformer: Annotated[
        LLMGraphTransformer, Depends(setup_llm_transformer)
    ],
    graph: Annotated[Neo4jGraph, Depends(get_neo4j_graph)],
):
    graph_documents = await llm_transformer.aconvert_to_graph_documents(
        documents
    )

    await logger.adebug("Documents converted to graph.")

    # Why the hell are these guys using `List` and not `list`
    graph.add_graph_documents(graph_documents, include_source=True)  # pyright: ignore

    await logger.adebug("Documents inserted.")


async def _download_file(url: str, out_filename: os.PathLike):
    """
    Downloads a file at a given URL using HTTP.
    """
    async with (
        httpx.AsyncClient() as http_client,
        aiofiles.open(out_filename, mode="wb+") as out_file,
    ):
        res = await http_client.get(url)
        if res.status_code >= 400:
            raise HTTPException(
                status_code=res.status_code,
                detail=f"Failed to download file at: {url}",
            )
        await out_file.write(res.content)
        await logger.adebug(
            "Downloaded file at %s successfully.",
            url,
            out_filename=out_filename,
        )


async def download_github_project(url: str, dest_directory: os.PathLike):
    """
    Downloads a GitHub repository as a zip file and extracts it to the specified directory.
    """
    # Create a temporary directory
    if not url.startswith("https://github.com"):
        raise ValueError("Invalid Github URL.")

    with tempfile.TemporaryDirectory() as tmpdirname:
        # Define paths
        clone_destination = Path(tmpdirname) / "repo.zip"

        await _download_file(
            f"{url}/archive/refs/heads/main.zip", clone_destination
        )

        # Extract the zip file to the destination directory
        shutil.unpack_archive(str(clone_destination), dest_directory)

    await logger.adebug(
        "Downloaded and extracted repository from %s to %s", url, dest_directory
    )


async def load_github_project(
    url: str,
    llm_transformer: Annotated[
        LLMGraphTransformer, Depends(setup_llm_transformer)
    ],
    graph: Annotated[Neo4jGraph, Depends(get_neo4j_graph)],
):
    """
    Loads a project from Github into Neo4j
    """
    structlog.contextvars.bind_contextvars(github_url=url)
    if not url.startswith("https://github.com"):
        raise ValueError(f"Invalid Github URL: {url}.")
    with tempfile.TemporaryDirectory() as project_src_directory:
        project_src_location = Path(project_src_directory)
        await download_github_project(url, project_src_location)
        documents = await load_documents(project_src_location)
        await insert_documents(documents, llm_transformer, graph)
