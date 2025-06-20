# IQDB API Python

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-stable-brightgreen.svg)

Thư viện Python để tìm kiếm hình ảnh ngược trên [IQDB.org](https://iqdb.org) (Internet Query Database). Đây là phiên bản Python được chuyển đổi từ thư viện C# [IqdbApi](https://github.com/ImoutoChan/IqdbApi) gốc.

## ✨ Tính năng

### 🔍 Core Features
- **Tìm kiếm hình ảnh ngược** trên IQDB.org
- **Tìm kiếm bằng URL** hoặc **upload file**
- **Hỗ trợ cả 2D và 3D IQDB**
  - `www.iqdb.org`: Anime, manga, và hình ảnh 2D
  - `3d.iqdb.org`: Cosplay và hình ảnh 3D
- **API async và sync** - linh hoạt cho mọi use case

### 🛡️ Protection
- **Ban Prevention System** - Hệ thống chống ban nâng cao
- **User-Agent Rotation** - Xoay vòng UA strings
- **Random Delays** - Delay ngẫu nhiên giống người dùng thực
- **Session Management** - Unique session cho mỗi client

### 🎨 Search Options
- **Ignore Colors** - Tìm kiếm bỏ qua màu sắc (`ignore_colors=True`)
- **Search More Sources** - Tìm kiếm nhiều database hơn (`search_more=True`)
- **Rate Limiting Tích hợp** - Tránh bị ban IP
- **Custom Configuration** - Tùy chỉnh timeout, delay, headers

### 📊 Information APIs (build-in)
- **Supported Formats** - Lấy danh sách format được hỗ trợ
- **Supported Sources** - Danh sách database theo từng IQDB
- **Client Info** - Thông tin cấu hình hiện tại
- **Session Tracking** - Monitor search sessions

### 🔧 Technical Features
- **Structured Data** - Kết quả parse thành Python objects
- **Error Handling** chi tiết với custom exceptions
- **Type Hints** đầy đủ cho development experience tốt hơn
- **Modern Packaging** - Python 3.8+ support

## 🚀 Cài đặt

### Từ PyPI (comming soon)
```bash
pip install iqdb-api
```

### Từ source
```bash
pip install --no-cache-dir "iqdb-api-python @ git+https://github.com/hieuxyz00/iqdb-api-python.git"
```

### Dependencies
```bash
pip install -r requirements.txt
```

## 📖 Cách sử dụng cơ bản

### Async API (Khuyên dùng)

```python
import asyncio
from iqdb_api import IqdbClient

async def main():
    async with IqdbClient(prevent_bans=True) as client:
        image_url = "https://cdn.discordapp.com/attachments/123/456/image.jpg"
        # TODO: Sử dụng stream để hiển thị trạng thái queue real-time
        async for result in client.search_url_stream(image_url):
            if result.queue_status:
                msg = f"\r⏳ Đang trong hàng đợi IQDB... Vị trí: {result.queue_status.queue_position} | Ước tính chờ: {result.queue_status.estimated_wait}s "
                print(msg, end="", flush=True)
            else:
                print("\r", end="")
                print(f"\u2705 Thành công! Tìm thấy {len(result.matches)} kết quả")
                if result.best_matches:
                    print("\n⭐️ Best match:")
                    for match in result.best_matches:
                        print(f"- URL: {match.url}")
                break  # Kết thúc khi đã có kết quả thực sự

asyncio.run(main())
```

### Sync API (Dễ sử dụng)

```python
from iqdb_api import SyncIqdbClient

with SyncIqdbClient() as client:
    result = client.search_url("https://example.com/image.jpg")
    print(f"Tìm thấy {len(result.matches)} kết quả")
    # In ra best match (nếu có)
    if result.best_matches:
        print("\n⭐️ Best match:")
        for match in result.best_matches:
            print(f"- URL: {match.url}")
            print(f"  - Similarity: {match.similarity}% | Source: {match.source.value if match.source else None}")
    # In ra các match khác
    other_matches = [m for m in result.matches if not m.is_best_match]
    if other_matches:
        print("\n🔎 Other matches:")
        for i, match in enumerate(other_matches, 1):
            print(f"[{i}] {match.url}")
```

### 3D IQDB (Cosplay & 3D Images)

```python
from iqdb_api import Iqdb3dClient

async with Iqdb3dClient() as client:
    result = await client.search_url("https://example.com/cosplay.jpg")
    print(f"3D IQDB: {len(result.matches)} kết quả")
```

## 🎯 Advanced Features

### Ban Prevention & Rate Limiting
```python
from iqdb_api import IqdbClient

# Cấu hình chống ban nâng cao
async with IqdbClient(
    prevent_bans=True,           # Bật chống ban
    rate_limit_seconds=6.0,      # Tăng delay giữa requests
    user_agent="Custom-Bot/1.0"  # Custom User-Agent
) as client:
    
    # Batch search an toàn
    urls = ["url1.jpg", "url2.jpg", "url3.jpg"]
    for url in urls:
        result = await client.search_url(url)
        print(f"Found {len(result.matches)} matches")
        # Tự động delay với random jitter
```

### Search Options
```python
# Tìm kiếm nâng cao
async with IqdbClient(
    ignore_colors=True,    # Bỏ qua màu sắc - tốt cho ảnh đen trắng
    search_more=True,      # Tìm trên nhiều database hơn
    prevent_bans=True      # Chống ban với User-Agent rotation
) as client:
    
    result = await client.search_url("https://example.com/image.jpg")
    
    # Lấy thông tin client
    info = client.get_search_info()
    print(f"Session: {info['session_id']}")
    print(f"Supported formats: {info['supported_formats']}")
    print(f"Supported sources: {info['supported_sources']}")
```

## 📊 Cấu trúc dữ liệu

### SearchResult
```python
@dataclass
class SearchResult:
    searched_images_count: int           # Số ảnh đã tìm kiếm
    searched_in_seconds: float           # Thời gian tìm kiếm
    matches: List[Match]                 # Danh sách kết quả (best match luôn ở đầu nếu có)
    your_image: Optional[YourImage]      # Thông tin ảnh đầu vào
    
    # Properties tiện ích
    is_found: bool                       # Có tìm thấy kết quả chính xác?
    best_matches: List[Match]            # Kết quả tốt nhất (có thể nhiều hơn 1)
    additional_matches: List[Match]      # Kết quả bổ sung
    possible_matches: List[Match]        # Kết quả có thể
```

- `matches`: Best match (nếu có) luôn là phần tử đầu tiên, các match khác theo sau.
- Dùng `result.best_matches` để lấy danh sách best match, hoặc lọc thủ công từ `result.matches`.

### Match
```python
@dataclass
class Match:
    match_type: MatchType               # BEST, ADDITIONAL, POSSIBLE
    url: str                           # URL ảnh gốc
    preview_url: Optional[str]         # URL thumbnail
    similarity: Optional[float]        # Độ tương tự (%)
    resolution: Optional[Resolution]   # Độ phân giải
    source: Optional[Source]           # Nguồn (Danbooru, Gelbooru, v.v.)
    tags: Optional[List[str]]          # Tags (nếu có)
```

## 🎯 Ví dụ nâng cao

### Batch Processing
```python
import asyncio
from iqdb_api import IqdbClient

async def search_multiple_images(urls):
    async with IqdbClient() as client:
        tasks = [client.search_url(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"URL {i+1} lỗi: {result}")
            else:
                print(f"URL {i+1}: {len(result.matches)} kết quả")

urls = [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg",
    "https://example.com/image3.jpg"
]
asyncio.run(search_multiple_images(urls))
```

### Custom Configuration
```python
from iqdb_api import IqdbClient

# Custom rate limiting và timeout
async with IqdbClient(
    rate_limit_seconds=3.0,    # 3 giây giữa mỗi request
    timeout=60.0,              # 60 giây timeout
    user_agent="MyApp/1.0"     # Custom User-Agent
) as client:
    result = await client.search_url("https://example.com/image.jpg")
```

### Error Handling
```python
from iqdb_api import IqdbClient
from iqdb_api.exceptions import (
    ImageTooLargeException,
    HttpRequestFailedException,
    NotImageException
)

async with IqdbClient() as client:
    try:
        result = await client.search_file("large_image.jpg")
    except ImageTooLargeException:
        print("Ảnh quá lớn (>8MB)")
    except HttpRequestFailedException:
        print("Không thể download ảnh từ URL")
    except NotImageException:
        print("File không phải là ảnh hợp lệ")
```

## 🌐 Supported Sources

### 2D IQDB (www.iqdb.org)
- Danbooru
- Konachan  
- Yande.re
- Gelbooru
- Sankaku Channel
- e-shuushuu
- The Anime Gallery
- Zerochan
- Anime-Pictures

### 3D IQDB (3d.iqdb.org)
- 3Dbooru
- Idol Complex

## ⚙️ Configuration

### Rate Limiting
IQDB yêu cầu delay giữa các request để tránh bị ban. Default là 5.1 giây.

```python
# Thay đổi rate limit (cẩn thận!)
client = IqdbClient(rate_limit_seconds=3.0)  # Ngắn hơn có thể bị ban
```

### File Size Limits
- Maximum file size: **8MB**
- Supported formats: JPG, PNG, GIF, WebP (và hầu hết image formats)

## 🚨 Lưu ý quan trọng

1. **Rate Limiting**: Luôn tôn trọng rate limiting để tránh bị ban IP
2. **Terms of Service**: Tuân thủ [ToS của IQDB](https://iqdb.org/)  
3. **Fair Use**: Không spam requests hoặc sử dụng cho mục đích thương mại mà không được phép
4. **Network**: IQDB có thể chậm hoặc không khả dụng tạm thời

## 🔧 Development

### Setup Development Environment
```bash
# Clone repository
git clone https://github.com/hieuxyz00/iqdb-api-python.git
cd iqdb-api-python

# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate     # Windows

# Install dependencies
pip install -e ".[dev]"
```

### Running Tests
```bash
pytest tests/ -v
```

### Code Quality
```bash
# Format code
black src/ tests/ examples/

# Check types
mypy src/

# Lint
flake8 src/ tests/
```

## 📝 Changelog

### v1.0.0 (2025-06-19)
- ✨ Initial release
- 🔍 Support cho search URL và file upload
- 🎯 Hỗ trợ cả 2D và 3D IQDB
- ⚡ Async và sync APIs
- 🛡️ Rate limiting và error handling
- 📦 Type hints đầy đủ
- 🛡️ **Ban Prevention** - User-Agent rotation, random delays
- 🎨 **Advanced Search Options** - ignore_colors, search_more parameters
- 📊 **Information APIs**(build-in) - get_supported_formats(), get_supported_sources()
- 🧪 **Comprehensive Testing** - Unit tests, integration tests
- 📦 **Better Packaging** - Auto-publish to PyPI

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [ImoutoChan/IqdbApi](https://github.com/ImoutoChan/IqdbApi) - Thư viện C# gốc
- [IQDB.org](https://iqdb.org) - Dịch vụ tìm kiếm hình ảnh ngược tuyệt vời
- Community - Tất cả những người đã đóng góp và feedback

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/hieuxyz00/iqdb-api-python/issues)
- 💡 **Feature Requests**: [GitHub Issues](https://github.com/hieuxyz00/iqdb-api-python/issues)
- 📧 **Email**: hieuxyzsmtp@gmail.com

## 🚀 Quick Start với Discord

```bash
# Test link
python -c "
import asyncio
from iqdb_api import IqdbClient

async def test():
    async with IqdbClient(prevent_bans=True) as client:
        # Thay YOUR_TEST_URL bằng link thực
        result = await client.search_url('YOUR_TEST_URL')
        print(f'Found {len(result.matches)} matches!')

asyncio.run(test())
"
```

## 🛠️ Fallback tự động khi gặp lỗi định dạng ảnh

Nếu gặp lỗi kiểu `Not an image or image format not supported (server says it is application/octet-stream)` khi tìm kiếm bằng URL, thư viện sẽ tự động tải ảnh về rồi upload lại để tăng khả năng nhận diện.

## ⏳ Timeout vô hạn

Mặc định mọi request tới IQDB sẽ không timeout (timeout=None). Bạn có thể cấu hình timeout khi khởi tạo client nếu muốn.

## ⚠️ Xử lý KeyboardInterrupt & CancelledError (User Cancel)

Khi người dùng nhấn Ctrl+C hoặc task bị hủy (asyncio.CancelledError), IQDB API Python sẽ raise exception `UserCancelledException`.

Bạn nên catch exception này để xử lý UI/UX đẹp, ví dụ:

```python
from iqdb_api import IqdbClient, UserCancelledException
import asyncio

async def main():
    try:
        async with IqdbClient() as client:
            async for result in client.search_url_stream("https://example.com/image.jpg"):
                # ... xử lý kết quả ...
    except UserCancelledException as e:
        print(f"Đã hủy thao tác: {e}")
    except Exception as e:
        print(f"Lỗi khác: {e}")

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Đã hủy thao tác bởi người dùng (KeyboardInterrupt)")
```

- Sync API cũng sẽ raise `UserCancelledException` nếu bị Ctrl+C.
- Exception này luôn có message rõ ràng, không để traceback xấu ra ngoài.

### Ví dụ truy cập kết quả:

```python
for match in result.matches:
    print(match.url)
    print(match.preview_url)
```
---

<div align="center">
Made with ❤️ by <strong>hieuxyz00 (aka hieuxyz)</strong>
</div>