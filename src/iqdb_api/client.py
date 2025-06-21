import asyncio
import hashlib
import os
import random
import time
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, List, Dict, Tuple, Union, Callable, Awaitable

import httpx
from PIL import Image
from bs4 import BeautifulSoup

from .exceptions import *
from .models import SearchResult
from .parser import SearchResultParser


class IqdbClient:
    """
    Client để tương tác với IQDB (Internet Query Database).
    """

    _DEFAULT_USER_AGENTS = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"]
    _DEFAULT_ACCEPT_HEADERS = ["text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"]
    _DEFAULT_REFERERS = ["https://iqdb.org/", "https://www.google.com/"]

    def __init__(
        self,
        base_url: str = "https://www.iqdb.org",
        rate_limit_seconds: float = 5.1,
        timeout: float = None,
        ignore_colors: bool = False,
        include_more_results: bool = False,
        max_retries: int = 3,
        retry_delay: float = 2.0,
        prevent_bans: bool = True,
    ):
        """
        Khởi tạo IQDB client.

        Args:
            base_url (str): URL của dịch vụ IQDB.
            rate_limit_seconds (float): Thời gian chờ tối thiểu giữa các request.
            timeout (float): Thời gian chờ cho HTTP request (mặc định: không giới hạn).
            ignore_colors (bool): Bỏ qua màu sắc khi tìm kiếm.
            include_more_results (bool): Nếu True, sẽ thực hiện request thứ hai để lấy
                                         toàn bộ kết quả từ trang "Give me more!".
            max_retries (int): Số lần thử lại tối đa khi gặp lỗi 'Can't read query result'.
            retry_delay (float): Thời gian chờ (giây) giữa các lần thử lại.
            prevent_bans (bool): Kích hoạt các cơ chế chống bị chặn.
        """
        self.base_url = base_url.rstrip("/")
        self.rate_limit_seconds = rate_limit_seconds
        self.timeout = timeout
        self.ignore_colors = ignore_colors
        self.include_more_results = include_more_results
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.prevent_bans = prevent_bans
        self._client = httpx.AsyncClient(timeout=timeout, follow_redirects=True)
        self._parser = SearchResultParser()
        self._last_request_time = 0.0
        self._rate_limit_lock = asyncio.Lock()
        self._session_id = self._generate_session_id()

    async def __aenter__(self): return self
    async def __aexit__(self, exc_type, exc_val, exc_tb): await self.close()
    async def close(self): await self._client.aclose()

    async def _make_request_with_retries(self, request_func: Callable[[], Awaitable[httpx.Response]]) -> httpx.Response:
        """Thực hiện request với cơ chế thử lại."""
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                await self._apply_rate_limit()
                response = await request_func()
                response.raise_for_status()
                # Phân tích sơ bộ để phát hiện lỗi có thể thử lại
                self._parser._check_for_errors(BeautifulSoup(response.text, 'lxml'), response.text)
                return response
            except ReadQueryResultException as e:
                last_exception = e
                if attempt >= self.max_retries: break
                if self._should_debug():
                    print(f"DEBUG: Gặp lỗi có thể thử lại, đang chờ {self.retry_delay}s... (Lần {attempt + 1}/{self.max_retries})")
                await asyncio.sleep(self.retry_delay + random.uniform(0, 1))
        raise last_exception

    async def search_url(self, image_url: str) -> SearchResult:
        try:
            if not image_url or not image_url.strip(): raise ValueError("URL hình ảnh không được để trống")
            
            def request_lambda():
                params = {"url": image_url}
                params.update(self._prepare_search_data())
                headers = self._get_random_headers()
                return self._client.get(f"{self.base_url}/", params=params, headers=headers)
            
            response = await self._make_request_with_retries(request_lambda)
            result = self._parser.parse_result(response.text, self._should_debug())
            return await self._fetch_more_results_if_needed(result)
        except NotImageException as e:
            try:
                image_data = await self._download_image_from_url(image_url.strip())
                return await self.search_file(image_data)
            except Exception as download_exc: raise e from download_exc
        except (KeyboardInterrupt, asyncio.CancelledError) as e:
            raise UserCancelledException(inner_exception=e) from e

    async def search_file(self, file_input: Union[str, Path, BinaryIO, bytes]) -> SearchResult:
        try:
            file_data, file_name = self._prepare_file_data(file_input)
            if len(file_data) > 8 * 1024 * 1024: raise ImageTooLargeException()

            def request_lambda():
                files = {"file": (file_name, BytesIO(file_data), "image/jpeg")}
                data = self._prepare_search_data(is_file_upload=True)
                headers = self._get_random_headers()
                return self._client.post(f"{self.base_url}/", files=files, data=data, headers=headers)
            
            response = await self._make_request_with_retries(request_lambda)
            result = self._parser.parse_result(response.text, self._should_debug())
            return await self._fetch_more_results_if_needed(result)
        except (KeyboardInterrupt, asyncio.CancelledError) as e:
            raise UserCancelledException(inner_exception=e) from e

    async def _fetch_more_results_if_needed(self, initial_result: SearchResult) -> SearchResult:
        """
        Lấy trang "more results" nếu được yêu cầu, với cơ chế thử lại.
        Kết quả từ trang "more" sẽ thay thế hoàn toàn kết quả ban đầu.
        """
        if not self.include_more_results or not initial_result.search_more_info:
            return initial_result

        more_url = f"{self.base_url}/{initial_result.search_more_info.href.lstrip('/')}"
        
        try:
            headers = self._get_random_headers()
            response = await self._make_request_with_retries(
                lambda: self._client.get(more_url, headers=headers)
            )
            more_page_result = self._parser.parse_result(response.text, self._should_debug())
            return more_page_result
        except (ReadQueryResultException, httpx.HTTPError) as e:
            if self._should_debug():
                print(f"DEBUG: Yêu cầu 'more results' thất bại sau khi đã thử lại. Trả về kết quả ban đầu. Lỗi: {e}")
            return initial_result
            
    def _prepare_search_data(self, is_file_upload: bool = False) -> dict:
        data: Dict[str, Union[str, List[int]]] = {}
        if self.ignore_colors: data["forcegray"] = "1"
        data["service"] = [1, 2, 3, 4, 5, 6, 10, 11, 13]
        if is_file_upload: data["url"] = ""
        return data

    async def _download_image_from_url(self, image_url: str) -> bytes:
        headers = self._get_random_headers()
        try:
            response = await self._client.get(image_url, headers=headers)
            response.raise_for_status()
            return response.content
        except httpx.HTTPError as e: raise HttpRequestFailedException(f"Không thể tải ảnh từ URL: {e}", e) from e

    def _prepare_file_data(self, fi: Union[str, Path, BinaryIO, bytes]) -> Tuple[bytes, str]:
        if isinstance(fi, (str, Path)):
            with open(fi, "rb") as f: raw_data = f.read()
        elif isinstance(fi, bytes): raw_data = fi
        elif hasattr(fi, "read"):
            if hasattr(fi, "seek"): fi.seek(0)
            raw_data = fi.read()
        else: raise TypeError("Loại file input không hợp lệ.")
        return self._convert_image_if_needed(raw_data)

    def _convert_image_if_needed(self, image_data: bytes) -> Tuple[bytes, str]:
        supported = ["jpeg", "jpg", "png", "gif"]
        try:
            img = Image.open(BytesIO(image_data))
            fmt = (img.format or "").lower()
            if fmt in supported: return image_data, f"image.{'jpg' if fmt == 'jpeg' else fmt}"
            with BytesIO() as out:
                if img.mode not in ("RGB", "RGBA", "L"): img = img.convert("RGBA" if "A" in img.mode else "RGB")
                img.save(out, format="PNG")
                return out.getvalue(), "image.png"
        except Exception as e: raise InvalidFileFormatException(f"Không thể xử lý file ảnh: {e}", e) from e
    
    async def _apply_rate_limit(self):
        async with self._rate_limit_lock:
            since = time.time() - self._last_request_time
            sleep_for = self.rate_limit_seconds - since
            if self.prevent_bans: sleep_for += random.uniform(1.0, 2.5)
            if sleep_for > 0: await asyncio.sleep(sleep_for)
            self._last_request_time = time.time()
            
    def _get_random_headers(self) -> Dict[str, str]:
        if not self.prevent_bans: return {"User-Agent": self._DEFAULT_USER_AGENTS[0]}
        return {"User-Agent": random.choice(self._DEFAULT_USER_AGENTS), "Accept": random.choice(self._DEFAULT_ACCEPT_HEADERS), "Accept-Language": "en-US,en;q=0.9", "Referer": random.choice(self._DEFAULT_REFERERS)}

    def _generate_session_id(self) -> str: return hashlib.md5(f"{time.time()}{random.random()}".encode()).hexdigest()[:16]
    def _should_debug(self): return os.environ.get("IQDB_DEBUG") == "1"

class Iqdb3dClient(IqdbClient):
    """Client cho IQDB 3D (3d.iqdb.org)."""
    def __init__(self, **kwargs):
        kwargs["base_url"] = kwargs.get("base_url", "https://3d.iqdb.org")
        super().__init__(**kwargs)

    def _prepare_search_data(self, is_file_upload: bool = False) -> dict:
        if is_file_upload:
            return {"MAX_FILE_SIZE": "8388608", "url": ""}
        return {}

class SyncIqdbClient:
    """Wrapper đồng bộ (synchronous) cho IqdbClient."""
    def __init__(self, **kwargs): self._async_client = IqdbClient(**kwargs)
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): self.close()
    def close(self): asyncio.run(self._async_client.close())
    def search_url(self, url: str) -> SearchResult: return asyncio.run(self._async_client.search_url(url))
    def search_file(self, fi: Union[str, Path, BinaryIO, bytes]) -> SearchResult: return asyncio.run(self._async_client.search_file(fi))

class SyncIqdb3dClient:
    """Wrapper đồng bộ (synchronous) cho Iqdb3dClient."""
    def __init__(self, **kwargs): self._async_client = Iqdb3dClient(**kwargs)
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): self.close()
    def close(self): asyncio.run(self._async_client.close())
    def search_url(self, url: str) -> SearchResult: return asyncio.run(self._async_client.search_url(url))
    def search_file(self, fi: Union[str, Path, BinaryIO, bytes]) -> SearchResult: return asyncio.run(self._async_client.search_file(fi))