"""
Ví dụ cơ bản về cách sử dụng IQDB API Python

Chạy với: python examples/basic_usage.py
"""
import asyncio
from pathlib import Path
import json
import sys

from iqdb_api import IqdbClient, SyncIqdbClient, UserCancelledException


async def async_example():
    """Ví dụ sử dụng async client"""
    # Sử dụng client với ban prevention
    async with IqdbClient(prevent_bans=True) as client:
        # Tìm kiếm bằng URL (có thể gặp queue)
        print("Tìm kiếm bằng URL (có thể gặp queue)...")
        image_url = "https://cdn.discordapp.com/attachments/1384841768897351770/1384844445945434122/9478860_9478860_d9629b21708c830e3c6f4c27360331be.jpg?ex=6853e865&is=685296e5&hm=35b9befaca878d9d11436814e5c22b51dd1d10c833ed1e4f7f2b23359e8476f1&"
        print(f"URL: {image_url[:80]}...")
        try:
            # TODO: Sử dụng stream để hiển thị queue real-time
            async for result in client.search_url_stream(image_url):
                if result.queue_status:
                    msg = f"\r⏳ Đang trong hàng đợi IQDB... Vị trí: {result.queue_status.queue_position} | Ước tính chờ: {result.queue_status.estimated_wait}s "
                    print(msg, end="", flush=True)
                else:
                    print("\r", end="")
                    print(f"\u2705 Thành công! Đã tìm kiếm {result.searched_images_count} hình ảnh trong {result.searched_in_seconds:.2f} giây")
                    print(f"Tìm thấy {len(result.matches)} kết quả")
                    # In ra best match (nếu có)
                    if result.best_matches:
                        print("\n⭐️ Best match:")
                        for match in result.best_matches:
                            print(f"- URL: {match.url}")
                            print(f"  - Similarity: {match.similarity}% | Source: {match.source.value if match.source else None} | Rating: {match.rating} | Score: {match.score}")
                            print(f"  - Tags: {', '.join(match.tags) if match.tags else None}")
                            print(f"  - Resolution: {match.resolution} | Preview: {match.preview_url}")
                    # In ra các match khác
                    other_matches = [m for m in result.matches if not m.is_best_match]
                    if other_matches:
                        print("\n🔎 Other matches:")
                        for i, match in enumerate(other_matches, 1):
                            print(f"[{i}] {match.url}")
                            print(f"    - Type: {match.match_type.value}")
                            print(f"    - Similarity: {match.similarity}%")
                            print(f"    - Source: {match.source.value if match.source else None}")
                            print(f"    - Rating: {match.rating}")
                            print(f"    - Score: {match.score}")
                            print(f"    - Tags: {', '.join(match.tags) if match.tags else None}")
                            print(f"    - Resolution: {match.resolution}")
                            print(f"    - Preview: {match.preview_url}")
                    break  # Kết thúc khi đã có kết quả thực sự
        except UserCancelledException as e:
            print(f"\n⛔ Đã hủy thao tác: {e}")
            return  # Dừng luôn, không propagate exception
        except Exception as e:
            print(f"Lỗi: {e}")


def sync_example():
    """Ví dụ sử dụng sync client"""
    # Sử dụng client với ban prevention
    with SyncIqdbClient(prevent_bans=True) as client:
        # Hiển thị thông tin client
        info = client.get_search_info()
        print(f"🔧 Client info: Session {info['session_id'][:8]}, Ban prevention: {info['prevent_bans']}")
        
        # Tìm kiếm bằng URL
        print("Tìm kiếm bằng URL...")
        try:
            image_url = "https://cdn.discordapp.com/attachments/1384841768897351770/1384844445945434122/9478860_9478860_d9629b21708c830e3c6f4c27360331be.jpg?ex=6853e865&is=685296e5&hm=35b9befaca878d9d11436814e5c22b51dd1d10c833ed1e4f7f2b23359e8476f1&"
            print(f"URL: {image_url[:80]}...")
            
            result = client.search_url(image_url)
            
            print(f"\u2705 Thành công!")
            print(f"Đã tìm kiếm {result.searched_images_count} hình ảnh trong {result.searched_in_seconds:.2f} giây")
            print(f"Tìm thấy {len(result.matches)} kết quả")
            # In ra best match (nếu có)
            if result.best_matches:
                print("\n⭐️ Best match:")
                for match in result.best_matches:
                    print(f"- URL: {match.url}")
                    print(f"  - Similarity: {match.similarity}% | Source: {match.source.value if match.source else None} | Rating: {match.rating} | Score: {match.score}")
                    print(f"  - Tags: {', '.join(match.tags) if match.tags else None}")
                    print(f"  - Resolution: {match.resolution} | Preview: {match.preview_url}")
            # In ra các match khác
            other_matches = [m for m in result.matches if not m.is_best_match]
            if other_matches:
                print("\n🔎 Other matches:")
                for i, match in enumerate(other_matches, 1):
                    print(f"[{i}] {match.url}")
                    print(f"    - Type: {match.match_type.value}")
                    print(f"    - Similarity: {match.similarity}%")
                    print(f"    - Source: {match.source.value if match.source else None}")
                    print(f"    - Rating: {match.rating}")
                    print(f"    - Score: {match.score}")
                    print(f"    - Tags: {', '.join(match.tags) if match.tags else None}")
                    print(f"    - Resolution: {match.resolution}")
                    print(f"    - Preview: {match.preview_url}")
        except UserCancelledException as e:
            print(f"\n⛔ Đã hủy thao tác: {e}")
        except Exception as e:
            print(f"Lỗi: {e}")


async def file_search_example():
    """Ví dụ tìm kiếm bằng file"""
    print("\n=== Ví dụ Tìm kiếm bằng File ===")
    
    # Tạo một file ảnh mẫu (1x1 pixel PNG)
    sample_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
    
    async with IqdbClient() as client:
        try:
            print("Tìm kiếm bằng bytes data...")
            result = await client.search_file(sample_image_data)
            
            print(f"Đã tìm kiếm {result.searched_images_count} hình ảnh")
            print(f"Tìm thấy {len(result.matches)} kết quả")
            
            if result.your_image:
                print("Thông tin ảnh của bạn:")
                if result.your_image.resolution:
                    print(f"  - Độ phân giải: {result.your_image.resolution}")
                if result.your_image.preview_url:
                    print(f"  - Preview URL: {result.your_image.preview_url}")
                    
        except Exception as e:
            print(f"Lỗi: {e}")


def main():
    """Chạy tất cả ví dụ"""
    print("🔍 IQDB API Python - Ví dụ cơ bản")
    print("================================")
    
    try:
        # Chạy async example
        asyncio.run(async_example())
        
        # Chạy sync example
        sync_example()
        
        # Chạy file search example
        #asyncio.run(file_search_example())
        
    except (KeyboardInterrupt, UserCancelledException):
        print("\n⛔ Đã hủy thao tác bởi người dùng (KeyboardInterrupt/UserCancelledException)")
    
    print("\n✅ Hoàn thành tất cả ví dụ!")


if __name__ == "__main__":
    main()
