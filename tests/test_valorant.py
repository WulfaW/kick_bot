import pytest
from bot.services.valorant import ValorantService
from bot.core.config import RiotConfig

class MockHttpClient:
    """Mock HTTP client for unit testing without making real network requests."""
    def __init__(self, response_text: str, should_fail: bool = False):
        self.response_text = response_text
        self.should_fail = should_fail

    async def get(self, url: str, params=None):
        if self.should_fail:
            raise Exception("Mocked HTTP Exception")
        return self.response_text

@pytest.mark.asyncio
async def test_get_rank_success():
    # Arrange
    mock_http = MockHttpClient("Platinum 2 - 24RR")
    config = RiotConfig(region="eu", name="TenZ", tag="NA1")
    service = ValorantService(mock_http, config)

    # Act
    rank = await service.get_rank()

    # Assert
    assert rank == "Platinum 2 - 24RR"

@pytest.mark.asyncio
async def test_get_rank_failure():
    # Arrange
    mock_http = MockHttpClient("", should_fail=True)
    config = RiotConfig(region="eu", name="TenZ", tag="NA1")
    service = ValorantService(mock_http, config)

    # Act
    rank = await service.get_rank()

    # Assert
    assert rank == "Could not fetch current rank."
