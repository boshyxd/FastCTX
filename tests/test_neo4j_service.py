import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from neo4j.exceptions import ServiceUnavailable
from ctx.services.neo4j_service import Neo4jService

@pytest.fixture
def mock_driver():
    with patch('ctx.services.neo4j_service.AsyncGraphDatabase.driver') as mock_driver_class:
        mock_driver_instance = AsyncMock()
        mock_driver_class.return_value = mock_driver_instance
        yield mock_driver_instance

@pytest.fixture
def neo4j_service(mock_driver):
    service = Neo4jService("bolt://localhost:7687", "neo4j", "password")
    service._driver = mock_driver # Manually set the mocked driver
    return service

@pytest.mark.asyncio
async def test_connect_success(neo4j_service, mock_driver):
    await neo4j_service.connect()
    mock_driver.verify_connectivity.assert_called_once()
    assert neo4j_service._driver is mock_driver

@pytest.mark.asyncio
async def test_connect_failure(neo4j_service, mock_driver):
    mock_driver.verify_connectivity.side_effect = ServiceUnavailable("Connection failed")
    with pytest.raises(ServiceUnavailable):
        await neo4j_service.connect()
    mock_driver.verify_connectivity.assert_called_once()
    assert neo4j_service._driver is mock_driver # Driver should still be set even on failure

@pytest.mark.asyncio
async def test_close(neo4j_service, mock_driver):
    await neo4j_service.close()
    mock_driver.close.assert_called_once()
    assert neo4j_service._driver is None

@pytest.mark.asyncio
async def test_get_driver(neo4j_service, mock_driver):
    driver = await neo4j_service.get_driver()
    assert driver is mock_driver
    mock_driver.verify_connectivity.assert_not_called() # Should not connect again if driver is already set

@pytest.mark.asyncio
async def test_run_query(neo4j_service, mock_driver):
    mock_session = AsyncMock()
    mock_driver.session.return_value.__aenter__.return_value = mock_session
    mock_result = AsyncMock()
    mock_session.run.return_value = mock_result

    query = "MATCH (n) RETURN n"
    parameters = {"param": "value"}
    result = await neo4j_service.run_query(query, parameters)

    mock_driver.session.assert_called_once()
    mock_session.run.assert_called_once_with(query, parameters)
    assert result is mock_result

@pytest.mark.asyncio
async def test_read_file_content_found(neo4j_service, mock_driver):
    mock_session = AsyncMock()
    mock_driver.session.return_value.__aenter__.return_value = mock_session
    mock_result = AsyncMock()
    mock_session.run.return_value = mock_result
    mock_result.single.return_value = {"content": "file content"}

    content = await neo4j_service.read_file_content("/path/to/file.txt")
    assert content == "file content"

@pytest.mark.asyncio
async def test_read_file_content_not_found(neo4j_service, mock_driver):
    mock_session = AsyncMock()
    mock_driver.session.return_value.__aenter__.return_value = mock_session
    mock_result = AsyncMock()
    mock_session.run.return_value = mock_result
    mock_result.single.return_value = None

    content = await neo4j_service.read_file_content("/path/to/nonexistent.txt")
    assert content is None

@pytest.mark.asyncio
async def test_write_file_content(neo4j_service, mock_driver):
    mock_session = AsyncMock()
    mock_driver.session.return_value.__aenter__.return_value = mock_session
    mock_result = AsyncMock()
    mock_session.run.return_value = mock_result

    await neo4j_service.write_file_content("/path/to/newfile.txt", "new content")
    mock_session.run.assert_called_once_with(
        "MERGE (f:File {path: $path}) SET f.content = $content",
        {"path": "/path/to/newfile.txt", "content": "new content"}
    )
