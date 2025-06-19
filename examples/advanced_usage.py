"""
Ví dụ nâng cao về cách sử dụng IQDB API Python

Bao gồm:
- Sử dụng cả 2D và 3D IQDB
- Xử lý lỗi chi tiết
- Rate limiting customization
- Batch processing

Chạy với: python examples/advanced_usage.py
"""
import asyncio
import time
from typing import List, Union
from pathlib import Path

from iqdb_api import IqdbClient, Iqdb3dClient, SearchResult
from iqdb_api.exceptions import (
    ImageTooLargeException,
    HttpRequestFailedException,
    NotImageException,
    IqdbApiException
)


class BatchIqdbSearcher:
    """Utility class để thực hiện batch search với rate limiting"""
    
    def __init__(self, client: Union[IqdbClient, Iqdb3dClient]):
        self.client = client
    
    async def search_multiple_urls(self, urls: List[str]) -> List[SearchResult]:
        """Tìm kiếm nhiều URL với rate limiting"""
        results = []
        
        print(f"Bắt đầu tìm kiếm {len(urls)} URLs...")
        
        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}] Tìm kiếm: {url}")
            
            try:
                start_time = time.time()
                result = await self.client.search_url(url)
                search_time = time.time() - start_time
                
                print(f"  ✅ Hoàn thành trong {search_time:.2f}s - Tìm thấy {len(result.matches)} kết quả")
                for m in result.matches:
                    print(f"    - URL: {m.url}")
                results.append(result)
                
            except Exception as e:
                print(f"  ❌ Lỗi: {e}")
                # Có thể thêm None hoặc error object vào results nếu cần
                
        return results


async def compare_2d_vs_3d():
    """So sánh kết quả tìm kiếm giữa 2D và 3D IQDB"""
    print("=== So sánh 2D vs 3D IQDB ===")
    
    # URL ảnh test (thay đổi theo nhu cầu)
    test_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png"
    
    async with IqdbClient() as client_2d, Iqdb3dClient() as client_3d:
        try:
            print("Tìm kiếm trên 2D IQDB...")
            result_2d = await client_2d.search_url(test_url)
            
            print("Tìm kiếm trên 3D IQDB...")
            result_3d = await client_3d.search_url(test_url)
            
            print("\n📊 Kết quả so sánh:")
            print(f"2D IQDB: {len(result_2d.matches)} kết quả")
            print(f"3D IQDB: {len(result_3d.matches)} kết quả")
            
            # Analyze results
            if result_2d.is_found and not result_3d.is_found:
                print("🎯 2D IQDB có kết quả tốt hơn!")
            elif result_3d.is_found and not result_2d.is_found:
                print("🎯 3D IQDB có kết quả tốt hơn!")
            elif result_2d.is_found and result_3d.is_found:
                print("🎯 Cả hai đều tìm thấy kết quả!")
            else:
                print("❌ Không có kết quả chính xác từ cả hai")
                
        except Exception as e:
            print(f"Lỗi: {e}")


async def error_handling_demo():
    """Demo các loại lỗi và cách xử lý"""
    print("\n=== Demo Xử lý Lỗi ===")
    
    async with IqdbClient() as client:
        # Test 1: URL không hợp lệ
        print("Test 1: URL không hợp lệ")
        try:
            await client.search_url("not-a-valid-url")
        except Exception as e:
            print(f"  ✅ Đã bắt lỗi: {type(e).__name__}: {e}")
        
        # Test 2: URL trống
        print("Test 2: URL trống")
        try:
            await client.search_url("")
        except ValueError as e:
            print(f"  ✅ Đã bắt lỗi: {type(e).__name__}: {e}")
        
        # Test 3: File quá lớn (giả lập)
        print("Test 3: File quá lớn")
        try:
            # Tạo data > 8MB
            large_data = b"x" * (8_388_609)  # > 8MB
            await client.search_file(large_data)
        except ImageTooLargeException as e:
            print(f"  ✅ Đã bắt lỗi: {type(e).__name__}: {e}")
        
        # Test 4: Data không phải ảnh
        print("Test 4: Data không phải ảnh")
        try:
            text_data = b"This is not an image file"
            await client.search_file(text_data)
        except Exception as e:
            print(f"  ✅ Đã bắt lỗi: {type(e).__name__}: {e}")


async def custom_rate_limiting():
    """Demo custom rate limiting"""
    print("\n=== Demo Custom Rate Limiting ===")
    
    # Client với rate limit ngắn hơn cho demo
    async with IqdbClient(rate_limit_seconds=2.0) as client:
        urls = [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png"
        ]
        
        searcher = BatchIqdbSearcher(client)
        
        start_time = time.time()
        results = await searcher.search_multiple_urls(urls)
        total_time = time.time() - start_time
        
        print(f"\nTổng thời gian: {total_time:.2f}s cho {len(urls)} requests")
        print(f"Trung bình: {total_time/len(urls):.2f}s per request")


async def detailed_result_analysis():
    """Phân tích chi tiết kết quả tìm kiếm"""
    print("\n=== Phân tích Chi tiết Kết quả ===")
    
    async with IqdbClient() as client:
        try:
            # Sử dụng một URL có khả năng có kết quả
            test_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png"
            
            result = await client.search_url(test_url)
            
            print(f"📈 Thống kê tìm kiếm:")
            print(f"  - Số ảnh đã tìm: {result.searched_images_count:,}")
            print(f"  - Thời gian: {result.searched_in_seconds:.3f}s")
            print(f"  - Tổng kết quả: {len(result.matches)}")
            
            # Phân tích theo loại match
            match_types = {}
            for match in result.matches:
                match_type = match.match_type.value
                if match_type not in match_types:
                    match_types[match_type] = []
                match_types[match_type].append(match)
            
            print(f"\n📊 Phân tích theo loại:")
            for match_type, matches in match_types.items():
                print(f"  - {match_type.title()}: {len(matches)} kết quả")
                
                # Hiển thị similarity range
                similarities = [m.similarity for m in matches if m.similarity is not None]
                if similarities:
                    print(f"    Độ tương tự: {min(similarities):.1f}% - {max(similarities):.1f}%")
            
            # Phân tích theo nguồn
            sources = {}
            for match in result.matches:
                if match.source:
                    source = match.source.value
                    sources[source] = sources.get(source, 0) + 1
            
            if sources:
                print(f"\n🌐 Phân tích theo nguồn:")
                for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
                    print(f"  - {source.title()}: {count} kết quả")
            
            # Your Image info
            if result.your_image:
                print(f"\n🖼️ Thông tin ảnh của bạn:")
                if result.your_image.resolution:
                    print(f"  - Độ phân giải: {result.your_image.resolution}")
                if result.your_image.preview_url:
                    print(f"  - Preview: {result.your_image.preview_url}")
                if result.your_image.size:
                    print(f"  - Kích thước: {result.your_image.size}")
                    
        except Exception as e:
            print(f"Lỗi: {e}")


async def main():
    """Chạy tất cả demo nâng cao"""
    print("🔬 IQDB API Python - Ví dụ nâng cao")
    print("===================================")
    
    # Demo các tính năng nâng cao
    await compare_2d_vs_3d()
    await error_handling_demo()
    await custom_rate_limiting()
    await detailed_result_analysis()
    
    print("\n✅ Hoàn thành tất cả demo nâng cao!")


if __name__ == "__main__":
    asyncio.run(main())
