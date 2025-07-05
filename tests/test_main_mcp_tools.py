import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from ctx.main import app

@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="module")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_read_file_tool_success(client, mocker):
    mocker.patch('ctx.main.neo4j_service.read_file_content', return_value="file content from neo4j")
    response = await client.post(
        "/api/mcp/tools/read_file/execute",
        json={
            "path": "/test/path.txt"
        }
    )
    assert response.status_code == 200
    assert response.json() == {"result": "file content from neo4j"}
    ctx.main.neo4j_service.read_file_content.assert_called_once_with("/test/path.txt")

@pytest.mark.asyncio
async def test_read_file_tool_not_found(client, mocker):
    mocker.patch('ctx.main.neo4j_service.read_file_content', return_value=None)
    response = await client.post(
        "/api/mcp/tools/read_file/execute",
        json={
            "path": "/nonexistent/path.txt"
        }
    )
    assert response.status_code == 404
    assert "File not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_read_file_tool_exception(client, mocker):
    mocker.patch('ctx.main.neo4j_service.read_file_content', side_effect=Exception("DB error"))
    response = await client.post(
        "/api/mcp/tools/read_file/execute",
        json={
            "path": "/error/path.txt"
        }
    )
    assert response.status_code == 500
    assert "Error reading file from Neo4j" in response.json()["detail"]

@pytest.mark.asyncio
async def test_write_file_tool_success(client, mocker):
    mocker.patch('ctx.main.neo4j_service.write_file_content', return_value=None)
    response = await client.post(
        "/api/mcp/tools/write_file/execute",
        json={
            "path": "/new/file.txt",
            "content": "new content"
        }
    )
    assert response.status_code == 200
    assert response.json() == {"result": "Successfully wrote to /new/file.txt in Neo4j"}
    ctx.main.neo4j_service.write_file_content.assert_called_once_with("/new/file.txt", "new content")

@pytest.mark.asyncio
async def test_write_file_tool_exception(client, mocker):
    mocker.patch('ctx.main.neo4j_service.write_file_content', side_effect=Exception("DB write error"))
    response = await client.post(
        "/api/mcp/tools/write_file/execute",
        json={
            "path": "/error/write.txt",
            "content": "error content"
        }
    )
    assert response.status_code == 500
    assert "Error writing to file in Neo4j" in response.json()["detail"]

@pytest.mark.asyncio
async def test_index_codebase_tool_success(client, mocker):
    mocker.patch('ctx.main.indexing_service.index_codebase', return_value=None)
    response = await client.post(
        "/api/mcp/tools/index_codebase/execute",
        json={
            "root_dir": "/codebase"
        }
    )
    assert response.status_code == 200
    assert response.json() == {"result": "Successfully initiated indexing for /codebase"}
    ctx.main.indexing_service.index_codebase.assert_called_once_with("/codebase")

@pytest.mark.asyncio
async def test_index_codebase_tool_exception(client, mocker):
    mocker.patch('ctx.main.indexing_service.index_codebase', side_effect=Exception("Indexing error"))
    response = await client.post(
        "/api/mcp/tools/index_codebase/execute",
        json={
            "root_dir": "/error_codebase"
        }
    )
    assert response.status_code == 500
    assert "Error indexing codebase" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_context_tool_success(client, mocker):
    mocker.patch('ctx.main.indexing_service.get_context', return_value=[
        {"content": "doc1", "metadata": {"source": "file1.py"}},
        {"content": "doc2", "metadata": {"source": "file2.py"}}
    ])
    response = await client.post(
        "/api/mcp/tools/get_context/execute",
        json={
            "query": "test query",
            "k": 2
        }
    )
    assert response.status_code == 200
    assert response.json() == {"result": [
        {"content": "doc1", "metadata": {"source": "file1.py"}},
        {"content": "doc2", "metadata": {"source": "file2.py"}}
    ]}
    ctx.main.indexing_service.get_context.assert_called_once_with("test query", k=2)

@pytest.mark.asyncio
async def test_get_context_tool_exception(client, mocker):
    mocker.patch('ctx.main.indexing_service.get_context', side_effect=Exception("Context error"))
    response = await client.post(
        "/api/mcp/tools/get_context/execute",
        json={
            "query": "error query"
        }
    )
    assert response.status_code == 500
    assert "Error retrieving context" in response.json()["detail"]