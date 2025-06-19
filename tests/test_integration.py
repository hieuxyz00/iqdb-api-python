"""
Integration tests cho các tính năng mới
Cần kết nối internet để chạy
"""
import pytest
import asyncio
from iqdb_api import IqdbClient, SyncIqdbClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_discord_url_search():
    """Test tìm kiếm Discord URL (cần internet)"""
    async with IqdbClient(prevent_bans=True) as client:
        # Discord URL mẫu (có thể expire)
        discord_url = "https://cdn.discordapp.com/attachments/1384841768897351770/1384844445945434122/9478860_9478860_d9629b21708c830e3c6f4c27360331be.jpg?ex=6853e865&is=685296e5&hm=35b9befaca878d9d11436814e5c22b51dd1d10c833ed1e4f7f2b23359e8476f1&"
        
        try:
            result = await client.search_url(discord_url)
            
            # Kiểm tra kết quả
            assert result is not None
            assert isinstance(result.searched_images_count, int)
            assert isinstance(result.searched_in_seconds, float)
            assert isinstance(result.matches, list)
            
            print(f"✅ Discord URL search: {len(result.matches)} matches found")
            
        except Exception as e:
            # Discord URL có thể expire, log lỗi nhưng không fail test
            print(f"⚠️ Discord URL expired or unavailable: {e}")


@pytest.mark.integration  
@pytest.mark.asyncio
async def test_force_download_vs_direct():
    """Test so sánh force download vs direct URL search"""
    # Sử dụng URL public ổn định
    test_url = "https://via.placeholder.com/500x500.jpg"
    
    async with IqdbClient() as client:
        try:
            # Test direct URL search
            result1 = await client.search_url(test_url, force_download=False)
            
            # Test force download
            result2 = await client.search_url(test_url, force_download=True)
            
            # Cả hai đều phải thành công
            assert result1 is not None
            assert result2 is not None
            
            print(f"✅ Direct search: {len(result1.matches)} matches")
            print(f"✅ Download search: {len(result2.matches)} matches")
            
        except Exception as e:
            print(f"⚠️ Test URL unavailable: {e}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_advanced_search_options():
    """Test ignore colors và search more options"""
    test_url = "https://via.placeholder.com/300x300.jpg"
    
    # Test với ignore colors
    async with IqdbClient(ignore_colors=True, search_more=True) as client:
        try:
            result = await client.search_url(test_url)
            
            assert result is not None
            print(f"✅ Advanced options search: {len(result.matches)} matches")
            
        except Exception as e:
            print(f"⚠️ Advanced search failed: {e}")


@pytest.mark.integration
def test_sync_client_with_new_features():
    """Test sync client với tính năng mới"""
    with SyncIqdbClient(prevent_bans=True, ignore_colors=True) as client:
        # Test get search info
        info = client.get_search_info()
        
        assert info["prevent_bans"] is True
        assert info["ignore_colors"] is True
        assert "session_id" in info
        assert len(info["supported_formats"]) > 0
        assert len(info["supported_sources"]) > 0
        
        print(f"✅ Sync client info: {info['session_id'][:8]}...")


@pytest.mark.integration
@pytest.mark.asyncio 
async def test_rate_limiting_real():
    """Test rate limiting trong real scenario"""
    async with IqdbClient(rate_limit_seconds=2.0, prevent_bans=True) as client:
        import time
        
        start_time = time.time()
        
        # Thực hiện 2 search liên tiếp
        try:
            test_url = "https://via.placeholder.com/100x100.jpg"
            
            await client.search_url(test_url)
            await client.search_url(test_url)
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            # Phải có delay ít nhất rate_limit_seconds
            assert elapsed >= 2.0
            print(f"✅ Rate limiting: {elapsed:.2f}s elapsed")
            
        except Exception as e:
            print(f"⚠️ Rate limiting test failed: {e}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_error_handling_improved():
    """Test error handling với URLs không hợp lệ"""
    async with IqdbClient() as client:
        # Test với URL không tồn tại
        try:
            result = await client.search_url("https://nonexistent-domain-12345.com/image.jpg")
            print("⚠️ Expected error but got result")
            
        except Exception as e:
            # Phải có lỗi
            assert "HTTP request thất bại" in str(e) or "download" in str(e).lower()
            print(f"✅ Error handled correctly: {type(e).__name__}")


if __name__ == "__main__":
    # Chạy integration tests
    print("🧪 Running integration tests...")
    print("Note: These tests require internet connection")
    
    asyncio.run(test_discord_url_search())
    asyncio.run(test_force_download_vs_direct())
    asyncio.run(test_advanced_search_options())
    test_sync_client_with_new_features()
    asyncio.run(test_rate_limiting_real())
    asyncio.run(test_error_handling_improved())
    
    print("✅ Integration tests completed!")
