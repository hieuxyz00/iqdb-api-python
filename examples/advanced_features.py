"""
Ví dụ nâng cao về các tính năng của IQDB API Python

Bao gồm:
- Tính năng ignore colors và search more
- Chống ban
- Lấy thông tin về tags và format được hỗ trợ

Chạy với: python examples/advanced_features.py
"""
import asyncio
from pathlib import Path
import json

from iqdb_api import IqdbClient, SyncIqdbClient, Iqdb3dClient


async def discord_media_example():
    """Ví dụ xử lý Discord media links"""
    print("=== Ví dụ Discord Media Links ===")
    
    async with IqdbClient(prevent_bans=True) as client:
        discord_url = "https://cdn.discordapp.com/attachments/1384841768897351770/1384844445945434122/9478860_9478860_d9629b21708c830e3c6f4c27360331be.jpg?ex=6853e865&is=685296e5&hm=35b9befaca878d9d11436814e5c22b51dd1d10c833ed1e4f7f2b23359e8476f1&"
        
        try:
            print("Tìm kiếm Discord media URL...")
            print(f"URL: {discord_url}")

            result = await client.search_url(discord_url)
            
            print(f"\u2705 Thành công! Tìm thấy {len(result.matches)} kết quả")
            for i, match in enumerate(result.matches, 1):
                print(f"[{i}] {match.url}")
                print(f"    - Type: {match.match_type.value}")
                print(f"    - Similarity: {match.similarity}%")
                print(f"    - Source: {match.source.value if match.source else None}")
                print(f"    - Rating: {match.rating}")
                print(f"    - Score: {match.score}")
                print(f"    - Tags: {', '.join(match.tags) if match.tags else None}")
                print(f"    - Resolution: {match.resolution}")
                print(f"    - Preview: {match.preview_url}")
            with open("last_iqdb_results_advanced.json", "w", encoding="utf-8") as f:
                json.dump({
                    "searched_images_count": result.searched_images_count,
                    "searched_in_seconds": result.searched_in_seconds,
                    "matches": [match.__dict__ for match in result.matches],
                    "your_image": result.your_image.__dict__ if result.your_image else None
                }, f, ensure_ascii=False, indent=2)
            print("\n\uD83D\uDCBE Đã lưu kết quả vào last_iqdb_results_advanced.json. Bạn có thể load lại file này để phân tích hoặc sử dụng tiếp!")
            
        except Exception as e:
            print(f"❌ Lỗi: {e}")


async def advanced_search_options():
    """Ví dụ các tùy chọn search nâng cao"""
    print("\n=== Ví dụ Advanced Search Options ===")
    
    # Sử dụng ignore colors và search more
    async with IqdbClient(
        ignore_colors=True,      # Bỏ qua màu sắc
        search_more=True,        # Tìm kiếm nhiều source hơn
        prevent_bans=True,       # Chống ban
        rate_limit_seconds=6.0   # Tăng delay để an toàn hơn
    ) as client:
        
        # Hiển thị thông tin client
        info = client.get_search_info()
        print("🔧 Cấu hình client:")
        print(f"  - Ignore colors: {info['ignore_colors']}")
        print(f"  - Search more: {info['search_more']}")
        print(f"  - Prevent bans: {info['prevent_bans']}")
        print(f"  - Rate limit: {info['rate_limit_seconds']}s")
        print(f"  - Session ID: {info['session_id']}")
        
        try:
            # Test với một URL ảnh anime
            test_url = "https://safebooru.org//images/4405/c1c7a6f8d5a39c6e97b7935f0a2a2e9fae29c056.jpg"
            print(f"\nTìm kiếm với advanced options...")
            print(f"URL: {test_url}")
            
            result = await client.search_url(test_url)
            
            print(f"📊 Kết quả:")
            print(f"  - Đã search {result.searched_images_count} ảnh")
            print(f"  - Thời gian: {result.searched_in_seconds:.2f}s")
            print(f"  - Tổng matches: {len(result.matches)}")
            
            # Phân loại kết quả
            print(f"  - Best matches: {len(result.best_matches)}")
            print(f"  - Additional matches: {len(result.additional_matches)}")
            print(f"  - Possible matches: {len(result.possible_matches)}")
            
        except Exception as e:
            print(f"❌ Lỗi: {e}")


def get_supported_info():
    """Lấy thông tin về các format và source được hỗ trợ"""
    print("\n=== Thông tin Format & Source được hỗ trợ ===")
    
    # 2D IQDB
    with SyncIqdbClient() as client:
        info = client.get_search_info()
        
        print("🖼️ 2D IQDB (www.iqdb.org):")
        print(f"  📁 Supported formats: {', '.join(info['supported_formats'])}")
        print(f"  📚 Supported sources: {', '.join(info['supported_sources'])}")
        print(f"  📏 Max file size: {info['max_file_size']}")
    
    # 3D IQDB
    print("\n🎭 3D IQDB (3d.iqdb.org):")
    async def get_3d_info():
        async with Iqdb3dClient() as client:
            info = client.get_search_info()
            print(f"  📁 Supported formats: {', '.join(info['supported_formats'])}")
            print(f"  📚 Supported sources: {', '.join(info['supported_sources'])}")
            print(f"  📏 Max file size: {info['max_file_size']}")
    
    asyncio.run(get_3d_info())


async def force_download_example():
    """Ví dụ ép buộc download ảnh thay vì search URL trực tiếp"""
    print("\n=== Ví dụ Force Download ===")
    
    async with IqdbClient() as client:
        # URL bình thường nhưng muốn download để tăng độ chính xác
        test_url = "https://safebooru.org//images/4405/c1c7a6f8d5a39c6e97b7935f0a2a2e9fae29c056.jpg"
        
        try:
            print("Search bằng URL trực tiếp:")
            result1 = await client.search_url(test_url, force_download=False)
            print(f"  - Tìm thấy {len(result1.matches)} kết quả")
            
            print("\nSearch bằng download rồi upload:")
            result2 = await client.search_url(test_url, force_download=True)
            print(f"  - Tìm thấy {len(result2.matches)} kết quả")
            
            # So sánh kết quả
            if len(result2.matches) != len(result1.matches):
                print(f"📈 Kết quả khác nhau! Download method: {len(result2.matches)} vs URL method: {len(result1.matches)}")
            else:
                print("📊 Cả hai method cho kết quả tương tự")
                
        except Exception as e:
            print(f"❌ Lỗi: {e}")


async def batch_search_with_prevention():
    """Ví dụ search nhiều ảnh với chống ban"""
    print("\n=== Ví dụ Batch Search với Ban Prevention ===")
    
    urls = [
        "https://safebooru.org//images/4405/c1c7a6f8d5a39c6e97b7935f0a2a2e9fae29c056.jpg",
        "https://safebooru.org//images/4404/f8b3d1c4e7a2b9d6f5e8c3a7b2d9c6e4f7a8b5d2.png",
        # Thêm Discord URL để test
        "https://cdn.discordapp.com/attachments/1384841768897351770/1384844445945434122/9478860_9478860_d9629b21708c830e3c6f4c27360331be.jpg?ex=6853e865&is=685296e5&hm=35b9befaca878d9d11436814e5c22b51dd1d10c833ed1e4f7f2b23359e8476f1&"
    ]
    
    async with IqdbClient(
        prevent_bans=True,
        rate_limit_seconds=7.0  # Tăng delay cho batch search
    ) as client:
        
        print(f"🔍 Tìm kiếm {len(urls)} ảnh với ban prevention...")
        
        results = []
        for i, url in enumerate(urls, 1):
            try:
                print(f"  [{i}/{len(urls)}] Searching: {url[:50]}...")
                result = await client.search_url(url)
                results.append(result)
                print(f"    ✅ Tìm thấy {len(result.matches)} kết quả")
                
            except Exception as e:
                print(f"    ❌ Lỗi: {e}")
                results.append(None)
        
        # Tổng kết
        successful = sum(1 for r in results if r is not None)
        total_matches = sum(len(r.matches) for r in results if r is not None)
        
        print(f"\n📊 Tổng kết batch search:")
        print(f"  - Thành công: {successful}/{len(urls)}")
        print(f"  - Tổng matches: {total_matches}")


def main():
    """Chạy tất cả ví dụ nâng cao"""
    print("🚀 IQDB API Python - Advanced Features Demo")
    print("=" * 50)
    
    # 1. Thông tin về format & source được hỗ trợ
    get_supported_info()
    
    # 2. Discord media links
    asyncio.run(discord_media_example())
    
    # 3. Advanced search options
    asyncio.run(advanced_search_options())
    
    # 4. Force download example
    asyncio.run(force_download_example())
    
    # 5. Batch search với ban prevention
    asyncio.run(batch_search_with_prevention())
    
    print("\n✅ Hoàn thành tất cả ví dụ nâng cao!")
    print("\n💡 Tips:")
    print("  - Sử dụng prevent_bans=True cho tìm kiếm an toàn")
    print("  - ignore_colors=True giúp tìm kiếm chính xác hơn với ảnh đen trắng")
    print("  - search_more=True tìm kiếm trên nhiều database hơn")


if __name__ == "__main__":
    main()
