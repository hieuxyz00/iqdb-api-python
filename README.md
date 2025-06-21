# IQDB API Python

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Một thư viện Python đơn giản và mạnh mẽ để tìm kiếm hình ảnh ngược trên [IQDB.org](https://iqdb.org) và [3d.iqdb.org](https://3d.iqdb.org), được port và đồng bộ hóa chức năng với [thư viện C# gốc](https://github.com/ImoutoChan/IqdbApi).

## Tính năng chính

- **Tìm kiếm bằng URL hoặc File**: Linh hoạt cho mọi nhu cầu.
- **Async và Sync**: Hỗ trợ `asyncio` cho hiệu năng cao và API đồng bộ cho sự đơn giản.
- **Lấy thêm kết quả**: Hỗ trợ tùy chọn `include_more_results` để tự động thực hiện yêu cầu thứ hai và trả về toàn bộ kết quả từ trang "Give me more!".
- **Chế độ Debug**: Đặt biến môi trường `IQDB_DEBUG=1` để in toàn bộ HTML của mỗi response, giúp theo dõi quá trình retry và phân tích lỗi.
---
- 3d có thể không hoạt động
---

## Cài đặt

```bash
pip install git+https://github.com/hieuxyz00/iqdb-api-python.git
```

## Cách sử dụng

### Async

```python
import asyncio
from iqdb_api import IqdbClient, NoMatchFoundException

async def main():
    # Khởi tạo
    async with IqdbClient(
        include_more_results=True,  # Lấy thêm được nhiều kết quả hơn nhưng thường độ tương đồng thấp do là other results - khi bật nó sẽ có thể chờ lâu hơn vì cần 2 requests
        max_retries=5,              # Thử lại tối đa 5 lần
        retry_delay=2               # Chờ 2 giây giữa các lần thử
    ) as client:
        image_url = "https://danbooru.donmai.us/data/sample/sample-5a3c6f1c4424684a3c10a4594c21b38e.jpg"
        
        try:
            print("Đang tìm kiếm...")
            result = await client.search_url(image_url)
            
            print(f"\n✅ Tìm kiếm hoàn tất! Tổng cộng {len(result.matches)} kết quả.")
            if result.is_found:
                best_match = result.best_matches
                print(f"⭐️ Best Match: {best_match.url} ({best_match.similarity}%)")
            else:
                print("😔 Không tìm thấy kết quả khớp hoàn toàn.")

        except NoMatchFoundException:
            print("😔 Không có kết quả nào được tìm thấy.")
        except Exception as e:
            print(f"Đã xảy ra lỗi: {e}")

asyncio.run(main())
```

## Tùy chọn khởi tạo Client
```python
client = IqdbClient(
    ignore_colors=True,        # Bỏ qua màu sắc - phù hợp cho ảnh đen trắng
    include_more_results=True, # Lấy thêm nhiều kết quả other results hơn
    max_retries=3,             # Số lần thử lại (mặc định: 3)
    retry_delay=2.0,           # Thời gian chờ giữa các lần thử (mặc định: 2.0s)
    prevent_bans=True          # Kích hoạt chống ban (mặc định: True)
)
```

## License
Dự án này được cấp phép theo [Giấy phép MIT](LICENSE).

---

<div align="center">
Made with ❤️ by <strong>hieuxyz00 (aka hieuxyz)</strong>
</div>