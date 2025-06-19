# Changelog

Tất cả thay đổi quan trọng của project này sẽ được ghi lại trong file này.

Format dựa trên [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
và project này tuân theo [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-06-19

### Added
- ✨ **Initial release** của IQDB API Python
- 🔍 **Tìm kiếm hình ảnh ngược** trên IQDB.org
- 🌐 **Hỗ trợ tìm kiếm bằng URL** và **upload file**
- 🎯 **Hỗ trợ cả 2D và 3D IQDB**
  - `IqdbClient` cho www.iqdb.org (anime, manga, 2D images)
  - `Iqdb3dClient` cho 3d.iqdb.org (cosplay, 3D images)
- ⚡ **API async và sync**
  - `IqdbClient` và `Iqdb3dClient` cho async/await
  - `SyncIqdbClient` và `SyncIqdb3dClient` cho synchronous calls
- 🛡️ **Rate limiting tích hợp** với default 5.1 seconds delay
- 🎨 **Structured data models**
  - `SearchResult` cho kết quả tìm kiếm
  - `Match` cho từng kết quả match
  - `YourImage` cho thông tin ảnh đầu vào
  - `Resolution` cho độ phân giải
- 🔧 **Custom exceptions** cho error handling
  - `ImageTooLargeException` cho file > 8MB
  - `HttpRequestFailedException` cho HTTP errors
  - `NotImageException` cho invalid image files
  - `InvalidFileFormatException` cho unsupported formats
- 📦 **Type hints đầy đủ** cho better development experience
- 🧩 **Enums cho data consistency**
  - `MatchType`: BEST, ADDITIONAL, POSSIBLE, OTHER
  - `Rating`: UNRATED, SAFE, QUESTIONABLE, EXPLICIT  
  - `Source`: DANBOORU, GELBOORU, KONACHAN, etc.
- 📖 **Comprehensive documentation**
  - Detailed README với examples
  - API documentation với docstrings
  - Examples cho basic và advanced usage
- 🧪 **Test suite và code quality tools**
  - Basic tests cho models và functionality
  - Syntax validation
  - Black formatting, mypy type checking, flake8 linting
- 📦 **Modern Python packaging**
  - `pyproject.toml` cho modern packaging
  - Support cho Python 3.8.+
  - Development dependencies với `pip install -e ".[dev]"`

### ✨ Features
- 🎨 **Ignore Colors Option** - Bỏ qua màu sắc trong tìm kiếm với parameter `ignore_colors=True`
- 🔍 **Search More Sources** - Tìm kiếm trên nhiều database hơn với parameter `search_more=True`
- 🛡️ **Enhanced Ban Prevention** - Hệ thống chống ban nâng cao với `prevent_bans=True`

### Technical Details
- **Dependencies**: Read requirements.txt
- **Python Support**: 3.8.+
- **License**: MIT License
- **Converted from**: [IqdbApi C# library](https://github.com/ImoutoChan/IqdbApi)
- **User-Agent Rotation** - Xoay vòng User-Agent strings để chống fingerprinting
- **Session Management** - Unique session IDs cho mỗi client instance
- **Rate Limiting** - Thêm random delay để mô phỏng hành vi người dùng thực
- **Improved Headers** - Headers đặc biệt cho từng loại media service

### Supported Sources
#### 2D IQDB (www.iqdb.org)
- Danbooru
- Konachan
- Yande.re  
- Gelbooru
- Sankaku Channel
- e-shuushuu
- The Anime Gallery
- Zerochan
- Anime-Pictures

#### 3D IQDB (3d.iqdb.org) 
- 3Dbooru
- Idol Complex

### Examples & Documentation
- `examples/basic_usage.py` - Basic async/sync usage
- `examples/advanced_usage.py` - Advanced features, error handling, batch processing
- **Advanced Features Example** - `examples/advanced_features.py` demo tất cả tính năng mới
- **Ban Prevention Demo** - Batch search với chống ban
- **Info API Demo** - Cách lấy thông tin về formats và sources được hỗ trợ

### Configuration Options
- Customizable rate limiting (default: 5.1s)
- Custom timeout settings (default: 30s)
- Custom User-Agent strings
- Support cho cả HTTP và HTTPS

### 📊 Information APIs
- `get_supported_image_formats()` - Danh sách format hình ảnh được hỗ trợ
- `get_supported_sources()` - Danh sách source databases theo từng IQDB type
- `get_search_info()` - Thông tin chi tiết về cấu hình client hiện tại

---

## Development Notes

### Breaking Changes
- None (initial release)

### Deprecations  
- None (initial release)

---

*For more details, see the [README.md](README.md) and [documentation](docs/).*