import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from ctx.services.indexing_service import IndexingService
from langchain_core.documents import Document

@pytest.fixture
def mock_neo4j_service():
    service = AsyncMock()
    service.uri = "bolt://mock:7687"
    service.username = "mock_user"
    service.password = "mock_pass"
    return service

@pytest.fixture
def indexing_service(mock_neo4j_service):
    return IndexingService(mock_neo4j_service)

@pytest.mark.asyncio
@patch('ctx.services.indexing_service.DirectoryLoader')
@patch('ctx.services.indexing_service.RecursiveCharacterTextSplitter')
@patch('ctx.services.indexing_service.OpenAIEmbeddings')
@patch('ctx.services.indexing_service.Neo4jVector')
async def test_index_codebase(mock_neo4j_vector, mock_openai_embeddings, mock_text_splitter, mock_directory_loader, indexing_service):
    # Mock DirectoryLoader
    mock_loader_instance = MagicMock()
    mock_directory_loader.return_value = mock_loader_instance
    mock_loader_instance.load.return_value = [Document(page_content="test content", metadata={'source': '/path/to/file.py'})]

    # Mock RecursiveCharacterTextSplitter
    mock_text_splitter_instance = MagicMock()
    mock_text_splitter.return_value = mock_text_splitter_instance
    mock_text_splitter_instance.split_documents.return_value = [MagicMock(page_content="chunk1", metadata={'source': '/path/to/file.py'})]

    # Mock OpenAIEmbeddings
    mock_embeddings_instance = MagicMock()
    mock_openai_embeddings.return_value = mock_embeddings_instance

    # Mock Neo4jVector
    mock_neo4j_vector_instance = AsyncMock()
    mock_neo4j_vector.from_existing_graph.return_value = mock_neo4j_vector_instance

    root_dir = "/mock/codebase"
    await indexing_service.index_codebase(root_dir)

    mock_directory_loader.assert_called_once_with(root_dir, glob="**/*", show_progress=True, use_multithreading=True)
    mock_loader_instance.load.assert_called_once()
    mock_text_splitter.assert_called_once_with(chunk_size=1000, chunk_overlap=200)
    mock_text_splitter_instance.split_documents.assert_called_once_with(mock_loader_instance.load.return_value)
    mock_openai_embeddings.assert_called_once()
    mock_neo4j_vector.from_existing_graph.assert_called_once_with(
        embedding=mock_embeddings_instance,
        url=indexing_service.neo4j_service.uri,
        username=indexing_service.neo4j_service.username,
        password=indexing_service.neo4j_service.password,
        index_name="code_embeddings",
        node_label="File",
        text_node_property="content",
        embedding_node_property="embedding",
    )
    mock_neo4j_vector_instance.add_documents.assert_called_once_with(mock_text_splitter_instance.split_documents.return_value)

@pytest.mark.asyncio
@patch('ctx.services.indexing_service.OpenAIEmbeddings')
@patch('ctx.services.indexing_service.Neo4jVector')
async def test_get_context(mock_neo4j_vector, mock_openai_embeddings, indexing_service):
    # Mock OpenAIEmbeddings
    mock_embeddings_instance = MagicMock()
    mock_openai_embeddings.return_value = mock_embeddings_instance

    # Mock Neo4jVector
    mock_neo4j_vector_instance = AsyncMock()
    mock_neo4j_vector.from_existing_graph.return_value = mock_neo4j_vector_instance
    
    dummy_docs = [
        Document(page_content="doc1 content", metadata={'source': 'file1.py'}),
        Document(page_content="doc2 content", metadata={'source': 'file2.py'})
    ]
    mock_neo4j_vector_instance.asimilarity_search.return_value = dummy_docs

    query = "test query"
    k = 2
    result = await indexing_service.get_context(query, k)

    mock_openai_embeddings.assert_called_once()
    mock_neo4j_vector.from_existing_graph.assert_called_once_with(
        embedding=mock_embeddings_instance,
        url=indexing_service.neo4j_service.uri,
        username=indexing_service.neo4j_service.username,
        password=indexing_service.neo4j_service.password,
        index_name="code_embeddings",
        node_label="File",
        text_node_property="content",
        embedding_node_property="embedding",
    )
    mock_neo4j_vector_instance.asimilarity_search.assert_called_once_with(query, k=k)
    assert result == [
        {"content": "doc1 content", "metadata": {'source': 'file1.py'}},
        {"content": "doc2 content", "metadata": {'source': 'file2.py'}}
    ]
