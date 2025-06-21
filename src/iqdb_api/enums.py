"""
Các enum được sử dụng trong IQDB API
"""
from enum import Enum


class MatchType(Enum):
    """Loại kết quả tìm kiếm"""
    BEST = "best"           # Best match
    ADDITIONAL = "additional"  # Additional match
    POSSIBLE = "possible"   # Possible match
    OTHER = "other"         # Other results (từ #more1/Give me more!)


class Rating(Enum):
    """Rating nội dung của hình ảnh"""
    UNRATED = "unrated"
    SAFE = "safe"
    QUESTIONABLE = "questionable"
    EXPLICIT = "explicit"


class Source(Enum):
    """Nguồn cơ sở dữ liệu hình ảnh"""
    # 2D Sources (www.iqdb.org)
    DANBOORU = "danbooru"
    KONACHAN = "konachan"
    YANDERE = "yandere"
    GELBOORU = "gelbooru"
    SANKAKU_CHANNEL = "sankaku_channel"
    ESHUUSHUU = "eshuushuu"
    THE_ANIME_GALLERY = "the_anime_gallery"
    ZEROCHAN = "zerochan"
    ANIME_PICTURES = "anime_pictures"
    
    # 3D Sources (3d.iqdb.org)
    THREEBOORU = "3dbooru"
    IDOL_COMPLEX = "idol_complex"