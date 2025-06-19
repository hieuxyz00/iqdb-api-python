"""
Test cases cho client với các tính năng mới
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from iqdb_api.client import IqdbClient, Iqdb3dClient, SyncIqdbClient
from iqdb_api.exceptions import HttpRequestFailedException, NotImageException
from iqdb_api import SearchResult
from iqdb_api.models import QueueStatus


class TestIqdbClient:
    """Test cho IqdbClient"""
    
    def test_init_default_params(self):
        """Test khởi tạo với tham số mặc định"""
        client = IqdbClient()
        assert client.base_url == "https://www.iqdb.org"
        assert client.rate_limit_seconds == 5.1
        assert client.ignore_colors is False
        assert client.search_more is False
        assert client.prevent_bans is True
    
    def test_init_custom_params(self):
        """Test khởi tạo với tham số tùy chỉnh"""
        client = IqdbClient(
            ignore_colors=True,
            search_more=True,
            prevent_bans=False,
            rate_limit_seconds=3.0
        )
        assert client.ignore_colors is True
        assert client.search_more is True
        assert client.prevent_bans is False
        assert client.rate_limit_seconds == 3.0
    
    def test_is_discord_media_url(self):
        """Test detection Discord media URLs"""
        client = IqdbClient()
        
        # Discord URLs
        assert client._is_discord_media_url("https://cdn.discordapp.com/attachments/123/456/image.jpg") is True
        assert client._is_discord_media_url("https://media.discordapp.net/attachments/123/456/image.png") is True
        
        # Non-Discord URLs
        assert client._is_discord_media_url("https://example.com/image.jpg") is False
        assert client._is_discord_media_url("https://imgur.com/image.png") is False
    
    def test_is_special_media_url(self):
        """Test detection special media URLs"""
        client = IqdbClient()
        
        # Special URLs
        assert client._is_special_media_url("https://cdn.discordapp.com/attachments/123/456/image.jpg") is True
        assert client._is_special_media_url("https://i.imgur.com/image.jpg") is True
        assert client._is_special_media_url("https://i.redd.it/image.png") is True
        assert client._is_special_media_url("https://pbs.twimg.com/media/image.jpg") is True
        
        # Normal URLs
        assert client._is_special_media_url("https://example.com/image.jpg") is False
        assert client._is_special_media_url("https://safebooru.org/image.png") is False
    
    def test_get_supported_formats(self):
        """Test lấy danh sách format được hỗ trợ"""
        client = IqdbClient()
        formats = client.get_supported_image_formats()
        
        assert isinstance(formats, list)
        assert "JPEG" in formats
        assert "PNG" in formats
        assert "GIF" in formats
        assert "WEBP" in formats
    
    def test_get_supported_sources_2d(self):
        """Test lấy danh sách source cho 2D IQDB"""
        client = IqdbClient()
        sources = client.get_supported_sources()
        
        assert isinstance(sources, list)
        assert "Danbooru" in sources
        assert "Gelbooru" in sources
        assert "Konachan" in sources
    
    def test_get_supported_sources_3d(self):
        """Test lấy danh sách source cho 3D IQDB"""
        client = Iqdb3dClient()
        sources = client.get_supported_sources()
        
        assert isinstance(sources, list)
        assert "3Dbooru" in sources
        assert "Idol Complex" in sources
    
    def test_get_search_info(self):
        """Test lấy thông tin cấu hình search"""
        client = IqdbClient(
            ignore_colors=True,
            search_more=True,
            prevent_bans=False
        )
        info = client.get_search_info()
        
        assert isinstance(info, dict)
        assert info["ignore_colors"] is True
        assert info["search_more"] is True
        assert info["prevent_bans"] is False
        assert info["base_url"] == "https://www.iqdb.org"
        assert info["max_file_size"] == "8MB"
        assert "session_id" in info
        assert "supported_formats" in info
        assert "supported_sources" in info
    
    def test_prepare_search_data(self):
        """Test chuẩn bị search data"""
        client = IqdbClient(ignore_colors=True, search_more=True)
        data = client._prepare_search_data()
        
        assert "forcegray" in data
        assert data["forcegray"] == "1"
        assert "service" in data
        assert data["service"] == "1,2,3,4,5,6,7,8,9,10,11,12,13"
    
    def test_prepare_search_data_defaults(self):
        """Test chuẩn bị search data với giá trị mặc định"""
        client = IqdbClient()  # ignore_colors=False, search_more=False
        data = client._prepare_search_data()
        
        assert data == {}  # Không có field nào được thêm
    
    @pytest.mark.asyncio
    async def test_download_image_from_url_success(self):
        """Test download ảnh thành công"""
        client = IqdbClient()
        
        # Mock response
        mock_response = Mock()
        mock_response.content = b"fake_image_data"
        mock_response.headers = {"content-type": "image/jpeg"}
        
        with patch.object(client._client, 'get', return_value=mock_response) as mock_get:
            mock_get.return_value.raise_for_status = Mock()
            
            result = await client._download_image_from_url("https://example.com/image.jpg")
            
            assert result == b"fake_image_data"
            mock_get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_download_discord_image_special_headers(self):
        """Test download Discord image với headers đặc biệt"""
        client = IqdbClient()
        
        # Mock response
        mock_response = Mock()
        mock_response.content = b"discord_image_data"
        mock_response.headers = {"content-type": "image/jpeg"}
        
        with patch.object(client._client, 'get', return_value=mock_response) as mock_get:
            mock_get.return_value.raise_for_status = Mock()
            
            discord_url = "https://cdn.discordapp.com/attachments/123/456/image.jpg"
            result = await client._download_image_from_url(discord_url)
            
            assert result == b"discord_image_data"
            
            # Kiểm tra Discord-specific headers
            call_args = mock_get.call_args
            headers = call_args[1]["headers"]
            assert "Referer" in headers
            assert headers["Referer"] == "https://discord.com/"
            assert headers["Origin"] == "https://discord.com"


class TestSyncClient:
    """Test cho sync client wrapper"""
    
    def test_sync_client_init(self):
        """Test khởi tạo sync client"""
        client = SyncIqdbClient(
            ignore_colors=True,
            prevent_bans=False
        )
        
        assert client._async_client.ignore_colors is True
        assert client._async_client.prevent_bans is False
    
    def test_sync_client_get_search_info(self):
        """Test lấy search info từ sync client"""
        client = SyncIqdbClient(ignore_colors=True)
        info = client.get_search_info()
        
        assert isinstance(info, dict)
        assert info["ignore_colors"] is True


@pytest.mark.asyncio
async def test_rate_limiting():
    """Test rate limiting logic"""
    client = IqdbClient(rate_limit_seconds=1.0, prevent_bans=True)
    
    import time
    start_time = time.time()
    
    # Gọi rate limit 2 lần
    await client._apply_rate_limit()
    await client._apply_rate_limit()
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    # Với prevent_bans=True, thời gian chờ sẽ > rate_limit_seconds
    assert elapsed >= 1.0  # Base rate limit
    assert elapsed >= 1.5  # Với random delay từ prevent_bans


def test_user_agent_rotation():
    """Test rotation của User-Agent"""
    client = IqdbClient(prevent_bans=True)
    
    # Lấy nhiều User-Agent và kiểm tra có rotation
    agents = [client._get_random_user_agent() for _ in range(10)]
    
    # Phải có ít nhất 2 User-Agent khác nhau trong 10 lần gọi
    unique_agents = set(agents)
    assert len(unique_agents) >= 2
    
    # Tất cả phải là User-Agent hợp lệ
    for agent in agents:
        assert agent in client._user_agents


def test_user_agent_no_rotation():
    """Test không rotation User-Agent khi prevent_bans=False"""
    custom_ua = "Custom-Agent/1.0"
    client = IqdbClient(prevent_bans=False, user_agent=custom_ua)
    
    # Luôn trả về user_agent gốc
    for _ in range(5):
        assert client._get_random_user_agent() == custom_ua


@pytest.mark.asyncio
async def test_fallback_download(monkeypatch):
    async def fake_download(*args, **kwargs):
        return b"fakeimage"
    async def fake_search_file(self, file_input):
        return SearchResult(1, 0.1, [], None)
    async def fake_search_url_direct(self, image_url):
        raise Exception("Not an image or image format not supported (server says it is application/octet-stream)")
    monkeypatch.setattr(IqdbClient, "_download_image_from_url", fake_download)
    monkeypatch.setattr(IqdbClient, "search_file", fake_search_file)
    monkeypatch.setattr(IqdbClient, "_search_url_direct", fake_search_url_direct)
    client = IqdbClient()
    result = await client.search_url("http://test")
    assert isinstance(result, SearchResult)


@pytest.mark.asyncio
async def test_queue_status_stream(monkeypatch):
    # Giả lập parser trả về queue_status
    class DummyClient(IqdbClient):
        async def search_url(self, image_url, force_download=None):
            return SearchResult(0, 0, [], None, queue_status=QueueStatus(2, 10, "<html>queue</html>", "In queue"))
    client = DummyClient()
    gen = client.search_url_stream("http://test")
    result = await gen.__anext__()
    assert result.queue_status is not None
    assert result.queue_status.queue_position == 2


@pytest.mark.asyncio
async def test_timeout_default():
    client = IqdbClient()
    assert client.timeout is None
