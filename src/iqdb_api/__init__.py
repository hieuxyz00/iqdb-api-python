"""
IQDB API Python - Thư viện tìm kiếm hình ảnh ngược trên IQDB.org

Thư viện này cung cấp giao diện Python để tương tác với dịch vụ tìm kiếm hình ảnh ngược
IQDB (Internet Query Database) tại iqdb.org và 3d.iqdb.org.
"""

from .client import IqdbClient, Iqdb3dClient, SyncIqdbClient, SyncIqdb3dClient
from .models import SearchResult, Match, YourImage, Resolution, SearchMoreInfo
from .enums import MatchType, Rating, Source
from .exceptions import (
    IqdbApiException,
    ImageTooLargeException,
    HttpRequestFailedException,
    NotImageException,
    InvalidFileFormatException,
    UserCancelledException,
    NoMatchFoundException,
    InvalidIqdbHtmlException,
    ParseException,
    ReadQueryResultException,
)

__version__ = "1.0.0"
__author__ = "hieuxyz"

__all__ = [
    # Clients
    "IqdbClient",
    "Iqdb3dClient",
    "SyncIqdbClient",
    "SyncIqdb3dClient",
    # Models
    "SearchResult",
    "Match",
    "YourImage",
    "Resolution",
    "SearchMoreInfo",
    # Enums
    "MatchType",
    "Rating",
    "Source",
    # Exceptions
    "IqdbApiException",
    "ImageTooLargeException",
    "HttpRequestFailedException",
    "NotImageException",
    "InvalidFileFormatException",
    "UserCancelledException",
    "NoMatchFoundException",
    "InvalidIqdbHtmlException",
    "ParseException",
    "ReadQueryResultException",
]