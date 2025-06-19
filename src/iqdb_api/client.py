"""
IQDB API clients - Main interface để tương tác với IQDB
"""
import asyncio
import time
from io import BytesIO
from pathlib import Path
from typing import Union, BinaryIO, Optional, List, Tuple
from urllib.parse import quote, urlparse
import hashlib
import random
import os

import httpx

from .models import SearchResult
from .parser import SearchResultParser
from .exceptions import ImageTooLargeException, IqdbApiException, HttpRequestFailedException, NotImageException, UserCancelledException


class IqdbClient:
    """
    Client để tương tác với IQDB (Internet Query Database)
    
    Hỗ trợ tìm kiếm hình ảnh ngược bằng URL hoặc file upload.
    """
    
    def __init__(
        self,
        base_url: str = "https://www.iqdb.org",
        rate_limit_seconds: float = 5.1,
        timeout: float = None,
        user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ignore_colors: bool = False,
        search_more: bool = False,
        prevent_bans: bool = True
    ):
        """
        Khởi tạo IQDB client
        
        Args:
            base_url: URL base của IQDB service (default: www.iqdb.org)
            rate_limit_seconds: Số giây delay giữa các request (default: 5.1s)
            timeout: Timeout cho HTTP requests (default: None, vô hạn)
            user_agent: User-Agent string để gửi với requests
            ignore_colors: Bỏ qua màu sắc trong tìm kiếm (default: False)
            search_more: Tìm kiếm nhiều hơn (default: False)
            prevent_bans: Sử dụng các biện pháp chống ban (default: True)
        """
        self.base_url = base_url.rstrip('/')
        self.rate_limit_seconds = rate_limit_seconds
        self.timeout = timeout
        self.user_agent = user_agent
        self.ignore_colors = ignore_colors
        self.search_more = search_more
        self.prevent_bans = prevent_bans
        
        # Rotating User-Agents để chống ban
        self._user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
        ]
        
        self._client = httpx.AsyncClient(
            timeout=timeout,
            headers={"User-Agent": self._get_random_user_agent()},
            follow_redirects=True
        )
        self._parser = SearchResultParser()
        self._last_request_time = 0.0
        self._rate_limit_lock = asyncio.Lock()
        
        # Session để giữ cookies và headers consistency
        self._session_id = self._generate_session_id()
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def close(self):
        """Đóng HTTP client"""
        await self._client.aclose()
    
    def _get_random_user_agent(self) -> str:
        """Lấy random User-Agent để chống ban"""
        if self.prevent_bans:
            return random.choice(self._user_agents)
        return self.user_agent
    
    def _generate_session_id(self) -> str:
        """Tạo session ID unique"""
        return hashlib.md5(f"{time.time()}{random.random()}".encode()).hexdigest()[:16]
    
    def _is_discord_media_url(self, url: str) -> bool:
        """Kiểm tra xem có phải Discord media URL"""
        parsed = urlparse(url)
        return parsed.hostname in ['cdn.discordapp.com', 'media.discordapp.net']
    
    def _is_special_media_url(self, url: str) -> bool:
        """Không domain nào là đặc biệt, luôn trả về False để luôn gửi URL trực tiếp cho IQDB"""
        return False
    
    async def _download_image_from_url(self, image_url: str) -> bytes:
        """
        Download ảnh từ URL với headers đặc biệt cho Discord và các services khác
        """
        headers = {
            "User-Agent": self._get_random_user_agent(),
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-Fetch-Dest": "image",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "cross-site"
        }
        
        # Thêm headers đặc biệt cho Discord
        if self._is_discord_media_url(image_url):
            headers.update({
                "Referer": "https://discord.com/",
                "Origin": "https://discord.com"
            })
        
        try:
            response = await self._client.get(image_url, headers=headers)
            response.raise_for_status()
            
            # Kiểm tra content type
            content_type = response.headers.get('content-type', '').lower()
            if not any(img_type in content_type for img_type in ['image/', 'application/octet-stream']):
                # Thử lại với headers khác
                headers['Accept'] = '*/*'
                response = await self._client.get(image_url, headers=headers)
                response.raise_for_status()
            
            return response.content
            
        except httpx.HTTPError as e:
            raise HttpRequestFailedException(f"Không thể download ảnh từ URL: {str(e)}") from e
    
    async def search_url_stream(self, image_url: str, force_download: bool = None, poll_interval: float = 2.0):
        """
        Tìm kiếm hình ảnh bằng URL, trả về tiến trình queue nếu IQDB quá tải (async generator).
        Yield từng SearchResult (queue_status != None nếu đang trong hàng đợi).
        """
        try:
            while True:
                result = await self.search_url(image_url, force_download=force_download)
                yield result
                if not result.queue_status:
                    break
                await asyncio.sleep(poll_interval)
        except (KeyboardInterrupt, asyncio.CancelledError):
            return
    
    async def search_file_stream(self, file_input: Union[str, Path, BinaryIO, bytes], poll_interval: float = 2.0):
        """
        Tìm kiếm hình ảnh bằng file upload, trả về tiến trình queue nếu IQDB quá tải (async generator).
        Yield từng SearchResult (queue_status != None nếu đang trong hàng đợi).
        """
        try:
            while True:
                result = await self.search_file(file_input)
                yield result
                if not result.queue_status:
                    break
                await asyncio.sleep(poll_interval)
        except (KeyboardInterrupt, asyncio.CancelledError):
            return
    
    async def search_url(self, image_url: str, force_download: bool = None) -> SearchResult:
        """
        Tìm kiếm hình ảnh bằng URL
        
        Args:
            image_url: URL của hình ảnh cần tìm kiếm
            force_download: Ép buộc download ảnh thay vì search bằng URL (default: auto-detect)
            
        Returns:
            SearchResult object chứa kết quả tìm kiếm
            
        Raises:
            IqdbApiException: Khi có lỗi trong quá trình tìm kiếm
        """
        try:
            if not image_url or not image_url.strip():
                raise ValueError("URL hình ảnh không được để trống")
            
            image_url = image_url.strip()
            
            # Quyết định có nên download hay search trực tiếp
            should_download = force_download
            if should_download is None:
                should_download = self._is_special_media_url(image_url)
            
            if should_download:
                # Download ảnh rồi search bằng file
                try:
                    image_data = await self._download_image_from_url(image_url)
                    return await self.search_file(image_data)
                except (HttpRequestFailedException, NotImageException) as e:
                    # Nếu download thất bại, thử search bằng URL
                    if not self._is_discord_media_url(image_url):  # Chỉ fallback nếu không phải Discord
                        return await self._search_url_direct(image_url)
                    raise e
            else:
                # Search trực tiếp bằng URL
                try:
                    return await self._search_url_direct(image_url)
                except NotImageException:
                    # Nếu gặp lỗi Not an image..., thử lại bằng cách tải về rồi upload file
                    image_data = await self._download_image_from_url(image_url)
                    return await self.search_file(image_data)
        except (KeyboardInterrupt, asyncio.CancelledError) as e:
            raise UserCancelledException("Tác vụ bị hủy bởi người dùng (KeyboardInterrupt/CanceledError).", e)
    
    def _should_debug(self):
        return os.environ.get("IQDB_DEBUG") == "1"
    
    async def _search_url_direct(self, image_url: str) -> SearchResult:
        """Search trực tiếp bằng URL (phương pháp gốc)"""
        # Apply rate limiting
        await self._apply_rate_limit()
        
        try:
            # Encode URL
            encoded_url = quote(image_url, safe=':/?#[]@!$&\'()*+,;=')
            
            # Prepare search parameters
            params = {"url": encoded_url}
            if self.ignore_colors:
                params["forcegray"] = "1"
            if self.search_more:
                params["service"] = "1,2,3,4,5,6,7,8,9,10,11,12,13"
            
            # Rotate User-Agent để chống ban
            if self.prevent_bans:
                self._client.headers["User-Agent"] = self._get_random_user_agent()
            
            # Make GET request
            response = await self._client.get(
                f"{self.base_url}/",
                params=params
            )
            response.raise_for_status()
            
            # Parse response
            return self._parser.parse_result(response.text, debug=self._should_debug(), debug_params=params if self._should_debug() else None)
            
        except httpx.HTTPError as e:
            raise IqdbApiException(f"HTTP request thất bại: {str(e)}") from e
        except Exception as e:
            if isinstance(e, IqdbApiException):
                raise
            raise IqdbApiException(f"Lỗi không xác định: {str(e)}") from e
    
    async def search_file(self, file_input: Union[str, Path, BinaryIO, bytes]) -> SearchResult:
        """
        Tìm kiếm hình ảnh bằng file upload
        
        Args:
            file_input: File để tìm kiếm, có thể là:
                       - Đường dẫn file (str hoặc Path)
                       - File-like object (BinaryIO)  
                       - Bytes data (bytes)
                       
        Returns:
            SearchResult object chứa kết quả tìm kiếm
            
        Raises:
            ImageTooLargeException: Khi file quá lớn (>8MB)
            IqdbApiException: Khi có lỗi trong quá trình tìm kiếm
        """
        try:
            # Chuẩn hóa input thành bytes
            file_data = await self._prepare_file_data(file_input)
            
            # Check file size (8MB limit)
            if len(file_data) > 8_388_608:  # 8MB in bytes
                raise ImageTooLargeException()
            
            # Apply rate limiting
            await self._apply_rate_limit()
            
            # Prepare form data
            form_data = self._prepare_form_data(file_data)
            search_data = self._prepare_search_data()
            
            # Rotate User-Agent để chống ban
            if self.prevent_bans:
                self._client.headers["User-Agent"] = self._get_random_user_agent()
            
            # Make POST request
            response = await self._client.post(
                f"{self.base_url}/",
                files=form_data,
                data=search_data
            )
            response.raise_for_status()
            
            # Parse response
            return self._parser.parse_result(response.text, debug=self._should_debug(), debug_params=search_data if self._should_debug() else None)
            
        except (KeyboardInterrupt, asyncio.CancelledError) as e:
            raise UserCancelledException("Tác vụ bị hủy bởi người dùng (KeyboardInterrupt/CanceledError).", e)
        except httpx.HTTPError as e:
            # Check for specific HTTP errors
            if hasattr(e, 'response') and e.response.status_code == 413:
                raise ImageTooLargeException() from e
            raise IqdbApiException(f"HTTP request thất bại: {str(e)}") from e
        except Exception as e:
            if isinstance(e, IqdbApiException):
                raise
            raise IqdbApiException(f"Lỗi không xác định: {str(e)}") from e
    
    async def _prepare_file_data(self, file_input: Union[str, Path, BinaryIO, bytes]) -> bytes:
        """Chuẩn hóa file input thành bytes"""
        if isinstance(file_input, (str, Path)):
            # Đọc từ file path
            with open(file_input, 'rb') as f:
                return f.read()
        elif isinstance(file_input, bytes):
            # Đã là bytes
            return file_input
        elif hasattr(file_input, 'read'):
            # File-like object
            if hasattr(file_input, 'seek'):
                file_input.seek(0)  # Reset position
            return file_input.read()
        else:
            raise ValueError("File input không hợp lệ. Hỗ trợ: str, Path, BinaryIO, bytes")
    
    def _prepare_form_data(self, file_data: bytes) -> dict:
        """Chuẩn bị form data cho POST request"""
        return {
            'file': ('image.jpg', BytesIO(file_data), 'image/jpeg')
        }
    
    def _prepare_search_data(self) -> dict:
        """Chuẩn bị data cho search với các options"""
        data = {}
        if self.ignore_colors:
            data["forcegray"] = "1"
        if self.search_more:
            data["service"] = "1,2,3,4,5,6,7,8,9,10,11,12,13"
        return data
    
    async def _apply_rate_limit(self):
        """Áp dụng rate limiting để tránh bị ban"""
        async with self._rate_limit_lock:
            current_time = time.time()
            time_since_last = current_time - self._last_request_time
            
            # Base rate limit
            sleep_time = max(0, self.rate_limit_seconds - time_since_last)
            
            # Thêm random delay để chống ban
            if self.prevent_bans:
                sleep_time += random.uniform(0.5, 2.0)  # Thêm 0.5-2 giây random
            
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
            
            self._last_request_time = time.time()
    
    def get_supported_image_formats(self) -> List[str]:
        """Lấy danh sách các format hình ảnh được hỗ trợ"""
        return [
            "JPEG", "JPG", "PNG", "GIF", "BMP", "WEBP", 
            "TIFF", "TIF", "SVG", "ICO", "PSD"
        ]
    
    def get_supported_sources(self) -> List[str]:
        """Lấy danh sách các source được hỗ trợ"""
        if "3d.iqdb.org" in self.base_url:
            return [
                "3Dbooru", "Idol Complex"
            ]
        else:
            return [
                "Danbooru", "Konachan", "Yande.re", "Gelbooru", 
                "Sankaku Channel", "e-shuushuu", "The Anime Gallery",
                "Zerochan", "Anime-Pictures"
            ]
    
    def get_search_info(self) -> dict:
        """Lấy thông tin về cấu hình search hiện tại"""
        return {
            "base_url": self.base_url,
            "ignore_colors": self.ignore_colors,
            "search_more": self.search_more,
            "prevent_bans": self.prevent_bans,
            "rate_limit_seconds": self.rate_limit_seconds,
            "supported_formats": self.get_supported_image_formats(),
            "supported_sources": self.get_supported_sources(),
            "max_file_size": "8MB",
            "session_id": self._session_id
        }


class Iqdb3dClient(IqdbClient):
    """
    Client cho IQDB 3D (3d.iqdb.org) - Chuyên về cosplay và hình ảnh 3D
    """
    
    def __init__(self, **kwargs):
        """
        Khởi tạo IQDB 3D client
        
        Args:
            **kwargs: Arguments được truyền cho IqdbClient
        """
        kwargs['base_url'] = kwargs.get('base_url', 'https://3d.iqdb.org')
        super().__init__(**kwargs)
    
    def _prepare_form_data(self, file_data: bytes) -> dict:
        """Chuẩn bị form data cho 3D IQDB với các field bổ sung"""
        # 3D IQDB cần thêm MAX_FILE_SIZE và url field
        files = {
            'file': ('image.jpg', BytesIO(file_data), 'image/jpeg')
        }
        
        return files
    
    async def search_file(self, file_input: Union[str, Path, BinaryIO, bytes]) -> SearchResult:
        """
        Tìm kiếm hình ảnh trên 3D IQDB bằng file upload
        
        Override để thêm các field đặc biệt cho 3D IQDB
        """
        try:
            # Chuẩn hóa input thành bytes
            file_data = await self._prepare_file_data(file_input)
            
            # Check file size
            if len(file_data) > 8_388_608:  # 8MB
                raise ImageTooLargeException()
            
            # Apply rate limiting
            await self._apply_rate_limit()
            
            # Prepare multipart data cho 3D IQDB
            files = {
                'file': ('image.jpg', BytesIO(file_data), 'image/jpeg')
            }
            
            data = {
                'MAX_FILE_SIZE': '8388608',  # 8MB limit
                'url': ''  # Empty URL field
            }
            
            headers = {
                'Origin': 'https://3d.iqdb.org'
            }
            
            # Make POST request với custom headers
            response = await self._client.post(
                f"{self.base_url}/",
                files=files,
                data=data,
                headers=headers
            )
            response.raise_for_status()
            
            # Parse response
            return self._parser.parse_result(response.text, debug=self._should_debug(), debug_params=data if self._should_debug() else None)
            
        except (KeyboardInterrupt, asyncio.CancelledError) as e:
            raise UserCancelledException("Tác vụ bị hủy bởi người dùng (KeyboardInterrupt/CanceledError).", e)
        except httpx.HTTPError as e:
            if hasattr(e, 'response') and e.response.status_code == 413:
                raise ImageTooLargeException() from e
            raise IqdbApiException(f"HTTP request thất bại: {str(e)}") from e
        except Exception as e:
            if isinstance(e, IqdbApiException):
                raise
            raise IqdbApiException(f"Lỗi không xác định: {str(e)}") from e


# Synchronous wrapper classes
class SyncIqdbClient:
    """Synchronous wrapper cho IqdbClient"""
    
    def __init__(self, **kwargs):
        self._async_client = IqdbClient(**kwargs)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """Đóng client"""
        asyncio.run(self._async_client.close())
    
    def search_url(self, image_url: str, force_download: bool = None) -> SearchResult:
        """Synchronous version của search_url"""
        return asyncio.run(self._async_client.search_url(image_url, force_download))
    
    def search_file(self, file_input: Union[str, Path, BinaryIO, bytes]) -> SearchResult:
        """Synchronous version của search_file"""
        return asyncio.run(self._async_client.search_file(file_input))

    def get_search_info(self) -> dict:
        """Lấy thông tin về cấu hình search hiện tại (synchronous)"""
        return self._async_client.get_search_info()


class SyncIqdb3dClient:
    """Synchronous wrapper cho Iqdb3dClient"""
    
    def __init__(self, **kwargs):
        self._async_client = Iqdb3dClient(**kwargs)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """Đóng client"""
        asyncio.run(self._async_client.close())
    
    def search_url(self, image_url: str, force_download: bool = None) -> SearchResult:
        """Synchronous version của search_url"""
        return asyncio.run(self._async_client.search_url(image_url, force_download))
    
    def search_file(self, file_input: Union[str, Path, BinaryIO, bytes]) -> SearchResult:
        """Synchronous version của search_file"""
        return asyncio.run(self._async_client.search_file(file_input))
