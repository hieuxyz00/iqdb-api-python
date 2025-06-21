import asyncio
import os
from iqdb_api import IqdbClient, SyncIqdbClient, Iqdb3dClient, SyncIqdb3dClient, NoMatchFoundException

ASSETS_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets')

async def async_2d_url_example():
    """Ví dụ sử dụng async client 2D với URL."""
    async with IqdbClient(include_more_results=True, max_retries=5, retry_delay=3) as client:
        image_url = "https://cdn.donmai.us/sample/19/76/__yuzuha_riko_stellive_drawn_by_yt9676__sample-1976d95aa69df203bd5279d970168a60.jpg"
        try:
            print(f"Đang tìm kiếm URL: {image_url[:70]}...")
            result = await client.search_url(image_url)
            
            print(f"\n✅ Tìm kiếm hoàn tất! Tổng cộng {len(result.matches)} kết quả.")
            
            if result.is_found:
                best_match = result.best_matches[0] 
                print("\n--- KẾT QUẢ TỐT NHẤT ---")
                print(f"- URL: {best_match.url}")
                print(f"- Similarity: {best_match.similarity}% | Source: {best_match.source.name if best_match.source else 'N/A'} | Rating: {best_match.rating.name} | Score: {best_match.score}")
            else:
                print("😔 Không tìm thấy kết quả tốt nào.")

        except Exception as e:
            print(f"❌ Đã xảy ra lỗi không mong muốn: {e}")

async def async_2d_file_example():
    """Ví dụ sử dụng async client 2D với FILE và >8MB."""
    PATH = os.path.join(ASSETS_DIR, 'large.jpg')
    if not os.path.exists(PATH):
        print(f"⚠️Không tìm thấy file tại '{PATH}'.")
        return

    async with IqdbClient() as client:
        try:
            print(f"Đang tìm kiếm file: {PATH}")
            result = await client.search_file(PATH)
            
            print(f"\n✅ Tìm kiếm hoàn tất! Tổng cộng {len(result.matches)} kết quả.")
            
            if result.is_found:
                best_match = result.best_matches[0]
                print("\n--- KẾT QUẢ TỐT NHẤT ---")
                print(f"- URL: {best_match.url}")
                print(f"- Similarity: {best_match.similarity}%")
            else:
                print("😔 Không tìm thấy kết quả tốt nào.")

        except Exception as e:
            print(f"❌ Đã xảy ra lỗi không mong muốn: {e}")

async def async_3d_example():
    """Ví dụ sử dụng async client 3D với URL."""
    async with Iqdb3dClient() as client:
        image_url = "https://iv.sankakucomplex.com/data/10/91/1091f52d07758970a5b2154430573a0c.jpg?e=1750482210&m=Y9GaHu77j3w60xkcL6RYyQ&expires=1750482210&token=quI6G1pQsJX_SBibWgomGVw6qvnw5yW-sUwMIYJU06Q"
        # post 1QaEo1EqR9L
        
        try:
            print(f"Đang tìm kiếm URL trên 3d.iqdb.org: {image_url[:70]}...")
            result = await client.search_url(image_url)
            
            print(f"\n✅ Tìm kiếm hoàn tất! Tổng cộng {len(result.matches)} kết quả.")
            
            if result.is_found:
                best_match = result.best_matches[0] 
                print("\n--- KẾT QUẢ TỐT NHẤT (3D) ---")
                print(f"- URL: {best_match.url}")
                print(f"  - Similarity: {best_match.similarity}% | Source: {best_match.source.name if best_match.source else 'N/A'}")
            else:
                print("😔 Không tìm thấy kết quả tốt nào.")

        except Exception as e:
            print(f"❌ Đã xảy ra lỗi: {e}")


def sync_2d_url_example():
    """Ví dụ sử dụng sync client 2D với URL."""
    
    with SyncIqdbClient() as client:
        image_url = "https://i.pximg.net/c/600x1200_90/img-master/img/2025/06/15/00/38/44/131567199_p0_master1200.jpg"
        print(f"Đang tìm kiếm URL: {image_url[:70]}...")
        try:
            result = client.search_url(image_url)
            print(f"\n✅ Tìm kiếm hoàn tất! Tổng cộng {len(result.matches)} kết quả.")
            if result.is_found:
                print(f"- Kết quả tốt nhất: {result.best_matches[0].url}")
            else:
                print("😔 Không tìm thấy kết quả tốt nào.")
        except Exception as e:
            print(f"\n❌ Đã xảy ra lỗi: {e}")

def sync_2d_file_example():
    """Ví dụ sử dụng sync client 2D với FILE."""
    PATH = os.path.join(ASSETS_DIR, 'test.jpg')
    if not os.path.exists(PATH):
        print(f"⚠️Không tìm thấy file tại '{PATH}'.")
        return

    with SyncIqdbClient() as client:
        try:
            print(f"Đang tìm kiếm file: {PATH}")
            result = client.search_file(PATH)
            
            print(f"\n✅ Tìm kiếm hoàn tất! Tổng cộng {len(result.matches)} kết quả.")
            
            if result.is_found:
                print(f"- Kết quả tốt nhất: {result.best_matches[0].url}")
            else:
                print("😔 Không tìm thấy kết quả tốt nào.")
        except Exception as e:
            print(f"❌ Đã xảy ra lỗi không mong muốn: {e}")

def sync_3d_example():
    """Ví dụ sử dụng sync client 3D với URL."""
    with SyncIqdb3dClient() as client:
        image_url = "https://iv.sankakucomplex.com/data/47/63/476304f69d349682bbe88c9aadfcaee5.jpg?e=1750482044&m=EwJ7cDon7UV45dta8ZUxTw&expires=1750482044&token=hv5NKgRW97xqc8LMINEPe-v54l33XwPYa5gPYSeQNLA"
        # post 1QaEo1GxR9L
        print(f"Đang tìm kiếm URL trên 3d.iqdb.org: {image_url[:70]}...")
        try:
            result = client.search_url(image_url)
            print(f"\n✅ Tìm kiếm hoàn tất! Tổng cộng {len(result.matches)} kết quả.")
            if result.is_found:
                print(f"- Kết quả tốt nhất: {result.best_matches[0].url}")
            else:
                print("😔 Không tìm thấy kết quả nào.")
        except Exception as e:
            print(f"\n❌ Đã xảy ra lỗi: {e}")

def main():
    try:
        asyncio.run(async_2d_url_example())
        asyncio.run(async_2d_file_example())
        asyncio.run(async_3d_example())

        sync_2d_url_example()
        sync_2d_file_example()
        sync_3d_example()

    except KeyboardInterrupt:
        print("\n⛔ Đã hủy bởi người dùng.")

if __name__ == "__main__":
    main()