"""
IQDB API Python - Thư viện tìm kiếm hình ảnh ngược trên IQDB.org

Thư viện này cung cấp giao diện Python để tương tác với dịch vụ tìm kiếm hình ảnh ngược
IQDB (Internet Query Database) tại iqdb.org.
"""

from .client import IqdbClient, Iqdb3dClient, SyncIqdbClient, SyncIqdb3dClient
from .models import SearchResult, Match, YourImage, Resolution
from .enums import MatchType, Rating, Source
from .exceptions import (
    IqdbApiException,
    ImageTooLargeException,
    HttpRequestFailedException,
    NotImageException,
    InvalidFileFormatException,
    UserCancelledException,
)

__version__ = "1.0.0"
__author__ = "hieuxyz"

__all__ = [
    # Async Clients
    "IqdbClient",
    "Iqdb3dClient",
    
    # Sync Clients
    "SyncIqdbClient", 
    "SyncIqdb3dClient",
    
    # Models
    "SearchResult", 
    "Match",
    "YourImage",
    "Resolution",
    
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
]
